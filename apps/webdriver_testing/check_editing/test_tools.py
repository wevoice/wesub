#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time 
from django.test import TestCase
from django.core import management
from webdriver_testing.pages.site_pages import site_modals
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing import data_helpers
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing.pages.site_pages import editor_page
from webdriver_testing.data_factories import UserFactory

class TestCaseTools(WebdriverTestCase):

    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseTools, cls).setUpClass()
        cls.modal = site_modals.SiteModals(cls)
        cls.user = UserFactory.create()
        data = {'url': 'http://www.youtube.com/watch?v=5CKwCfLUwj4', 
                'video__title': 'Open Source Philosophy',
                'video__primary_audio_language_code': 'en',
                'type': 'Y' 
               } 

        cls.data_utils = data_helpers.DataHelpers()
        cls.video = cls.data_utils.create_video(**data) 
        subs_data = {
                        'language_code': 'en',
                        'complete': True,
                        'visibility': 'public'
                     }

        cls.data_utils.add_subs(video=cls.video, **subs_data) 
        management.call_command('update_index', interactive=False) 
        cls.editor_pg = editor_page.EditorPage(cls)
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_pg.open_page('auth/login/', alert_check=True)
        cls.video_pg.log_in(cls.user.username, 'password')

    def tearDown(self):
        self.browser.get_screenshot_as_file("%s.png" % self.id())
        try:
            self.editor_pg.exit()
        except:
            self.editor_pg.open_page('/')
            self.editor_pg.handle_js_alert('accept') 

    def test_timings_present_for_new_translation(self):
        """New translation starts with lines and times. """

        self.video_pg.open_video_page(self.video.video_id)
        self.video_pg.add_subtitles()
        self.modal.add_language('Polish')
        working_times = self.editor_pg.start_times()
        ref_times = self.editor_pg.reference_times()
        self.assertEqual(ref_times[:5], working_times[:5]) 
        self.assertEqual(len(ref_times), len(working_times))


    def test_copy_timings_to_txt_upload(self):
        """Copy timings to untimed text upload. """
        sub_file = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                'subtitle_data', 'Untimed_text.txt')
        self.video_pg.log_in(self.user.username, 'password')
        self.video_pg.open_video_page(self.video.video_id)
        self.video_pg.upload_subtitles('Dutch', sub_file)
        self.editor_pg.open_editor_page(self.video.video_id, 'nl')
        self.editor_pg.copy_timings()
        working_times = self.editor_pg.start_times()
        ref_times = self.editor_pg.reference_times()
        self.assertEqual(ref_times[:5], working_times[:5]) 


    def test_copy_timings_change_reference(self):
        """Change reference lang then copy timings. """
        test_user = UserFactory.create()
        sub_file = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                'subtitle_data', 'Untimed_text.txt')
        self.video_pg.log_in(test_user.username, 'password')
        self.video_pg.open_video_page(self.video.video_id)
        self.video_pg.upload_subtitles('Dutch', sub_file)
        self.editor_pg.open_editor_page(self.video.video_id, 'nl')
        self.editor_pg.select_ref_language('Danish')
        self.editor_pg.copy_timings()
        working_times = self.editor_pg.start_times()
        ref_times = self.editor_pg.reference_times()
        self.assertEqual(ref_times[:5], working_times[:5]) 

    def test_copy_timings_reference_unsynced(self):
        """No copy in menu if reference subs are unsynced. """
        test_user = UserFactory.create()
        sub_file = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                'subtitle_data', 'Untimed_text.txt')
        self.video_pg.log_in(test_user.username, 'password')
        self.video_pg.open_video_page(self.video.video_id)
        self.video_pg.upload_subtitles('Dutch', sub_file)
        self.editor_pg.open_ed_with_base(self.video.video_id, 'sv', 'nl')
        self.editor_pg.select_ref_language('Dutch')
        time.sleep(3)
        self.assertEqual("Element not displayed", self.editor_pg.copy_timings())

    def test_copy_timings_reference_draft(self):
        """No copy in menu if reference subs are draft (incomplete). """
        test_user = UserFactory.create()
        self.video_pg.log_in(test_user.username, 'password')
        self.editor_pg.open_editor_page(self.video.video_id, 'en')
        self.editor_pg.select_ref_language('Turkish')
        self.assertEqual("Element not displayed", self.editor_pg.copy_timings())

    def test_copy_timings_working_blank(self):
        """No copy in menu if there are no working subs. """
        test_user = UserFactory.create()
        self.video_pg.log_in(test_user.username, 'password')
        self.editor_pg.open_editor_page(self.video.video_id, 'hr')
        self.assertEqual("Element not displayed", self.editor_pg.copy_timings())
