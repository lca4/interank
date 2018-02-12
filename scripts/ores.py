#!/usr/bin/env python3
"""
ORES (Objective Revision Evaluation Service) is Wikimedia's "ML-as-a-service"
web API to score edit quality and article quality. It is used by various other
tools that alleviate the work of moderators.

Resources:

- <https://www.mediawiki.org/wiki/ORES>
- <https://www.mediawiki.org/wiki/ORES/Examples>
- <https://ores.wikimedia.org/>
- <https://ores.wikimedia.org/v3/#/scoring>
- <https://ores.wmflabs.org/v2/scores/trwiki/reverted?model_info>
- <https://github.com/wiki-ai>
- <https://ores.wikimedia.org/versions/>

Example usage of this script:

    /ores.py --model reverted trwiki 1001125 1082825

To see the supported languages, visit <https://ores.wikimedia.org/v3/scores/>.
"""

import argparse
import json
import urllib.request


MODELS = ["damaging", "goodfaith", "reverted"]
URL_TEMPLATE = ("https://ores.wikimedia.org/v3/scores/{lang}"
        "?revids={revids}&models={models}")


def main(lang, revisions, model):
    revids = "|".join(str(r) for r in revisions)
    if model is None:
        model = "|".join(MODELS)
    url = URL_TEMPLATE.format(lang=lang, revids=revids, models=model)
    with urllib.request.urlopen(url) as f:
        data = json.loads(f.read().decode())
    formatted = json.dumps(data, indent=4, sort_keys=True)
    print(formatted)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("lang")
    parser.add_argument("revisions", nargs="+", type=int)
    parser.add_argument("--model", choices=MODELS)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    main(args.lang, args.revisions, args.model)
