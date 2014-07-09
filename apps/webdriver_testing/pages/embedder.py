#!/usr/bin/env python

import time

from selenium.common.exceptions import ElementNotVisibleException
from webdriver_testing.pages.site_pages import UnisubsPage

class Embedder(UnisubsPage):
    """
     This is the embedder
    """

    _CURRENT_LANGUAGE = "a.amara-current-language"
    _IMPROVE_MENU = "li.unisubs-subtitle-homepage a"
    _LANGUAGES = "ul#language-list-inside li a.language-item"
    _LOADING_GIF = "div img[src*='loading.gif']"
    _TRANSCRIPT_TOGGLE = "a.amara-transcript-button"
    _SUBTITLES_TOGGLE = "a.amara-subtitles-button"
    _TRANSCRIPT = "div.amara-transcript-body"
    _CURRENT_SUB = "div.amara-popcorn-subtitles div"


    def wait_for_embedder_load(self):
        self.wait_for_element_not_visible(self._LOADING_GIF)

    def available_languages(self):
        els = self.get_elements_list(self._LANGUAGES) 
        return [e.text for e in els]

    def loading_gif(self):
        return self.is_element_visible(self._LOADING_GIF)


