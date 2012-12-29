#!/usr/bin/env python
from apps.webdriver_testing.pages.site_pages.teams import ATeamPage
import time

class DashboardTab(ATeamPage):
    """Actions for the dashboard tab of a Team Page.

    """
    _URL = 'teams/%s/'
    _VIDEO = 'ul.listing.videos li'
    _VIDEO_TITLE = 'div.thumb h4 a'
    _VIDEO_LANGS = 'div.langs a'
    _SHOW_LANGS = 'div.langs div span.expand'
    _LANG_LIST = 'div.langs div ul li a'


    _NO_VIDEOS_TEXT = "Sorry, we couldn't find any videos for you." 
    _LANGUAGE_SUGGESTION = 'ul.suggestions li a#lang_select_btn'
    _BROWSE_SUGGESTION = 'ul.suggestions li a[href*="/videos/"]'
    _ADD_SUGGESTION = 'ul.suggestions li a[href*="/add/video/"]'



    # Suggestion helpers when no videos are present
    def suggestion_present(self, suggestion_type):
        suggest_css = '_'.join(['', suggestion_type.upper(), 'SUGGESTION'])
        if self.is_element_visible(suggest_css):
            return True

    def click_suggestion(self, suggestion_type):
        suggest_css = '_'.join(['', suggestion_type.upper(), 'SUGGESTION'])
        self.click_by_css(suggest_css)
    
    def no_videos_found(self):
        if self.is_text_visible(self._NO_VIDEOS_TEXT):
            return True

    def _video_element(self, video):
        """Return the webdriver object for a video based on the title.

        """
        time.sleep(2)  #Make sure all the vids have a chance to load.
        video_els = self.browser.find_elements_by_css_selector(
                      self._VIDEO)

        for el in video_els:
            try:
                title_el = el.find_element_by_css_selector(self._VIDEO_TITLE)
                print title_el.text
                if video in title_el.text:
                    return el
            except:
                continue

    def languages_needed(self, video):
        langs_needed = []
        video_el = self._video_element(video)
        lang_el = video_el.find_element_by_css_selector(
                self._VIDEO_LANGS)
        if 'languages need your help' in lang_el.text:
            show_el = video_el.find_element_by_css_selector(self._SHOW_LANGS)
            show_el.click()
            lang_list = video_el.find_elements_by_css_selector(
                self._LANG_LIST)
            for el in lang_list:
                langs_needed.append(el.text)
        else:
            langs_needed.append(lang_el.text)
        return langs_needed







        
