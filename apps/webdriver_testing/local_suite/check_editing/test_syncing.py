#!/usr/bin/python
# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.site_pages import video_page
from apps.webdriver_testing.editor_pages import dialogs
from apps.webdriver_testing.editor_pages import unisubs_menu
from apps.webdriver_testing.editor_pages import subtitle_editor 
from apps.webdriver_testing.data_factories import UserFactory
import os
import time

class TestCasePartialSync(WebdriverTestCase):
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
            'http://www.youtube.com/watch?v=jbgWSF65aE0')

        #Open the video page and sync the first 3 subs
        num_synced_subs = 3
        self.video_pg.open_video_page(self.test_video.video_id)
        self.video_pg.add_subtitles()
        self.create_modal.create_original_subs('English', 'English')
        self.create_modal.continue_past_help()
        self.typed_subs = self.sub_editor.type_subs()
        self.sub_editor.continue_to_next_step()
        self.sub_editor.sync_subs(num_synced_subs)


    def test_display__normal(self):
        """Manually entered unsynced subs display in editor.

        """

        timing_list = self.sub_editor.sub_timings()
        print timing_list
        #Verify synced subs are increasing
        self.assertGreater(float(timing_list[1]), float(timing_list[0]))
        #Verify last sub is blank
        self.assertEqual(timing_list[-1], '')

       
    def test_save(self):
        """Manually entered unsynced subs are saved upon save and exit.
        
        """
        timing_list = self.sub_editor.sub_timings()
        curr_url = self.sub_editor.current_url()
        self.sub_editor.save_and_exit()
        self.sub_editor.open_page(curr_url)
        self.sub_editor.continue_to_next_step()
        #Verify sub timings are same as pre-save timings 
        self.assertEqual(timing_list, self.sub_editor.sub_timings())


    def test_close__abruptly(self):
        """Test subs are saved when browser closes abruptly.
      
        Note: the browser needs to be open for about 80 seconds for saving.
        """
        timing_list = self.sub_editor.sub_timings()
        print 'sleeping for 90 seconds to initiate automatic save'
        time.sleep(90)
        self.sub_editor.open_page("")
        self.sub_editor.handle_js_alert('accept')
        time.sleep(5)
        self.video_pg.open_video_page(self.test_video.video_id)
        self.unisubs_menu.open_menu()

        self.assertEqual(self.create_modal.warning_dialog_title(), 
            'Resume editing?')

        # Resume dialog - click OK
        self.create_modal.resume_dialog_ok()
 
        # Helper videos if exists click continue
        self.create_modal.continue_past_help()

        #Move to the syncing screen
        self.sub_editor.continue_to_next_step()

        #Verify sub timings are same as pre-save timings 
        self.assertEqual(timing_list, self.sub_editor.sub_timings())

    def test_download(self):
        """Manually entered unsynced subs can be download from check page.

        """
        timing_list = self.sub_editor.sub_timings()
        print timing_list
        #Past Sync
        self.sub_editor.continue_to_next_step()
        #Past Description
        self.sub_editor.continue_to_next_step()
        #In Check Step - download subtitles
        saved_subs = self.sub_editor.download_subtitles()
        print saved_subs
        #Verify timings are in the saved list
        time_check = timing_list[1].replace('.', ',')
        print time_check
        self.assertIn(time_check, saved_subs)
            

        

