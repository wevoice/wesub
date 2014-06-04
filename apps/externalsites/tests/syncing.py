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
import itertools
import string

from django.test import TestCase
from django.db.models.signals import post_save
from django.utils import simplejson as json
import babelsubs
import mock

from externalsites import tasks
from externalsites import signalhandlers
from externalsites.exceptions import SyncingError
from externalsites.models import (KalturaAccount, SyncedSubtitleVersion,
                                  SyncHistory)
from externalsites.syncing import kaltura, brightcove
from subtitles import pipeline
from teams.permissions_const import ROLE_ADMIN
from utils import test_utils
from utils.factories import *
from utils.test_utils import patch_for_test
import subtitles.signals

class SignalHandlingTest(TestCase):
    @patch_for_test('externalsites.tasks.update_all_subtitles')
    @patch_for_test('externalsites.tasks.update_subtitles')
    @patch_for_test('externalsites.tasks.delete_subtitles')
    def setUp(self, mock_delete_subtitles, mock_update_subtitles,
              mock_update_all_subtitles):
        self.mock_delete_subtitles = mock_delete_subtitles
        self.mock_update_subtitles = mock_update_subtitles
        self.mock_update_all_subtitles = mock_update_all_subtitles
        self.video = KalturaVideoFactory(name='video')
        self.video_url = self.video.get_primary_videourl_obj()
        team_video = TeamVideoFactory(video=self.video)
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
        self.assertEqual(self.mock_update_subtitles.delay.call_count, 1)
        self.mock_update_subtitles.delay.assert_called_with(
            KalturaAccount.account_type, self.account.id, self.video_url.id,
            lang.id)

    def test_delete_subititles_on_language_deleted(self):
        lang = self.video.subtitle_language('en')
        subtitles.signals.language_deleted.send(lang)

        self.assertEqual(self.mock_delete_subtitles.delay.call_count, 1)
        self.mock_delete_subtitles.delay.assert_called_with(
            KalturaAccount.account_type, self.account.id, self.video_url.id,
            lang.id)

    def test_update_all_subtitles_on_account_save(self):
        post_save.send(KalturaAccount, instance=self.account, created=True)
        self.assertEqual(self.mock_update_all_subtitles.delay.call_count, 1)
        self.mock_update_all_subtitles.delay.assert_called_with(
            KalturaAccount.account_type, self.account.id)
        # we should update all subtitles on a save as well as a create, since
        # the new info may allow us to successfully sync subtitles that we
        # couldn't before.
        self.mock_update_all_subtitles.reset_mock()
        post_save.send(KalturaAccount, instance=self.account, created=False)
        self.assertEqual(self.mock_update_all_subtitles.delay.call_count, 1)
        self.mock_update_all_subtitles.delay.assert_called_with(
            KalturaAccount.account_type, self.account.id)

    def check_tasks_not_called(self, video):
        lang = pipeline.add_subtitles(video, 'en', None).subtitle_language
        subtitles.signals.public_tip_changed.send(
            sender=lang, version=lang.get_tip())
        self.assertEquals(self.mock_update_subtitles.call_count, 0)

        subtitles.signals.language_deleted.send(lang)
        self.assertEquals(self.mock_delete_subtitles.call_count, 0)

    def test_tasks_not_called_for_non_team_videos(self):
        video = KalturaVideoFactory(name='video2')
        self.check_tasks_not_called(video)

    def test_tasks_not_called_if_no_account(self):
        # for non-team videos, we shouldn't schedule a task
        video = KalturaVideoFactory(name='video2')
        other_team = TeamFactory()
        TeamVideoFactory(team=other_team, video=video)
        self.check_tasks_not_called(video)

    def test_tasks_not_called_for_non_team_videos(self):
        video = VideoFactory()
        TeamVideoFactory(team=self.team, video=video)
        self.check_tasks_not_called(video)

