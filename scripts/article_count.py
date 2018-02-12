#!/usr/bin/env python3

"""Basic analysis script that can produce statistics and summaries.

The script can generate summary statistics for the overall wiki (Edit/article/user counts,
average edits per user etc.) and also produce more detailed data per article/user
basis in the form of a CSV file.

Note that for more detailed results for individual edits, compute_quality makes more sense
in terms of performance and data."""

import xml.etree.ElementTree as ET
import argparse
import sys
import datetime
import calendar

# parse command line arguments
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("what", choices=["users", "articles"])
arg_parser.add_argument("xml_file", metavar="XML file", help="The XML file to be processed.")
args = arg_parser.parse_args()

# flags for the computation
FLAG_INCLUDE_DISAMB = True  # include the disambiguation pages in the count?
FLAG_INCLUDE_REDIRECT = True
XML_FILE = args.xml_file

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


def is_disambiguation_page(elem, lang=None):
    """Given an xml element, decide if disambiguation page."""

    # TODO can distiguish these tags better
    disambiguation_tags = {"simple": ["{{disambig}}"],
                           "bar": ["{{Begriffsklärung}}"],
                           "tr": ["{{anlam ayrımı}}"],
                           "fr": ["{{Homonymie}}", "{{homonymie}}"],
                           "en": ["{{Disambiguation", "{{disambiguation", "disambiguation}}"]}

    tags = []
    if lang is None:
        tags = [item for sublist in disambiguation_tags.values() for item in sublist]
    else:
        tags = disambiguation_tags[lang]

    for text_elem in elem.iter(tag=TEXT_TAG):
        if text_elem.text is not None:
            for tag in tags:
                if tag in text_elem.text:
                    return True

    return False


def get_contributor(rev_elem):
    """Given revision element return user data."""

    contributor_elem = rev_elem.find(CONTRIBUTOR_TAG)
    if contributor_elem is not None:
        id_elem = contributor_elem.find(ID_TAG)
        if id_elem is not None:  # registered user with id
            if id_elem.text == "0":
                if contributor_elem.find(USERNAME_TAG).text is not None:
                    return ("r" + id_elem.text + "|" + contributor_elem.find(USERNAME_TAG).text,
                            contributor_elem.find(USERNAME_TAG).text)
                else:
                    return None, None
            else:
                return ("r" + id_elem.text,
                        contributor_elem.find(USERNAME_TAG).text)

        ip_elem = contributor_elem.find(IP_TAG)
        if ip_elem is not None:  # unregistered user with ip
            return ("u" + ip_elem.text, "-")

    # no id data (probably due to account deletion)
    return None, None


def process_user_stats(article_elem):
    editors = set()
    for rev_elem in article_elem.iter(REVISION_TAG):
        contr_id, contr_name = get_contributor(rev_elem)

        # ignore deleted users
        if contr_id is not None:
            date_edit_ts = calendar.timegm(datetime.datetime.strptime(rev_elem.find(TIMESTAMP_TAG).text, "%Y-%m-%dT%H:%M:%SZ")
                                           .timetuple())

            if contr_id in user_stats:
                name, first_edit, last_edit, edits, articles = user_stats[contr_id]

                first_edit = min(first_edit, date_edit_ts)
                last_edit = max(last_edit, date_edit_ts)

                if contr_id not in editors:
                    editors.add(contr_id)
                    articles += 1

                edits += 1

                user_stats[contr_id] = (contr_name, first_edit, last_edit, edits, articles)
            else:
                user_stats[contr_id] = (contr_name, date_edit_ts, date_edit_ts, 1, 1)
                editors.add(contr_id)


def process_article_stats(article_elem):
    editors = set()
    n_edits = 0

    article_name = article_elem.find(TITLE_TAG).text
    article_id = int(article_elem.find(ID_TAG).text)

    for rev_elem in article_elem.iter(REVISION_TAG):
        contr_id, contr_name = get_contributor(rev_elem)
        if contr_id is None:
            contr_id = "-"

        editors.add(contr_id)
        n_edits += 1

    print("{}#{}#{}#{}".format(article_id, article_name, n_edits, len(editors)))


## open XML file
parse_iterator = ET.iterparse(XML_FILE, events=('end','start'))
parse_iterator = iter(parse_iterator)

user_stats = {}

# get the root node of the XML
event, root = next(parse_iterator)
# while event != "start":
#     event, root = next(parse_iterator)

# iterate through all nodes in the xml
for event, elem in parse_iterator:
    if elem.tag == PAGE_TAG and event == "end":
        # check to see if an article
        ns = elem.find(NS_TAG)
        title = elem.find(TITLE_TAG)

        # check if page is an article, articles live in the mediawiki
        # namespace number 0
        if ns is not None and ns.text == "0":
            # check for redirects
            if FLAG_INCLUDE_REDIRECT or elem.find(REDIRECT_TAG) is None:
                # check for disambiguation pages
                if FLAG_INCLUDE_DISAMB or not is_disambiguation_page(elem):

                    if args.what == "users":
                        process_user_stats(elem)
                    else:  # args.what == "articles"
                        process_article_stats(elem)

        # delete already processed nodes for memory
        elem.clear()
        root.clear()

if args.what == "users":
    for u in user_stats:
        print("{}#{}#{}#{}#{}#{}".format(u, *user_stats[u]))
