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

from django.test import TestCase
from nose.tools import assert_equal

from search.forms import SearchForm
from utils.rpc import RpcMultiValueDict
from videos.search_indexes import VideoIndex
from utils import test_utils

def assert_search_querysets_equal(sqs1, sqs2):
    assert_equal(type(sqs1), type(sqs2))
    assert_equal(str(sqs1.query), str(sqs2.query))

class SearchTest(TestCase):
    def get_search_qs(self, query, **params):
        form = SearchForm(RpcMultiValueDict(dict(q=query, **params)))
        return form.queryset()

    def test_simple_query(self):
        assert_search_querysets_equal(self.get_search_qs('foo'),
                                      VideoIndex.public()
                                      .auto_query('foo')
                                      .filter_or(title='foo'))

    def test_clean_input(self):
        assert_search_querysets_equal(self.get_search_qs('foo?'),
                                      VideoIndex.public()
                                      .auto_query('foo?')
                                      .filter_or(title='foo\\?'))

    def test_empty_query(self):
        assert_search_querysets_equal(self.get_search_qs(''),
                                      VideoIndex.public().none())

    def test_video_lang_filter(self):
        # set up fake faceting info so that we can select english as the
        # filter
        test_utils.get_language_facet_counts.return_value = (
            [('en', 10)], []
        )

        sqs = self.get_search_qs('foo', video_lang='en')
        assert_search_querysets_equal(sqs,
                                      VideoIndex.public()
                                      .auto_query('foo')
                                      .filter_or(title='foo')
                                      .filter(video_language_exact='en'))

    def check_choices(self, field, correct_choices):
        self.assertEqual([c[0] for c in field.choices],
                         correct_choices)

    def check_get_language_facet_counts_query(self, correct_queryset):
        self.assertEqual(test_utils.get_language_facet_counts.call_count, 1)
        assert_search_querysets_equal(
            test_utils.get_language_facet_counts.call_args[0][0],
            correct_queryset)

    def test_facet_choices(self):
        video_lang_facet_info = [
            ('en', 10),
            ('fr', 20),
        ]
        language_facet_info = [
            ('en', 10),
            ('es', 7),
        ]
        test_utils.get_language_facet_counts.return_value = (
            video_lang_facet_info, language_facet_info
        )
        form = SearchForm(RpcMultiValueDict(dict(q='foo')))
        # we should always list the blank choice first, then the languages
        # with facet info, in descending order
        self.check_choices(form.fields['video_lang'], ['', 'fr', 'en'])
        self.check_choices(form.fields['langs'], ['', 'en', 'es'])
        # check that get_language_facet_counts() was presented with the
        # correct query
        self.check_get_language_facet_counts_query(VideoIndex.public()
                                                   .auto_query('foo')
                                                   .filter_or(title='foo'))

    def test_facet_choices_empty_query(self):
        form = SearchForm(RpcMultiValueDict(dict(q='')))
        # If we don't have a query, we should use the all videos
        self.check_get_language_facet_counts_query(VideoIndex.public())
