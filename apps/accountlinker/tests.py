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

from accountlinker.models import ThirdPartyAccount, YoutubeSyncRule
from videos.models import Video
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
