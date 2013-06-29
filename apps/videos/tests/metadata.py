# -*- coding: utf-8 -*-
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from django.test import TestCase

from apps.videos import metadata_manager
from apps.videos.models import Video
from apps.videos.tests.data import (
    get_video, make_subtitle_language, make_subtitle_version
)


class TestMetadataManager(TestCase):
    def test_language_count(self):
        video = get_video()
        video_pk = video.pk

        def _assert_count(n):
            metadata_manager.update_metadata(video_pk)
            video = Video.objects.get(pk=video_pk)
            self.assertEqual(video.languages_count, n)

        _assert_count(0)

        # Empty languages do not count toward the language count!
        sl_en = make_subtitle_language(video, 'en')
        _assert_count(0)

        # Neither do empty versions.
        make_subtitle_version(sl_en, subtitles=[])
        _assert_count(0)

        # But languages with non-empty versions do.
        make_subtitle_version(sl_en, subtitles=[(100, 200, 'foo')])
        _assert_count(1)

        # One more for good measure.
        sl_fr = make_subtitle_language(video, 'fr')
        _assert_count(1)

        make_subtitle_version(sl_fr, subtitles=[])
        _assert_count(1)

        make_subtitle_version(sl_fr, subtitles=[(100, 200, 'bar')])
        _assert_count(2)
