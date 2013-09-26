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

from dockerdev.paths import unisubs_root, image_dir
from dockerdev.rundocker import get_docker_output, run_docker

ALL_IMAGES = [
    'amara',
    'amara-dev',
    'amara-dev-mysql',
    'amara-dev-rabbitmq',
    'amara-dev-solr',
    'amara-dev-memcache',
]

def build_image(image_name):
    run_docker('build -t=%s %s', image_name, image_dir(image_name))

def rebuild_images():
    for image_name in ALL_IMAGES:
        build_image(image_name)
