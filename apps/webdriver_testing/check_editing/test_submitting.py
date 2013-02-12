#!/usr/bin/python
# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.pages.site_pages import video_page
from apps.webdriver_testing.pages.site_pages import video_language_page
from apps.webdriver_testing.pages.editor_pages import dialogs
from apps.webdriver_testing.pages.editor_pages import unisubs_menu
from apps.webdriver_testing.pages.editor_pages import subtitle_editor 
from apps.webdriver_testing.data_factories import UserFactory
import os
import time

class TestCaseSubmittable(WebdriverTestCase):
    """Tests for the Subtitle Transcription editor page.  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseSubmittable, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()

        cls.video_pg = video_page.VideoPage(cls)
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)

        cls.user = UserFactory.create(username = 'user')
        cls.create_modal = dialogs.CreateLanguageSelection(cls)
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)
        cls.unisubs_menu = unisubs_menu.UnisubsMenu(cls)
        td = {'url': ('http://qa.pculture.org/amara_tests/'
                     'Birds_short.mp4')
             }
        cls.test_video = cls.data_utils.create_video(**td)
        cls.video_pg.open_video_page(cls.test_video.video_id)
        cls.video_pg.log_in(cls.user.username, 'password')
        cls.video_pg.set_skiphowto()
 
        #Open the video page and sync the first 3 subs
        cls.video_pg.add_subtitles()
        cls.create_modal.create_original_subs('English', 'English')

        cls.logger.info('typing subs')
        cls.typed_subs = cls.sub_editor.type_subs()
        cls.sub_editor.continue_to_next_step()
        cls.logger.info('syncing subs')
        cls.sub_editor.sync_subs(len(cls.typed_subs)+2)
        cls.timing_list = cls.sub_editor.sub_timings()
        cls.sub_editor.save_and_exit()

    def setUp(self):
        super(TestCaseSubmittable, self).setUp()
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
                                                    'en')
        #time.sleep(2)
        self.video_language_pg.handle_js_alert('accept')
        self.video_language_pg.edit_subtitles()
        self.sub_editor.continue_to_next_step()
        self.logger.info('continue to description screen')
        self.sub_editor.continue_to_next_step()
        self.logger.info('continue to review screen')
        self.sub_editor.continue_to_next_step()

        #All tests start in check step with fully synced subs 


    def test_display__checkpage(self):
        """Manually entered synced subs display in check step.

        """
        #Verify synced subs are increasing in time
        try:
            self.assertGreater(float(self.timing_list[5]), 
                               float(self.timing_list[4]))
        except ValueError as e:
            self.fail(e)
        #Verify last sub is not blank
        self.assertNotEqual(self.timing_list[-1], '')

       
    def test_save(self):
        """Manually entered unsynced subs are saved upon save and exit.
        
        """
        curr_url = self.sub_editor.current_url()
        self.sub_editor.save_and_exit()
        self.sub_editor.open_page(curr_url)

        #Past transcribe
        self.sub_editor.continue_to_next_step()

        #Past sync
        self.sub_editor.continue_to_next_step()

        #Past Description
        self.sub_editor.continue_to_next_step()

        #Verify sub timings are same as pre-save timings 
        self.assertEqual(self.timing_list, 
            self.sub_editor.sub_timings(check_step=True))


    def test_download(self):
        """Manually entered synced subs can be download from check page.

        """
        saved_subs = self.sub_editor.download_subtitles()
        #Verify each line is present in the copy-able text. 
        for line in saved_subs:
            self.assertIn(line, saved_subs)


    def test_submit__complete(self):
        """Manually entered subs are submitted and marked as complete.
        """
        self.sub_editor.submit(complete=True)
        complete_langs = self.test_video.completed_subtitle_languages()
        sub_lang = self.test_video.subtitle_language('en')
        self.assertTrue(True, sub_lang.subtitles_complete)
        video_language_pg = video_language_page.VideoLanguagePage(self)
        video_language_pg.open_video_lang_page(self.test_video.video_id, 'en')
        self.assertEqual(6, sub_lang.get_subtitle_count())



class TestCaseIncomplete(WebdriverTestCase):
    """Tests for the Subtitle Transcription editor page.  """
    NEW_BROWSER_PER_TEST_CASE = True

    def setUp(self):
        super(TestCaseIncomplete, self).setUp()
        self.data_utils = data_helpers.DataHelpers()
        self.video_pg = video_page.VideoPage(self)
        self.user = UserFactory.create(username = 'user')
        self.create_modal = dialogs.CreateLanguageSelection(self)
        self.sub_editor = subtitle_editor.SubtitleEditor(self)
        self.unisubs_menu = unisubs_menu.UnisubsMenu(self)
        td = {'url': ('http://qa.pculture.org/amara_tests/'
                   'Birds_short.webmsd.webm')
             }

        self.test_video = self.data_utils.create_video(**td)
        self.video_pg.open_video_page(self.test_video.video_id)
        self.video_pg.log_in(self.user.username, 'password')
        self.video_pg.set_skiphowto()
 
        #Open the video page and sync the first 3 subs
        self.video_pg.add_subtitles()
        self.create_modal.create_original_subs('English', 'English')

        self.logger.info('typing subs')
        self.typed_subs = self.sub_editor.type_subs()
        self.sub_editor.continue_to_next_step()
        
        self.logger.info('syncing subs')
        self.sub_editor.sync_subs(len(self.typed_subs)+2)
        self.timing_list = self.sub_editor.sub_timings()
        self.sub_editor.continue_to_next_step()
        self.logger.info('continue to description screen')
        self.sub_editor.continue_to_next_step()
        self.logger.info('continue to review screen')
        self.sub_editor.continue_to_next_step()

    def test_submit__incomplete(self):
        """Manually entered are submitted, but not marked complete.

        """
        self.sub_editor.submit(complete=False)
        sub_lang = self.test_video.subtitle_language('en')
        self.assertEqual(False, sub_lang.subtitles_complete)
        self.assertEqual(6, sub_lang.get_subtitle_count())

