#!/usr/bin/python

from dockerdev import images, containers

if images.any_image_out_of_date():
    containers.stop_services()
    images.rebuild_images()
containers.start_services()
