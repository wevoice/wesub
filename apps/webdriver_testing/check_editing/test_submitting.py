#!/usr/bin/python
# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.site_pages import video_page
from apps.webdriver_testing.site_pages import video_language_page
from apps.webdriver_testing.editor_pages import dialogs
from apps.webdriver_testing.editor_pages import unisubs_menu
from apps.webdriver_testing.editor_pages import subtitle_editor 
from apps.webdriver_testing.data_factories import UserFactory
import os
import time

class TestCaseSubmittable(WebdriverTestCase):
    """Tests for the Subtitle Transcription editor page.
        
    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.video_pg = video_page.VideoPage(self)
        self.user = UserFactory.create(username = 'user')
        self.create_modal = dialogs.CreateLanguageSelection(self)
        self.sub_editor = subtitle_editor.SubtitleEditor(self)
        self.unisubs_menu = unisubs_menu.UnisubsMenu(self)
        self.video_pg.log_in(self.user.username, 'password')
        self.test_video = data_helpers.create_video(self, 
            'http://qa.pculture.org/amara_tests/Birds_short.mp4')

        #Open the video page and sync the first 3 subs
        self.video_pg.open_video_page(self.test_video.video_id)
        self.video_pg.add_subtitles()
        self.create_modal.create_original_subs('English', 'English')
        self.create_modal.continue_past_help()
        self.typed_subs = self.sub_editor.type_subs()
        self.sub_editor.continue_to_next_step()
        self.sub_editor.sync_subs(len(self.typed_subs)+2)
        self.timing_list = self.sub_editor.sub_timings()
        #Past Sync
        self.sub_editor.continue_to_next_step()
        #Past Description
        self.sub_editor.continue_to_next_step()

        #All tests start in check step with fully synced subs 



    def test_display__checkpage(self):
        """Manually entered synced subs display in check step.

        """
        #Verify synced subs are increasing in time
        self.assertGreater(float(self.timing_list[5]), 
            float(self.timing_list[4]))
        #Verify last sub is not blank
        self.assertNotEqual(self.timing_list[-1], '')

       
    def test_save(self):
        """Manually entered unsynced subs are saved upon save and exit.
        
        """
        curr_url = self.sub_editor.current_url()
        self.sub_editor.save_and_exit()
        self.sub_editor.open_page(curr_url)
        #self.sub_editor.continue_to_next_step() #to Sync
        #self.sub_editor.continue_to_next_step() #to Description
        #self.sub_editor.continue_to_next_step() #to Check

        #Verify sub timings are same as pre-save timings 
        self.assertEqual(self.timing_list, 
            self.sub_editor.sub_timings(check_step=True))


    def test_close__abruptly(self):
        """Test subs are saved when browser closes abruptly.
      
        Note: the browser needs to be open for about 80 seconds for saving.
        """
        #self.skipTest("bug: https://unisubs.sifterapp.com/issue/1552")
        time.sleep(90)
        self.sub_editor.open_page("")
        self.sub_editor.handle_js_alert('accept')
        time.sleep(5)
        self.video_pg.open_video_page(self.test_video.video_id)
        self.unisubs_menu.open_menu()
        self.assertEqual(self.create_modal.warning_dialog_title(), 
            'Resume editing?')
        self.create_modal.click_dialog_continue()
        self.create_modal.click_dialog_continue()
        self.sub_editor.continue_to_next_step() #to Sync
        self.sub_editor.continue_to_next_step() #to Description
        self.sub_editor.continue_to_next_step() #to Check

        #Verify sub timings are same as pre-save timings 
        self.assertEqual(self.timing_list, self.sub_editor.sub_timings())

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
        print dir(sub_lang.version())
        self.assertTrue(True, sub_lang.subtitles_complete)
        video_language_pg = video_language_page.VideoLanguagePage(self)
        video_language_pg.open_video_lang_page(self.test_video.video_id, 'en')
        print sub_lang.is_complete_and_synced()
        self.assertEqual(6, sub_lang.get_subtitle_count())
       

    def test_submit__incomplete(self):
        """Manually entered are submitted, but not marked complete.

        """
        self.sub_editor.submit(complete=False)
        sub_lang = self.test_video.subtitle_language('en')
        self.assertEqual(False, sub_lang.subtitles_complete)
        self.assertEqual(6, sub_lang.get_subtitle_count())



            

        

