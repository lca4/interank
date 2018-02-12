import numpy as np


def print_subsystems_summary(difficulties, subsystems, n=10):
    def print_summary(sid):
        diff = difficulties[sid]
        sub = subsystems[sid]
        print("{: >2} {:+.3f} {} ({} patches, {} users)".format(
                i, diff, sub[0], sub[1], sub[4]))
        print('    rate: {:.4f}%, main contributor: {}'
              .format(sub[3] * 100, sub[2]))
    idx = np.argsort(difficulties)
    print("### {} most difficult subsystems:".format(n))
    for i, aid in enumerate(idx[::-1][:n], start=1):
        print_summary(aid)
    print()
    print("### {} least difficult subsystems:".format(n))
    for i, aid in enumerate(idx[:n], start=1):
        print_summary(aid)


def print_users_summary(skills, users, n=10):
    def print_summary(uid):
        skill = skills[uid]
        user = users[uid]
        print("{: >2} {:+.3f} {} from {} ({} patches, {} subsystems)".format(
                i, skill, user[0], user[1], user[2], user[5]))
        print('    rate: {:.4f}%, main sub: {}'.format(user[4] * 100, user[3]))
    idx = np.argsort(skills)
    print("### {} most skilled users:".format(n))
    for i, uid in enumerate(idx[::-1][:n], start=1):
        print_summary(uid)
    print()
    print("### {} least skilled users:".format(n))
    for i, uid in enumerate(idx[:n], start=1):
        print_summary(uid)
