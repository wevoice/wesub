# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

import os
import subprocess
import uuid

from dockerdev.paths import cid_path, unisubs_root

def run_docker(arguments, *params, **kwargs):
    cmdline = "docker " + arguments % params
    print '* %s' % cmdline
    subprocess.call(cmdline, shell=True, **kwargs)

def get_docker_output(arguments, *params, **kwargs):
    cmdline = "docker " + arguments % params
    print '* %s' % cmdline
    return subprocess.check_output(cmdline, shell=True, **kwargs)

def run_manage(manage_args, docker_args=None, settings='docker_dev_settings',
               wrapper_script=None):
    image_name = unique_image_name('amara-dev-manage')
    run_cmd = _docker_manage_args(image_name, settings)
    if docker_args:
        run_cmd.extend(docker_args)
    run_cmd.append('amara-dev')
    if wrapper_script is not None:
        run_cmd.append(wrapper_script)
    run_cmd.extend([
        '/opt/ve/unisubs/bin/python',
        '/opt/apps/unisubs/manage.py',
    ] + manage_args)
    run_and_cleanup(image_name, run_cmd)

def run_shell(docker_args=None):
    image_name = unique_image_name('amara-dev-shell')
    run_cmd = _docker_manage_args(image_name)
    if docker_args is not None:
        run_cmd.extend(docker_args)
    run_cmd.extend(['amara-dev', '/bin/bash', '--init-file',
                    '/opt/ve/unisubs/bin/activate'])
    run_and_cleanup(image_name, run_cmd)

def run_and_cleanup(image_name, command):
    run_docker(" ".join(command))
    cid = open(cid_path(image_name)).read().strip()
    with open("/dev/null", "w") as dev_null:
        run_docker("stop %s" % cid, stdout=dev_null)
        run_docker("wait %s" % cid, stdout=dev_null)
        run_docker("rm %s" % cid, stdout=dev_null)
    os.remove(cid_path(image_name))

def unique_image_name(prefix):
    return '%s-%s' % (prefix, uuid.uuid1().hex[:10])

def _docker_manage_args(image_name, settings='docker_dev_settings'):
    volume_arg = '%s:/opt/apps/unisubs' % (unisubs_root(),)
    return [
        'run',
        '-i', '-t',
        '-h=unisubs.example.com',
        '-cidfile=%s' % cid_path(image_name),
        '-e', 'DJANGO_SETTINGS_MODULE=%s' % settings,
        '-e', 'DJANGO_LIVE_TEST_SERVER_ADDRESS=localhost:8090-8100,9000-9200', 
        '-v', volume_arg,
        '-w', '/opt/apps/unisubs/',
    ]
