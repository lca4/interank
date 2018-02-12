import json
import math
import numpy as np
import os.path


# Set seed for shuffling minibatch
np.random.seed(0)


class WikiData:
    """Helper class for loading pre-generated Wiki observations."""

    def __init__(self, base_directory):
        self.base_directory = base_directory
        with open(os.path.join(base_directory, "metadata.json")) as f:
            self._meta = json.load(f)

    def _get_data(self, filename):
        path = os.path.join(self.base_directory, filename)
        uids = list()
        aids = list()
        qs = list()
        ts = list()
        with open(path) as f:
            for line in f:
                uid, aid, q, t = line.strip().split("#")
                uids.append(int(uid))
                aids.append(int(aid))
                qs.append(float(q))
                ts.append(int(t))
        return (np.array(uids), np.array(aids), np.array(qs), np.array(ts))

    def _get_raw_data(self, filename):
        path = os.path.join(self.base_directory, filename)
        eids, ts, aids, uids, qs, ds, ls_before, ls_after, n_judges = (
                [], [], [], [], [], [], [], [], [])
        with open(path) as f:
            for line in f:
                elems = line.strip().split("#")
                eids.append(int(elems[0]))  # Edit ID.
                ts.append(int(elems[1]))  # Timestamp.
                aids.append(int(elems[2]))  # Article ID.
                uids.append(elems[3])  # User ID (or IP address).
                qs.append(float(elems[4]))  # Computed quality score.
                ds.append(int(elems[5]))  # Edit distance w.r.t. previous rev.
                ls_before.append(int(elems[6]))  # Length before.
                ls_after.append(int(elems[7]))  # Length after.
                n_judges.append(int(elems[8]))  # Number of judges.
        return (np.array(eids), np.array(ts), np.array(aids), np.array(uids),
                np.array(qs), np.array(ds), np.array(ls_before),
                np.array(ls_after), np.array(n_judges))

    def get_train_data(self):
        return self._get_data("train.txt")

    def get_test_data(self):
        return self._get_data("test.txt")

    def get_combined_data(self):
        return self._get_data("combined.txt")

    def get_raw_test_data(self):
        return self._get_raw_data("raw-test.txt")

    def get_raw_combined_data(self):
        return self._get_raw_data("raw-combined.txt")

    def get_users(self):
        users = dict()
        with open(os.path.join(self.base_directory, "users.txt")) as f:
            for line in f:
                uid, wiki_id, name, t_first, t_last, n_edits, n_articles = (
                        line.strip().split("#"))
                users[int(uid)] = (wiki_id, name, int(t_first), int(t_last),
                        int(n_edits), int(n_articles))
        return users

    def get_articles(self):
        articles = dict()
        with open(os.path.join(self.base_directory, "articles.txt")) as f:
            for line in f:
                aid, wiki_id, title, n_edits, n_editors = (
                        line.strip().split("#"))
                articles[int(aid)] = (wiki_id, title,
                        int(n_edits), int(n_editors))
        return articles

    def get_bots(self):
        """Get a list of bots."""
        bots = list()
        with open(os.path.join(self.base_directory, "bots.txt")) as f:
            for line in f:
                bots.append(line.strip())
        return bots

    @property
    def n_users(self):
        return self._meta["n_users"]

    @property
    def n_articles(self):
        return self._meta["n_articles"]

    @staticmethod
    def minibatches(data, minibatch_size):
        data_size = len(data[0])
        # Shuffle dataset
        perm = np.random.permutation(data_size)
        # Generate minibatches
        for i in range(math.ceil(data_size / minibatch_size)):
            idx = perm[i * minibatch_size:(i+1) * minibatch_size]
            yield (data[0][idx], data[1][idx], data[2][idx])
