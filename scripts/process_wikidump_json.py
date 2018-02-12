#!/usr/bin/env python
"""Extract URLs from a WikiMedia dump JSON file.

This short script extracts a list of URLs from the JSON description of a
WikiMedia dump, as available on <https://www.wikimedia.org>.
"""
import argparse
import json


URL_TEMPLATE = "https://dumps.wikimedia.org{}"


def main(path):
    with open(path) as f:
        data = json.load(f)
    for name, obj in data["jobs"]["metahistorybz2dump"]["files"].items():
        print(URL_TEMPLATE.format(obj["url"]))


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    main(args.path)
