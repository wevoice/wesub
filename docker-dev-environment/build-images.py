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

def get_image_id(tag):
    id_path = os.path.join(unisubs_root(), 'docker-dev-environment',
                           'imageids', tag)
    return open(id_path).read().strip()

def get_current_image_id(tag):
    output = subprocess.check_output("docker images -q %s" % tag, shell=True)
    return output.strip()

def build_image(tag, docker_dir):
    cmdline = 'docker build -t=%s %s' % (tag, docker_dir)
    subprocess.check_call(cmdline, shell=True)

def build_image_if_needed(tag, docker_dir):
    if get_image_id(tag) != get_current_image_id(tag):
        build_image(tag, docker_dir)

def main():
    root = unisubs_root()
    build_image_if_needed('amara', unisubs_root())
    build_image_if_needed('amara-dev', imagedir('amara-dev'))
    build_image_if_needed('amara-dev-mysql', imagedir('mysql'))
    build_image_if_needed('amara-dev-rabbitmq', imagedir('rabbitmq'))
    build_image_if_needed('amara-dev-solr', imagedir('solr'))
    build_image_if_needed('amara-dev-memcache', imagedir('memcache'))

if __name__ == '__main__':
    main()
