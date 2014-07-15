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

from django.test import TestCase

from externalsites.exceptions import YouTubeAccountExistsError
from externalsites.models import (BrightcoveAccount, YouTubeAccount,
                                  lookup_accounts, account_models)
from videos.models import VideoFeed
from utils import test_utils
from utils.factories import *

class LookupAccountTest(TestCase):
    def check_lookup_accounts(self, video, account):
        self.assertEquals(lookup_accounts(video), [
            (account, video.get_primary_videourl_obj())
        ])

    def check_lookup_accounts_returns_nothing(self, video):
        self.assertEquals(lookup_accounts(video), [])

    def check_is_for_video_url(self, account, video, correct_value):
        video_url = video.get_primary_videourl_obj()
        self.assertEquals(account.is_for_video_url(video_url), correct_value)

    def test_team_account(self):
        video = BrightcoveVideoFactory()
        team_video = TeamVideoFactory(video=video)
        account = BrightcoveAccountFactory(team=team_video.team)
        self.check_lookup_accounts(video, account)

    def test_user_account(self):
        user = UserFactory()
        video = BrightcoveVideoFactory(user=user)
        account = BrightcoveAccountFactory(user=user)
        self.check_lookup_accounts(video, account)

    def test_user_account_ignored_for_team_videos(self):
        user = UserFactory()
        video = BrightcoveVideoFactory(user=user)
        account = BrightcoveAccountFactory(user=user)
        team_video = TeamVideoFactory(video=video)

        self.check_lookup_accounts_returns_nothing(video)

    def test_youtube(self):
        team = TeamFactory()
        account1 = YouTubeAccountFactory(channel_id='user1', team=team)
        account2 = YouTubeAccountFactory(channel_id='user2', team=team)
        video1 = YouTubeVideoFactory(video_url__owner_username='user1')
        video2 = YouTubeVideoFactory(video_url__owner_username='user2')
        # video for a user that we don't have an account for
        video3 = YouTubeVideoFactory(video_url__owner_username='user3')
        # video without a username set
        video4 = YouTubeVideoFactory(video_url__owner_username='')
        for video in (video1, video2, video3):
            TeamVideoFactory(video=video, team=team)

        self.check_lookup_accounts(video1, account1)
        self.check_lookup_accounts(video2, account2)
        self.check_lookup_accounts_returns_nothing(video3)
        self.check_lookup_accounts_returns_nothing(video4)
        # test ExternalAccount.is_for_video_url() which works in the reverse
        # direction
        self.check_is_for_video_url(account1, video1, True)
        self.check_is_for_video_url(account1, video2, False)
        self.check_is_for_video_url(account1, video3, False)
        self.check_is_for_video_url(account1, video4, False)

class BrightcoveAccountTest(TestCase):
    def setUp(self):
        self.team = TeamFactory()
        self.account = BrightcoveAccountFactory.create(team=self.team,
                                                       publisher_id='123')
        self.player_id = '456'

    def check_feed(self, feed_url):
        self.assertEquals(self.account.import_feed.url, feed_url)
        self.assertEquals(self.account.import_feed.user, None)
        self.assertEquals(self.account.import_feed.team, self.team)

    def test_make_feed(self):
        self.assertEquals(self.account.import_feed, None)
        self.account.make_feed(self.player_id)
        self.check_feed(
            'http://link.brightcove.com/services/mrss/player456/123/new')
        self.account.make_feed(self.player_id, ['cats', 'dogs'])
        self.check_feed(
            'http://link.brightcove.com/services/mrss/player456/123/tags/cats/dogs')
        # test with chars that need to be quoted
        self.account.make_feed(self.player_id, ['~cats and dogs'])
        self.check_feed(
            'http://link.brightcove.com/services/mrss/player456/123/tags/%7Ecats+and+dogs')

    def test_make_feed_again(self):
        # test calling make feed twice.  We should use the same VideoFeed
        # object and change its URL.
        self.assertEquals(self.account.import_feed, None)
        self.account.make_feed(self.player_id)
        first_import_feed_id = self.account.import_feed.id
        self.account.make_feed(self.player_id, ['cats'])
        self.assertEquals(self.account.import_feed.id, first_import_feed_id)

    def test_remove_feed(self):
        self.account.make_feed(self.player_id)
        self.account.remove_feed()
        self.assertEquals(self.account.import_feed, None)

    def test_feed_info(self):
        self.assertEquals(self.account.feed_info(), None)

        self.account.make_feed(self.player_id)
        self.assertEquals(self.account.feed_info(), (self.player_id, None))

        self.account.make_feed(self.player_id, ['cats', 'dogs'])
        self.assertEquals(self.account.feed_info(),
                          (self.player_id, ('cats', 'dogs')))

    def test_feed_removed_externally(self):
        # test what happens if the feed is deleted not through
        # BrightcoveAccount.remove_feed()
        self.account.make_feed(self.player_id)
        self.account.import_feed.delete()

        account = BrightcoveAccount.objects.get(id=self.account.id)
        self.assertEquals(account.import_feed, None)

class YoutubeAccountTest(TestCase):
    def test_revoke_token_on_delete(self):
        account = YouTubeAccountFactory(user=UserFactory())
        account.delete()
        self.assertEquals(test_utils.youtube_revoke_auth_token.call_count, 1)
        test_utils.youtube_revoke_auth_token.assert_called_with(
            account.oauth_refresh_token)

    def test_create_feed(self):
        account = YouTubeAccountFactory(user=UserFactory(),
                                        channel_id='test-channel-id')
        self.assertEqual(account.import_feed, None)
        account.create_feed()
        self.assertNotEqual(account.import_feed, None)
        self.assertEqual(account.import_feed.url,
                         'https://gdata.youtube.com/'
                         'feeds/api/users/test-channel-id/uploads')

    def test_delete_feed_on_account_delete(self):
        account = YouTubeAccountFactory(user=UserFactory(),
                                        channel_id='test-channel-id')
        account.create_feed()
        self.assertEqual(VideoFeed.objects.count(), 1)
        account.delete()
        self.assertEqual(VideoFeed.objects.count(), 0)

    def test_create_or_update(self):
        # if there are no other accounts for a channel_id, create_or_update()
        # should create the account and return it
        user = UserFactory()
        auth_info = {
            'username': 'YouTubeUser',
            'channel_id': 'test-channel-id',
            'oauth_refresh_token':
            'test-refresh-token',
        }
        self.assertEquals(YouTubeAccount.objects.all().count(), 0)
        YouTubeAccount.objects.create_or_update(user=user, **auth_info)
        self.assertEquals(YouTubeAccount.objects.all().count(), 1)

        # Now that there is an account, it should update the existing account
        # and throw a YouTubeAccountExistsError
        team = TeamFactory()
        auth_info['oauth_refresh_token'] = 'test-refresh-token2'
        self.assertRaises(YouTubeAccountExistsError,
                          YouTubeAccount.objects.create_or_update, team=team,
                          **auth_info)
        self.assertEquals(YouTubeAccount.objects.all().count(), 1)
        account = YouTubeAccount.objects.all().get()
        self.assertEquals(account.oauth_refresh_token, 'test-refresh-token2')
