#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time 
from django.test import TestCase
from django.core import management
from videos.models import Video
from webdriver_testing.pages.site_pages import site_modals
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing import data_helpers
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing.pages.site_pages import editor_page
from utils.factories import * 
from subtitles import pipeline


class TestCaseTools(WebdriverTestCase):

    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseTools, cls).setUpClass()
        cls.modal = site_modals.SiteModals(cls)
        cls.data_utils = data_helpers.DataHelpers()
        cls.editor_pg = editor_page.EditorPage(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.user = UserFactory()
        cls.video_pg.open_page('auth/login/')
        cls.video_pg.log_in(cls.user.username, 'password')
        cls.video = VideoFactory(video_url='http://www.youtube.com/watch?v=5CKwCfLUwj4',
                                 title='Open Source Philosophy',
                                 #primary_audio_language_code='en'
                                 )
        cls.data_utils.add_subs(video=cls.video)
        langs = ['en', 'da', 'nl']

        for lc in langs:
            defaults = {
                        'video': cls.video,
                        'language_code': lc,
#                        'complete': True,
                        'visibility': 'public',
                        'committer': cls.user,
                        'subtitles': ('apps/webdriver_testing/subtitle_data/'
                                     'Open Source Philosophy.%s.dfxp' % lc)
                   }
            cls.data_utils.add_subs(**defaults)

        pipeline.add_subtitles(cls.video, 'hr', SubtitleSetFactory())
        hr = {
                    'video': cls.video,
                    'language_code': 'hr',
                    'visibility': 'public',
                    'committer': cls.user,
                    'subtitles': ('apps/webdriver_testing/subtitle_data/'
                                  'Untimed_text.txt')
                   }
        cls.data_utils.add_subs(**hr)
        management.call_command('update_index', interactive=False) 

    def tearDown(self):
        try:
            self.editor_pg.exit()
        except:
            pass

    def test_timings_present_for_new_translation(self):
        """New translation starts with lines and times. """

        self.video_pg.open_video_page(self.video.video_id)
        self.video_pg.add_subtitles()
        self.modal.add_language('Polish', audio='English')
        working_times = self.editor_pg.start_times()
        ref_times = self.editor_pg.reference_times()
        self.assertEqual(ref_times[:5], working_times[:5]) 
        self.assertEqual(len(ref_times), len(working_times))


    def test_copy_timings_to_untimed_text(self):
        """Copy timings to untimed text. """
        self.editor_pg.open_editor_page(self.video.video_id, 'nl')
        self.editor_pg.copy_timings()
        working_times = self.editor_pg.start_times()
        ref_times = self.editor_pg.reference_times()
        self.assertEqual(ref_times[:5], working_times[:5]) 


    def test_copy_timings_change_reference(self):
        """Change reference lang then copy timings. """
        self.editor_pg.open_editor_page(self.video.video_id, 'nl')
        self.editor_pg.select_ref_language('Danish')
        self.editor_pg.copy_timings()
        working_times = self.editor_pg.start_times()
        ref_times = self.editor_pg.reference_times()
        self.assertEqual(ref_times[:5], working_times[:5]) 

    def test_copy_timings_reference_unsynced(self):
        """No copy in menu if reference subs are unsynced. """
        self.editor_pg.open_ed_with_base(self.video.video_id, 'sv')
        time.sleep(2)
        self.editor_pg.select_ref_language('Croatian')
        time.sleep(3)
        self.assertEqual('Element not displayed', self.editor_pg.copy_timings())

    def test_remove_active_subtitle(self):
        """Remove the selected subtitle line.
        """
        self.editor_pg.open_editor_page(self.video.video_id, 'en')
        subtext = self.editor_pg.working_text()
        removed_text = self.editor_pg.remove_active_subtitle(3)
        self.assertEqual(subtext[2], removed_text)
        subtext = self.editor_pg.working_text()
        self.assertNotEqual(subtext[2], removed_text)


    def test_remove_shortcut(self):
        """Remove the selected subtitle line.
        """
        self.editor_pg.open_editor_page(self.video.video_id, 'en')
        subtext = self.editor_pg.working_text()
        removed_text = self.editor_pg.remove_active_subtitle(3, shortcut=True)
        self.assertEqual(subtext[2], removed_text)
        subtext = self.editor_pg.working_text()
        self.assertNotEqual(subtext[2], removed_text)

    def test_insert_subtitle(self):
        self.editor_pg.open_editor_page(self.video.video_id, 'en')
        starttext = self.editor_pg.working_text()
        self.editor_pg.insert_sub_above(3)
        newtext = self.editor_pg.working_text()
        self.assertGreater(len(newtext), len(starttext)) 

    def test_add_subtitle_note(self):
        """add a note with the subtitle start time""" 
        self.editor_pg.open_editor_page(self.video.video_id, 'en')
        self.editor_pg.insert_sub_note(3, 'this is the new timed note')
        note = self.editor_pg.current_notes()
        self.assertEqual(u'0:05.72\nthis is the new timed note', note)
         
