import argparse


def process_users(args):
    next_id = 0
    with open(args.path) as f:
        for line in f:
            if args.ignore_unregistered and line.startswith("u"):
                continue
            print("{}#{}".format(next_id, line), end="")
            next_id += 1


def process_articles(args):
    with open(args.path) as f:
        for i, line in enumerate(f):
            print("{}#{}".format(i, line), end="")


def process_qualities(args):
    wiki2uid = dict()
    with open(args.users) as f:
        for line in f:
            uid, wiki_id, _ = line.strip().split("#", 2)
            wiki2uid[wiki_id] = int(uid)
    wiki2aid = dict()
    with open(args.articles) as f:
        for line in f:
            aid, wiki_id, _ = line.strip().split("#", 2)
            wiki2aid[wiki_id] = int(aid)
    with open(args.path) as f:
        for line in f:
            _, ts, wiki_aid, wiki_uid, q, _, _, _, n_judges = (line
                    .strip().split("#"))
            if ((wiki_uid not in wiki2uid)
                    or (int(n_judges) < args.ignore_less_than)):
                continue
            uid = wiki2uid[wiki_uid]
            aid = wiki2aid[wiki_aid]
            q = (float(q) + 1) / 2
            print("{}#{}#{}#{}".format(uid, aid, q, ts))


def _parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    # Subparser for users file.
    sp_users = subparsers.add_parser("users")
    sp_users.add_argument("path")
    sp_users.add_argument("--ignore-unregistered", action="store_true")
    sp_users.set_defaults(func=process_users)
    # Subparser for articles file.
    sp_articles = subparsers.add_parser("articles")
    sp_articles.add_argument("path")
    sp_articles.set_defaults(func=process_articles)
    # Subparser for qualities file.
    sp_quals = subparsers.add_parser("qualities")
    sp_quals.add_argument("path")
    sp_quals.add_argument("--users", required=True)
    sp_quals.add_argument("--articles", required=True)
    sp_quals.add_argument("--ignore-less-than", type=int, default=2)
    sp_quals.set_defaults(func=process_qualities)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    args.func(args)
