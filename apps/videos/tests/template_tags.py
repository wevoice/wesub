# -*- coding: utf-8 -*-
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from django.core.urlresolvers import reverse
from django.test import TestCase

from apps.videos.templatetags.subtitles_tags import language_url
from apps.videos.templatetags.videos_tags import shortlink_for_video
from apps.videos.tests.data import get_video, make_subtitle_language



class TestTemplateTags(TestCase):
    def test_language_url_for_empty_lang(self):
        v = get_video(1)
        sl = make_subtitle_language(v, 'en')
        self.assertIsNotNone(language_url(None, sl))

class ShortUrlTest(TestCase):
    def setUp(self):
        self.video = get_video(1)

    def test_short_url(self):
        short_url = shortlink_for_video(self.video)
        response = self.client.get(short_url)
        regular_url = reverse("videos:video", args=(self.video.video_id,))
        # short urls have no language path on the url, so take that out
        regular_url = regular_url[regular_url.find('/videos'):]
        self.assertIn(regular_url , response['Location'])
