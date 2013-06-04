#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from apps.videos.models import Video

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.pages.site_pages import video_page
from apps.webdriver_testing.pages.site_pages import editor_page
from apps.webdriver_testing.data_factories import UserFactory

class TestCaseLeftSide(WebdriverTestCase):
    fixtures = ['apps/webdriver_testing/fixtures/editor_auth.json', 
                'apps/webdriver_testing/fixtures/editor_videos.json',
                'apps/webdriver_testing/fixtures/editor_subtitles.json']
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseLeftSide, cls).setUpClass()
        cls.logger.info("""Default Test Data

                        English, source primary v2 -> v6
                                 v1 -> deleted

                        Chinese v1 -> v3
                                v3 {"zh-cn": 2, "en": 6}

                        Danish v1 --> v4
                               v4 {"en": 5, "da": 3}
                               
                        Swedish v1 --> v3 FORKED
                                v3 {"sv": 2}
                                v1 --> private

                        Turkish (tr) v1 incomplete {"en": 5}
                       """)
        cls.editor_pg = editor_page.EditorPage(cls)
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create()
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_pg.open_page('videos/watch/')
        cls.video_pg.log_in(cls.user, 'password')
        
        
    def test_reference_lang__forked(self):
        """Default reference lang for forked translation is the same lang. """
        video = Video.objects.all()[0]
        self.editor_pg.open_editor_page(video.video_id, 'sv')
        self.assertEqual('Swedish', self.editor_pg.selected_ref_language())


    def test_reference_lang__primary(self):
        """Default reference lang for transcription is the same lang. """
        video = Video.objects.all()[0]
        self.editor_pg.open_editor_page(video.video_id, 'en')
        self.assertEqual('English', self.editor_pg.selected_ref_language())

    def test_reference_lang__translation(self):
        """Default reference lang for translation is the parent lang. """
        video = Video.objects.all()[0]
        self.editor_pg.open_editor_page(video.video_id, 'da')
        self.assertEqual('English', self.editor_pg.selected_ref_language())

    def test_reference_version__translation_latest(self):
        """Default reference version is version translatied from source. """
        video = Video.objects.all()[0]
        self.editor_pg.open_editor_page(video.video_id, 'zh-cn')
        self.assertEqual('Version 6', self.editor_pg.selected_ref_version())
        self.editor_pg.open_editor_page(video.video_id, 'da')
        self.assertEqual('Version 5', self.editor_pg.selected_ref_version())

    def test_reference_text_displayed(self):
        """Reference language text updated when language and version changed.

        """
        video = Video.objects.all()[0]
        self.editor_pg.open_editor_page(video.video_id, 'da')
        self.assertEqual('Tangible problems.', 
                         self.editor_pg.reference_text()[0])
        self.editor_pg.select_ref_language('Danish')
        self.assertEqual('Konkrete problemer', 
                         self.editor_pg.reference_text()[0])
        self.editor_pg.select_ref_language('Turkish')
        self.assertEqual(u'\xe7\xf6zmekte olan g\xfcc\xfcn\xfc hep hissettim.', 
                         self.editor_pg.reference_text()[2])

class TestCaseCenter(WebdriverTestCase):
    fixtures = ['apps/webdriver_testing/fixtures/editor_auth.json', 
                'apps/webdriver_testing/fixtures/editor_videos.json',
                'apps/webdriver_testing/fixtures/editor_subtitles.json']
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseCenter, cls).setUpClass()
        cls.logger.info("""Default Test Data

                        English, source primary v2 -> v6
                                 v1 -> deleted

                        Chinese v1 -> v3
                                v3 {"zh-cn": 2, "en": 6}

                        Danish v1 --> v4
                               v4 {"en": 5, "da": 3}
                               
                        Swedish v1 --> v3 FORKED
                                v3 {"sv": 2}
                                v1 --> private

                        Turkish (tr) v1 incomplete {"en": 5}
                       """)
        cls.editor_pg = editor_page.EditorPage(cls)
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create()
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_pg.open_page('videos/watch/')
        cls.video_pg.log_in(cls.user, 'password')

    def test_selected_subs_on_video(self):
        """Clicking a working subs displays it on the video."""
        self.skipTest('incomplete')
        video = Video.objects.all()[0]
        self.editor_pg.open_editor_page(video.video_id, 'en')
        sub_text = self.editor_pg.click_working_sub_line(3)
        self.assertEqual(sub_text, self.editor_pg.sub_overlayed_text())



