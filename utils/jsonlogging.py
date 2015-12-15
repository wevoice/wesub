# Amara, universalsubtitles.org
#
# Copyright (C) 2015 Participatory Culture Foundation
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

from datetime import datetime
import json
import logging

EXTRA_FIELDS = ['path', 'view', 'query', 'data', 'metrics']

def record_data(record):
    data = {
        '@version': '1',
        '@timestamp': format_timestamp(record.created),
        'message': record.getMessage(),
        'level': record.levelname,
        'name': record.name,
    }
    if record.exc_info:
        data['exception'] = str(record.exc_info[1])
    for name in EXTRA_FIELDS:
        if hasattr(record, name):
            data[name] = getattr(record, name)
    return data

def format_timestamp(time):
    tstamp = datetime.utcfromtimestamp(time)
    return (tstamp.strftime("%Y-%m-%dT%H:%M:%S") +
            ".%03d" % (tstamp.microsecond / 1000) + "Z")

class JSONHandler(logging.Handler):
    def emit(self, record):
        print(json.dumps(record_data(record)))