class SubtitleTaskTest(TestCase):
    @patch_for_test('externalsites.models.now')
    @patch_for_test('externalsites.models.KalturaAccount.do_update_subtitles')
    @patch_for_test('externalsites.models.KalturaAccount.do_delete_subtitles')
    def setUp(self, mock_delete_subtitles, mock_update_subtitles, mock_now):
        self.now = datetime.datetime(2013, 1, 1)
        mock_now.side_effect = self.make_now
        self.mock_update_subtitles = mock_update_subtitles
        self.mock_delete_subtitles = mock_delete_subtitles
        self.video = KalturaVideoFactory(name='video')
        self.video_url = self.video.get_primary_videourl_obj()
        team_video = TeamVideoFactory(video=self.video)
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

    def run_update_subtitles(self, language):
        args = ('K', self.account.id, self.video_url.id, language.id)
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
            self.assertEquals(history.result, history_values[1])
            self.assertEquals(history.datetime, history_values[2])
            self.assertEquals(history.version, history_values[3])
            self.assertEquals(history.details, history_values[4])

    def test_upload_subtitles(self):
        now = self.now
        language = self.video.subtitle_language('en')
        version = language.get_tip()
        self.run_update_subtitles(language)
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
        self.run_update_subtitles(language)
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

        def update_subtitles(video_url, language, tip):
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
        en_1 = self.video.subtitle_language('en').get_tip()
        en_2 = pipeline.add_subtitles(self.video, 'en', None)
        fr_1 = pipeline.add_subtitles(self.video, 'fr', None)
        en = en_1.subtitle_language
        fr = fr_1.subtitle_language
        self.reset_history()

        english_history = []
        french_history = []

        def create_update_success(version):
            return SyncHistory.objects.create_for_success(
                account=self.account,
                video_url=self.video_url,
                action=SyncHistory.ACTION_UPDATE_SUBTITLES,
                language=version.subtitle_language,
                version=version)

        def create_delete_success(language):
            return SyncHistory.objects.create_for_success(
                account=self.account,
                video_url=self.video_url,
                action=SyncHistory.ACTION_DELETE_SUBTITLES,
                language=language)

        def create_update_error(version, message):
            return SyncHistory.objects.create_for_error(
                SyncingError(message),
                account=self.account,
                video_url=self.video_url,
                action=SyncHistory.ACTION_UPDATE_SUBTITLES,
                language=version.subtitle_language,
                version=version)

        def create_delete_error(language, message):
            return SyncHistory.objects.create_for_error(
                SyncingError(message),
                account=self.account,
                video_url=self.video_url,
                action=SyncHistory.ACTION_DELETE_SUBTITLES,
                language=language)

        # create a bunch of random events and make sure that we store them
        # correctly
        english_history.append(create_update_success(en_1))
        english_history.append(create_update_success(en_2))
        english_history.append(create_update_error(en_1, 'Bad auth'))
        english_history.append(create_delete_success(en))
        english_history.append(create_update_success(en_2))

        french_history.append(create_update_error(fr_1, 'Server down'))
        french_history.append(create_delete_error(fr, 'Invalid entry id'))
        french_history.append(create_delete_success(fr))

        self.assertEquals(list(SyncHistory.objects.get_for_language(en)),
                          list(reversed(english_history)))

        self.assertEquals(list(SyncHistory.objects.get_for_language(fr)),
                          list(reversed(french_history)))

class KalturaAccountTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.partner_id = 1234
        self.secret = 'Secret'
        self.account = KalturaAccount.objects.create(
            team=TeamFactory(), partner_id=self.partner_id,
            secret = self.secret)
        self.entry_id = 'EntryId'
        url = ('http://cdnbakmi.kaltura.com'
                '/p/1492321/sp/149232100/serveFlavor/entryId/'
                '%s/flavorId/1_dqgopb2z/name/video.mp4') % self.entry_id
        self.video = VideoFactory(video_url__url=url, video_url__type='K')
        self.video_url = self.video.get_primary_videourl_obj()
        self.version = pipeline.add_subtitles(self.video, 'en',
                                              [(100, 200, "sub 1")])
        self.language = self.version.subtitle_language

    @patch_for_test('externalsites.syncing.kaltura.update_subtitles')
    def test_kalturaaccount_update_subtitles(self, mock_update_subtitles):
        srt_data = babelsubs.to(self.version.get_subtitles(), 'srt')
        self.account.update_subtitles(self.video_url, self.language)
        mock_update_subtitles.assert_called_with(self.partner_id, self.secret,
                                                 self.entry_id, 'en',
                                                 srt_data)

    @patch_for_test('externalsites.syncing.kaltura.delete_subtitles')
    def test_kalturaaccount_delete_subtitles(self, mock_delete_subtitles):
        self.account.delete_subtitles(self.video_url, self.language)
        mock_delete_subtitles.assert_called_with(self.partner_id, self.secret,
                                                 self.entry_id, 'en')


