#!/usr/bin/python
# Copyright 2014 Participatory Culture Foundation, All Rights Reserved
# -*- coding: utf-8 -*-

import os
import unittest
import json
import itertools
import time
from rest_framework.test import APILiveServerTestCase, APIClient

from videos.models import *
from utils.factories import *
from subtitles import pipeline
from webdriver_testing.webdriver_base import WebdriverTestCase

class TestCaseVideos(APILiveServerTestCase, WebdriverTestCase):
    """TestSuite for site video searches.  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseVideos, cls).setUpClass()
        cls.user = UserFactory()
        cls.client = APIClient
        for x in range(5):
            VideoFactory()

    def _get (self, url='/api/videos/'):
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        response.render()
        r = (json.loads(response.content))
        return r

    def _post(self, url='/api/videos/', data=None):
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)
        response.render()
        r = (json.loads(response.content))
        return r

    def test_not_logged_in(self):
        """non-authed users can't access"""
        expected_error = {u'detail':
                          u'Authentication credentials were not provided.'}
        response = self.client.get('/api/videos/')
        self.assertEqual(expected_error, response.data)

    def test_get_videos(self):
        """get all videos"""
        r = self._get()
        self.assertEqual(5, r['meta']['total_count'])

    def test_query_url(self):
        """get video with url lookup"""
        r = self._get()
        video_url = r['objects'][0]['all_urls'][0]
        url = '/api/videos/?video_url='+ video_url
        r = self._get(url)
        self.assertEqual(1, r['meta']['total_count'])


    def test_get_video(self):
        """Get request pulls all languages"""
        video = VideoFactory(primary_audio_language_code = 'en')
        subtitle_langs = ['en', 'pt-br', 'en-gb']
        for lc in subtitle_langs:
            pipeline.add_subtitles(video, lc, SubtitleSetFactory(), 
                                   committer=self.user,
                                   author=self.user, action='publish')
        url = '/api/videos/%s/' % video.video_id
        r = self._get(url)
        languages = [l['code'] for l in r['languages']]
        self.assertEqual(sorted(subtitle_langs), sorted(languages))

    def test_sort(self):
        """Results are sorted as requested"""
        url = '/api/videos/'
        r = self._get(url)
        video_urls = [v['all_urls'][0] for v in r['objects']]
        # order by title
        url = '/api/videos/?order_by=-title'
        r = self._get(url)
        sorted_data = [v['all_urls'][0] for v in r['objects']]
        self.assertEqual(video_urls[::-1], sorted_data)

        # order by created, newest first
        url = '/api/videos/?order_by=-created'
        r = self._get(url)
        sorted_data = [v['all_urls'][0] for v in r['objects']]
        self.assertEqual(video_urls[::-1], sorted_data)

    def test_post(self):
        """post a new video with all metadata for public video""" 
        data = {
                "video_url": "http://unisubs.example.com:8000/video.mp4", 
                "primary_audio_language_code": "en", 
                "title": "This is a test", 
                "description": "The description of the test video", 
                "duration": 320, 
                "thumbnail": "https://i.ytimg.com/vi/BXMPp0TLSEo/hqdefault.jpg", 
                }
        r = self._post(data=data)

        #Check response content
        self.assertEqual(data['primary_audio_language_code'], r['primary_audio_language_code'])
        self.assertEqual(data['title'], r['title'])
        self.assertEqual(data['description'], r['description'])
        self.assertEqual(data['duration'], r['duration'])
        self.assertEqual(data['thumbnail'], r['thumbnail'])
        self.assertEqual(data['video_url'], r['all_urls'][0])
        self.assertEqual(None, r['project'])
        self.assertEqual(None, r['team'])
        self.assertEqual('en', r['original_language'])
        self.assertEqual({}, r['metadata'])

        #Check database content 
        video, created = Video.get_or_create_for_url(data['video_url'])
        self.assertFalse(created) 
        self.assertEqual(data['primary_audio_language_code'], video.primary_audio_language_code)
        self.assertEqual(data['title'], video.title)
        self.assertEqual(data['description'], video.description)
        self.assertEqual(data['duration'], video.duration)

