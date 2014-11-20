# Amara, universalsubtitles.org
#
# Copyright (C) 2014 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

"""
Cache Groups
------------

Cache groups are used to manage a group of related cache values.  They add
some extra functionality to the regular django caching system:

- **Key prefixing**: cache keys are prefixed with a string to avoid name
  collisions
- **Invalidation**: all values in the cache group can be invalidated together.
  Optionally, all values can be invalidated on server deploy
- **Optimized fetching**: we can remember cache usage patterns in order to use
  get_many() to fetch all needed keys at once (see :ref:`cache-patterns`)
- **Protection against race conditions**: (see
  :ref:`cache-race-condition-prevention`)

Typically cache groups are associated with objects.  For example we create a
cache group for each user and each video.  The user cache group stores things
like the user menu HTML and message HTML.  The video cache group stores the
language list and other sections of the video/language pages.

.. _cache-patterns:

Cache Patterns
^^^^^^^^^^^^^^

Cache patterns help optimize cache access.  When a cache pattern is set for a
CacheGroup we will do a couple things:

- Remember which keys were fetched from cache.
- On subsequent runs, we will try to use get_many() to fetch all cache
  values at once.

This speeds things up by reducing the number of round trips to memcached.

Behind the scenes
^^^^^^^^^^^^^^^^^

The main trick that CacheGroup uses is to store a "version" value in the
cache, which is simply a random string.  We also pack the version value
together with all of our cache values.  If a cache value's version doesn't
match the version for the cache group, then it's considered invalid.  This
allows us to invalidate the entire cache group by changing the version value
to a different string.

Here's some example data to show how it works.

========  ==============   ==============
key       value in cache   computed value
========  ==============   ==============
version   abc              N/A
X         abc:foo          foo
Y         abc:bar          bar
Z         def:bar          *invalid*
========  ==============   ==============

.. note::

    We also will prefix the all cache keys with the "<prefix>:" using the
    prefix passed into the CacheGroup constructor.

.. note::

    If invalidate_on_deploy is True, then we will append ":<commit-id>" to the
    version key.  This way the version key changes for each deploy, which will
    invalidate all values.

.. _cache-race-condition-prevention:

Race condition prevention
^^^^^^^^^^^^^^^^^^^^^^^^^

The typical cache usage pattern is:

  1. Fetch from the cache
  2. If there is a cache miss then:

      a) calculate the value
      b) store it to cache.

This pattern will often have a race condition if another process updates the
DB between steps 2a and 2b.  Even if the other process invalidates the cache,
the step 2b will overwrite it, storing an outdated value.

This is not a problem with CacheGroup because of the way it handles the
version key.  When we get the value from cache, we also fetch the version
value.  If the version value isn't set, we set it right then.  Then when we
store the value, we also store the version key that we saw when we did the
get.  If the version changes between the get() and set() calls, then the
value stored with set() will not be valid.  This works somewhat similarly to
the memcached GETS and CAS operations.

.. autoclass:: CacheGroup
"""
from __future__ import absolute_import
import collections

from django.conf import settings
from django.core.cache import cache

from utils import codes

def get_commit_id():
    return settings.LAST_COMMIT_GUID

class _CacheWrapper(object):
    """Wrap cache access for CacheGroup.

    This class helps CacheGroup access the cache.  It does 2 things:
        - adds the key prefix
        - remembers previously fetched values and avoids fetching them again
        - handles prefetching keys for a cache pattern
    """
    def __init__(self, prefix):
        self.prefix = prefix
        self._cache_data = {}

    def get(self, key):
        value = cache.get(self._prefix_key(key))
        self._cache_data[key] = value
        return value

    def get_many(self, keys):
        unfetched_keys = [key for key in keys if key not in self._cache_data]
        if unfetched_keys:
            self._run_get_many(unfetched_keys)
        return dict((key, self._cache_data.get(key)) for key in keys)

    def _run_get_many(self, keys):
        result = cache.get_many([self._prefix_key(key) for key in keys])
        for key in keys:
            self._cache_data[key] = result.get(self._prefix_key(key))

    def set(self, key, value, timeout=None):
        cache.set(self._prefix_key(key), value)
        self._cache_data[key] = value

    def set_many(self, values, timeout=None):
        raw_values = dict((self._prefix_key(key), value)
                          for (key, value) in values.items())
        cache.set_many(raw_values, timeout)
        self._cache_data.update(values)

    def _prefix_key(self, key):
        return '{0}:{1}'.format(self.prefix, key)