class KalturaApiMocker(test_utils.RequestsMocker):
    api_url = 'http://www.kaltura.com/api_v3/'

    def __init__(self, partner_id, secret, video_id):
        test_utils.RequestsMocker.__init__(self)
        self.partner_id = partner_id
        self.secret = secret
        self.video_id = video_id
        self.session_id = 'SessionString'

    def expect_api_call(self, service, action, data, body):
        params={'service': service, 'action': action}
        self.expect_request('post', self.api_url, params=params,
                            data=data, body=body)

    def expect_session_start(self, return_error=False):
        if return_error:
            result = self.session_start_error_response()
        else:
            result = self.kaltura_result(self.session_id)
        self.expect_api_call(
            'session', 'start', {
                'secret': self.secret,
                'partnerId': self.partner_id,
                'type': 2, # SESSION_TYPE_ADMIN
            },
            result,
        )

    def expect_session_end(self):
        self.expect_api_call(
            'session', 'end', {
                'ks': self.session_id,
            },
            self.kaltura_result('')
        )

    def expect_captionasset_list(self, return_captions):
        self.expect_api_call(
            'caption_captionasset', 'list', {
                'ks': self.session_id,
                'filter:entryIdEqual': self.video_id,
            },
            self.caption_list_response(return_captions)
        )

    def expect_captionasset_add(self, caption_id, language):
        self.expect_api_call(
            'caption_captionasset', 'add', {
                'ks': self.session_id,
                'entryId': self.video_id,
                'captionAsset:partnerData': kaltura.PARTNER_DATA_TAG,
                'captionAsset:language': language,
                'captionAsset:format': 1, # SRT
                'captionAsset:fileExt': 'srt',
            },
            self.caption_response(caption_id, language, 0,
                                  kaltura.PARTNER_DATA_TAG))

    def expect_captionasset_add_return_error(self, language):
        self.expect_api_call(
            'caption_captionasset', 'add', {
                'ks': self.session_id,
                'entryId': self.video_id,
                'captionAsset:partnerData': kaltura.PARTNER_DATA_TAG,
                'captionAsset:language': language,
                'captionAsset:format': 1, # SRT
                'captionAsset:fileExt': 'srt',
            },
            self.entry_not_found_response())

    def expect_captionasset_setcontent(self, caption_id, caption_data,
                                       language):
        self.expect_api_call(
            'caption_captionasset', 'setcontent', {
                'ks': self.session_id,
                'id': caption_id,
                'contentResource:objectType': 'KalturaStringResource',
                'contentResource:content': caption_data,
            },
            self.caption_response(caption_id, language, len(caption_data),
                                  kaltura.PARTNER_DATA_TAG)
        )

    def expect_captionasset_delete(self, caption_id):
        self.expect_api_call(
            'caption_captionasset', 'delete', {
                'ks': self.session_id,
                'captionAssetId': caption_id,
            },
            self.kaltura_result(''),
        )

    def kaltura_result(self, result):
        return string.Template(
            '<?xml version="1.0" encoding="utf-8"?><xml>'
            '<result>$result</result>'
            '<executionTime>1.0</executionTime></xml>').substitute(
                result=result)

    def caption_response(self, caption_id, language, size, partner_data):
        return self.kaltura_result(
            self.caption_asset_response(caption_id, language, size,
                                        partner_data))

    def caption_list_response(self, caption_info):
        object_list = [
            self.caption_asset_response(cid, language, size, partner_data)
            for (cid, language, size, partner_data) in caption_info
        ]
        return self.kaltura_result(string.Template(
            '<objectType>KalturaCaptionAssetListResponse</objectType>'
            '<objects>$objects</objects>'
            '<totalCount>$count</totalCount>').substitute(
                count=len(caption_info),
                objects=''.join('<item>%s</item>' % o for o in object_list)))

    def caption_asset_response(self, caption_id, language, size,
                               partner_data):
        if language == 'English':
            language_code = 'en'
        elif language == 'French':
            language_code = 'fr'
        else:
            raise ValueError("Unknown language: %s" % language)
        return string.Template(
            '<objectType>KalturaCaptionAsset</objectType>'
            '<captionParamsId></captionParamsId>'
            '<language>$language</language>'
            '<languageCode>$language_code</languageCode>'
            '<isDefault></isDefault>'
            '<label></label>'
            '<format>$format_id</format>'
            '<status>0</status>'
            '<id>$caption_id</id>'
            '<entryId>$video_id</entryId>'
            '<partnerId>$partner_id</partnerId>'
            '<version></version>'
            '<size>$size</size>'
            '<tags></tags><fileExt></fileExt>'
            '<createdAt>1378994564</createdAt>'
            '<updatedAt>1378994564</updatedAt>'
            '<deletedAt></deletedAt>'
            '<description></description>'
            '<partnerData>$partner_data</partnerData>'
            '<partnerDescription></partnerDescription>'
            '<actualSourceAssetParamsIds></actualSourceAssetParamsIds>'
        ).substitute(
            caption_id=caption_id,
            video_id=self.video_id,
            partner_id=self.partner_id,
            partner_data=partner_data,
            language=language,
            language_code=language_code,
            size=size,
            format_id=1, # SRT
        )

    def error_response(self, code, message):
        return self.kaltura_result(string.Template(
            '<error><code>$code</code>'
            '<message>$message</message></error>').substitute(
                code=code, message=message))

    def session_start_error_response(self):
        return self.error_response(
            'START_SESSION_ERROR',
            'Error while starting session for partner [%s]' % self.partner_id)

    def entry_not_found_response(self):
        return self.error_response(
            'ENTRY_ID_NOT_FOUND',
            'Entry id not found')

