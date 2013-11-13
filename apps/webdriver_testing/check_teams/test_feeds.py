# -*- coding: utf-8 -*-

from webdriver_testing.pages.site_pages.teams import add_feed_page
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import TeamMemberFactory
from videos.models import VideoUrl




class TestCaseAddFeeds(WebdriverTestCase):
    """ TestSuite for adding video feeds. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseAddFeeds, cls).setUpClass()
        cls.user = UserFactory.create()
        cls.team = TeamMemberFactory.create(
            user = cls.user).team

        cls.feed_pg = add_feed_page.AddFeedPage(cls)
        cls.feed_pg.open_feed_page(cls.team.slug)
        cls.feed_pg.log_in(cls.user.username, 'password')

    def setUp(self):
        self.feed_pg.open_feed_page(self.team.slug)

    def test_duplicate_youtube_user(self):
        """Add a youtube user feed

        """
        youtube_user = 'latestvideoss'
        self.feed_pg.submit_youtube_users_videos(youtube_user)
        self.assertTrue(self.feed_pg.submit_successful())
        self.feed_pg.open_feed_page(self.team.slug)
        self.feed_pg.submit_youtube_users_videos(youtube_user)
        expected_error = ('Feed for https://gdata.youtube.com/feeds/api/users'
                          '/latestvideoss/uploads already exists')
        self.assertEqual(expected_error, self.feed_pg.submit_error())


    def test_youtube_user_url(self):
        """Add a youtube user url feed

        """
        url = "http://www.youtube.com/user/jdragojevic"
        self.feed_pg.submit_youtube_user_page(url)
        self.assertTrue(self.feed_pg.submit_successful())

    def test_vimeo(self):
        """Add a vimeo feed

        """
        url = "http://vimeo.com/jeroenhouben/videos/rss"
        self.feed_pg.submit_feed_url(url)
        self.assertTrue(self.feed_pg.submit_successful())

    def test_youtube_feed(self):
        """Add a youtube feed

        """
        url = "http://gdata.youtube.com/feeds/api/users/amaratestuser/uploads"
        video_url = ("http://www.youtube.com/watch?v=q26umaF242I")
        self.feed_pg.submit_feed_url(url)
        self.assertTrue(self.feed_pg.submit_successful())
        vurl = VideoUrl.objects.get(url=video_url)
        self.assertTrue('Y', vurl.type)
        self.assertEqual(self.team.name, vurl.video.teamvideo.team.name)

    def test_kaltura_yahoo_feed(self):
        """Add a kaltura yahoo feed

        """
        url = "http://qa.pculture.org/feeds_test/kaltura_yahoo_feed.rss"
        video_url = ("http://cdnbakmi.kaltura.com/p/1492321/sp/149232100/"
                     "serveFlavor/entryId/1_ydvz9mq1/flavorId/1_i3dcmygl/"
                     "name/a.mp4")
        self.feed_pg.submit_feed_url(url)
        self.assertTrue(self.feed_pg.submit_successful())
        vurl = VideoUrl.objects.get(url=video_url)
        self.assertTrue('K', vurl.type)
        self.assertEqual(self.team.name, vurl.video.teamvideo.team.name)

    def test_kaltura_itunes_feed(self):
        """Add a kaltura itunes feed

        """
        url = "http://qa.pculture.org/feeds_test/kaltura_itunes_feed.rss"
        video_url = ("http://cdnbakmi.kaltura.com/p/1492321/sp/149232100/"
                     "serveFlavor/entryId/1_zlgl6ut8/flavorId/1_dqgopb2z/"
                     "name/a.mp4")
        self.feed_pg.submit_feed_url(url)
        self.assertTrue(self.feed_pg.submit_successful())
        vurl = VideoUrl.objects.get(url=video_url)
        self.assertTrue('K', vurl.type)
        self.assertEqual(self.team.name, vurl.video.teamvideo.team.name)
