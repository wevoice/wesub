#!/usr/bin/python

import sys

from dockerdev import images, containers

if '--rebuild' in sys.argv:
    images.rebuild_images()
else:
    images.build_images()
containers.start_services()
