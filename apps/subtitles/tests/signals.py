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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

"""Test signal emmission."""

from __future__ import absolute_import

from django.test import TestCase
import mock
from utils.factories import *
from utils.test_utils import patch_for_test
from subtitles import signals
from subtitles import pipeline

class SignalsTest(TestCase):
    def setUp(self):
        self.team_video = TeamVideoFactory()
        self.video = self.team_video.video
        self.team = self.team_video.team
        self.member = self.team.get_member(self.team_video.added_by)
        self.subtitles_changed_handler = mock.Mock()
        signals.subtitles_changed.connect(self.subtitles_changed_handler,
                                          weak=False)
        self.addCleanup(signals.subtitles_changed.disconnect,
                        self.subtitles_changed_handler)
        self.language_deleted_handler = mock.Mock()
        signals.language_deleted.connect(self.language_deleted_handler,
                                         weak=False)
        self.addCleanup(signals.subtitles_changed.disconnect,
                        self.language_deleted_handler)

    def test_language_deleted(self):
        v1 = pipeline.add_subtitles(self.video, 'en', None)
        self.subtitles_changed_handler.reset_mock()
        language = v1.subtitle_language
        language.nuke_language()
        self.assertEquals(self.language_deleted_handler.call_count, 1)
        self.language_deleted_handler.assert_called_with(signal=mock.ANY,
                                                         sender=language)
        # deleting the language shouldn't result in the subtitles_changed
        # signal being emitted
        self.assertEquals(self.subtitles_changed_handler.call_count, 0)

    def test_subtitles_changed_on_new_version(self):
        # adding a version should result in the signal being sent
        v1 = pipeline.add_subtitles(self.video, 'en', None)
        language = v1.subtitle_language
        self.assertEquals(self.subtitles_changed_handler.call_count, 1)
        self.subtitles_changed_handler.assert_called_with(
            signal=mock.ANY, sender=language)

    def test_subtitles_changed_on_language_change(self):
        v1 = pipeline.add_subtitles(self.video, 'en', None)
        language = v1.subtitle_language
        self.subtitles_changed_handler.reset_mock()

        language.subtitles_complete = True
        language.save()

        self.assertEquals(self.subtitles_changed_handler.call_count, 1)
        self.subtitles_changed_handler.assert_called_with(
            signal=mock.ANY, sender=language)

    def test_send_subtitles_changed_false(self):
        v1 = pipeline.add_subtitles(self.video, 'en', None)
        language = v1.subtitle_language
        self.subtitles_changed_handler.reset_mock()

        language.subtitles_complete = True
        language.save(send_subtitles_changed=False)
        self.assertEquals(self.subtitles_changed_handler.call_count, 0)
