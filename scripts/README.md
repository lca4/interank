# Notes on processing Wikipedia datasets

This file contains some notes on how to process Wikipedia full history XML
dumps using the scripts in this directory.


## Datasets used

- frwiki: 2017-09-01 (<https://dumps.wikimedia.org/frwiki/20170901/>).
    - Number of `bz2` files: 90
    - Total size, compressed: 139 GB
    - Total size, uncompressed: 2.4 TB
- trwiki: 2017-10-01 (<https://dumps.wikimedia.org/trwiki/20171001/>)
    - Number of `bz2` files: 1
    - Total size, compressed: 6.9 GB
    - Total size, uncompressed: 30 GB


## Processing `trwiki`

The Turkish Wikipedia consists of a single file, so it is much easier to
process.

1. Extract data about users: `article_count.py users path/to/xml > users.txt`
   (takes ~50 min).
2. Extract data about articles:
   `article_count.py articles path/to/xml > articles.txt` (takes ~1h)
3. Compute the qualities:
   `compute_quality.py --processes=48 path/to/xml > qualities.txt`. (takes ~20
   hours)
4. Remove the first line of `qualities.txt`, as it just contains the path to
   the XML file that was processed (useful in the multi-file case).
5. Sort the edits by timestamp:
   `sort --field-separator='#' --key=2 qualities.txt > combined.txt`
6. Find the timestamp that split the dataset into two:

        wc -l combined.txt
        # Compute (by hand) which line would represent 90% of the data, then:
        head -8859878 combined.txt | tail -1
        # Finally, write down the corresponding timestamp (2nd column).

7. Compute the qualities again, but this time ignore edits in the test set:

        compute_quality.py ---processes=48 --threshold=1469817271 \
            path/to/xml > qualities.txt

   Once done, don't forget to remove the first line of the file.
8. Finally, split the resulting file into training set and test set.

        sort --field-separator='#' --key=2 qualities.txt > temp.txt
        head -8859877 temp.txt > train.txt
        # Beware, the number of lines differs by one in the next command.
        tail --lines=+8859878 temp.txt > test.txt

From this, one gets the *raw* data: `users.txt`, `articles.txt`,
`combined.txt`, `train.txt` and `test.txt`. The next step is to process the raw
dataset in order to have consecutive user & article IDs. Here are the commands.

    # Process users (takes a few seconds).
    process_raw.py users raw/users.txt > processed/users.txt

    # Process articles (takes a few seconds).
    process_raw.py articles raw/articles.txt > processed/articles.txt

    # Process combined dataset (takes ~1 min).
    process_raw.py qualities \
        --ignore-less-than 2
        --users processed/users.txt \
        --articles processed/articles.txt \
        raw/combined.txt > processed/combined.txt

The last command should be repeated for `train.txt` and `test.txt`. Lastly,
create a file `processed/metadata.json` with contents as follows.

    {
        "n_users": 1393027,
        "n_articles": 541476
    }

The number of users and articles can be found by inspecting the first first of
the last lines in `users.txt` and `articles.txt`.

Finally, it is important to remove from `raw/combined` and `raw/test.txt` the
edits that are no longer in the respective processed versions. For this, the
following commands helped.

    dos2unix raw-test.txt
    cat raw-test.txt | grep -v "#0$" | grep -v "#1$" > raw-test2.txt


## Processing `frwiki`

The French Wikipedia dump consists of many files, so we take advantage of the
Condor cluster in order to process the XML files in parallel. In general, the
procedure follows that of `trwiki`, with a few tweaks.

### Information about users and articles

    # Make sure this directory doesn't contain anything beforehand.
    mkdir /dfs/ephemeral/storage/maystre/condor-out
    ./article_count_condor.py users path/to/folder > condor.submit
    condor_submit condor.submit

To aggregate the outputs, use the script `combine_users.py`:

    ./combine_users path/to/folder/out.* > users.txt

The same procedure can be used to extract information about the articles. Note
that these jobs perform poorly on the server, for a strange reason that I don't
understand at this point (probably has to do with GlusterFS caching). Expect it
to take ~3 hours for each of the user / article info extraction.

Some useful tricks.

- In order to check whether some jobs failed, I used the follwing command:
  `cat log.* | grep "return value" | uniq`.
- In order to aggregate the output of the articles jobs:
  `cat out.* | sort > articles.txt` (takes ~10 secs)

### Computing the quality of edits

    # Make sure this directory doesn't contain anything beforehand.
    mkdir /dfs/ephemeral/storage/maystre/condor-out
    ./compute_quality_condor.py path/to/folder > condor.submit
    condor_submit condor.submit

It takes about 48 hours for most jobs to finish, and another 24 hours for the
inevitable few stragglers. To combine and sort the results:

    # Took ~10 seconds.
    time cat out.* | grep -v "^///" > combined.txt
    # Took ~3 mins.
    time sort --field-separator='#' --key=2 combined.txt > frwiki.combined

I found that line no `63948964` represents 90% of the dataset, and that this
corresponds to the timestamp `1462222957`.

Commands used to separate the combined (sorted) output into training / test
sets.

    head -63948963 sorted.txt > frwiki.train
    tail -n+63948964 sorted.txt > frwiki.test

Sanity check: the last few lines of frwiki.train should only contain `0`
quality values.
