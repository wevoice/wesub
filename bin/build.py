#!/usr/bin/env python

import os
import sys
import subprocess

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

def update_commit_file():
    cmdline = ['git', 'rev-parse', '--short=8', 'HEAD']
    commit_id = subprocess.check_output(cmdline).strip()
    print 'git commit: {}'.format(commit_id)
    with open(os.path.join(ROOT_DIR, 'commit.py'), 'w') as f:
        f.write("LAST_COMMIT_GUID = '{0}'\n".format(commit_id))

def run_docker_build(image_name):
    cmdline = ['docker', 'build', '-t', image_name, ROOT_DIR]
    print 'running docker build'
    subprocess.check_call(cmdline)

def main(argv):
    image_name = sys.argv[1]
    update_commit_file()
    run_docker_build(image_name)

if __name__ == '__main__':
    main(sys.argv)
