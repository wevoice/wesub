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

from subtitles import workflows
from subtitles import pipeline
from subtitles.exceptions import ActionError
from utils.factories import *
from utils import test_utils

class TestAction(workflows.Action):
    def __init__(self, name, complete=None):
        self.name = self.label = name
        self.complete = complete
        self.do_perform = mock.Mock()

class ActionsTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.video = VideoFactory()
        pipeline.add_subtitles(self.video, 'en',
                               SubtitleSetFactory(num_subs=10))
        self.subtitle_language = self.video.subtitle_language('en')

        self.action1 = TestAction('action1', True)
        self.action2 = TestAction('action2', False)
        self.workflow = workflows.Workflow(self.video, 'en')
        self.workflow.get_actions = mock.Mock(return_value=[
            self.action1, self.action2
        ])

    def perform_action(self, action_name, saved_version=None):
        self.workflow.perform_action(self.user, action_name, saved_version)

    def test_perform_action(self):
        version = pipeline.add_subtitles(self.video, 'en',
                                         SubtitleSetFactory(num_subs=10))
        self.perform_action('action1')
        self.action1.do_perform.assert_called_with(
            self.user, self.video, version.subtitle_language, None)

    def test_perform_action_with_version(self):
        version = pipeline.add_subtitles(self.video, 'en',
                                         SubtitleSetFactory(num_subs=10))
        self.perform_action('action1', version)
        self.action1.do_perform.assert_called_with(
            self.user, self.video, version.subtitle_language, version)

    def test_perform_with_invalid_action(self):
        with assert_raises(LookupError):
            self.perform_action('other-action')

    def test_needs_complete_subtitles(self):
        # With 0 subtitles, we shouldn't be able to perform an action with
        # complete=True
        pipeline.add_subtitles(self.video, 'en',
                               SubtitleSetFactory(num_subs=0))
        with assert_raises(ActionError):
            self.perform_action('action1', None)
