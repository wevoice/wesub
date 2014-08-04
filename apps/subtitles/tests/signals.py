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

    @patch_for_test('subtitles.signals.public_tip_changed')
    @patch_for_test('subtitles.signals.language_deleted')
    def test_language_deleted(self, mock_signal, mock_public_tip_changed):
        v1 = pipeline.add_subtitles(self.video, 'en', None)
        mock_public_tip_changed.send.reset_mock()
        language = v1.subtitle_language
        language.nuke_language()
        self.assertEquals(mock_signal.send.call_count, 1)
        mock_signal.send.assert_called_with(language)
        # deleting the language shouldn't result in the public_tip_changed
        # signal being emitted
        self.assertEquals(mock_public_tip_changed.send.call_count, 0)

    def check_public_tip_changed(self, mock_signal, language, version):
        self.assertEquals(mock_signal.send.call_count, 1)
        self.assertEquals(mock_signal.send.call_args[0][0], language)
        self.assertEquals(mock_signal.send.call_args[1]['version'], version)

    def check_subtitles_complete_changed(self, mock_signal, language):
        self.assertEquals(mock_signal.send.call_count, 1)
        self.assertEquals(mock_signal.send.call_args[0], (language,))

    @patch_for_test('subtitles.signals.language_deleted')
    @patch_for_test('subtitles.signals.public_tip_changed')
    def test_public_tip_changed(self, mock_signal,
                                mock_language_deleted_signal):
        # adding a version should result in the signal being sent
        v1 = pipeline.add_subtitles(self.video, 'en', None)
        language = v1.subtitle_language
        self.check_public_tip_changed(mock_signal, language, v1)
        mock_signal.send.reset_mock()
        # try that again with a second version
        v2 = pipeline.add_subtitles(self.video, 'en', None)
        self.check_public_tip_changed(mock_signal, language, v2)
        mock_signal.send.reset_mock()
        # adding a non-public version shouldn't send the signal
        v3 = pipeline.add_subtitles(self.video, 'en', None,
                                    visibility='private')
        self.assertEquals(mock_signal.send.call_count, 0)
        # but we should when the language gets published
        v3.publish()
        self.check_public_tip_changed(mock_signal, language, v3)
        mock_signal.send.reset_mock()
        # unpublishing a language should result in the signal getting sent for
        # the new tip
        v3.unpublish()
        self.check_public_tip_changed(mock_signal, language, v2)
        mock_signal.send.reset_mock()
        # try that again
        v2.unpublish()
        self.check_public_tip_changed(mock_signal, language, v1)
        mock_signal.send.reset_mock()
        # unpublishing the last version should result in the language deleted
        # signal being emitted
        v1.unpublish()
        self.assertEquals(mock_signal.send.call_count, 0)
        mock_language_deleted_signal.send.assert_called_once_with(language)

    @patch_for_test('subtitles.signals.subtitles_complete_changed')
    def test_subtitles_complete_changed(self, mock_subtitle_complete_changed):
        # initial version with complete=False should result in no signal
        v = pipeline.add_subtitles(self.video, 'en', None, complete=False)
        language = v.subtitle_language
        self.assertEquals(mock_subtitle_complete_changed.send.call_count, 0)
        # initial version with complete=True should result in a signal
        v = pipeline.add_subtitles(self.video, 'es', None, complete=True)
        language_es = v.subtitle_language
        self.check_subtitles_complete_changed(mock_subtitle_complete_changed,
                                              language_es)
        mock_subtitle_complete_changed.reset_mock()
        # adding a new version with a different value of subtitles_complete
        # should result in a signal
        pipeline.add_subtitles(self.video, 'en', None, complete=True)
        self.check_subtitles_complete_changed(mock_subtitle_complete_changed,
                                              language)
        mock_subtitle_complete_changed.reset_mock()
        # adding a new version with the same value of subtitles_complete
        # should result in no signal
        pipeline.add_subtitles(self.video, 'en', None, complete=True)
        self.assertEquals(mock_subtitle_complete_changed.send.call_count, 0)
        # adding a new version with the subtitles_complete=None
        # should result in no signal
        pipeline.add_subtitles(self.video, 'en', None, complete=None)
        self.assertEquals(mock_subtitle_complete_changed.send.call_count, 0)
        # changing the subtitles_complete attribute and saving the model
        # should also result in a signal
        language.subtitles_complete = True
        language.save()
        self.check_subtitles_complete_changed(mock_subtitle_complete_changed,
                                              language)
        mock_subtitle_complete_changed.reset_mock()
        # A save with no change to subtitles_complete should result in no
        # signal
        language.save()
        self.assertEquals(mock_subtitle_complete_changed.send.call_count, 0)
