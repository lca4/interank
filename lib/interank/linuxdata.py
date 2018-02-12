import math
import json
import numpy as np
import os.path


# Set seed for shuffling minibatch
np.random.seed(0)


class LinuxData:
    '''Helper class for loading Linux dataset.'''

    def __init__(self, base_directory):
        self.base_directory = base_directory
        with open(os.path.join(base_directory, "metadata.json")) as f:
            self._meta = json.load(f)

    def _get_data(self, filename):
        path = os.path.join(self.base_directory, filename)
        user_ids = list()
        subsystem_ids = list()
        accepted = list()
        timestamps = list()
        with open(path) as f:
            for line in f:
                uid, sid, a, t = line.strip().split(',')
                user_ids.append(int(uid))
                subsystem_ids.append(int(sid))
                accepted.append(int(a))
                timestamps.append(int(t))
        return (np.array(user_ids),
                np.array(subsystem_ids),
                np.array(accepted),
                np.array(timestamps))

    def get_train_data(self):
        return self._get_data("train.txt")

    def get_test_data(self):
        return self._get_data("test.txt")

    def get_combined_data(self):
        return self._get_data("combined.txt")

    def get_users(self):
        users = dict()
        with open(os.path.join(self.base_directory, "users.txt")) as f:
            for line in f:
                (uid,
                 name,
                 company,
                 patch_cnt,
                 sub,
                 rate,
                 n_sub) = line.strip().split(',')
                users[int(uid)] = (name, company, int(patch_cnt),
                                   sub, float(rate), int(n_sub))
        return users

    def get_subsystems(self):
        subsystems = dict()
        with open(os.path.join(self.base_directory, "subsystems.txt")) as f:
            for line in f:
                (sid,
                 sub,
                 patch_cnt,
                 main_contrib,
                 rate,
                 n_users) = line.strip().split(',')
                subsystems[int(sid)] = (sub, int(patch_cnt), main_contrib,
                                        float(rate), int(n_users))
        return subsystems

    @property
    def n_users(self):
        return self._meta["n_users"]

    @property
    def n_subsystems(self):
        return self._meta["n_subsystems"]

    @staticmethod
    def minibatches(data, minibatch_size):
        data_size = len(data[0])
        # Shuffle dataset
        perm = np.random.permutation(data_size)
        # Generate minibatches
        for i in range(math.ceil(data_size / minibatch_size)):
            idx = perm[i * minibatch_size:(i+1) * minibatch_size]
            yield (data[0][idx], data[1][idx], data[2][idx])
