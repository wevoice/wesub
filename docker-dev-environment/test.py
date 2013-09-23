#!/usr/bin/python

import manage
import sys

def runserver(args):
    manage.run_manage(["test"] + args, settings='docker_dev_settings_test')

if __name__ == '__main__':
    runserver(sys.argv[1:])
