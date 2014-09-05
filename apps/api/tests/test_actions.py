# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
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

import json

from django.test import TestCase
from django.test.client import Client
from nose.tools import *
import mock

from subtitles import actions
from subtitles import pipeline
from subtitles.tests.actions_tests import TestAction
from utils import test_utils
from utils.factories import *

class TestActionsAPI(TestCase):
    @test_utils.patch_for_test('subtitles.actions.get_actions')
    def setUp(self, mock_get_actions):
        self.mock_get_actions = mock_get_actions
        self.setup_actions()
        self.setup_video()
        self.user = UserFactory()
        self.client = Client()
        self.client.login(username=self.user, password='password')

    def setup_actions(self):
        self.action1 = TestAction('action1', False)
        self.action2 = TestAction('action2', True)
        self.action3 = TestAction('action2', None)
        self.mock_get_actions.return_value = [
            self.action1, self.action2, self.action3
        ]

    def setup_video(self):
        self.video = VideoFactory()
        pipeline.add_subtitles(self.video, 'en', None)
        self.api_path = ('/api2/partners/videos/{0}/languages/en'
                         '/subtitles/actions/'.format(self.video.video_id))

    def test_list(self):
        response = self.client.get(self.api_path)
        assert_equal(response.status_code, 200)
        data = json.loads(response.content)
        assert_equal(data, [
            self.api_data_for_action(self.action1),
            self.api_data_for_action(self.action2),
            self.api_data_for_action(self.action3),
        ])

    def api_data_for_action(self, action):
        return {
            'name': action.name,
            'label': action.label,
            'complete': action.complete,
        }

    def test_perform(self):
        response = self.client.post(self.api_path, {
            'action': 'action1',
        })
        assert_equal(response.status_code, 200, response.content)
        assert_equal(self.action1.handle.call_count, 1)

    def test_perform_with_bad_data(self):
        response = self.client.post(self.api_path, {})
        assert_equal(response.status_code, 400, response.content)

    def test_perform_with_bad_action(self):
        response = self.client.post(self.api_path, {
            'action': 'bad-action',
        })
        assert_equal(response.status_code, 400, response.content)
