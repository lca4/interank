#!/usr/bin/env python3
"""Combine user information from multiple Condor outputs.

This script is useful in order to build a single, unified `users.txt` file from
the output of multiple Condor jobs."""
import argparse


def parse_line(line):
    idx, name, first_edit, last_edit, n_edits, n_arts = line.strip().split("#")
    return (idx, name,
            int(first_edit), int(last_edit), int(n_edits), int(n_arts))


def main(files):
    data = dict()
    for path in files:
        with open(path) as f:
            for line in f:
                (idx, name, first_edit, last_edit, n_edits, n_arts) = line.strip().split("#")
                first_edit, last_edit, n_edits, n_arts = map(
                        int, (first_edit, last_edit, n_edits, n_arts))
                if idx not in data:
                    data[idx] = [name, first_edit, last_edit, n_edits, n_arts]
                else:
                    data[idx][0] = name
                    data[idx][1] = min(data[idx][1], first_edit)
                    data[idx][2] = max(data[idx][2], last_edit)
                    data[idx][3] += n_edits
                    data[idx][4] += n_arts
    for idx, elems in data.items():
        print("{}#{}".format(idx, "#".join(str(x) for x in elems)))


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    main(args.files)
