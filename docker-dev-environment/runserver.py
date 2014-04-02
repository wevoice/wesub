#!/usr/bin/python

from dockerdev.rundocker import run_manage

run_manage(["runserver", "0.0.0.0:8000"],
           docker_args=['-p', '8000:8000'])
