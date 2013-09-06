#!/usr/bin/python

import manage

def runworker():
    manage.run_manage([
        "celery", "worker",
        "--scheduler=djcelery.schedulers.DatabaseScheduler",
        "--loglevel=DEBUG",
        "--autoreload",
    ])

if __name__ == '__main__':
    runworker()
