# Amara, universalsubtitles.org
#
# Copyright (C) 2016 Participatory Culture Foundation
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

"""memoize -- simple memoization utilities."""

import functools

NOT_COMPUTED = object()

class MemoStore(object):
    """Helper class for memoize().

    This provides some functionality, but the main thing it gets around is the
    fact that python2.7 doesn't have the nonlocal keyword.
    """
    def __init__(self):
        self.value = None
        self.is_set = False

    def set_value(self, value):
        self.value = value
        self.is_set = True

def memoize(func):
    """Memoize a function.

    This wrapper remembers the return value of the first call.  On subsequent
    calls, it simple returns it rather than calling the wrapped function
    again.

    The wrapped function must take no arguments.
    """
    memo = MemoStore()
    @functools.wraps(func)
    def wrapper():
        if not memo.is_set:
            memo.set_value(func())
        return memo.value
    return wrapper
