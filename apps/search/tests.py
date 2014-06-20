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

from search.forms import SearchForm
from utils.rpc import RpcMultiValueDict
from videos.search_indexes import VideoIndex

class SearchTest(TestCase):
    def get_search_qs(self, query, **params):
        form = SearchForm(RpcMultiValueDict(dict(q=query, **params)))
        return form.queryset()

    def test_simple_query(self):
        sqs = self.get_search_qs('foo')
        correct_sqs = (VideoIndex.public()
                       .auto_query('foo')
                       .filter_or(title='foo'))
        self.assertEqual(str(sqs.query), str(correct_sqs.query))

    def test_clean_input(self):
        sqs = self.get_search_qs('foo?')
        correct_sqs = (VideoIndex.public()
                       .auto_query('foo?')
                       .filter_or(title='foo\\?'))
        self.assertEqual(str(sqs.query), str(correct_sqs.query))

    def test_empty_query(self):
        self.assertEqual(str(self.get_search_qs('')),
                         str(VideoIndex.public().none()))

    def test_language_filter(self):
        sqs = self.get_search_qs('foo', video_lang='en')
        correct_sqs = (VideoIndex.public()
                       .auto_query('foo')
                       .filter_or(title='foo')
                       .filter(video_language_exact='en'))
        self.assertEqual(str(sqs.query), str(correct_sqs.query))
