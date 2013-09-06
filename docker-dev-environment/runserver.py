#!/usr/bin/python

import manage

def runserver():
    manage.run_manage(["runserver", "0.0.0.0:8000"],
                      docker_args=["-p", "8000:8000"])

if __name__ == '__main__':
    runserver()
