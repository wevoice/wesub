#!/usr/bin/python

from dockerdev.rundocker import run_manage

run_manage([
    "celery", "worker",
    "--scheduler=djcelery.schedulers.DatabaseScheduler",
    "--loglevel=DEBUG",
    "--autoreload",
])