class KalturaSyncingTest(TestCase):
    def setUp(self):
        self.partner_id = 12345
        self.secret = 'SecretString'
        self.video_id = 'VideoId'

    def caption_asset_data(self, size=None):
        if size is None:
            size = len(self.subtitle_data)
        return {
            'format_id': 1, # SRT
            'size': size,
            'entry_id': self.caption_id,
            'video_id': self.video_id,
            'partner_id': self.partner_id,
        }

    def test_upload_first_time(self):
        mocker = KalturaApiMocker(self.partner_id, self.secret, self.video_id)
        mocker.expect_session_start()
        mocker.expect_captionasset_list(return_captions=[])
        mocker.expect_captionasset_add('captionid', 'English')
        mocker.expect_captionasset_setcontent('captionid', "CaptionData",
                                              "English")
        mocker.expect_session_end()
        with mocker:
            kaltura.update_subtitles(self.partner_id, self.secret,
                                     self.video_id, "en", "CaptionData")

    def test_upload_subsequent_times(self):
        mocker = KalturaApiMocker(self.partner_id, self.secret, self.video_id)
        mocker.expect_session_start()
        mocker.expect_captionasset_list(return_captions=[
            ('captionid', 'English', 100, kaltura.PARTNER_DATA_TAG),
        ])
        mocker.expect_captionasset_setcontent('captionid', "CaptionData",
                                              "English")
        mocker.expect_session_end()
        with mocker:
            kaltura.update_subtitles(self.partner_id, self.secret,
                                     self.video_id, 'en', "CaptionData")

    def test_upload_with_other_language(self):
        mocker = KalturaApiMocker(self.partner_id, self.secret, self.video_id)
        mocker.expect_session_start()
        mocker.expect_captionasset_list(return_captions=[
            ('captionid', 'French', 100, kaltura.PARTNER_DATA_TAG)
        ])
        mocker.expect_captionasset_add('captionid', 'English')
        mocker.expect_captionasset_setcontent('captionid', "CaptionData",
                                              "English")
        mocker.expect_session_end()
        with mocker:
            kaltura.update_subtitles(self.partner_id, self.secret,
                                     self.video_id, 'en', "CaptionData")

    def test_upload_with_other_subtitles(self):
        mocker = KalturaApiMocker(self.partner_id, self.secret, self.video_id)
        mocker.expect_session_start()
        mocker.expect_captionasset_list(return_captions=[
            ('captionid', 'English', 100, 'other-partner-data'),
        ])
        mocker.expect_captionasset_add('captionid', 'English')
        mocker.expect_captionasset_setcontent('captionid', "CaptionData",
                                              "English")
        mocker.expect_session_end()
        with mocker:
            kaltura.update_subtitles(self.partner_id, self.secret,
                                     self.video_id, 'en', "CaptionData")

    def test_delete(self):
        mocker = KalturaApiMocker(self.partner_id, self.secret, self.video_id)
        mocker.expect_session_start()
        mocker.expect_captionasset_list(return_captions=[
            ('captionid', 'English', 100, kaltura.PARTNER_DATA_TAG),
            ('captionid2', 'French', 100, kaltura.PARTNER_DATA_TAG),
        ])
        mocker.expect_captionasset_delete('captionid')
        mocker.expect_session_end()
        with mocker:
            kaltura.delete_subtitles(self.partner_id, self.secret,
                                     self.video_id, 'en')

    def test_auth_error(self):
        mocker = KalturaApiMocker(self.partner_id, self.secret, self.video_id)
        mocker.expect_session_start(return_error=True)
        with mocker:
            self.assertRaises(SyncingError, kaltura.update_subtitles,
                              self.partner_id, self.secret, self.video_id,
                              'en', "CaptionData")

    def test_video_not_found(self):
        mocker = KalturaApiMocker(self.partner_id, self.secret, self.video_id)
        mocker.expect_session_start()
        mocker.expect_captionasset_list(return_captions=[])
        mocker.expect_captionasset_add_return_error('English')
        mocker.expect_session_end()
        with mocker:
            self.assertRaises(SyncingError, kaltura.update_subtitles,
                              self.partner_id, self.secret, self.video_id,
                              'en', "CaptionData")

    def test_invalid_kaltura_language(self):
        # test what happens when we try to sync a language that doesn't map to
        # a kaltura language, like pt-br
        mocker = KalturaApiMocker(self.partner_id, self.secret, self.video_id)
        mocker.expect_session_start()
        mocker.expect_session_end()
        with mocker:
            self.assertRaises(SyncingError, kaltura.update_subtitles,
                              self.partner_id, self.secret, self.video_id,
                              'pt-br', "CaptionData")

