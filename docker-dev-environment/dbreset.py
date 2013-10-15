#!/usr/bin/python

import sys

from dockerdev.rundocker import run_manage

run_manage(['drop_all_tables'])
run_manage(['syncdb', '--all'])
run_manage(['migrate', '--fake'])
