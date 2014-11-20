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

from django.core.cache import cache
from django.test import TestCase
from django.test.utils import override_settings
from nose.tools import *
import mock

from caching.cachegroup import CacheGroup, _cache_pattern_memory

def make_cache_group(**kwargs):
    if 'invalidate_on_deploy' not in kwargs:
        kwargs['invalidate_on_deploy'] = False
    return CacheGroup('cache-group-prefix', **kwargs)

class CacheGroupTest(TestCase):
    CACHE_VALUE = 'cached-value'

    def setUp(self):
        self.work_func = mock.Mock(return_value=self.CACHE_VALUE)

    def check_cache_miss(self, key):
        assert_equal(make_cache_group().get(key), None)

    def check_cache_hit(self, key):
        assert_equal(make_cache_group().get(key), self.CACHE_VALUE)

    def populate_key(self, key):
        make_cache_group().set(key, self.CACHE_VALUE)

    def invalidate_group(self):
        make_cache_group().invalidate()

    def test_get(self):
        self.populate_key('key')
        cache_group = make_cache_group()
        assert_equal(cache_group.get('key'), self.CACHE_VALUE)

    def test_get_with_missing_value(self):
        cache_group = make_cache_group()
        assert_equal(cache_group.get('key'), None)

    def test_set(self):
        cache_group = make_cache_group()
        cache_group.set('key', self.CACHE_VALUE)
        self.check_cache_hit('key')

    def test_get_many(self):
        self.populate_key('key1')
        self.populate_key('key2')
        cache_group = make_cache_group()
        assert_equal(cache_group.get_many(['key1', 'key2', 'key3']), {
            'key1': self.CACHE_VALUE,
            'key2': self.CACHE_VALUE,
        })

    def test_set_many(self):
        cache_group = make_cache_group()
        cache_group.set_many({
            'key1': self.CACHE_VALUE,
            'key2': self.CACHE_VALUE,
        })
        self.check_cache_hit('key1')
        self.check_cache_hit('key2')

    def test_invalidate(self):
        self.populate_key('key1')
        self.populate_key('key2')
        self.invalidate_group()

        self.check_cache_miss('key1')
        self.check_cache_miss('key2')

    def patch_get_commit_id(self):
        return mock.patch('caching.cachegroup.get_commit_id')

    def test_invalidate_on_new_commit(self):
        cache_group = make_cache_group(invalidate_on_deploy=True)
        cache_group.set('key', self.CACHE_VALUE)
        with self.patch_get_commit_id() as mock_get_commit_id:
            mock_get_commit_id.return_value = 'new-commit-id'
            cache_group2 = make_cache_group(invalidate_on_deploy=True)
            assert_equal(cache_group2.get('key'), None)

    def test_dont_invalidate_on_new_commit(self):
        cache_group = make_cache_group(invalidate_on_deploy=False)
        cache_group.set('key', self.CACHE_VALUE)
        with self.patch_get_commit_id() as mock_get_commit_id:
            mock_get_commit_id.return_value = 'new-commit-id'
            cache_group2 = make_cache_group(invalidate_on_deploy=False)
            assert_equal(cache_group2.get('key'), self.CACHE_VALUE)

    def test_get_version_missing(self):
        # test a corner case where the version value gets deleted from the
        # cache
        self.populate_key('key')
        cache.delete('cache-group-prefix:{0}'.format(
            make_cache_group().version_key))
        self.check_cache_miss('key')

    def test_get_with_update_version_midway(self):
        # See the documentation for the race condition this is testing
        cache_group = make_cache_group()
        cache_group.get('key')
        self.invalidate_group() # causes the corner case
        cache_group.set('key', self.CACHE_VALUE)

        self.check_cache_miss('key')

    def test_key_prefix(self):
        # we should store values using <prefix>:key
        cache_group = make_cache_group()
        cache_group.set('key', self.CACHE_VALUE)
        assert_not_equal(cache.get('cache-group-prefix:key'), None)

    def test_version_key_prefix(self):
        # we should store versions using <prefix>:version
        cache_group = make_cache_group()
        version_key = 'cache-group-prefix:{0}'.format(cache_group.version_key)
        self.invalidate_group()
        assert_not_equal(cache.get(version_key), None)

class CacheGroupTest2(CacheGroupTest):
    # test non-string values, which go through a slightly different codepath
    CACHE_VALUE = {'value': 'test'}

class CachePatternTest(TestCase):
    def tearDown(self):
        _cache_pattern_memory.clear()

    def test_remember_keys(self):
        # test that we remember fetched keys
        cache_group = make_cache_group(cache_pattern='foo')
        cache_group.get('a')
        cache_group.get_many(['b', 'c'])
        assert_items_equal(_cache_pattern_memory['foo'], ['a', 'b', 'c'])

    def test_remember_keys_two_runs(self):
        # test remembering fetched keys after multiple runs
        cache_group = make_cache_group(cache_pattern='foo')
        cache_group.get('a')
        cache_group2 = make_cache_group(cache_pattern='foo')
        cache_group2.get_many(['b', 'c'])
        assert_items_equal(_cache_pattern_memory['foo'], ['a', 'b', 'c'])

    def make_mocked_cache_group(self):
        cache_group = make_cache_group(cache_pattern='foo')
        def mock_get_many(keys):
            return dict((k, None) for k in keys)
        cache_group.cache_wrapper = mock.Mock()
        cache_group.cache_wrapper.get_many.side_effect = mock_get_many
        return cache_group

    def test_get_with_previous_key(self):
        # test calling get() with previously seen keys.  We should use
        # get_many() to fetch them all at once
        _cache_pattern_memory['foo'] = set(['a', 'b'])
        cache_group = self.make_mocked_cache_group()
        cache_group.get('a')
        assert_equal(cache_group.cache_wrapper.get_many.call_args,
                     mock.call(set(['a', 'b', cache_group.version_key])))

    def test_get_twice(self):
        # test calling get() twice.  On the first call we should fetch the
        # previous keys, but on the second one we should just fetch the new
        # value
        _cache_pattern_memory['foo'] = set(['a', 'b'])
        cache_group = self.make_mocked_cache_group()
        cache_group.get('a')
        cache_group.cache_wrapper.get_many.reset_mock()
        cache_group.get('d')
        assert_equal(cache_group.cache_wrapper.get_many.call_args,
                     mock.call(set(['d'])))

    def test_get_with_new_key(self):
        # test calling get() with a key not previously seen.  We should fetch
        # that value plus the previously seen ones
        _cache_pattern_memory['foo'] = set(['a', 'b'])
        cache_group = self.make_mocked_cache_group()
        cache_group.get('c')
        assert_equal(cache_group.cache_wrapper.get_many.call_args,
                     mock.call(set(['a', 'b', 'c', cache_group.version_key])))

    def test_get_many(self):
        # test calling get_many() with some previous keys and some new keys.
        # We should fetch all the previous keys and also any new keys passed
        # to get_many()
        _cache_pattern_memory['foo'] = set(['a', 'b'])
        cache_group = self.make_mocked_cache_group()
        cache_group.get_many(['b', 'c'])
        assert_equal(cache_group.cache_wrapper.get_many.call_args,
                     mock.call(set(['a', 'b', 'c', cache_group.version_key])))
