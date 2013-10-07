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

from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from accountlinker.models import (
    ThirdPartyAccount, YoutubeSyncRule, check_authorization, can_be_synced,
    add_amara_description_credit
)
from videos.models import Video, VideoUrl, SubtitleLanguage
from videos.types import UPDATE_VERSION_ACTION
from videos.types import video_type_registrar
from videos.types.youtube import YoutubeVideoType
from teams.models import Team, TeamVideo
from auth.models import CustomUser as User
from tasks import get_youtube_data
from subtitles.pipeline import add_subtitles
from apps.testhelpers import views as helpers
from utils import test_factories

import mock

class AccountTest(TestCase):
    def setUp(self):
        self.video, _ = Video.get_or_create_for_url(
            'http://www.youtube.com/watch?v=q26umaF242I')
        self.video.primary_audio_language_code = 'en'
        self.video.save()
        self.vurl = self.video.get_primary_videourl_obj()
        add_subtitles(self.video, 'en', [
            (0, 1000, 'Hello', {}),
            (2000, 5000, 'word', {})
        ])

    def test_retrieval(self):
        tpa = test_factories.create_third_party_account(self.vurl)
        tpa.users.add(test_factories.create_user())

        with self.assertRaises(ImproperlyConfigured):
            ThirdPartyAccount.objects.always_push_account()

        setattr(settings, 'YOUTUBE_ALWAYS_PUSH_USERNAME', tpa.username)
        self.assertEquals(ThirdPartyAccount.objects.always_push_account(),
                          tpa)

    def test_rules(self):
        team_video = test_factories.create_team_video()
        video = team_video.video
        username = video.user.username

        def check_sync_rule(should_sync, **rule_kwargs):
            YoutubeSyncRule.objects.all().delete()
            rule = YoutubeSyncRule.objects.create(**rule_kwargs)
            self.assertEquals(rule.should_sync(video), should_sync)

        check_sync_rule(False) # blank rule
        check_sync_rule(True, team=team_video.team.slug)
        check_sync_rule(True, user=username)
        check_sync_rule(True, video=video.video_id)
        check_sync_rule(True, team='*')
        # Videos can have the user field set to None
        video.user = None
        video.save()
        check_sync_rule(False, user=username)

    def test_check_authorization_no_account(self):
        # test check_authorization with no ThirdPartyAccount set up
        self.assertEquals(check_authorization(self.video), (False, False))

    def test_check_authorization_not_linked(self):
        # test check_authorization when not linked to a user or team
        test_factories.create_third_party_account(self.vurl)
        self.assertEquals(check_authorization(self.video), (False, False))

    def test_check_authorization_individual(self):
        # test check_authorization when linked to a user
        tpa = test_factories.create_third_party_account(self.vurl)
        tpa.users.add(test_factories.create_user())
        # FIXME: should this return True if the user for the ThirdPartyAccount
        # doesn't match the user of the video?
        self.assertEquals(check_authorization(self.video), (True, True))

    def test_check_authorization_team(self):
        # test check_authorization when linked to a team
        team = test_factories.create_team()
        tpa = test_factories.create_third_party_account(self.vurl)
        tpa.teams.add(team)

        self.assertEquals(check_authorization(self.video), (False, False))
        test_factories.create_team_video(team, video=self.video)
        self.video.clear_team_video_cache()
        self.assertEquals(check_authorization(self.video), (True, True))

    def make_language_complete(self):
        language = self.video.subtitle_language()
        language.subtitles_complete = True
        language.save()

    def test_can_be_synced(self):
        lang = self.video.subtitle_language()
        self.assertFalse(can_be_synced(lang.get_tip()))
        self.make_language_complete()
        self.assertTrue(can_be_synced(lang.get_tip()))

    def test_mirror_existing(self):
        user = test_factories.create_user()
        tpa1 = ThirdPartyAccount.objects.create(username='a1')
        tpa2 = ThirdPartyAccount.objects.create(username='a2')
        self.vurl.owner_username = 'a1'
        self.vurl.save()
        self.make_language_complete()
        user.third_party_accounts.add(tpa1)
        user.third_party_accounts.add(tpa2)

        data = get_youtube_data(user.pk)
        self.assertEquals(1, len(data))

        video, language, version = data[0]
        self.assertTrue(version.is_public)
        self.assertTrue(version.is_synced())
        self.assertTrue(language.subtitles_complete)
        self.assertTrue(video.get_team_video() is None)

        self.assertTrue(can_be_synced(version))

    def test_resolve_ownership(self):
        tpa = test_factories.create_third_party_account(self.vurl)

        # test with a video that should be linked to an account
        owner = ThirdPartyAccount.objects.resolve_ownership(self.vurl)
        self.assertEquals(owner, tpa)

        # test with a video that shouldn't be linked to an account
        video, _ = Video.get_or_create_for_url(
            'http://www.youtube.com/watch?v=pQ9qX8lcaBQ')
        video_url = video.get_primary_videourl_obj()
        owner = ThirdPartyAccount.objects.resolve_ownership(video_url)
        self.assertEquals(owner, None)

    def test_resolve_ownership_with_bad_username(self):
        # for some reason, some of our VideoURL objects have the full name in
        # onwer_username instead of the username.  In that case, we should
        # re-fetch the video type, use that username, and update the
        # owner_username field

        # create 2 accounts with the same full name
        account = test_factories.create_third_party_account(
            self.vurl, full_name='Amara Test')
        other_account = ThirdPartyAccount.objects.create(
            type=self.vurl.type, username='other_user', 
            full_name='Amara Test', oauth_access_token='123',
            oauth_refresh_token='')
        # force the vurl to have the full name in owner_username
        self.vurl.owner_username = 'Amara Test'
        self.vurl.save()
        # try calling resolve_ownership.
        self.assertEquals(
            ThirdPartyAccount.objects.resolve_ownership(self.vurl), account)
        # resolve_ownership should also fix the owner_username
        self.assertEquals(self.vurl.owner_username, 'amaratestuser')

    def test_mirror_on_third_party(self):
        tpa = test_factories.create_third_party_account(self.vurl)
        tpa.users.add(test_factories.create_user())
        self.make_language_complete()
        lang = self.video.subtitle_language()

        version = self.video.subtitle_language().get_tip()

        youtube_type_mock = mock.Mock(spec=YoutubeVideoType)
        spec = 'videos.types.video_type_registrar.video_type_for_url'
        with mock.patch(spec) as video_type_for_url_mock:
            video_type_for_url_mock.return_value = youtube_type_mock
            ThirdPartyAccount.objects.mirror_on_third_party(
                self.video, 'en', UPDATE_VERSION_ACTION, version)

        youtube_type_mock.update_subtitles.assert_called_once_with(version,
                                                                   tpa)

    def test_credit(self):
        old = 'abc'
        url = 'http://test.com'
        new = add_amara_description_credit(old, url)

        self.assertTrue(new.startswith('abc'))
        self.assertTrue(new.endswith(url))

        new = add_amara_description_credit(old, url, prepend=True)
        self.assertTrue(new.startswith('Help us caption & translate'))
        self.assertTrue(new.endswith('abc'))

        new = add_amara_description_credit(new, url)
        self.assertTrue(new.startswith('Help us caption & translate'))
        self.assertFalse(new.endswith('Help us caption & translate'))
        self.assertEquals(1, new.count('Help us caption & translate'))

        # And empty description
        old = ''
        new = add_amara_description_credit(old, url)

        self.assertFalse(new == '')
