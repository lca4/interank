"""Utility script to build a small random batch of articles from a full dump."""

import xml.etree.ElementTree as ET
import argparse
import random

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("xml_file", metavar="XML file", help="The XML file to be processed.")
arg_parser.add_argument("-o", "--out", required=True, help="Output XML file.")
arg_parser.add_argument("-f", "--full", action="store_true", help="Do a full sweep across the dump.")
arg_parser.add_argument("-c", "--count", type=int, required=False, help="Number of articles to save")
arg_parser.add_argument("-p", "--prob", type=float, required=False, help="Probability of keeping an article.")
args = arg_parser.parse_args()

NAMESPACE = "{http://www.mediawiki.org/xml/export-0.10/}"
PAGE_TAG = NAMESPACE + "page"
NS_TAG = NAMESPACE + "ns"
TITLE_TAG = NAMESPACE + "title"
REDIRECT_TAG = NAMESPACE + "redirect"
TEXT_TAG = NAMESPACE + "text"

if args.count is None and args.prob is None:
    print("Inconsistent parameters.")
    exit()
elif args.full is not None and (args.count is not None or args.prob is None):
    print("Inconsistent parameters.")
    exit()


# include the disambiguation pages in the count?
FLAG_INCLUDE_DISAMB = True

# xml file to output
OUTPUT_FILE = args.out
ARTICLES_TO_SAVE = args.count
PROB = args.prob
FULL_SWEEP = args.full

if ARTICLES_TO_SAVE is None:
    ARTICLES_TO_SAVE = 0

def is_disambiguation_page(elem, lang=None):
    """Given an xml element, decide if disambiguition page."""

    # TODO can distiguish these tags better
    disambiguation_tags = {"simple": ["{{disambig}}"],
                           "bar": ["{{Begriffsklärung}}"],
                           "tr": ["{{anlam ayrımı}}"],
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


parse_iterator = ET.iterparse(args.xml_file, events=('start', 'end', 'start-ns', 'end-ns'))
parse_iterator = iter(parse_iterator)

article_count = ARTICLES_TO_SAVE
count = 0

event, root = next(parse_iterator)
while event != "start":
    event, root = next(parse_iterator)

for event, elem in parse_iterator:
    if event == 'end':
        if elem.tag == PAGE_TAG:
            # check to see if an article
            ns = elem.find(NS_TAG)
            title = elem.find(TITLE_TAG)

            # check if page is an article
            if ns is not None and ns.text == "0":
                # check for redirects
                if elem.find(REDIRECT_TAG) is None:
                    # check for disambiguition pages
                    if FLAG_INCLUDE_DISAMB or not is_disambiguation_page(elem):
                        if random.random() > PROB:
                            elem.clear()
                            root.remove(elem)
                        else:
                            article_count = article_count - 1
                            count += 1
                    else:
                        elem.clear()
                        root.remove(elem)
                else:
                    elem.clear()
                    root.remove(elem)
            else:
                elem.clear()
                root.remove(elem)

        if article_count <= 0 and not FULL_SWEEP:
            break

# clear the last element
for article in root.iter(PAGE_TAG):
    pass
root.remove(article)

xmlfile = open(OUTPUT_FILE, "wb")
xmlfile.write(ET.tostring(root))
xmlfile.close()

print("Articles saved: %d" % count)
