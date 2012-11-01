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

import babelsubs
from babelsubs.parsers.dfxp import DFXPParser
from django.core.urlresolvers import reverse
from django.test import TestCase

from apps.subtitles import models as sub_models
from apps.videos.models import Video
from apps.videos.tests.utils import quick_add_subs


class DFXPTest(TestCase):
    def _download_subs(self, language, format):
        url = reverse("widget:download" , args=(format,))
        res = self.client.get(url, {
            'video_id': language.video.video_id,
            'lang_pk': language.pk
        })
        self.assertEqual(res.status_code, 200)
        return res.content

    def setUp(self):
        self.auth = dict(username='admin', password='admin')
        self.video = Video.get_or_create_for_url("http://www.example.com/video.mp4")[0]
        self.language = sub_models.SubtitleLanguage.objects.get_or_create(
            video=self.video,  language_code='en')[0]

    def test_dfxp_serializer(self):
        quick_add_subs(self.language, [ 'Here we go!'])
        content = self._download_subs(self.language, 'dfxp')
        serialized = DFXPParser(content)
        self.assertEqual(len(serialized.to_internal()), 1)
        self.assertEqual(babelsubs.storage.get_contents(serialized.to_internal().get_subtitles()[0]),'Here we go!')

