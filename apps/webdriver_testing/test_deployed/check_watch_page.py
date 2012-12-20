#!/usr/bin/python
# -*- coding: utf-8 -*-
from setup_base import WebdriverRemote
from apps.webdriver_testing.pages.site_pages import watch_page
from apps.webdriver_testing.pages.site_pages import video_page
from apps.webdriver_testing.pages.site_pages import search_results_page
import time


class TestCaseWatchPageSearch(WebdriverRemote):
    """TestSuite for site video searches.

    """

    def setUp(self):
        WebdriverRemote.setUp(self)
        self.watch_pg = watch_page.WatchPage(self)
        self.watch_pg.open_watch_page()

    def test_advanced_search(self):
        """Search for videos by text, video lang and translation.
 
        """
        results_pg = self.watch_pg.advanced_search(
            search_term = 'Firefox',
            orig_lang = 'English', 
            trans_lang='English')

        #WORKAROUND for testing on jenkins, where submitting search give err page.
        results_pg.open_page(results_pg.current_url())
 
        self.assertTrue(results_pg.page_has_video( 'Switch to Firefox'))


class TestCaseWatchPageListings(WebdriverRemote):
    """TestSuite for watch page latest videos section.

    """

    def setUp(self):
        WebdriverRemote.setUp(self)

        self.watch_pg = watch_page.WatchPage(self)
        #Open the watch page as a test starting point.
        self.watch_pg.open_watch_page()


    def test_popular__section(self):
        """Popular section displays videos.

        """
        video_list = self.watch_pg.section_videos(section='popular')
        self.assertGreater(len(video_list), 0)
