#!/usr/bin/env python3

"""Computes the qualities (based on the Adler, 2008 paper) of each edit in a Wikipedia dump.

Subsequent edits by the same user in a short period of time are merged into one as described
in the paper. The script produces a CSV file with the quality of each edit along with some other
basic

Edit ID#Timestamp#Article ID#User ID#Quality#Edit delta#Length of article before edit#Length of
article after edit#The number of upcoming edits considered

The deltas are computed in characters, unlike the original article (which uses words as a unit).
The last number signifies how many future edits the algorithm managed to user when computing the
quality (therefore has to between 0-10), might be useful for excluding edge cases.
"""

import multiprocessing as mp
import queue
import itertools
import time
import sys
import argparse
import edlib
import xml.etree.ElementTree as ET
import datetime
import calendar
import csv
import os

NEW_EDIT_TIME = datetime.timedelta(hours=3)

# constants for the wiki dump xml
NAMESPACE = "{http://www.mediawiki.org/xml/export-0.10/}"
PAGE_TAG = NAMESPACE + "page"
NS_TAG = NAMESPACE + "ns"
TITLE_TAG = NAMESPACE + "title"
REDIRECT_TAG = NAMESPACE + "redirect"
TEXT_TAG = NAMESPACE + "text"
ID_TAG = NAMESPACE + "id"
IP_TAG = NAMESPACE + "ip"
CONTRIBUTOR_TAG = NAMESPACE + "contributor"
REVISION_TAG = NAMESPACE + "revision"
TIMESTAMP_TAG = NAMESPACE + "timestamp"
USERNAME_TAG = NAMESPACE + "username"
WIKI_TAG = NAMESPACE + "mediawiki"

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("xml_file", metavar="XML file", help="The XML file to be processed.")
arg_parser.add_argument("-p", "--processes", required=True, type=int, action="store", help="Number of parallel processes.")
arg_parser.add_argument("-t", "--threshold", required=False, type=int,
                        action="store", help="The threshold date to separate training/test sets.")
args = arg_parser.parse_args()


def distance(s1, s2):
    """Compute the Levenshtein edit distance between two strings."""
    if len(s1) == 0 or len(s2) == 0:
        return max(len(s1), len(s2))
    else:
        return edlib.align(s1, s2)["editDistance"]


def process_edit(q, editid, userid, articleid, timestamp, text_prev, text_final,
                 text_upcoming, timestamps_upcoming, split_threshold):
    """Produces the entry for a single edit, for multithreaded use."""
    quality = 0
    delta_edit = distance(text_prev, text_final)

    restrict_computation = (split_threshold is not None) and \
                           (timestamp < split_threshold)
    future_edits = 0

    if delta_edit > 0 and len(text_upcoming) > 0:
        for i in range(len(text_upcoming)):
            if (not restrict_computation) or \
               calendar.timegm(timestamps_upcoming[i].timetuple()) < split_threshold:
                quality += (distance(text_prev, text_upcoming[i]) \
                            - distance(text_final, text_upcoming[i]))\
                           / delta_edit
                future_edits += 1

        if future_edits > 0:
            quality /= future_edits

    q.put((editid, timestamp, articleid, userid, quality, delta_edit,
           len(text_prev), len(text_final), future_edits))

print("//{}".format(args.xml_file))

# number of processes to use
NUMBER_PROCESSES = args.processes

# whether should 'cleanly' separate the computations into test/training sets
THRESHOLD_TIMESTAMP = args.threshold

# time start in seconds
time_start = time.time()

## open XML file
parse_iterator = ET.iterparse(args.xml_file, events=('end', 'start'))
parse_iterator = iter(parse_iterator)

# keep track of the root element
event, root = next(parse_iterator)

