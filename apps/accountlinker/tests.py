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
    ThirdPartyAccount, YoutubeSyncRule, check_authorization, can_be_synced
)
from videos.models import Video, VideoUrl, SubtitleLanguage
from teams.models import Team, TeamVideo
from auth.models import CustomUser as User
from tasks import get_youtube_data
from subtitles.pipeline import add_subtitles


class AccountTest(TestCase):
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]

    def setUp(self):
        self.vurl = VideoUrl.objects.filter(type='Y')[1]
        subs = [
            (0, 1000, 'Hello', {}),
            (2000, 5000, 'word', {})
        ]
        add_subtitles(self.vurl.video, 'en', subs)

    def test_retrieval(self):

        acc = ThirdPartyAccount.objects.create(type='Y', username='abc',
                oauth_access_token='a', oauth_refresh_token='b')

        with self.assertRaises(ImproperlyConfigured):
            ThirdPartyAccount.objects.always_push_account()

        setattr(settings, 'YOUTUBE_ALWAYS_PUSH_USERNAME', 'abc')
        self.assertEquals(ThirdPartyAccount.objects.always_push_account().pk,
                acc.pk)

    def test_rules(self):
        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = User.objects.get(username='admin')
        team = video.get_team_video().team
        team = team.slug

        r = YoutubeSyncRule.objects.create()
        self.assertFalse(r.should_sync(video))

        YoutubeSyncRule.objects.all().delete()
        r = YoutubeSyncRule.objects.create(team=team)
        self.assertTrue(r.should_sync(video))

        YoutubeSyncRule.objects.all().delete()
        r = YoutubeSyncRule.objects.create(user='admin')
        self.assertTrue(r.should_sync(video))

        YoutubeSyncRule.objects.all().delete()
        r = YoutubeSyncRule.objects.create(video=video.video_id)
        self.assertTrue(r.should_sync(video))

        YoutubeSyncRule.objects.all().delete()
        r = YoutubeSyncRule.objects.create(team='*')
        self.assertTrue(r.should_sync(video))

        # Videos can have the user field set to None
        video.user = None
        video.save()

        YoutubeSyncRule.objects.all().delete()
        r = YoutubeSyncRule.objects.create(user='admin')
        self.assertFalse(r.should_sync(video))

    def test_not_part_of_team(self):
        vurl = VideoUrl.objects.filter(type='Y',
                video__teamvideo__isnull=True)[0]
        vurl.owner_username = 'test'
        vurl.save()
        video = vurl.video
        third = ThirdPartyAccount.objects.all().exists()
        self.assertFalse(third)

        is_authorized, ignore = check_authorization(video)
        self.assertTrue(is_authorized)
        self.assertFalse(ignore)

        ThirdPartyAccount.objects.create(type='Y',
                username=vurl.owner_username)

        is_authorized, ignore = check_authorization(video)
        self.assertFalse(is_authorized)
        self.assertEquals(None, ignore)

    def test_part_of_team(self):
        # Prep stuff
        vurl = VideoUrl.objects.filter(type='Y')[0]
        vurl.owner_username = 'test'
        vurl.save()

        video = vurl.video
        user = User.objects.get(username='admin')

        team = Team.objects.all()[0]
        TeamVideo.objects.create(video=video, team=team, added_by=user)

        third = ThirdPartyAccount.objects.all().exists()
        self.assertFalse(third)

        # Start testing
        is_authorized, ignore = check_authorization(video)
        self.assertFalse(is_authorized)
        self.assertEquals(None, ignore)

        account = ThirdPartyAccount.objects.create(type='Y',
                username=vurl.owner_username)
        team.third_party_accounts.add(account)

        is_authorized, ignore = check_authorization(video)
        self.assertTrue(is_authorized)
        self.assertTrue(ignore)

    def test_not_complete(self):
        version = self.vurl.video.subtitle_language().get_tip()
        self.assertFalse(version.subtitle_language.subtitles_complete)
        self.assertFalse(can_be_synced(version))

        version.subtitle_language.subtitles_complete = True
        version.subtitle_language.save()

        self.assertTrue(version.is_public)
        self.assertTrue(version.is_synced())

        self.assertTrue(can_be_synced(version))

    def test_mirror_existing(self):
        user = User.objects.get(username='admin')

        tpa1 = ThirdPartyAccount.objects.create(username='a1')
        tpa2 = ThirdPartyAccount.objects.create(username='a2')

        user.third_party_accounts.add(tpa1)
        user.third_party_accounts.add(tpa2)

        for url in VideoUrl.objects.all():
            url.owner_username = 'a1'
            url.type = 'Y'
            url.save()

        for sl in SubtitleLanguage.objects.all():
            sl.is_complete = True
            sl.save()

        data = get_youtube_data(user.pk)
        self.assertEquals(1, len(data))

        synced_sl = filter(lambda x: x.is_complete_and_synced(),
                SubtitleLanguage.objects.all())
        self.assertEquals(len(synced_sl), len(data))

        video, language, version = data[0]
        self.assertTrue(version.is_public)
        self.assertTrue(version.is_synced())
        self.assertTrue(language.is_complete)
        self.assertTrue(video.get_team_video() is None)

        self.assertTrue(can_be_synced(version))

    def test_individual(self):
        vurl = VideoUrl.objects.filter(type='Y',
                video__teamvideo__isnull=True)[0]
        vurl.owner_username = 'test'
        vurl.save()
        video = vurl.video
        third = ThirdPartyAccount.objects.all().exists()
        self.assertFalse(third)

        is_authorized, ignore = check_authorization(video)
        self.assertTrue(is_authorized)
        self.assertFalse(ignore)

        account = ThirdPartyAccount.objects.create(type='Y',
                username=vurl.owner_username)

        team = Team.objects.get(slug='volunteer')

        is_authorized, ignore = check_authorization(video)
        self.assertTrue(is_authorized)

        team.third_party_accounts.add(account)

        is_authorized, ignore = check_authorization(video)
        self.assertFalse(is_authorized)

        user = User.objects.get(username='admin')
        team.third_party_accounts.clear()
        user.third_party_accounts.add(account)

        is_authorized, ignore = check_authorization(video)
        self.assertTrue(is_authorized)
