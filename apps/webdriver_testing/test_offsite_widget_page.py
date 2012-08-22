# -*- coding: utf-8 -*-
import time
import os
from nose.tools import assert_true, assert_false 
from webdriver_base import WebdriverTestCase 
from site_pages import offsite_page
from apps.webdriver_testing.testdata_factories import *
from apps.webdriver_testing.site_pages import auth_page
from django.core.urlresolvers import reverse





class WebdriverTestCaseOffsiteWidget(WebdriverTestCase):
    def _create_video_with_subs(self, videoURL=None):
        #The videos on the pagedemo pages don't come with subs, so we have to add some
        #in order to test their display during playback.
        self.user = UserFactory.create(username='tester')
        video, created = Video.get_or_create_for_url(videoURL)
        self.client.login(**self.auth)
        data = {
            'language': 'en',
            'video_language': 'en',
            'video': video.pk,
            'draft': open('apps/videos/fixtures/test.srt'),
            'is_complete': True
            }
        self.client.post(reverse('videos:upload_subtitles'), data)
        return video
       
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.offsite_pg = offsite_page.OffsitePage(self)
        self.auth = dict(username='tester', password='password')


    def test_widget__nytimes(self):
        self.skipTest("FIXME: This videos and widget fail to load when loading site in vagrant vm")
        url = "pagedemo/nytimes_youtube_embed"
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()

    def test_widget__youtube(self):
        url = "pagedemo/blog_youtube_embed"
        video = self._create_video_with_subs(videoURL='http://www.youtube.com/watch?v=-RSjbtJHi_Q')
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()

    def test_widget__gapminder(self):
        url = "pagedemo/gapminder"
        video = self._create_video_with_subs(videoURL='http://www.youtube.com/watch?v=jbkSRLYSojo')
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()

    def test_widget__aljazeera(self):
        self.skipTest("FIXME: This test works intermittantly and sometimes hangs everything.")
        url = "pagedemo/aljazeera_blog"
        video = self._create_video_with_subs(videoURL='http://www.youtube.com/watch?v=Oraas1O7DIc')
        self.offsite_pg.open_offsite_page(url)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()
    
    def test_widget__boingboing(self):
        url = "pagedemo/boingboing_embed"
        # video = self._create_video_with_subs(videoURL='http://www.youtube.com/watch?v=Oraas1O7DIc')
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()


class WebdriverTestCaseOffsiteWidgetizer(WebdriverTestCase):


    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.offsite_pg = offsite_page.OffsitePage(self)
        self.auth = dict(username='tester', password='password')

    def test_widgetizer__khan(self):
        url = "pagedemo/khan_widgetizer"
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()

    def test_widgetizer__boingboing(self):
        url = "pagedemo/boingboing_widgetizer"
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()