rev_count = 0
results = []
with mp.Pool(NUMBER_PROCESSES) as pool:
    manager = mp.Manager()
    q = manager.Queue()
    writer = csv.writer(sys.stdout, delimiter='#')

    edits11 = [""]
    ids11 = ["-"]
    users11 = [-1]
    timestamps11 = ["-"]

    # iterate through all nodes in the xml
    for event, elem in parse_iterator:
        if elem.tag == REVISION_TAG and event == "end":
            # article_elem = elem.getparent()

            # print("end edit: %d" % int(elem.find(ID_TAG).text))

            ns = article_elem.find(NS_TAG)
            redirect = elem.find(REDIRECT_TAG)

            if ns is not None and ns.text == "0" and redirect == None:
                edit_id = int(elem.find(ID_TAG).text)
                article_id = int(article_elem.find(ID_TAG).text)
                edit_text = elem.find(TEXT_TAG).text
                timestamp = datetime.datetime.strptime(elem.find(TIMESTAMP_TAG).text, "%Y-%m-%dT%H:%M:%SZ")
                contributor_elem = elem.find(CONTRIBUTOR_TAG)

                user_id = None
                if contributor_elem is not None:
                    id_elem = contributor_elem.find(ID_TAG)
                    if id_elem is not None:  # registered user with id
                        if id_elem.text == "0":
                            if contributor_elem.find(USERNAME_TAG).text is not None:
                                user_id = "r" + id_elem.text + "|" + contributor_elem.find(USERNAME_TAG).text
                            else:
                                user_id = None
                        else:
                            user_id = "r" + id_elem.text

                    ip_elem = contributor_elem.find(IP_TAG)
                    if ip_elem is not None:  # unregistered user with ip
                        user_id = "u" + ip_elem.text

                if edit_text is None:  # likely a result of vandalism
                    edit_text = ""

                # arrived at a new article node
                if user_id is None:
                    if users11[-1] is not None or timestamp - timestamps11[-1] > NEW_EDIT_TIME:
                        ids11.append(edit_id)
                        edits11.append(edit_text)
                        users11.append(user_id)
                        timestamps11.append(timestamp)
                    else:
                        edits11[-1] = edit_text
                        ids11[-1] = edit_id
                        users11[-1] = user_id
                        timestamps11[-1] = timestamp
                elif user_id != users11[-1] or timestamp - timestamps11[-1] > NEW_EDIT_TIME:
                    ids11.append(edit_id)
                    edits11.append(edit_text)
                    users11.append(user_id)
                    timestamps11.append(timestamp)
                elif user_id == users11[-1] and timestamp - timestamps11[-1] <= NEW_EDIT_TIME:
                    edits11[-1] = edit_text
                    ids11[-1] = edit_id
                    users11[-1] = user_id
                    timestamps11[-1] = timestamp

                # accumulated enough for a quality computation
                if len(edits11) >= 12:
                    if users11[1] is not None:
                        results.append(
                            pool.apply_async(process_edit, args=(q, ids11[1],
                                                                 users11[1],
                                                                 article_id,
                                                                 calendar.timegm(timestamps11[1].timetuple()),
                                                                 edits11[0],
                                                                 edits11[1],
                                                                 edits11[2:],
                                                                 timestamps11[2:],
                                                                 THRESHOLD_TIMESTAMP)))

                    edits11.pop(0)
                    users11.pop(0)
                    ids11.pop(0)
                    timestamps11.pop(0)

            article_elem.remove(elem)
            rev_count += 1

            if rev_count % 1000 == 0:
                rev_count = 0
                sys.stdout.flush()

                left = len(results)
                ended = 0
                while left > 16 * NUMBER_PROCESSES:
                    results = list(itertools.filterfalse(lambda x: x.ready(), results))
                    left2 = len(results)
                    ended += left - left2
                    left = left2

                while ended > 0:
                    try:
                        res = q.get(block=False)
                        ended -= 1
                        writer.writerow(res)
                    except queue.Empty:
                        pass

        elif elem.tag == PAGE_TAG and event == "start":
            article_elem = elem

            edits11 = [""]
            ids11 = ["-"]
            users11 = [-1]
            timestamps11 = ["-"]

            # print("start art: %d" % int(article_elem.find(ID_TAG).text))

        elif elem.tag == PAGE_TAG and event == "end":
            # print("end art: %d" % int(article_elem.find(ID_TAG).text))

            article_id = int(article_elem.find(ID_TAG).text)
            # consume the remaining revisions
            while len(edits11) >= 2:
                if users11[1] is not None:
                    results.append(
                        pool.apply_async(process_edit, args=(q, ids11[1],
                                                             users11[1],
                                                             article_id,
                                                             calendar.timegm(timestamps11[1].timetuple()),
                                                             edits11[0],
                                                             edits11[1],
                                                             edits11[2:],
                                                             timestamps11[2:],
                                                             THRESHOLD_TIMESTAMP)))

                edits11.pop(0)
                users11.pop(0)
                ids11.pop(0)
                timestamps11.pop(0)

            elem.clear()
            root.remove(elem)


    # end of the mediawiki dump
    while len(edits11) >= 2:
        if users11[1] is not None:
            results.append(
                pool.apply_async(process_edit, args=(q, ids11[1],
                                                     users11[1],
                                                     article_id,
                                                     calendar.timegm(timestamps11[1].timetuple()),
                                                     edits11[0],
                                                     edits11[1],
                                                     edits11[2:],
                                                     timestamps11[2:],
                                                     THRESHOLD_TIMESTAMP)))

        edits11.pop(0)
        users11.pop(0)
        ids11.pop(0)
        timestamps11.pop(0)

    # wait for the completion of remaining results
    left = len(results)
    ended = 0
    while left > 0:
        results = list(itertools.filterfalse(lambda x: x.ready(), results))
        left2 = len(results)
        ended += left - left2
        left = left2

    while ended > 0:
        try:
            res = q.get(block=False)
            ended -= 1
            writer.writerow(res)
        except queue.Empty:
            pass


# end time, in seconds
time_end = time.time()