# map cache pattern IDs to the keys we've seen used
_cache_pattern_memory = collections.defaultdict(set)

class CacheGroup(object):
    """Manage a group of cached values

    Args:
        prefix(str): prefix keys with this
        cache_pattern(str): :ref:`cache pattern <cache-patterns>` identifier
        invalidate_on_deploy(bool): Invalidate values when we redeploy

    .. automethod:: get
    .. automethod:: get_many
    .. automethod:: set
    .. automethod:: set_many
    .. automethod:: invalidate

    """

    def __init__(self, prefix, cache_pattern=None, invalidate_on_deploy=True):
        self.cache_wrapper = _CacheWrapper(prefix)
        if cache_pattern:
            # copy the values from _cache_pattern_memory now.  It's going to
            # change as we fetch keys and for sanity sake we should not care
            # about that
            self._cache_pattern_keys = \
                    set(_cache_pattern_memory[cache_pattern])
        else:
            self._cache_pattern_keys = None
        self.cache_pattern = cache_pattern
        self.current_version = None
        if invalidate_on_deploy:
            self.version_key = 'version:{0}'.format(get_commit_id())
        else:
            self.version_key = 'version'
        self.invalidate_on_deploy = invalidate_on_deploy

    def invalidate(self):
        """Invalidate all values in this CacheGroup."""
        self.current_version = codes.make_code()
        self.cache_wrapper.set(self.version_key, self.current_version)

    def ensure_version(self):
        if self.current_version is not None:
            return
        version = self.cache_wrapper.get(self.version_key)
        if version is None:
            self.invalidate()
        else:
            self.current_version = version

    def get(self, key):
        """Get a value from the cache

        This method also checks that the version of the value stored matches
        the version in our version key.

        If there is no value set for our version key, we set it now.
        """
        # Delegate to get_many().  This function is just for convenience.
        return self.get_many([key]).get(key)

    def get_many(self, keys):
        """Get multiple keys at once

        If there is no value set for our version key, we set it now.
        """
        if self.cache_pattern:
            _cache_pattern_memory[self.cache_pattern].update(keys)
        keys_to_fetch = set(keys)
        if self.current_version is None:
            keys_to_fetch.add(self.version_key)
        if self._cache_pattern_keys:
            keys_to_fetch.update(self._cache_pattern_keys)
            self._cache_pattern_keys = None
        get_many_result = self.cache_wrapper.get_many(keys_to_fetch)
        # first of all, handle the version.
        if self.current_version is None:
            if get_many_result[self.version_key] is None:
                self.invalidate()
                return {}
            else:
                self.current_version = get_many_result[self.version_key]
        result = {}
        for key in keys:
            cache_value = get_many_result.get(key)
            version, value = self._unpack_cache_value(cache_value)
            if version == self.current_version:
                result[key] = value
        return result

    def set(self, key, value, timeout=None):
        """Set a value in the cache """
        self.ensure_version()
        self.cache_wrapper.set(key, self._pack_cache_value(value), timeout)

    def set_many(self, values, timeout=None):
        """Set multiple values in the cache """
        self.ensure_version()
        values_to_set = dict(
            (key, self._pack_cache_value(value))
            for key, value in values.items()
        )
        self.cache_wrapper.set_many(values_to_set, timeout)

    def _pack_cache_value(self, value):
        """Combine our version and value together to get a value to store in
        the cache.
        """
        if isinstance(value, basestring):
            # if the value is a string, let's not create a tuple.  This avoids
            # having to pickle the data
            return ':'.join((self.current_version, value))
        else:
            return (self.current_version, value)

    def _unpack_cache_value(self, cache_value):
        """Unpack a value stored in the cache to a (version, value) tuple
        """
        if isinstance(cache_value, basestring):
            split = cache_value.split(':', 1)
            if len(split) == 2:
                return split
        elif isinstance(cache_value, tuple):
            if len(cache_value) == 2:
                return cache_value
        return (None, None)
