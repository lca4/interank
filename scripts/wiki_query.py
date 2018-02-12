#!/usr/bin/env python3

"""Utility script to fetch article/edit/contributor information from internal IDs from the Wiki site.

Each Wikipedia page, registered user and edit has a unique internal ID number assigned, as found in
the dumps. It can get tedious to track which ID corresponds to what page, so the script can be used
quickly query a number using the official Wiki API, especially useful when doing sanity checks.

Basic usage:

# check a user from the ID number:
./wiki_query.py -u 4573

# check article no 146 in the simple wikipedia
./wiki_query.py -a 146 -l simple

# check an edit in the English wikipedia
./wiki_query.py -e 532467 -l en
"""

import urllib.request, json
import argparse

def read_json(query_url):
    with urllib.request.urlopen(query_url) as url:
        data = json.loads(url.read().decode())
        return data


def get_edit_info(edit_ids, lang="simple"):
    """Uses Wikipedia API to query json data from the internal id of an edit."""
    if isinstance(edit_ids, int):
        query_url = r"https://{0}.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&revids={1}"\
                    .format(lang, edit_ids)
    else:
        query_url = r"https://{0}.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&revids={1}"\
                    .format(lang, "|".join(str(x) for x in edit_ids))

    return read_json(query_url)


def get_article_info(article_ids, lang="simple"):
    """Uses Wikipedia API to query json data from the internal id of an article page."""
    if isinstance(article_ids, int):
        query_url = r"https://{0}.wikipedia.org/w/api.php?action=query&format=json&prop=info&pageids={1}&inprop=url" \
                    .format(lang, article_ids)
    else:
        query_url = r"https://{0}.wikipedia.org/w/api.php?action=query&format=json&prop=info&pageids={1}&inprop=url" \
                    .format(lang, "|".join(str(x) for x in article_ids))

    return read_json(query_url)


def get_user_info(user_ids, lang="simple"):
    """Uses Wikipedia API to query json data from the internal id of a user."""
    if isinstance(user_ids, int):
        query_url = r"https://{0}.wikipedia.org/w/api.php?action=query&format=json&list=users&ususers={1}" \
                    r"&usprop=groups|editcount|gender|registration"\
                    .format(lang, user_ids)
    else:
        query_url = r"https://{0}.wikipedia.org/w/api.php?action=query&format=json&list=users&ususerids={1}" \
                    r"&usprop=groups|editcount|gender|registration"\
                    .format(lang, "|".join(str(x) for x in user_ids))

    return read_json(query_url)


def get_user_info_from_name(names, lang="simple"):
    """Uses Wikipedia API to query json data from the name of a user."""
    if isinstance(names, str):
        query_url = r"https://{0}.wikipedia.org/w/api.php?action=query&format=json&list=users&ususers={1}" \
                    r"&usprop=groups|editcount|gender|registration".format(lang, names)
    else:
        names = "|".join(names)
        query_url = r"https://{0}.wikipedia.org/w/api.php?action=query&format=json&list=users&ususers={1}" \
                    r"&usprop=groups|editcount|gender|registration".format(lang, names)

    return read_json(query_url)


argparser = argparse.ArgumentParser()
argparser.add_argument("-e", "--edit", action="append", default=[], type=int, help="Edit ids to view.")
argparser.add_argument("-a", "--article", action="append", default=[], type=int, help="Article ids to view.")
argparser.add_argument("-u", "--user", action="append", default=[], type=int, help="User ids to view.")
argparser.add_argument("-n", "--name", action="append", default=[], type=str, help="User names to view.")
argparser.add_argument("-l", "--lang", action="store", default="simple", required=False)

# Note: user r"http://en.wikipedia.org/?curid=REV_ID" to view any edit
if __name__ == "__main__":
    args = argparser.parse_args()

    if len(args.edit) > 0:
        print("Edits:\n")
        print(json.dumps(get_edit_info(args.edit, lang=args.lang), indent=4, sort_keys=True))

    if len(args.article) > 0:
        print("Articles:\n")
        print(json.dumps(get_article_info(args.article, lang=args.lang), indent=4, sort_keys=True))

    if len(args.user) > 0:
        print("Users (from id):\n")
        print(json.dumps(get_user_info(args.user, lang=args.lang), indent=4, sort_keys=True))

    if len(args.name) > 0:
        print("Users (from name):\n")
        print(json.dumps(get_user_info_from_name(args.name, lang=args.lang), indent=4, sort_keys=True))
