# -*- coding: utf-8 -*-
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
import mock

from videos.forms import AddFromFeedForm, VideoForm
from videos.models import Video, VideoFeed
from videos.types import video_type_registrar
from utils import test_factories, test_utils

class TestVideoForm(TestCase):
    def setUp(self):
        self.vimeo_urls = ("http://vimeo.com/17853047",)
        self.youtube_urls = ("http://youtu.be/HaAVZ2yXDBo",
                             "http://www.youtube.com/watch?v=HaAVZ2yXDBo")
        self.html5_urls = ("http://blip.tv/file/get/Miropcf-AboutUniversalSubtitles715.mp4",)
        self.daily_motion_urls = ("http://www.dailymotion.com/video/xb0hsu_qu-est-ce-que-l-apache-software-fou_tech",)

    def _test_urls(self, urls):
        for url in urls:
            form = VideoForm(data={"video_url":url})
            self.assertTrue(form.is_valid())
            video = form.save()
            video_type = video_type_registrar.video_type_for_url(url)
            # double check we never confuse video_id with video.id with videoid, sigh
            model_url = video.get_video_url()
            if hasattr(video_type, "videoid"):
                self.assertTrue(video_type.videoid  in model_url)
            # check the pk is never on any of the urls parts
            for part in model_url.split("/"):
                self.assertTrue(str(video.pk)  != part)
            self.assertTrue(video.video_id  not in model_url)

            self.assertTrue(Video.objects.filter(videourl__url=model_url).exists())

    def test_youtube_urls(self):
        self._test_urls(self.youtube_urls)

    def test_vimeo_urls(self):
        self._test_urls(self.vimeo_urls)

    def test_html5_urls(self):
        self._test_urls(self.html5_urls)

    def test_dailymotion_urls(self):
        self._test_urls(self.daily_motion_urls)


class AddFromFeedFormTestCase(TestCase):
    @test_utils.patch_for_test('videos.forms.FeedParser')
    def setUp(self, MockFeedParserClass):
        TestCase.setUp(self)
        self.user = test_factories.create_user()
        mock_feed_parser = mock.Mock()
        mock_feed_parser.version = 1.0
        MockFeedParserClass.return_value = mock_feed_parser

    def make_form(self, **data):
        return AddFromFeedForm(self.user, data=data)

    def make_feed(self, url):
        return VideoFeed.objects.create(user=self.user, url=url)

    def youtube_url(self, username):
        return 'https://gdata.youtube.com/feeds/api/users/%s/uploads' % (
            username,)

    def youtube_user_url(self, username):
        return 'http://www.youtube.com/user/%s' % (username,)

    def check_feed_urls(self, *feed_urls):
        self.assertEquals(set(f.url for f in VideoFeed.objects.all()),
                          set(feed_urls))

    def test_success(self):
        form = self.make_form(
            feed_url='http://example.com/feed.rss',
            usernames='testuser, testuser2',
            youtube_user_url=self.youtube_user_url('testuser3'))
        self.assertEquals(form.errors, {})
        form.save()
        self.check_feed_urls(
            'http://example.com/feed.rss',
            self.youtube_url('testuser'),
            self.youtube_url('testuser2'),
            self.youtube_url('testuser3'),
        )

    def test_duplicate_feeds(self):
        # test trying to add feed that already exists
        url = 'http://example.com/feed.rss'
        self.make_feed(url)
        form = self.make_form(feed_url=url)
        self.assertNotEquals(form.errors, {})

    def test_duplicate_feeds_with_youtube_users(self):
        # test trying to add a youtube user when the feed for that user
        # already exists
        self.make_feed(self.youtube_url('testuser'))
        form = self.make_form(usernames='testuser')
        self.assertNotEquals(form.errors, {})

    def test_duplicate_feeds_with_youtube_urls(self):
        # test trying to add a youtube url when the feed for that user already
        # exists
        self.make_feed(self.youtube_url('testuser'))
        form = self.make_form(
            youtube_user_url=self.youtube_user_url('testuser'))
        self.assertNotEquals(form.errors, {})

    def test_duplicate_feeds_in_form(self):
        # test having duplicate feeds in 1 form, for example when the feed url
        # is the same as the URL for a youtube user.
        form = self.make_form(
            feed_url=self.youtube_url('testuser'),
            youtube_user_url=self.youtube_user_url('testuser'))
        self.assertNotEquals(form.errors, {})

        form = self.make_form(
            usernames='testuser',
            youtube_user_url=self.youtube_user_url('testuser'))
        self.assertNotEquals(form.errors, {})

        form = self.make_form(
            feed_url=self.youtube_url('testuser'),
            usernames='testuser')
        self.assertNotEquals(form.errors, {})
