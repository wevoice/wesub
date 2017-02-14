#!/usr/bin/python
# Copyright 2014 Participatory Culture Foundation, All Rights Reserved
# -*- coding: utf-8 -*-

import os
import unittest
import json
import itertools
import time
from rest_framework.test import APILiveServerTestCase, APIClient
from django.core import management
from caching.tests.utils import assert_invalidates_model_cache
from videos.models import *
from utils.factories import *
from subtitles import pipeline
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages import video_page


class TestCaseVideos(APILiveServerTestCase, WebdriverTestCase):
    """TestSuite for site video searches.  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseVideos, cls).setUpClass()
        management.call_command('flush', interactive=False)
        cls.video_pg = video_page.VideoPage(cls)
        cls.user = UserFactory()
        cls.client = APIClient(enforce_csrf_checks=True)
        for x in range(5):
            VideoFactory()

    def _get (self, url='/api/videos/'):
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        response.render()
        r = (json.loads(response.content))
        return r

    def _put(self, url='/api/videos/', data=None):
        self.client.force_authenticate(self.user)
        response = self.client.put(url, data)
        response.render()
        r = (json.loads(response.content))
        self.logger.info(r)
        return r

    def _post(self, url='/api/videos/', data=None):
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)
        response.render()
        r = (json.loads(response.content))
        return r

    def test_not_logged_in(self):
        """non-authed users get public video information"""
        response = self.client.get('/api/videos/')
        response.render()
        r = (json.loads(response.content))
        self.assertEqual(5, r['meta']['total_count'])

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
        video = VideoFactory(title="ZZZZ test video")
        """Results are sorted as requested"""
        # order by title
        url = '/api/videos/?order_by=-title'
        r = self._get(url)
        sorted_data = [v['title'] for v in r['objects']]
        self.assertEqual(sorted_data[0], video.title)

        url = '/api/videos/?order_by=title'
        r = self._get(url)
        sorted_data = [v['title'] for v in r['objects']]
        self.assertEqual(sorted_data[-1], video.title)

        url = '/api/videos/?order_by=-created'
        r = self._get(url)
        sorted_data = [v['title'] for v in r['objects']]
        self.assertEqual(sorted_data[0], video.title)

        url = '/api/videos/?order_by=created'
        r = self._get(url)
        sorted_data = [v['title'] for v in r['objects']]
        self.assertEqual(sorted_data[-1], video.title)

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
        video = Video.get(videourl__url=data['video_url'])
        self.assertEqual(data['primary_audio_language_code'], video.primary_audio_language_code)
        self.assertEqual(data['title'], video.title)
        self.assertEqual(data['description'], video.description)
        self.assertEqual(data['duration'], video.duration)

    def test_update_metadata(self):
        video = VideoFactory()
        data = {
                "title": "updated video title",
               }
        
        url = "/api/videos/%s/" % video.video_id
        self._put(url=url, data=data)
        self.video_pg.open_video_page(video.video_id)
        #Check video title displays on the site
        self.assertEqual(data['title'],
            self.video_pg.video_title())


    def test_get_urls(self):
        """Verify video urls for a particular video are listed.

        GET /api/videos/[video-id]/urls/
        """
        video = VideoFactory()
        url = '/api/videos/%s/urls/' % video.video_id
        r = self._get(url)
        urls = [x['url'] for x in r]
        self.assertIn(video.get_video_url(), urls)

    def test_url_post(self):
        """Add an additional new url.  """
        video = VideoFactory()
        new_url = 'http://unisubs.example.com/newurl.mp4' 
        url = '/api/videos/%s/urls/' % video.video_id
        data = { 'url': new_url }
        with assert_invalidates_model_cache(video):
            r = self._post(url, data)
        r = self._get(url)
        urls = [x['url'] for x in r]
        self.logger.info(r)
        self.assertIn(video.get_video_url(), urls)
        self.assertIn(new_url, urls)


    def test_update_primary_url(self):
        """Can not change the primary url with a put request.
        """
        video = VideoFactory()
        new_url = 'http://unisubs.example.com/newurl.mp4' 
        url = '/api/videos/%s/urls/' % video.video_id
        data = { 'url': new_url }
        r = self._post(url, data)

        #Put an updated url on the video and set it as primary 
        data = { 'url': 'http://unisubs.example.com/newerurl.mp4'}
        self.client.force_authenticate(self.user)
        response = self.client.put(url, data)
        response.render()
        r = (json.loads(response.content))
        self.assertEqual(r, {u'detail': u"Method 'PUT' not allowed."})

        #Old message:  'Changing the URL of a VideoURLResource is not permitted', r)

    def test_switch_primary_url(self):
        """Use PUT request to switch primary url

           PUT /api2/partners/videos/[video-id]/urls/[url-id]/
        """
        #Post an additional url to the video
        video = VideoFactory()
        new_url = 'http://unisubs.example.com/newurl.mp4' 
        url = '/api/videos/%s/urls/' % video.video_id
        data = { 'url': new_url }
        r = self._post(url, data)

        #Set the new url as as primary 
        put_url = '/api/videos/{0}/urls/{1}/'.format(video.video_id, r['id'])
        put_data = { 'url': new_url,
                     'primary': True }
        with assert_invalidates_model_cache(video):
            self.client.force_authenticate(self.user)
            response = self.client.put(put_url, put_data)
            response.render()
            r = (json.loads(response.content))
        self.assertEqual(new_url, video.get_video_url())

    def test_url_delete(self):
        """Delete a url.
        """
        video = VideoFactory()
        new_url = 'http://unisubs.example.com/newurl.mp4' 
        url = '/api/videos/%s/urls/' % video.video_id
        data = { 'url': new_url }
        r = self._post(url, data)

        update_url = '/api/videos/{0}/urls/{1}/'.format(video.video_id, r['id'])
        with assert_invalidates_model_cache(video):
            self.client.force_authenticate(self.user)
            response = self.client.delete(update_url, data)
            self.logger.info(response)

        r = self._get(url)
        urls = [x['url'] for x in r]
        self.logger.info(r)
        self.assertIn(video.get_video_url(), urls)
        self.assertNotIn(new_url, urls)

    def test_url_delete_primary(self):
        """Can not delete the primary url. 
        """
        video = VideoFactory()
        new_url = 'http://unisubs.example.com/newurl.mp4' 
        url = '/api/videos/%s/urls/' % video.video_id
        data = { 'url': new_url,
                 'primary': True }
        r = self._post(url, data)
        update_url = '/api/videos/{0}/urls/{1}/'.format(video.video_id, r['id'])
        self.client.force_authenticate(self.user)
        response = self.client.delete(update_url, {'url': new_url})
        response.render()
        r = (json.loads(response.content))
        self.assertEqual(["Can't delete the primary URL"], r)


