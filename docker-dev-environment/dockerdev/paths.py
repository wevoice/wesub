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

def unisubs_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def env_root():
    return os.path.join(unisubs_root(), 'docker-dev-environment')

def image_dir(image_name):
    if image_name == 'amara':
        return unisubs_root()
    else:
        return os.path.join(env_root(), 'dockerfiles', image_name)

def cid_path(image_name):
    return os.path.join(env_root(), 'cidfiles', image_name)
