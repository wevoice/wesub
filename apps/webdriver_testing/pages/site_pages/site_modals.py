#!/usr/bin/env python
import time
from apps.webdriver_testing.pages.site_pages import UnisubsPage

class SiteModals(UnisubsPage):
    """Modal dialogs on site.

    """

    _PRIMARY_AUDIO = "tr.with-help td select"
    _LANGUAGE = "select#id_subtitle_language_code"
    _CLOSE = ".close"


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
            self.click_by_css(self._PRIMARY_AUDIO)
            self.select_option_by_text(self._PRIMARY_AUDIO, audio)

        self.click_continue() 
        
