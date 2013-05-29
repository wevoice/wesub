#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from apps.videos.models import Video

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.pages.site_pages import video_page
from apps.webdriver_testing.pages.site_pages import editor_page
from apps.webdriver_testing.pages.editor_pages import dialogs
from apps.webdriver_testing.pages.editor_pages import unisubs_menu
from apps.webdriver_testing.data_factories import UserFactory



class TestCaseEntryExit(WebdriverTestCase):
    """Entry and Exit points to New Editor. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseEntryExit, cls).setUpClass()

        cls.create_modal = dialogs.CreateLanguageSelection(cls)
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)
        cls.unisubs_menu = unisubs_menu.UnisubsMenu(cls)


    def test_open_via_url(self):
        self.skipTest('incomplete')


       
