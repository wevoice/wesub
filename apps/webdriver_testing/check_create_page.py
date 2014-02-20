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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from webdriver_testing.pages.site_pages import create_page
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages import video_page
from videos.models import VideoUrl

class TestCaseCreateVideos(WebdriverTestCase):
    """ TestSuite for video submission tests. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseCreateVideos, cls).setUpClass()
        cls.create_pg = create_page.CreatePage(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.create_pg.open_create_page()
    

    def tearDown(self):
        super(TestCaseCreateVideos, self).setUp()
        self.create_pg.open_create_page()

    def test_create_youtube(self):
        """Add a youtube video.

        """
        url = 'http://www.youtube.com/watch?v=WqJineyEszo'
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())
        self.assertTrue(self.video_pg.video_embed_present())

    def test_create_link_brightcove(self):
        """Add a brightcove video that resolves to link.bright...

        """
        url = 'http://bcove.me/8yxc6sxy'
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())
        self.assertTrue(self.video_pg.video_embed_present())


    def test_create_bcove_me(self):
        """Add a brightcove that resolves to bcove.me/...

        """
        url = 'http://bcove.me/1ub2ar8x'
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())
        self.assertTrue(self.video_pg.video_embed_present())



    def test_create_dailymotion(self):
        """Add a dailymotion video.

        """

        url = ('http://www.dailymotion.com/video/'
               'xlh9h1_fim-syndicat-des-apiculteurs-de-metz-environs_news')
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())
        self.assertTrue(self.video_pg.video_embed_present())

    def test_create_vimeo(self):
        """Add a vimeo video.

        """

        url = "http://vimeo.com/26487510"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())
        self.assertTrue(self.video_pg.video_embed_present())

    def test_create_ogg(self):
        """Add an ogg video video.

        """

        url = "http://qa.pculture.org/amara_tests/Birds_short.oggtheora.ogg"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())
        self.assertTrue(self.video_pg.video_embed_present())

    def test_create_mp4(self):
        """Add a an mp4 video.

        """

        url = "http://qa.pculture.org/amara_tests/Birds_short.mp4"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())
        self.assertTrue(self.video_pg.video_embed_present())

    def test_create_blip_flv(self):
        """Add a blip video.

        """
        self.skipTest('the test link no longer works, seems like blip support is broken for now')
        url = "http://blip.tv/file/get/Linuxconfau-LightningTalks606.flv"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())

    def test_create_webm(self):
        """Add a webM video.

        """

        url = "http://qa.pculture.org/amara_tests/Birds_short.webmsd.webm"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())
        self.assertTrue(self.video_pg.video_embed_present())

    def test_create_youtu_be_url(self):
        """Add a youtube video with youtu.be url.

        """

        url = "http://youtu.be/q26umaF242I"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())
        self.assertTrue(self.video_pg.video_embed_present())



class TestCaseAddFeeds(WebdriverTestCase):
    """ TestSuite for adding video feeds. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseAddFeeds, cls).setUpClass()
        cls.create_pg = create_page.CreatePage(cls)
        cls.create_pg.open_create_page()
    

    def tearDown(self):
        self.create_pg.open_create_page()

    def setUp(self):
        super(TestCaseAddFeeds, self).setUp()
        self.create_pg = create_page.CreatePage(self)
        self.create_pg.open_create_page()

    def test_feed__youtube_user(self):
        """Add a youtube user feed

        """
        youtube_user = 'janetefinn'
        self.create_pg.submit_youtube_users_videos(youtube_user)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__youtube_user_url(self):
        """Add a youtube user url feed

        """
        url = "http://www.youtube.com/user/jdragojevic"
        self.create_pg.submit_youtube_user_page(url)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__vimeo(self):
        """Add a vimeo feed

        """
        url = "http://vimeo.com/jeroenhouben/videos/rss"
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__dailymotion(self):
        """Add a dailymotion feed

        """
        url = "http://www.dailymotion.com/rss/user/WildFilmsIndia/1"
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__dailymotion_large(self):
        """Add a v. large dailymotion feed

        """
        url = "http://www.dailymotion.com/rss/user/LocalNews-GrabNetworks/1"
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__blip(self):
        """Add a blip feed

        """
        url = "http://blip.tv/stitchnbitch/rss"
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__blip_workaround(self):
        """Add a individual blip video as feed (blip workaround)

        """
        url = ('http://blip.tv/cord-cutters/'
               'cord-cutters-sync-mobile-media-with-miro-4-5280931?skin=rss')
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())




    def test_youtube_feed(self):
        """Add a youtube feed

        """
        url = "http://gdata.youtube.com/feeds/api/users/amaratestuser/uploads"
        video_url = ("http://www.youtube.com/watch?v=q26umaF242I")
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())
        vurl = VideoUrl.objects.get(url=video_url)
        self.assertTrue('Y', vurl.type)

    def test_kaltura_yahoo_feed(self):
        """Add a kaltura yahoo feed

        """
        url = "http://qa.pculture.org/feeds_test/kaltura_yahoo_feed.rss"
        video_url = ("http://cdnbakmi.kaltura.com/p/1492321/sp/149232100/"
                     "serveFlavor/entryId/1_ydvz9mq1/flavorId/1_i3dcmygl/"
                     "name/a.mp4")
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())
        vurl = VideoUrl.objects.get(url=video_url)
        self.assertTrue('K', vurl.type)

    def test_kaltura_itunes_feed(self):
        """Add a kaltura itunes feed

        """
        url = "http://qa.pculture.org/feeds_test/kaltura_itunes_feed.rss"
        video_url = ("http://cdnbakmi.kaltura.com/p/1492321/sp/149232100/"
                     "serveFlavor/entryId/1_zlgl6ut8/flavorId/1_dqgopb2z/"
                     "name/a.mp4")
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())
        vurl = VideoUrl.objects.get(url=video_url)
        self.assertTrue('K', vurl.type)
