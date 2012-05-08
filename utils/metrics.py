# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
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

import socket, time
from contextlib import contextmanager

from django.conf import settings

try:
    # from bernhard import Client
    from riemanned import RiemannClient as Client
except ImportError:
    # Just use a dummy client if we don't have a Riemann client installed.
    class Client(object):
        def __init__(self, *args, **kwargs):
            pass

        def send(self, *args, **kwargs):
            pass



# Currently uses a TCP transport, but we can switch to a UDP transport if
# performance becomes an issue.
c = Client(getattr(settings, 'RIEMANN_HOST', '127.0.0.1'))
host = socket.gethostname()


def send(service, tag, metric=None):
    data = {'host': host, 'service': service, 'tags': [tag]}
    if metric:
        data['metric'] = metric
    try:
        c.send(data)
    except:
        pass


class Metric(object):
    def __init__(self, name):
        self.name = name


class Occurrence(Metric):
    def mark(self):
        send(self.name, 'occurrence')

class Meter(Metric):
    def inc(self, n=1):
        send(self.name, 'meter', n)

class Histogram(Metric):
    def record(self, value):
        send(self.name, 'histogram', value)

@contextmanager
def Timer(name):
    start = time.time()

    try:
        yield
    finally:
        ms = (time.time() - start) * 1000
        send(name, 'timer', ms)

class ManualTimer(Metric):
    def record(self, value):
        send(self.name, 'timer', value)
