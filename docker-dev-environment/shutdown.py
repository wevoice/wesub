#!/usr/bin/python

import sys


from dockerdev import containers

if '--rm' in sys.argv:
    containers.remove_services()
else:
    containers.stop_services()
