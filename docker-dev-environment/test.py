#!/usr/bin/python

import sys

from dockerdev.rundocker import run_manage

run_manage(["test"] + sys.argv[1:], settings='docker_dev_settings_test',
           wrapper_script='xvfb-run --server-args="-screen 0 2048x1600x24"')
