#!/usr/bin/env python

import optparse
import os
import sys
import subprocess

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def optional_dir():
    return os.path.join(root_dir, 'optional')

def repo_dir(repo_name):
    return os.path.join(root_dir, repo_name)

def get_repo_names():
    return [f for f in os.listdir(optional_dir())
            if not f.startswith(".")]

def get_repo_commit(repo_name):
    path = os.path.join(optional_dir(), repo_name)
    return open(path).read().strip()

def run_command(*args):
    subprocess.check_call(args, stdout=open(os.devnull, 'w'))

def run_git_clone(repo_name):
    os.chdir(root_dir)
    url = "git@github.com:pculture/{0}.git".format(repo_name)
    print "{0}: cloning".format(repo_name)
    run_command("git", "clone", url)
    commit_id = get_repo_commit(repo_name)
    os.chdir(repo_dir(repo_name))
    print "{0}: reset to {1}".format(repo_name, commit_id)
    run_command("git", "reset", "--hard", commit_id)

def run_git_reset(repo_name, skip_fetch):
    os.chdir(repo_dir(repo_name))
    if not skip_fetch
        print "{0}: fetching".format(repo_name)
        run_command("git", "fetch", "origin")
    else:
        print "{0}: skipping fetch".format(repo_name)
    commit_id = get_repo_commit(repo_name)
    print "{0} reset to {1}".format(repo_name, commit_id)
    run_command("git", "reset", "--hard", commit_id)

def make_option_parser():
    parser = optparse.OptionParser()
    parser.add_option("--skip-fetch'", help="skip_fetch",
                      action='store_true', help="don't run git fetch")
    parser.add_option("--clone-missing", dest="clone_missing",
                      action='store_true', help="clone missing repositories")
    return parser

def main(argv):
    parser = make_option_parser()
    (options, args) = parser.parse_args(argv)
    for repo_name in get_repo_names():
        if os.path.exists(repo_dir(repo_name)):
            run_git_reset(repo_name, options.skip_fetch)
        elif options.clone_missing:
            run_git_clone(repo_name)
        else:
            print ("{0}: directory doesn't exist use --clone-missing "
                   "to create it".format(repo_name))

if __name__ == '__main__':
    main(sys.argv)
