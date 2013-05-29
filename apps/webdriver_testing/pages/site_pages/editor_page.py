#!/usr/bin/env python

import time

from apps.webdriver_testing.pages.site_pages import UnisubsPage


class EditorPage(UnisubsPage):
    """
     This is the NEW subtitle editor.
    """

    _URL = "subtitles/editor/{0}/{1}/"  # (video_id, lang_code)

    _EXIT = 'a.discard'

    #EXIT MODAL
    _BACK_TO_FULL = 'button.yes'
    _EXIT_BUTTON = 'button.no'
    _WAIT = 'button.last-chance'

    _SAVE = 'a.save'
    #SAVE ERROR MODAL
    _SAVE_ERROR = 'div.modal div h1'
    _SAVE_ERROR_TEXT = ("There was an error saving your subtitles. You'll "
                        "need to copy and save your subtitles below, and "
                        "upload them to the system later.")
    _SAVE_SUBS = 'div.download textarea'
    _CLOSE = 'button.no'

    #LEFT COLUMN
    _HELP_KEYS = 'div.help-panel ul li span.key'
    _FEEDBACK = 'div.preview a'
    _REFERENCE_SELECT = "div.language-selections div select[name='language']"
    _VERSION_SELECT = "div.language-selections select[name='version']"
    _REF_SUB_ITEM = 'div.reference ul li.subtitle-list-item'
    _SUB_TIME = 'span.start-time'
    _SUB_TEXT = 'span.subtitle-text'
     

    #CENTER COLUMN
    _VIDEO_TITLE = "section.video span.video-title"
    _VIDEO_LANG = "section.video span.subtitles-language"

    _EMBEDDED_VIDEO = "div#video"
    _VIDEO_SUBTITLE = 'div.amara-popcorn-subtitles div'
    _WORKING_LANGUAGE = 'section.center div.subtitles-language'

    #SUBTITLES
    _REFERENCE_LIST = ('div.reference ul[subtitle-list='
                       '"reference-subtitle-set"]')
    _WORKING_LIST = 'div.reference ul#working-subtitle-set'
    _SUBTITLE_ITEM = 'li.subtitle-list-item'
    _SUB_TIME = 'span.start-time'
    _SUB_TEXT = 'span.subtitle-text'



    def open_editor_page(self, video_id, lang):
        self.open_page(self._URL.format(video_id, lang))

    def keyboard_controls_help(self):
        pass

    def feedback_link(self):
        pass

    def default_ref_language(self):
        return self.get_element_attribute(self._REFERENCE_SELECT, 
                                        'initial-language-code')

    def default_ref_version(self):
        return self.get_element_attribute(self._REFERENCE_SELECT, 
                                        'initial-version-number')

    def selected_ref_language(self):
        return self.get_text_by_css(self._REFERENCE_SELECT + (' option'
                                    '[selected="selected"]'))

    def selected_ref_version(self):
        return self.get_text_by_css(self._VERSION_SELECT + (' option'
                                    '[selected="selected"]'))

    def select_ref_language(self, language):
        self.select_option_by_text(self._REFERENCE_SELECT, language)
        time.sleep(2)

    def select_ref_version(self, version_no):
        self.select_option_by_text(self._VERSION_SELECT, version_no)

    def sub_overlayed_text(self):
        self.wait_for_element_present(self._VIDEO_SUBTITLE, wait_time=20)
        return self.get_text_by_css(self._VIDEO_SUBTITLE)

    def save_disabled(self):
        return ('disabled' in self.get_element_attribute(self._SAVE, 'class'))

    def reference_text(self):
        els = self.get_elements_list(' '.join([self._REFERENCE_LIST, 
                                                 self._SUB_TEXT]))
        subs = []
        for el in els:
            subs.append(el.text)
        return subs

    def working_text(self, position=None):
        els = self.get_elements_list(' '.join([self._WORKING_LIST, 
                                                 self._SUB_TEXT]))
        subs = []
        for el in els:
            subs.append(el.text)
        if position:
            return subs[position]
        else:
            return subs


    def click_working_sub_line(self, position):
        els = self.get_elements_list(' '.join([self._WORKING_LIST, 
                                                 self._SUB_TEXT]))
        sub_text = els[position].text
        els[position].click()
        return sub_text

        
           


   
