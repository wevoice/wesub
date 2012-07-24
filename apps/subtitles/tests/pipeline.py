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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

"""Tests for the subtitle pipeline implementation."""

from django.test import TestCase

from apps.subtitles import pipeline
from apps.subtitles.models import SubtitleLanguage, SubtitleVersion
from apps.videos.models import Video


VIDEO_URL = 'http://youtu.be/heKK95DAKms'

def make_video():
    video, _ = Video.get_or_create_for_url(VIDEO_URL)
    return video


class TestHelperFunctions(TestCase):
    def setUp(self):
        self.video = make_video()

    def test_get_language(self):
        sl, needs_save = pipeline._get_language(self.video, 'en')
        self.assertEqual(sl.language_code, 'en')
        self.assertEqual(needs_save, True)

        sl, needs_save = pipeline._get_language(self.video, 'fr')
        self.assertEqual(sl.language_code, 'fr')
        self.assertEqual(needs_save, True)

        l = SubtitleLanguage(video=self.video, language_code='en')
        l.save()

        sl, needs_save = pipeline._get_language(self.video, 'en')
        self.assertEqual(sl.language_code, 'en')
        self.assertEqual(needs_save, False)
        self.assertEqual(sl.id, l.id)

        sl, needs_save = pipeline._get_language(self.video, 'fr')
        self.assertEqual(sl.language_code, 'fr')
        self.assertEqual(needs_save, True)


class TestBasicAdding(TestCase):
    def setUp(self):
        self.video = make_video()

    def test_add_subtitles(self):
        # Start with no SubtitleLanguages.
        self.assertEqual(
            SubtitleLanguage.objects.filter(video=self.video).count(), 0)

        # Put a version through the pipeline.
        pipeline.add_subtitles(self.video, 'en')

        # It should create the SubtitleLanguage automatically, with one version.
        self.assertEqual(
            SubtitleLanguage.objects.filter(video=self.video).count(), 1)
        self.assertEqual(
            SubtitleVersion.objects.filter(video=self.video).count(), 1)

        sl = SubtitleLanguage.objects.get(video=self.video, language_code='en')

        # Make sure the version seems sane.
        v = sl.get_tip()
        self.assertEqual(v.version_number, 1)
        self.assertEqual(v.language_code, 'en')

        # Put another version through the pipeline.
        pipeline.add_subtitles(self.video, 'en')

        # Now we should have two versions for a single language.
        self.assertEqual(
            SubtitleLanguage.objects.filter(video=self.video).count(), 1)
        self.assertEqual(
            SubtitleVersion.objects.filter(video=self.video).count(), 2)

        # Make sure it looks sane too.
        v = sl.get_tip()
        self.assertEqual(v.version_number, 2)
        self.assertEqual(v.language_code, 'en')

