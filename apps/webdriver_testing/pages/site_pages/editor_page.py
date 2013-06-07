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
    _VIDEO_SUBTITLE = 'div.subtitle-overlay div'
    _WORKING_LANGUAGE = 'section.center div.subtitles-language'
    _REMOVE_SUBTITLE = 'a.remove-subtitle'
    _ADD_SUBTITLE = 'a.add-subtitle'
    _SYNC_HELP = 'div.sync-help'
    _INFO_TRAY = 'div.info-tray'
    _INFO_DETAILS = 'div.info-tray tr td'
    _ADD_SUB_TO_END = 'a.end'

    #SUBTITLES
    _REFERENCE_LIST = ('div.reference ul[subtitle-list='
                       '"reference-subtitle-set"]')
    _WORKING_LIST = 'ul#working-subtitle-set'
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
        """return the value for the default reference language. """

        return self.get_element_attribute(self._REFERENCE_SELECT, 
                                        'initial-language-code')

    def default_ref_version(self):
        """Return the value for the default reference version. """

        return self.get_element_attribute(self._REFERENCE_SELECT, 
                                        'initial-version-number')

    def selected_ref_language(self):
        """Return the currently selected reference language. """

        return self.get_text_by_css(self._REFERENCE_SELECT + (' option'
                                    '[selected="selected"]'))

    def selected_ref_version(self):
        """Return the currently selected reference version number. """

        return self.get_text_by_css(self._VERSION_SELECT + (' option'
                                    '[selected="selected"]'))

    def select_ref_language(self, language):
        """Choose a reference language from the list. """

        self.select_option_by_text(self._REFERENCE_SELECT, language)
        time.sleep(2)

    def select_ref_version(self, version_no):
        """Choose a reference version from the list. """

        self.select_option_by_text(self._VERSION_SELECT, version_no)

    def sub_overlayed_text(self):
        """Return the text overlayed on the video. """

        self.wait_for_element_present(self._VIDEO_SUBTITLE, wait_time=20)
        return self.get_text_by_css(self._VIDEO_SUBTITLE)

    def save_disabled(self):
        """Return whether the Save button is disabled. """

        return ('disabled' in self.get_element_attribute(self._SAVE, 'class'))

    def reference_text(self):
        """Return the list of subtitles for the reference language."""
        els = self.get_elements_list(' '.join([self._REFERENCE_LIST, 
                                                 self._SUB_TEXT]))
        subs = []
        for el in els:
            subs.append(el.text)
        return subs


    def working_language(self):
        """Return the curren working language displayed. """

        return self.get_text_by_css(self._WORKING_LANGUAGE)

    def working_text(self, position=None):
        """Return the list of working subtitles. 

        If position is supplied, just return that line of text.
        """

        els = self.get_elements_list(' '.join([self._WORKING_LIST, 
                                               self._SUBTITLE_ITEM, 
                                               self._SUB_TEXT]))
        if position:
            return els[position].text
        else:
            subs = []
            for el in els:
                subs.append(el.text)
            return subs


    def video_title(self):
        """Return the text displayed for the video title. """

        return self.get_text_by_css(self._VIDEO_TITLE)

    def click_working_sub_line(self, position):
        """Click in a sublie of the working text. """

        els = self.get_elements_list(' '.join([self._WORKING_LIST, 
                                               self._SUBTITLE_ITEM]))

        try:
            subline = els[position].find_element_by_css_selector(self._SUB_TEXT)
        except:
            self.record_error('subtitle text element not found')

        sub_text = subline.text
        subline.click()
        return sub_text, els[position]

    def remove_active_subtitle(self, position):
        """Click on a subtitle and delete it. """

        removed_text, el = self.click_working_sub_line(position)
        try:
            rem = el.find_element_by_css_selector(self._REMOVE_SUBTITLE)
        except:
            self.record_error('remove button not found')
        rem.click()
        return removed_text

    def add_subs_to_the_end(self, subs):
        """Click Add subtitles at the end and add new lines"""
        
        self.browser.execute_script("window.location.hash='add-sub-at-end'")
        self.click_by_css(self._ADD_SUB_TO_END)
        for line in subs:
            els = self.browser.find_elements_by_css_selector(' '.join(
                    [self._WORKING_LIST, self._SUBTITLE_ITEM, 'textarea']))
            el = els[-1]
            el.send_keys(line + '\n')

    def exit_to_full_editor(self):
        """Click exit and return to the full editor. """

        self.click_by_css(self._EXIT)
        self.click_by_css(self._BACK_TO_FULL)

    def subtitle_info(self, position):
        """Return the info tray values of the selected subtitle. """
        
        self.click_working_sub_line(position)
        self.wait_for_element_visible(self._INFO_TRAY)
        fields = ['start', 'stop', 'char_count', 'char_rate']
        els = self.get_elements_list(self._INFO_DETAILS)
        values = []
        for el in els:
            values.append(el.text)
        return dict(zip(fields, values))
        

