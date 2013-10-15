#!/usr/bin/python

import sys

from dockerdev import images

try:
    image_name = sys.argv[1]
except IndexError:
    sys.stderr.write("Usage: ./build.py [image_name | all]\n")
    sys.exit(1)
if image_name == 'all':
    images.rebuild_images()
else:
    images.build_image(sys.argv[1])
