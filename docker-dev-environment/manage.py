#!/usr/bin/python

import os
import uuid
import subprocess
import sys

def get_cid_path():
    filename = 'amara-dev-manage-%s' % (uuid.uuid1().hex[:10],)
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'cidfiles', filename))

def get_cid(cidpath):
    return open(cidpath).read().strip()

def run_manage(manage_args, docker_args=None, settings='docker_dev_settings'):
    cidpath = get_cid_path()
    unisubs_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..'))
    volume_arg = '%s:/opt/apps/unisubs' % (unisubs_root,)
    run_cmd = [
        '/usr/bin/docker', 'run',
        '-i', '-t',
        '-cidfile=%s' % cidpath,
        '-e', 'DJANGO_SETTINGS_MODULE=%s' % settings,
        '-v', volume_arg,
        '-w', '/opt/apps/unisubs/',
    ]
    if docker_args:
        run_cmd.extend(docker_args)
    run_cmd.extend([
        'amara-dev',
        '/opt/ve/unisubs/bin/python',
        '/opt/apps/unisubs/manage.py',
    ] + manage_args)
    subprocess.check_call(run_cmd)
    cid = get_cid(cidpath)
    with open("/dev/null", "w") as dev_null:
        subprocess.check_call(['/usr/bin/docker', 'stop', cid],
                              stdout=dev_null)
        subprocess.check_call(['/usr/bin/docker', 'wait', cid],
                              stdout=dev_null)
        subprocess.check_call(['/usr/bin/docker', 'rm', cid],
                              stdout=dev_null)
    os.unlink(cidpath)

if __name__ == '__main__':
    run_manage(sys.argv[1:])
