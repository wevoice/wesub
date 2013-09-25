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

from dockerdev.paths import cid_path
from dockerdev.rundocker import run_docker, get_docker_output

SERVICE_IMAGES = [
    'amara-dev-mysql',
    'amara-dev-rabbitmq',
    'amara-dev-solr',
    'amara-dev-memcache',
]

def get_cid(image_name):
    if not os.path.exists(cid_path(image_name)):
        return None
    return open(cid_path(image_name)).read().strip()

def running_images():
    output = get_docker_output("ps -q")
    return [line.strip() for line in output.split("\n")]

def run_image(image_name):
    run_docker("run -d -cidfile=%s -h=%s %s", cid_path(image_name),
               image_name, image_name)

def start_image(image_name):
    run_docker("start %s" % (get_cid(image_name)))

def stop_image(image_name):
    run_docker("stop %s" % (get_cid(image_name)))

def remove_image(image_name):
    run_docker("rmi %s" % (get_cid(image_name)))
    os.remove(cid_path(image_name))

def start_services():
    currently_running = running_images()
    for image_name in SERVICE_IMAGES:
        if not os.path.exists(cid_path(image_name)):
            run_image(image_name)
        elif get_cid(image_name) not in currently_running:
            start_image(image_name)

def stop_services():
    currently_running = running_images()
    for image_name in SERVICE_IMAGES:
        if get_cid(image_name) in currently_running:
            stop_image(image_name)

def remove_services():
    stop_services()
    for image_name in SERVICE_IMAGES:
        if get_cid(image_name) is not None:
            remove_image(image_name)
