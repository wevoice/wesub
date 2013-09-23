#!/usr/bin/python

import os
import subprocess
import sys

ALL_IMAGES = [
    'amara-dev-mysql',
    'amara-dev-rabbitmq',
    'amara-dev-solr',
    'amara-dev-memcache',
]

def print_usage_and_exit():
    print "USAGE python services.py [start|stop|remove|info]"
    sys.exit(1)

def get_cid_path(image_name):
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'cidfiles', image_name))

def get_cid(cidpath):
    return open(cidpath).read().strip()

def running_images():
    cmdline = "docker ps -q"
    output = subprocess.check_output(cmdline, shell=True)
    return [line.strip() for line in output.split("\n")]

def docker_run(image_name, cidpath):
    print 'running: %s' % (image_name,)
    cmdline = "docker run -d -cidfile=%s -h=%s %s" % (cidpath, image_name, image_name)
    subprocess.check_call(cmdline, shell=True)

def docker_start(image_name, cidpath, currently_running):
    cid = get_cid(cidpath)
    if cid in currently_running:
        print 'already started: %s' % (image_name,)
        return
    print 'starting: %s' % (image_name,)
    cmdline = "docker start %s" % (cid,)
    subprocess.check_call(cmdline, shell=True)

def docker_stop(image_name, cidpath, currently_running):
    cid = get_cid(cidpath)
    if cid not in currently_running:
        print 'already stopped: %s' % (image_name,)
        return
    print 'stopping: %s' % (image_name,)
    cmdline = "docker stop %s" % (cid,)
    subprocess.check_call(cmdline, shell=True)

def start_services():
    currently_running = running_images()
    for image_name in ALL_IMAGES:
        cidpath = get_cid_path(image_name)
        if not os.path.exists(cidpath):
            docker_run(image_name, cidpath)
        else:
            docker_start(image_name, cidpath, currently_running)

def stop_services():
    currently_running = running_images()
    for image_name in ALL_IMAGES:
        cidpath = get_cid_path(image_name)
        if os.path.exists(cidpath):
            docker_stop(image_name, cidpath, currently_running)

def remove_services():
    currently_running = running_images()
    for image_name in ALL_IMAGES:
        cidpath = get_cid_path(image_name)
        if os.path.exists(cidpath):
            cid = get_cid(cidpath)
            if cid in currently_running:
                docker_stop(image_name, cidpath, currently_running)
            cmdline = "docker rm %s" % (cid,)
            subprocess.check_call(cmdline, shell=True)
            os.remove(cidpath)

def print_info():
    currently_running = running_images()
    for image_name in ALL_IMAGES:
        cidpath = get_cid_path(image_name)
        if os.path.exists(cidpath):
            cid = get_cid(cidpath)
            if cid in currently_running:
                print '%s: %s running' % (image_name, cid)
            else:
                print '%s: %s stopped' % (image_name, cid)
        else:
            print '%s: not running' % (image_name,)

def main(argv):
    try:
        cmd = argv[1]
    except IndexError:
        print_usage_and_exit()
    if cmd == 'start':
        start_services()
    elif cmd == 'stop':
        stop_services()
    elif cmd == 'remove':
        remove_services()
    elif cmd == 'info':
        print_info()
    else:
        print_usage_and_exit()

if __name__ == '__main__':
    main(sys.argv)
