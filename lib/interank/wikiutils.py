import numpy as np

from urllib.parse import quote


def print_articles_summary(difficulties, articles, n=10):
    def print_summary(aid):
        diff = difficulties[aid]
        art = articles[aid]
        url = "https://tr.wikipedia.org/wiki/{}".format(quote(art[1]))
        print("{: >2} {:+.3f} {} ({} edits, {} users)".format(
                i, diff, art[1], art[2], art[3]))
        print("    {}".format(url))
    idx = np.argsort(difficulties)
    print("### {} most difficult articles:".format(n))
    for i, aid in enumerate(idx[::-1][:n], start=1):
        print_summary(aid)
    print()
    print("### {} least difficult articles:".format(n))
    for i, aid in enumerate(idx[:n], start=1):
        print_summary(aid)


def print_users_summary(skills, users, n=10):
    def print_summary(uid):
        skill = skills[uid]
        user = users[uid]
        url = "https://tr.wikipedia.org/wiki/User:{}".format(quote(user[1]))
        print("{: >2} {:+.3f} {} ({} edits, {} articles)".format(
                i, skill, user[1], user[4], user[5]))
        print("    {}".format(url))
    idx = np.argsort(skills)
    print("### {} most skilled users:".format(n))
    for i, uid in enumerate(idx[::-1][:n], start=1):
        print_summary(uid)
    print()
    print("### {} least skilled users:".format(n))
    for i, uid in enumerate(idx[:n], start=1):
        print_summary(uid)
