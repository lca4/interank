#!/usr/bin/env python3

"""Script for extracting a list of officially recognized bots from a wikipedia XML dump.

Wikipedia's policy on bots requires all bots to be marked with the {{bot}} flag on their
corresponding user pages (independent of language it seems). The script scans through the
dump for user pages including the flag, producing list of known bots, which usually make
small formality edits across many pages.
"""

import argparse
import xml.etree.ElementTree as ET
import csv

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
arg_parser.add_argument("-b", "--bots", required=True, help="File to store list of detected bots.")
args = arg_parser.parse_args()

parse_iterator = ET.iterparse(args.xml_file, events=('start', 'end'))
parse_iterator = iter(parse_iterator)

# keep track of the root element
event, root = next(parse_iterator)

bot_dict = {}

with open(args.bots, "w", encoding='utf-8') as f_edits:
    writer = csv.writer(f_edits, delimiter='#')

    # iterate through all nodes in the xml
    for event, elem in parse_iterator:
        if elem.tag == PAGE_TAG and event == "end":
            ns_tag = elem.find(NS_TAG)

            # user pages have namespace code 2
            if ns_tag is not None and ns_tag.text == "2":
                username = elem.find(TITLE_TAG)
                if username is None or username.text is None:
                    username = ""
                else:
                    # keep the user name without the "User:" prefix
                    # found in the titles of wikpedia user pages
                    colon_index = username.text.find(":")
                    if colon_index < 0:
                        username = username.text[5:]
                    else:
                        username = username.text[colon_index + 1:]

                for rev_elem in elem.iter(REVISION_TAG):
                    text_elem = rev_elem.find(TEXT_TAG)

                    if text_elem is not None:
                        text = text_elem.text
                        if text is None:
                            text = ""

                        # officially recognized bots should have the {{bot}} tag
                        # on their designated user page
                        bot_label = text.lower().find("{{bot")

                        if bot_label >= 0: # found a bot
                            # the bot tag can also contain some data about the owner,
                            # the wiki the bot originates from etc.
                            close_paren = text.find("}}", bot_label)
                            sep = text.find("|", bot_label)

                            if sep == -1 or sep > close_paren:
                                bot_dict[username] = "-"
                            else:
                                # find the matching parenthesis for the bot tag
                                count = 0
                                i = sep
                                while count >= 0 and i < len(text):
                                    if text[i] == "{":
                                        count += 1
                                    elif text[i] == "}":
                                        count -= 1
                                    i += 1

                                bot_dict[username] = text[sep + 1:i - 1]

            elem.clear()
            root.remove(elem)

    # write accumulated list of bots
    for k, v in bot_dict.items():
        writer.writerow((k, v))


