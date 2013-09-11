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

from externalsites import tasks
from externalsites import urls
from externalsites.exceptions import SyncingError
from externalsites.models import (KalturaAccount, SyncedSubtitleVersion,
                                  SyncHistory)
from subtitles import pipeline
from teams.permissions_const import ROLE_ADMIN
from utils import test_factories
from utils import test_utils
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
        self.video_url = self.video.get_primary_videourl_obj()
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
            KalturaAccount.account_type, self.account.id, self.video_url.id,
            lang.id, tip.id)

    def test_delete_subititles_on_language_deleted(self):
        lang = self.video.subtitle_language('en')
        subtitles.signals.language_deleted.send(lang)

        self.assertEqual(self.mock_delete_subtitles.call_count, 1)
        self.mock_delete_subtitles.assert_called_with(
            KalturaAccount.account_type, self.account.id, self.video_url.id,
            lang.id)

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

class SubtitleTaskTest(TestCase):
    @patch_for_test('externalsites.models.now')
    @patch_for_test('externalsites.models.KalturaAccount.update_subtitles')
    @patch_for_test('externalsites.models.KalturaAccount.delete_subtitles')
    def setUp(self, mock_delete_subtitles, mock_update_subtitles, mock_now):
        self.now = datetime.datetime(2013, 1, 1)
        mock_now.side_effect = self.make_now
        self.mock_update_subtitles = mock_update_subtitles
        self.mock_delete_subtitles = mock_delete_subtitles
        self.video = create_kaltura_video('video')
        self.video_url = self.video.get_primary_videourl_obj()
        team_video = test_factories.create_team_video(video=self.video)
        self.team = team_video.team
        self.account = KalturaAccount.objects.create(
            team=self.team, partner_id=1234, secret='abcd')
        pipeline.add_subtitles(self.video, 'en', None)
        self.reset_history()

    def reset_history(self):
        """Reset all mock objects and delete SyncedSubtitleVersion and
        SyncHistory.

        Call this after making calls that might result in syncing to happen
        that you don't want to test
        """
        self.mock_update_subtitles.reset_mock()
        self.mock_delete_subtitles.reset_mock()
        SyncHistory.objects.all().delete()
        SyncedSubtitleVersion.objects.all().delete()

    def make_now(self):
        rv = self.now
        self.now += datetime.timedelta(minutes=1)
        return rv

    def run_update_subtitles(self, language, version):
        args = ('K', self.account.id, self.video_url.id, language.id,
                version.id)
        test_utils.update_subtitles.original_func.apply(args=args)

    def run_delete_subtitles(self, language):
        args = ('K', self.account.id, self.video_url.id, language.id)
        test_utils.delete_subtitles.original_func.apply(args=args)

    def run_update_all_subtitles(self):
        args = ('K', self.account.id)
        test_utils.update_all_subtitles.original_func.apply(args=args)

    def check_synced_version(self, language, version):
        synced_version = SyncedSubtitleVersion.objects.get(
            account_type=self.account.account_type,
            account_id=self.account.id, language=language)
        self.assertEquals(synced_version.version, version)

    def check_no_synced_version(self, language):
        synced_version_qs = SyncedSubtitleVersion.objects.filter(
            account_type=self.account.account_type,
            account_id=self.account.id, language=language)
        self.assert_(not synced_version_qs.exists())

    def check_sync_history(self, language, correct_history):
        history_qs = SyncHistory.objects.filter(language=language)
        self.assertEquals(len(history_qs), len(correct_history))
        for (history, history_values) in zip(history_qs, correct_history):
            self.assertEquals(history.account_id, self.account.id)
            self.assertEquals(history.account_type, self.account.account_type)
            self.assertEquals(history.action, history_values[0])
            self.assertEquals(history.status, history_values[1])
            self.assertEquals(history.datetime, history_values[2])
            self.assertEquals(history.version, history_values[3])
            self.assertEquals(history.details, history_values[4])

    def test_upload_subtitles(self):
        now = self.now
        language = self.video.subtitle_language('en')
        version = language.get_tip()
        self.run_update_subtitles(language, version)
        self.assertEquals(self.mock_update_subtitles.call_count, 1)
        self.mock_update_subtitles.assert_called_with(self.video_url,
                                                      language, version)
        self.check_sync_history(language, [
            ('U', 'S', now, version, ''),
        ])
        self.check_synced_version(language, version)

    def test_upload_subtitles_error(self):
        now = self.now
        exc = SyncingError('Site exploded')
        self.mock_update_subtitles.side_effect = exc
        language = self.video.subtitle_language('en')
        version = language.get_tip()
        self.run_update_subtitles(language, version)
        self.assertEquals(self.mock_update_subtitles.call_count, 1)
        self.mock_update_subtitles.assert_called_with(self.video_url,
                                                      language, version)
        self.check_sync_history(language, [
            ('U', 'E', now, version, exc.msg)
        ])
        self.check_no_synced_version(language)

    def test_delete_subtitles(self):
        now = self.now
        language = self.video.subtitle_language('en')
        version = language.get_tip()
        SyncedSubtitleVersion.objects.set_synced_version(
            self.account, self.video_url, language, version)
        self.run_delete_subtitles(language)
        self.assertEquals(self.mock_delete_subtitles.call_count, 1)
        self.mock_delete_subtitles.assert_called_with(self.video_url,
                                                      language)
        self.check_sync_history(language, [
            ('D', 'S', now, None, '')
        ])
        self.check_no_synced_version(language)

    def test_delete_subtitles_error(self):
        now = self.now
        exc = SyncingError('Site exploded')
        self.mock_delete_subtitles.side_effect = exc
        language = self.video.subtitle_language('en')
        version = language.get_tip()
        SyncedSubtitleVersion.objects.set_synced_version(
            self.account, self.video_url, language, version)
        self.run_delete_subtitles(language)
        self.assertEquals(self.mock_delete_subtitles.call_count, 1)
        self.mock_delete_subtitles.assert_called_with(self.video_url,
                                                      language)
        self.check_sync_history(language, [
            ('D', 'E', now, None, exc.msg)
        ])
        self.check_synced_version(language, version)

    def test_upload_all_subtitles(self):
        to_sync = [self.video.subtitle_language('en').get_tip()]
        pipeline.add_subtitles(self.video, 'fr', None)
        to_sync.append(pipeline.add_subtitles(self.video, 'fr', None))
        to_sync.append(pipeline.add_subtitles(self.video, 'de', None))
        to_sync.append(pipeline.add_subtitles(self.video, 'es', None))
        pipeline.add_subtitles(self.video, 'es', None, visibility='private')
        pipeline.add_subtitles(self.video, 'pt-br', None, visibility='private')
        self.reset_history()

        now_values = {}

        def update_subtitles(video_url, language, version):
            now_values[language.id] = self.now
            if language.language_code == 'es':
                raise SyncingError('Error')
        self.mock_update_subtitles.side_effect = update_subtitles

        self.run_update_all_subtitles()
        self.assertEquals(self.mock_update_subtitles.call_count,
                          len(to_sync))
        for version in to_sync:
            language = version.subtitle_language
            self.mock_update_subtitles.assert_any_call(self.video_url,
                                                       language, version)
            if language.language_code != 'es':
                self.check_sync_history(language, [
                    ('U', 'S', now_values[language.id], version, '')
                ])
                self.check_synced_version(language, version)
            else:
                self.check_sync_history(language, [
                    ('U', 'E', now_values[language.id], version, 'Error'),
                ])
                self.check_no_synced_version(language)

    def test_history(self):
        pass

class KalturaSyncingTest(TestCase):
    def test_upload(self):
        pass

    def test_reupload(self):
        pass
