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

from __future__ import absolute_import
import datetime
import hashlib
import itertools

from django.test import TestCase
from django.db.models.signals import post_save

import mock

from teams.permissions_const import ROLE_ADMIN
from externalsites.models import KalturaAccount
from subtitles import pipeline
from utils import test_factories
from utils.test_utils import patch_for_test
import subtitles.signals

def create_kaltura_video(name):
    # generate something that looks like a kaltura id
    entry_id = '1_' + hashlib.md5(name).hexdigest()[:8]
    url = ('http://cdnbakmi.kaltura.com'
            '/p/1492321/sp/149232100/serveFlavor/entryId/'
            '%s/flavorId/1_dqgopb2z/name/%s.mp4') % (entry_id, name)
    return test_factories.create_video(url=url, video_type='K')

class SignalHandlingTest(TestCase):
    @patch_for_test('externalsites.tasks.update_all_subtitles')
    @patch_for_test('externalsites.tasks.update_subtitles')
    @patch_for_test('externalsites.tasks.delete_subtitles')
    def setUp(self, mock_delete_subtitles, mock_update_subtitles,
              mock_update_all_subtitles):
        self.mock_delete_subtitles = mock_delete_subtitles
        self.mock_update_subtitles = mock_update_subtitles
        self.mock_update_all_subtitles = mock_update_all_subtitles
        self.video = create_kaltura_video('video')
        team_video = test_factories.create_team_video(video=self.video)
        self.team = team_video.team
        self.account = KalturaAccount.objects.create(
            team=self.team, partner_id=1234, secret='abcd')
        pipeline.add_subtitles(self.video, 'en', None)
        self.mock_update_all_subtitles.reset_mock()
        self.mock_update_subtitles.reset_mock()
        self.mock_delete_subtitles.reset_mock()

    def test_update_subtitles_on_public_tip_changed(self):
        lang = self.video.subtitle_language('en')
        tip = lang.get_tip()
        subtitles.signals.public_tip_changed.send(
            sender=lang, version=tip)
        self.assertEqual(self.mock_update_subtitles.call_count, 1)
        self.mock_update_subtitles.assert_called_with(
            KalturaAccount.account_type, self.account.id, lang.id, tip.id)

    def test_delete_subititles_on_language_deleted(self):
        lang = self.video.subtitle_language('en')
        subtitles.signals.language_deleted.send(lang)

        self.assertEqual(self.mock_delete_subtitles.call_count, 1)
        self.mock_delete_subtitles.assert_called_with(
            KalturaAccount.account_type, self.account.id, lang.id)

    def test_update_all_subtitles_on_account_save(self):
        post_save.send(KalturaAccount, instance=self.account, created=True)
        self.assertEqual(self.mock_update_all_subtitles.call_count, 1)
        self.mock_update_all_subtitles.assert_called_with(
            KalturaAccount.account_type, self.account.id)
        # we should update all subtitles on a save as well as a create, since
        # the new info may allow us to successfully sync subtitles that we
        # couldn't before.
        self.mock_update_all_subtitles.reset_mock()
        post_save.send(KalturaAccount, instance=self.account, created=False)
        self.assertEqual(self.mock_update_all_subtitles.call_count, 1)
        self.mock_update_all_subtitles.assert_called_with(
            KalturaAccount.account_type, self.account.id)

    def check_tasks_not_called(self, video):
        lang = pipeline.add_subtitles(video, 'en', None).subtitle_language
        subtitles.signals.public_tip_changed.send(
            sender=lang, version=lang.get_tip())
        self.assertEquals(self.mock_update_subtitles.call_count, 0)

        subtitles.signals.language_deleted.send(lang)
        self.assertEquals(self.mock_delete_subtitles.call_count, 0)

    def test_tasks_not_called_for_non_team_videos(self):
        video = create_kaltura_video('video2')
        self.check_tasks_not_called(video)

    def test_tasks_not_called_if_no_account(self):
        # for non-team videos, we shouldn't schedule a task
        video = create_kaltura_video('video2')
        other_team = test_factories.create_team()
        test_factories.create_team_video(other_team, video=video)
        self.check_tasks_not_called(video)

    def test_tasks_not_called_for_non_team_videos(self):
        video = test_factories.create_video()
        test_factories.create_team_video(team=self.team, video=video)
        self.check_tasks_not_called(video)