class BrightcoveAccountSyncingTest(TestCase):
    # Test that the BrightcoveAccount model makes the correct calls in
    # response to update_subtitles() and delete_subtitles()

    def setUp(self):
        self.account = BrightcoveAccountFactory(team=TeamFactory())
        self.video_id = '1234'
        self.video = BrightcoveVideoFactory(brightcove_id=self.video_id,
                                            primary_audio_language_code='en')
        TeamVideoFactory(video=self.video, team=self.account.team)
        self.video_url = self.video.get_primary_videourl_obj()

    def add_subtitles(self, language_code):
        pipeline.add_subtitles(self.video, language_code, [
            (100, 200, 'content'),
        ])
        self.video.clear_language_cache()
        self.account.update_subtitles(
            self.video_url, self.video.subtitle_language(language_code))

    def delete_subtitles(self, language_code):
        language = self.video.subtitle_language(language_code)
        language.nuke_language()
        self.video.clear_language_cache()
        self.account.delete_subtitles(self.video_url, language)

    @test_utils.patch_for_test('externalsites.syncing.brightcove.update_subtitles')
    @test_utils.patch_for_test('externalsites.syncing.brightcove.delete_subtitles')
    def test_brightcove_account_syncing(self, mock_delete_subtitles,
                                        mock_update_subtitles):
        # when we add subtitles, update_subtitles() should be called.
        self.add_subtitles('en')
        mock_update_subtitles.assert_called_with(self.account.write_token,
                                                 self.video_id, self.video)
        mock_update_subtitles.reset()
        self.add_subtitles('fr')
        mock_update_subtitles.assert_called_with(self.account.write_token,
                                                 self.video_id, self.video)
        mock_update_subtitles.reset()
        # when we delete subtitles, we should still call update_subtitles()
        # since we are updating the entire set of subtitles
        self.delete_subtitles('fr')
        mock_update_subtitles.assert_called_with(self.account.write_token,
                                                 self.video_id, self.video)
        mock_update_subtitles.reset()
        # until we delete the last language, then we should call
        # delete_subtitles()
        self.delete_subtitles('en')
        mock_delete_subtitles.assert_called_with(self.account.write_token,
                                                 self.video_id)

    @test_utils.patch_for_test('externalsites.syncing.brightcove.update_subtitles')
    @test_utils.patch_for_test('externalsites.syncing.brightcove.delete_subtitles')
    def test_no_write_token(self, mock_delete_subtitles,
                            mock_update_subtitles):
        # if we don't have a write token set, we should skip syncing
        self.account.write_token = ''
        self.account.save()
        self.add_subtitles('en')
        self.assertEquals(mock_update_subtitles.call_count, 0)
        # we shouldn't record sync history either in this case
        self.assertEquals(SyncHistory.objects.count(), 0)
        # the same should happen on delete
        self.delete_subtitles('en')
        self.assertEquals(mock_delete_subtitles.call_count, 0)
        self.assertEquals(SyncHistory.objects.count(), 0)

