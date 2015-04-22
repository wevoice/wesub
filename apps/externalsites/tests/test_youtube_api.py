# Amara, universalsubtitles.org
#
# Copyright (C) 2014 Participatory Culture Foundation
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

import json

from django.conf import settings
from django.test import TestCase
from nose.tools import *

from utils import test_utils
from utils.subtitles import load_subtitles
from externalsites import google

class YouTubeTestCase(TestCase):
    def test_get_user_info(self):
        mocker = test_utils.RequestsMocker()
        mocker.expect_request(
            'get', 'https://www.googleapis.com/youtube/v3/channels', params={
                'part': 'id,snippet',
                'mine': 'true',
            }, headers={
                'Authorization': 'Bearer test-access-token',
            }, body=json.dumps({
                'items': [
                    {
                        'id': 'test-channel-id',
                        'snippet': {
                            'title': 'test-username',
                        },
                    }
                ]
            })
        )
        google.get_youtube_user_info.run_original_for_test()
        with mocker:
            user_info = google.get_youtube_user_info('test-access-token')
        self.assertEqual(user_info, ('test-channel-id', 'test-username'))

    def test_get_video_info(self):
        mocker = test_utils.RequestsMocker()
        mocker.expect_request(
            'get', 'https://www.googleapis.com/youtube/v3/videos', params={
                'part': 'snippet,contentDetails',
                'id': 'test-video-id',
                'key': settings.YOUTUBE_API_KEY,
            }, body=json.dumps({
                'items': [
                    {
                        'snippet': {
                            'title': 'test-title',
                            'channelId': 'test-channel-id',
                            'description': 'test-description',
                            'thumbnails': {
                                'high': {
                                    'url': 'test-thumbnail-url',
                                }
                            }
                        },
                        'contentDetails': {
                            'duration': 'PT10M10S',
                        }
                    }
                ]
            })
        )
        google.get_video_info.run_original_for_test()
        with mocker:
            video_info = google.get_video_info('test-video-id')
        self.assertEqual(video_info.channel_id, 'test-channel-id')
        self.assertEqual(video_info.title, 'test-title')
        self.assertEqual(video_info.description, 'test-description')
        self.assertEqual(video_info.duration, 610)
        self.assertEqual(video_info.thumbnail_url, 'test-thumbnail-url')

    def test_get_video_invalid_body(self):
        mocker = test_utils.RequestsMocker()
        mocker.expect_request(
            'get', 'https://www.googleapis.com/youtube/v3/videos', params={
                'part': 'snippet,contentDetails',
                'id': 'test-video-id',
                'key': settings.YOUTUBE_API_KEY,
            }, body="Invalid body")
        google.get_video_info.run_original_for_test()
        with mocker:
            with assert_raises(google.APIError):
                google.get_video_info('test-video-id')

    def test_get_video_info_no_items(self):
        mocker = test_utils.RequestsMocker()
        mocker.expect_request(
            'get', 'https://www.googleapis.com/youtube/v3/videos', params={
                'part': 'snippet,contentDetails',
                'id': 'test-video-id',
                'key': settings.YOUTUBE_API_KEY,
            }, body=json.dumps({
                'items': [
                ]
            })
        )
        google.get_video_info.run_original_for_test()
        with mocker:
            with assert_raises(google.APIError):
                google.get_video_info('test-video-id')

    def test_update_video_description(self):
        mocker = test_utils.RequestsMocker()
        mocker.expect_request(
            'get', 'https://www.googleapis.com/youtube/v3/videos', params={
                'part': 'snippet',
                'id': 'test-video-id',
            }, headers={
                'Authorization': 'Bearer test-access-token',
            }, body=json.dumps({
                'items': [
                    {
                        'snippet': {
                            'title': 'test-title',
                            'channelId': 'test-channel-id',
                            'description': 'test-description',
                            'thumbnails': {
                                'high': {
                                    'url': 'test-thumbnail-url',
                                }
                            }
                        }
                    }
                ]
            })
        )
        mocker.expect_request(
            'put', 'https://www.googleapis.com/youtube/v3/videos', params={
                'part': 'snippet',
            }, headers={
                'Authorization': 'Bearer test-access-token',
                'content-type': 'application/json',
            }, data=json.dumps({
                'id': 'test-video-id',
                'snippet': {
                    'title': 'test-title',
                    'channelId': 'test-channel-id',
                    'description': 'test-updated-description',
                    'thumbnails': {
                        'high': {
                            'url': 'test-thumbnail-url',
                        }
                    }
                }
            })
        )
        google.update_video_description.run_original_for_test()
        with mocker:
            google.update_video_description('test-video-id',
                                                   'test-access-token',
                                                   'test-updated-description')

class TestTimeParsing(TestCase):
    def test_with_minutes(self):
        self.assertEqual(google._parse_8601_duration('PT10M10S'), 610)

    def test_without_minutes(self):
        self.assertEqual(google._parse_8601_duration('PT10S'), 10)

    def test_invalid(self):
        self.assertEqual(google._parse_8601_duration('foo'), None)
