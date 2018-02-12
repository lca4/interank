#!/usr/bin/env python3
import argparse
import glob
import os.path


PYTHON = "/dfs/ephemeral/storage/maystre/miniconda3/bin/python"

HEADER = """
# Check condor primer (standard / vanilla).
Universe = vanilla

InputDir = /dfs/ephemeral/storage/maystre
OutputDir = /dfs/ephemeral/storage/maystre/condor-out

# Absolute path to executable (not relative to InitialDir).
Executable = {executable}

# Do not edit.
InitialDir = $(InputDir)

Error  = $(OutputDir)/err.$(Process)
Log    = $(OutputDir)/log.$(Process)
Output = $(OutputDir)/out.$(Process)

# This is to be turned on.
GetEnv = true

# IMPORTANT!!!! Otherwise you get screwed!
notification = Never

# Require NFS and `ephemeral` DFS.
requirements = nfshome_storage==true && ephemeral_storage==true

### END OF HEADER"""

JOB_TPL = """
Arguments = ./compute_quality.py {xml_path} --processes=2 \
    --threshold={threshold}
Queue 1"""


def main(input_dir, threshold):
    print(HEADER.format(executable=PYTHON))
    for path in glob.glob(os.path.join(input_dir, "*xml*")):
        path = os.path.abspath(path)
        print(JOB_TPL.format(xml_path=path, threshold=threshold))


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("--threshold", default="")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    main(args.input_dir, args.threshold)
