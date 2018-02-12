#!/usr/bin/env python3
"""Get ORES predictions given a raw test set file.

This script can be used to collect ORES predictions for a given set of
revisions, parsed from a raw data file. Example:

    ./collect_ores.py trwiki path/to/raw-test.txt > output.txt

The flag --ignore-from `path/to/output.txt` can be used to resume the
collection after an interruption without re-querying revisions that have
already been collected.
"""
import argparse
import collections
import json
import urllib.request


MODELS = ["damaging", "goodfaith", "reverted"]
URL_TEMPLATE = ("https://ores.wikimedia.org/v3/scores/{lang}"
        "?revids={revids}&models={models}")


def get_revids(path):
    revids = list()
    with open(path) as f:
        for line in f:
            data = json.loads(line.strip())
            revids.extend(data.keys())
    return set(revids)


def main(lang, testfile, chunk_size, model, ignore_from):
    if model is None:
        model = "|".join(MODELS)
    revids = set()
    with open(testfile) as f:
        for line in f:
            revid, _ = line.strip().split("#", 1)
            revids.add(revid)
    if ignore_from is not None:
        ignored = get_revids(ignore_from)
        revids = list(filter(lambda x: x not in ignored, revids))
    else:
        revids = list(revids)
    for i in range(0, len(revids), chunk_size):
        chunk = revids[i:i+chunk_size]
        rids = "|".join(r for r in chunk)
        url = URL_TEMPLATE.format(lang=lang, revids=rids, models=model)
        with urllib.request.urlopen(url) as f:
            res = json.loads(f.read().decode())
        scores = res[lang]["scores"]
        print(json.dumps(scores))


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("lang")
    parser.add_argument("testfile")
    parser.add_argument("--chunk-size", type=int, default=50)
    parser.add_argument("--model", choices=MODELS)
    parser.add_argument("--ignore-from")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    main(
            args.lang, args.testfile, args.chunk_size, args.model,
            args.ignore_from)
