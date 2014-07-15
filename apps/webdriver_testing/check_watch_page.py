#!/usr/bin/python
# -*- coding: utf-8 -*-
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages import watch_page
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing.pages.site_pages import search_results_page
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import UserLangFactory
from webdriver_testing.data_factories import VideoFactory 
from webdriver_testing import data_helpers
from django.core import management
import datetime
import time
import os

class TestCaseWatchPageSearch(WebdriverTestCase):
    """TestSuite for site video searches.  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseWatchPageSearch, cls).setUpClass()
        management.call_command('update_index', interactive=False)
        cls.watch_pg = watch_page.WatchPage(cls)
        cls.data = data_helpers.DataHelpers()
        testdata = {'url': 'http://www.youtube.com/watch?v=WqJineyEszo',
                    'video__title': ('X Factor Audition - Stop Looking At My '
                                    'Mom Rap - Brian Bradley'),
                    'type': 'Y',
                    'video__primary_audio_language_code': 'en'
                   }

        video = cls.data.create_video(**testdata)
        data = {
                'language_code': 'en',
                'subtitles': ('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'complete': True,
                'video': video
               }
        cls.data.add_subs(**data)
        cls.user = UserFactory()        
        cls.data.create_videos_with_fake_subs('apps/webdriver_testing/'
                                         'subtitle_data/fake_subs.json')
        VideoFactory.create(title = u'不过这四个问题')
        video = VideoFactory.create(title = "my test vid")
        data = {
                'language_code': 'zh-cn',
                'subtitles': ('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.zh-cn.sbv'),
                'complete': True
               }
        test_video = cls.data.create_video_with_subs(cls.user, **data)
        management.call_command('update_index', interactive=False)



    def setUp(self):
        super(TestCaseWatchPageSearch, self).setUp()
        self.watch_pg.open_watch_page()
        

    def test_search__simple(self):
        """Search for text contained in video title.

        """
        test_text = 'X factor'
        results_pg = self.watch_pg.basic_search(test_text)
        self.assertTrue(results_pg.search_has_results())

    def test_search_subs_nonascii(self):
        """Search for sub content with non-ascii char strings.
 
        """
        test_text = u'不过这四个问题'
        results_pg = self.watch_pg.basic_search(test_text)
        self.assertTrue(results_pg.search_has_results())

    def test_search__title_nonascii(self):
        """Search title content with non-ascii char strings.
 
        """
        
        #Search for: chinese chars by opening entering the text 
        #via javascript because webdriver can't type those characters.
        self.browser.execute_script("document.getElementsByName"
                               "('q')[1].value='不过这四个问题'")
        results_pg = self.watch_pg.advanced_search()
        self.assertTrue(results_pg.search_has_results())
       

    def test_search_sub_content(self):
        """Search contents in subtitle text.

        """
        test_text = '[Zeus]'
        results_pg = self.watch_pg.basic_search(test_text)
        self.assertTrue(results_pg.search_has_results())

    def test_search_video_lang(self):
        """Search for videos by video language.
 
        """
        results_pg = self.watch_pg.advanced_search(orig_lang='en')
        self.assertTrue(results_pg.page_has_video(
            'original english with incomplete pt'))
        self.assertEqual(2, len(results_pg.page_videos()))

    def test_search__trans_lang(self):
        """Search for videos by translations language.
 
        """
        results_pg = self.watch_pg.advanced_search(trans_lang='pt')
        self.assertTrue(results_pg.page_has_video(
            'original english with incomplete pt'))
        self.assertEqual(1, len(results_pg.page_videos()))

    def test_search__trans_and_video_lang(self):
        """Search for videos by video lang and translations language.
 
        """
        results_pg = self.watch_pg.advanced_search(orig_lang = 'en', 
            trans_lang='Portuguese')
        self.assertTrue(results_pg.page_has_video(
            'original english with incomplete pt'))
        self.assertEqual(1, len(results_pg.page_videos()))

    def test_search__text_trans_video(self):
        """Search for videos by text, video lang and translation.
 
        """
        self.browser.execute_script("document.getElementsByName('q')[1].value='subs'")
        results_pg = self.watch_pg.advanced_search(
            orig_lang = 'ar', 
            trans_lang='en')
        self.assertTrue(results_pg.page_has_video(
            'original ar with en complete subs'))
        self.assertEqual(1, len(results_pg.page_videos()))

    def test_result__language_menu(self):
        user = UserFactory()
        user_speaks = ['en', 'pt', 'ru', 'ar']
        for lang in user_speaks:
            UserLangFactory(user = user,
                            language = lang)
        self.watch_pg.log_in(user.username, 'password')
        test_text = 'english'
        title = 'original english with incomplete'
        results_pg = self.watch_pg.basic_search(test_text)
        expected_langs = ['English', 'Portuguese']
        if results_pg.search_has_results():
            self.assertEqual(expected_langs, results_pg.pulldown_languages(title))
        else: 
            self.fail('Video search returned no results') 


class TestCaseWatchPageListings(WebdriverTestCase):
    """TestSuite for watch page latest videos section.  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseWatchPageListings, cls).setUpClass()
        management.call_command('clear_index', interactive=False)

        cls.watch_pg = watch_page.WatchPage(cls)
        cls.data = data_helpers.DataHelpers()
        cls.user = UserFactory()
        cls.data.create_videos_with_fake_subs('apps/webdriver_testing/subtitle_data/fake_subs.json')

        #create a video and mark as featured.
        cls.feature_vid = cls.data.create_video_with_subs(cls.user)
        cls.feature_vid.featured=datetime.datetime.now()
        cls.feature_vid.save()
       
        #update solr index
        management.call_command('update_index', interactive=False)

        cls.expected_videos = [ 'original ar with en complete subs',
                                 'original english with incomplete pt', 
                                 'original pt-br incomplete 4 lines', 
                                 'original russian with pt-br subs',
                                 'original swa incomplete 2 lines' ]

    def setUp(self):
        super(TestCaseWatchPageListings, self).setUp()
        #Open the watch page as a test starting point.
        self.watch_pg.open_watch_page()

    def test_latest__section(self):
        """Latest section displays the expected videos.

        """
        video_list = self.watch_pg.section_videos(section='latest')
        for vid in self.expected_videos:
            self.assertIn(vid, video_list)


    def test_latest__page(self):
        """Latest page opens when 'More' clicked and displays videos.

        """
        self.watch_pg.display_more(section='latest')
        self.watch_pg.search_complete()
        video_list = self.watch_pg.section_videos(section='featured')
        for vid in self.expected_videos:
            self.assertIn(vid, video_list)

    def test_popular__section(self):
        """Popular section displays expected videos.

        """
        video_list = self.watch_pg.section_videos(section='popular')
        for vid in self.expected_videos:
            self.assertIn(vid, video_list)

    def test_popular__default_week(self):
        """Sort by week is the default sort value.

        """
        default_sort = self.watch_pg.popular_current_sort()
        self.assertEqual('This Week', default_sort)

    def test_popular__sort_year(self):
        """Sort by year displays correct value and link with sort parameter.

        """
        self.watch_pg.popular_sort('year')
        self.assertEqual('This Year', self.watch_pg.popular_current_sort())
        self.assertIn('sort=year', self.watch_pg.popular_more_link())


    def test_popular__sort_today(self):
        """Sort by today displays correct value and link with sort parameter.

        """
        self.watch_pg.popular_sort('today')
        self.assertEqual('Today', self.watch_pg.popular_current_sort())
        self.assertIn('sort=today', self.watch_pg.popular_more_link())

    def test_popular__sort_alltime(self):
        """Sort by alltime displays correct value and link with sort parameter.

        """
        self.watch_pg.popular_sort('total')
        self.assertEqual('All Time', self.watch_pg.popular_current_sort())
        self.assertIn('sort=total', self.watch_pg.popular_more_link())

    def test_popular__sort_month(self):
        """Sort by month displays correct value and link with sort parameter.

        """
        self.watch_pg.popular_sort('month')
        self.assertEqual('This Month', self.watch_pg.popular_current_sort())
        self.assertIn('sort=month', self.watch_pg.popular_more_link())


    def test_popular__page(self):
        """Popular page opens when 'More' clicked and displays videos.

        """
        self.watch_pg.display_more(section='popular')
        video_list = self.watch_pg.section_videos(section='popular')
        for vid in self.expected_videos:
            self.assertIn(vid, video_list)


    def test_featured__section(self):
        """Featured section only displays featured videos.

        """
        video_list = self.watch_pg.section_videos(section='featured')
        self.assertEqual([self.feature_vid.title], video_list)

    def test_featured__page(self):
        """Featured page opens when 'More' clicked and displays videos.

        """
        self.watch_pg.display_more(section='featured')
        video_list = self.watch_pg.section_videos(section='featured')
        self.assertEqual([self.feature_vid.title], video_list)
