#!/usr/bin/env python

from apps.webdriver_testing.page import Page

class UnisubsMenu(Page):

    #LANGUAGE DISPLAY OPTIONS
    _MENU = 'span.unisubs-tabTextchoose'
    _SUBTITLES_OFF = 'div.unisubs-languageList li'
    _LANG_LIST = 'div.unisubs-languageList'
    _LANG_TITLE = '.unisubs-languageTitle'
    _ACTIVE_LANG = 'li.unisubs-activeLanguage span.unisubs-languageTitle'

    #ACTIONS
    _NEW_TRANSLATION = '.unisubs-addTranslation a'
    _IMPROVE_SUBS = '.unisubs-improveSubtitles a'
    _SUB_HOMEPAGE = '.unisubs-subtitleHomepage a'
    #_EMBED_CODE = ''  #Just links to homepage - not useful.
    _DOWNLOAD_SUBTITLES = '.unisubs-downloadSubtitles a'

    #CURRENT USER SETTINGS 
    _USER_PAGE = '%s'    #visible text link - provide username
    _LOGOUT = 'Logout'   #visible text link
    _LANG_PREFERENCES = '.unisubs-languagePreferences'



    def _visible_menu_text(self):
        """Return the text displayed for the Subs menu.

        """
        self.wait_for_element_present(self._MENU)
        return self.get_text_by_css(self._MENU)

    def _available_languages(self):
        """Return a list of available languages in the menu.

        """
        language_list = []
        elements = self.browser.find_elements_by_css_selector(
            self._LANG_LIST)
        for el in elements():
            lang = el.find_element_by_css(self._LANG_TITLE).text
            language_list.append(lang)
        return language_list

    def _language_status(self, language):
        """Return the displayed status for the language.

        """
        elements = self.browser.find_elements_by_css_selector(
            self._LANG_TITLE)
        for el in elements():
            if el.text == language:
                parent = el.parent()
                status = parent.find_element_by_css_selector(
                    self._LANG_STATUS).text
                return status

    def _language_element(self, language):
        """Return the webdriver object for the language element.

        """
        elements = self.browser.find_elements_by_css_selector(
            self._LANG_TITLE)
        for el in elements():
            if el.text == language:
                return el

    def select_language(self, language):
        """Choose a language from the subs menu.

        """
        self._language_element(language).click()
 

    def open_menu(self):
        """Click the Subs menu to open it.

        """
        self.wait_for_element_present(self._MENU)
        self.click_by_css(self._MENU)

    def improve_subtitles(self):
        self.open_menu()
        self.click_by_css(self._IMPROVE_SUBS)


 
    def open_subtitle_homepage(self):
        """Open the subtitle homepage.

        """
        self.open_menu()
        self.click_by_css(self._SUB_HOMEPAGE) 

    
    def download_subtitles_url(self, language):
        """Returns the download url of the specified language.

        """
        if self._visible_menu_text is not language:
            self.open_menu()
            self.select_language(language)
        self.open_menu()
        return self.get_element_attribute(self._DOWNLOAD_SUBTITLES, 'href')


             