class BrightcoveAPITest(TestCase):
    WRITE_URL = 'https://api.brightcove.com/services/post'

    @test_utils.patch_for_test('externalsites.syncing.brightcove.requests')
    def setUp(self, mock_requests):
        self.mock_requests = mock_requests
        self.write_token = 'abc'
        self.video_id = '123'
        self.video = BrightcoveVideoFactory(brightcove_id=self.video_id,
                                            primary_audio_language_code='en')
        pipeline.add_subtitles(self.video, 'en', [
            (100, 200, 'content'),
        ])
        pipeline.add_subtitles(self.video, 'fr', [
            (100, 200, 'fr content'),
        ])

    def test_upload_subtitles(self):
        self.setup_add_captions_success_response()
        brightcove.update_subtitles(self.write_token, self.video_id,
                                    self.video)

        data = {
            'method': 'add_captioning',
            'params': {
                'token': self.write_token,
                'video_id': self.video_id,
                'caption_source': {
                    'displayName': 'Amara Captions',
                }
            }
        }
        self.mock_requests.post.assert_called_with(
            self.WRITE_URL,
            data={ 'JSONRPC': json.dumps(data) },
            files={ 'file': self.video.get_merged_dfxp() }
        )

    def test_delete_subtitles(self):
        self.setup_delete_captions_success_response()
        brightcove.delete_subtitles(self.write_token, self.video_id)

        data = {
            'method': 'delete_captioning',
            'params': {
                'token': self.write_token,
                'video_id': self.video_id,
            }
        }

        self.mock_requests.post.assert_called_with(
            self.WRITE_URL,
            data={ 'json': json.dumps(data) })

    def test_update_subtitles_invalid_write_token(self):
        self.setup_invalid_token_response()
        self.assertRaises(SyncingError, brightcove.update_subtitles,
                          self.write_token, self.video_id, self.video)

    def test_update_subtitles_invalid_video_id(self):
        self.setup_invalid_video_id_response()
        self.assertRaises(SyncingError, brightcove.update_subtitles,
                          self.write_token, self.video_id, self.video)

    def test_delete_subtitles_invalid_write_token(self):
        self.setup_invalid_token_response()
        self.assertRaises(SyncingError, brightcove.delete_subtitles,
                          self.write_token, self.video_id)

    def test_delete_subtitles_invalid_video_id(self):
        self.setup_invalid_video_id_response()
        self.assertRaises(SyncingError, brightcove.delete_subtitles,
                          self.write_token, self.video_id)

    def setup_add_captions_success_response(self):
        self.mock_requests.post.return_value.json ={
            'id': None,
            'error': None,
            'result': {
                'captionSources': [
                    {'url': None,
                     'isRemote': False,
                     'displayName': 'Amara Captions',
                     'complete': False,
                     'id': 3569221155001,
                    }
                ],
                'id': self.video_id,
            },
        }

    def setup_delete_captions_success_response(self):
        self.mock_requests.post.return_value.json = {
            'id': None,
            'result': {},
            'error': None,
        }

    def setup_invalid_token_response(self):
        self.mock_requests.post.return_value.json = {
            'id': None,
            'result': None,
            'error': {
                'message': 'invalid token',
                'code': 210,
                'name': 'InvalidTokenError',
            }
        }

    def setup_invalid_video_id_response(self):
        self.mock_requests.post.return_value.json = {
            'id': None,
            'result': None,
            'error': {
                'message': 'Cannot find the specified video.',
                'code': 304,
                'name': 'IllegalValueError',
            }
        }
