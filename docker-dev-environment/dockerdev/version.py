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

import re

from dockerdev.rundocker import get_docker_output

_get_version_cache = None
def get_version():
    global _get_version_cache
    if _get_version_cache is None:
        _get_version_cache = calc_version()
    return _get_version_cache

def calc_version():
    version_info = get_docker_output("-v")
    version = re.search(r'version ([\d\.]+)', version_info).group(1)
    return tuple(int(num) for num in version.split("."))

