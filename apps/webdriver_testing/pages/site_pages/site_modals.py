#!/usr/bin/env python

from webdriver_testing.pages.site_pages import UnisubsPage
import time

class SiteModals(UnisubsPage):
    """Modal dialogs on site.

    """

    _PRIMARY_AUDIO = "tr.with-help td select"
    _LANGUAGE = "select#id_subtitle_language_code"
    _CLOSE = ".close"
    _SELECT_LANGUAGE = "div#language_modal"
    _SUBMIT = "button.submit_button"

    def click_continue(self):
        button_els = self.browser.find_elements_by_css_selector("button")
        for el in button_els:
            if 'Continue' in el.text:
                el.click()
                return
        else:
            self.logger.info('continue button not found')

    def add_language(self, language, audio=None): 
        """Choose the subtitle language, and set primary audio if specified.

        """
        self.select_option_by_text(self._LANGUAGE, language)
        if audio:
            #self.click_by_css(self._PRIMARY_AUDIO)
            self.select_option_by_text(self._PRIMARY_AUDIO, audio)
        self.click_continue() 

    def select_spoken_languages(self, languages):
        for x in range(0, len(languages)):
            sel_field = "select#id_language%d" % (x+1)
            self.select_option_by_text(sel_field, languages[x])
        self.click_by_css(self._SUBMIT)
        time.sleep(2)
