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
from apps.subtitles.tests.utils import make_video
from libs.dxfpy import SubtitleSet


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

    def test_add_empty_versions(self):
        # Start with no SubtitleLanguages.
        self.assertEqual(
            SubtitleLanguage.objects.filter(video=self.video).count(), 0)

        # Put a version through the pipeline.
        pipeline.add_subtitles(self.video, 'en', None)

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
        pipeline.add_subtitles(self.video, 'en', None)

        # Now we should have two versions for a single language.
        self.assertEqual(
            SubtitleLanguage.objects.filter(video=self.video).count(), 1)
        self.assertEqual(
            SubtitleVersion.objects.filter(video=self.video).count(), 2)

        # Make sure it looks sane too.
        v = sl.get_tip()
        self.assertEqual(v.version_number, 2)
        self.assertEqual(v.language_code, 'en')

    def test_add_subtitles(self):
        def _get_tip_subs():
            sl = SubtitleLanguage.objects.get(video=self.video,
                                              language_code='en')
            return list(sl.get_tip().get_subtitles().subtitle_items())

        # Passing nil.
        pipeline.add_subtitles(self.video, 'en', None)

        self.assertEqual(_get_tip_subs(), [])

        # Passing a list of tuples.
        pipeline.add_subtitles(self.video, 'en', [(100, 200, "foo"),
                                                  (300, None, "bar")])

        self.assertEqual(_get_tip_subs(), [(100, 200, "foo"),
                                           (300, None, "bar")])

        # Passing an iterable of tuples.
        pipeline.add_subtitles(self.video, 'en', (s for s in
                                                  [(101, 200, "foo"),
                                                   (300, None, "bar")]))

        self.assertEqual(_get_tip_subs(), [(101, 200, "foo"),
                                           (300, None, "bar")])

        # Passing a SubtitleSet.
        subs = SubtitleSet.from_list([(110, 210, "foo"),
                                      (310, 410, "bar"),
                                      (None, None, '"baz"')])

        pipeline.add_subtitles(self.video, 'en', subs)

        self.assertEqual(_get_tip_subs(), [(110, 210, "foo"),
                                           (310, 410, "bar"),
                                           (None, None, '"baz"')])

        # Passing a hunk of XML.
        subs = SubtitleSet.from_list([(10000, 22000, "boots"),
                                      (23000, 29000, "cats")])

        pipeline.add_subtitles(self.video, 'en', subs.to_xml())

        self.assertEqual(_get_tip_subs(), [(10000, 22000, "boots"),
                                           (23000, 29000, "cats")])


        # Passing nonsense should TypeError out.
        self.assertRaises(TypeError,
                          lambda: pipeline.add_subtitles(self.video, 'en', 1))

        # Make sure all the versions are there.
        sl = SubtitleLanguage.objects.get(video=self.video,
                                          language_code='en')
        self.assertEqual(sl.subtitleversion_set.count(), 5)

