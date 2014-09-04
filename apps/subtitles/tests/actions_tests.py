# Amara, universalsubtitles.org
#
# Copyright (C) 2014 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.html.

from __future__ import absolute_import

from django.test import TestCase
from nose.tools import *
import mock

from subtitles import actions
from subtitles import pipeline
from utils.factories import *
from utils import test_utils

class TestAction(actions.Action):
    def __init__(self, name, complete=None):
        self.name = self.label = name
        self.complete = complete
        self.handle = mock.Mock()

class ActionsTest(TestCase):
    @test_utils.patch_for_test('subtitles.actions.get_actions')
    def setUp(self, mock_get_actions):
        self.user = UserFactory()
        self.video = VideoFactory()
        pipeline.add_subtitles(self.video, 'en',
                               SubtitleSetFactory(num_subs=10))
        self.subtitle_language = self.video.subtitle_language('en')

        self.action1 = TestAction('action1', True)
        self.action2 = TestAction('action2', False)
        mock_get_actions.return_value = [ self.action1, self.action2 ]


    def perform_action(self, action_name, saved_version=None):
        actions.perform_action(self.user, self.video, 'en', action_name,
                               saved_version)

    def can_perform_action(self, action_name):
        return actions.can_perform_action(self.user, self.video, 'en',
                                          action_name)

    def test_perform_action(self):
        self.perform_action('action1')
        self.action1.handle.assert_called_with(
            self.user, self.subtitle_language, None)

    def test_perform_action_with_version(self):
        version = pipeline.add_subtitles(self.video, 'en',
                                         SubtitleSetFactory(num_subs=10))
        self.perform_action('action1', version)
        self.action1.handle.assert_called_with(
            self.user, self.subtitle_language, version)

    def test_perform_with_invalid_action(self):
        with assert_raises(ValueError):
            self.perform_action('other-action')

    def test_set_subtitles_complete_flag(self):
        # when we run an action with complete=True, it should set
        # subtitles_complete to True
        self.subtitle_language.subtitles_complete = False
        self.perform_action('action1', None)
        assert_equals(self.subtitle_language.subtitles_complete, True)

    def test_unset_subtitles_complete_flag(self):
        self.subtitle_language.subtitles_complete = True
        self.perform_action('action2', None)
        assert_equals(self.subtitle_language.subtitles_complete, False)

    def test_complete_set_requires_completed_subs(self):
        # With 0 subtitles, we shouldn't be able to perform an action with
        # complete=True
        pipeline.add_subtitles(self.video, 'en',
                               SubtitleSetFactory(num_subs=0))
        assert_false(self.can_perform_action('action1'))
        with assert_raises(ValueError):
            self.perform_action('action1', None)
