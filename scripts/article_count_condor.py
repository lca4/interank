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
requirements = ((nfshome_storage == true) \
    && (ephemeral_storage == true) \
    && (SlotID == 1) \
    && ((realmachine == "pcdr17-99.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-100.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-101.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-102.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-103.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-104.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-105.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-106.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-108.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-109.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-110.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-111.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-112.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-113.icsil1.epfl.ch") \
        || (realmachine == "pcdr17-114.icsil1.epfl.ch")))

### END OF HEADER"""

JOB_TPL = """
Arguments = ./article_count.py {what} {xml_path}
Queue 1"""


def main(what, input_dir):
    print(HEADER.format(executable=PYTHON))
    for path in glob.glob(os.path.join(input_dir, "*xml*")):
        path = os.path.abspath(path)
        print(JOB_TPL.format(what=what, xml_path=path))


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("what", choices=["articles", "users"])
    parser.add_argument("input_dir")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    main(args.what, args.input_dir)
