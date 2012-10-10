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

from teams.moderation_const import APPROVED, UNMODERATED, WAITING_MODERATION
from accountlinker.models import (
    ThirdPartyAccount, YoutubeSyncRule, check_authorization, can_be_synced
)
from videos.models import Video, VideoUrl, SubtitleVersion
from teams.models import Team, TeamVideo
from auth.models import CustomUser as User


class AccountTest(TestCase):
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]

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
        vurl = VideoUrl.objects.filter(type='Y')[1]
        version = vurl.video.subtitle_language('en').latest_version()
        self.assertFalse(version.language.is_complete)
        self.assertFalse(can_be_synced(version))

        version.language.is_complete = True
        version.language.save()

        self.assertTrue(version.is_public)
        self.assertTrue(version.is_synced())
        self.assertEquals(version.moderation_status, UNMODERATED)

        self.assertTrue(can_be_synced(version))

        vurl = VideoUrl.objects.filter(type='Y')[0]
        version = vurl.video.subtitle_language('en').latest_version()

        language = version.language
        language.is_complete = True
        language.save()

        self.assertTrue(version.language.is_complete)
        self.assertEquals(version.moderation_status, UNMODERATED)
        self.assertTrue(version.is_public)
        self.assertFalse(version.is_synced())

        self.assertFalse(can_be_synced(version))

    def test_not_approved(self):
        vurl = VideoUrl.objects.filter(type='Y')[1]
        version = vurl.video.subtitle_language('en').latest_version()

        version.language.is_complete = True
        version.language.save()

        self.assertTrue(version.is_public)
        self.assertTrue(version.is_synced())
        self.assertEquals(version.moderation_status, UNMODERATED)

        version.moderation_status = WAITING_MODERATION
        version.save()
        self.assertFalse(can_be_synced(version))

        version.moderation_status = APPROVED
        version.save()
        self.assertTrue(can_be_synced(version))
