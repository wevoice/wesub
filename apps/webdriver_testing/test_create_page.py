# -*- coding: utf-8 -*-

from nose.tools import assert_true, assert_false
from nose import with_setup
from site_pages import create_page
from webdriver_base import WebdriverTestCase 

class WebdriverTestCaseVideosCreateVideos(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.create_pg = create_page.CreatePage(self)
        self.create_pg.open_create_page()
  
    def test_create_video__youtube(self):
        url = 'http://www.youtube.com/watch?v=WqJineyEszo'
        self.create_pg.submit_video(url)
        assert_true(self.create_pg.submit_success())

    def test_create_video__dailymotion(self):
        url = 'http://www.dailymotion.com/video/xlh9h1_fim-syndicat-des-apiculteurs-de-metz-environs_news'
        self.create_pg.submit_video(url)
        assert_true(self.create_pg.submit_success())

    def test_create_video__vimeo(self):
        url = "http://vimeo.com/26487510"
        self.create_pg.submit_video(url)
        assert_true(self.create_pg.submit_success())

    def test_create_video__ogg(self):
        url = "http://qa.pculture.org/amara_tests/Birds_short.oggtheora.ogg"
        self.create_pg.submit_video(url)
        assert_true(self.create_pg.submit_success())

    def test_create_video__mp4(self):
        url = "http://qa.pculture.org/amara_tests/Birds_short.mp4"
        self.create_pg.submit_video(url)
        assert_true(self.create_pg.submit_success())

    def test_create_video__blip_flv(self):
        url = "http://blip.tv/file/get/Linuxconfau-LightningTalks606.flv"
        self.create_pg.submit_video(url)
        assert_true(self.create_pg.submit_success())

    def test_create_video__webm(self):
        url = "http://qa.pculture.org/amara_tests/Birds_short.webmsd.webm"
        self.create_pg.submit_video(url)
        assert_true(self.create_pg.submit_success())

    def test_create_video__youtu_be_url(self):
        url = "http://youtu.be/BXMPp0TLSEo"
        self.create_pg.submit_video(url)
        assert_true(self.create_pg.submit_success())

class WebdriverTestCaseVideosCreateFeedVideos(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.create_pg = create_page.CreatePage(self)
        self.create_pg.open_create_page()

    def test_create_feed__youtube_user(self):
        youtube_user = 'croatiadivers'
        self.create_pg.submit_youtube_users_videos(youtube_user, save=True)
        assert_true(self.create_pg.multi_submit_successful())

        
    def test_create_feed__youtube_user_url(self):
        url = "http://www.youtube.com/user/jdragojevic"
        self.create_pg.submit_youtube_user_page(url, save=True)
        assert_true(self.create_pg.multi_submit_successful())

    def test_create_feed__vimeo(self):
        url = "http://vimeo.com/jeroenhouben/videos/rss"
        self.create_pg.submit_feed_url(url)
        assert_true(self.create_pg.multi_submit_successful())

    def test_create_feed__dailymotion(self):
        url = "http://www.dailymotion.com/rss/user/WildFilmsIndia/1"
        self.create_pg.submit_feed_url(url)
        assert_true(self.create_pg.multi_submit_successful())

    def test_create_feed__dailymotion_large(self):
        self.skipTest("This is just too slow, and probably not that necessary")
        url = "http://www.dailymotion.com/rss/user/LocalNews-GrabNetworks/1"
        self.create_pg.submit_feed_url(url)
        assert_true(self.create_pg.multi_submit_successful())

    def test_create_feed__blip(self):
        url = "http://blip.tv/stitchnbitch/rss"
        self.create_pg.submit_feed_url(url)
        assert_true(self.create_pg.multi_submit_successful())

    def test_create_feed__blip_video_workaround(self):
        url = "http://blip.tv/cord-cutters/cord-cutters-sync-mobile-media-with-miro-4-5280931?skin=rss"
        self.create_pg.submit_feed_url(url)
        assert_true(self.create_pg.multi_submit_successful())

    def test_create_feed__youtube_feed(self):
        url = "http://gdata.youtube.com/feeds/api/users/janetefinn/uploads"
        self.create_pg.submit_feed_url(url)
        assert_true(self.create_pg.multi_submit_successful())
   
    
