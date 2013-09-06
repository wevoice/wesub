#!/usr/bin/python

import subprocess
import os

def unisubs_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def imagedir(dirname):
    return os.path.join(unisubs_root(),
                        'docker-dev-environment',
                        'dockerfiles',
                        dirname)

def build_image(tag, docker_dir):
    cmdline = 'docker build -t=%s %s' % (tag, docker_dir)
    subprocess.check_call(cmdline, shell=True)

def main():
    root = unisubs_root()
    build_image('amara', unisubs_root())
    build_image('amara-dev', imagedir('amara-dev'))
    build_image('amara-dev-mysql', imagedir('mysql'))
    build_image('amara-dev-rabbitmq', imagedir('rabbitmq'))
    build_image('amara-dev-solr', imagedir('solr'))
    build_image('amara-dev-memcache', imagedir('memcache'))

if __name__ == '__main__':
    main()
