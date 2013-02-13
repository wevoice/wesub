#!/usr/bin/env python
import time
from video_listings import VideoListings
from video_page import VideoPage


class SearchResultsPage(VideoListings):
    """
     Unisubs page contains common web elements found across
     all Universal Subtitles pages. Every new page class is derived from
     UnisubsPage so that every child class can have access to common web
     elements and methods that pertain to those elements.
    """

    _PAGE_HEADING = "h2.search-header"
    _NO_RESULTS = "ul.video_list p"
    _SEARCHING_INDICATOR = "img.placeholder"
    _SORT_HEADING = "div#sidebar h2"
    _LANGUAGES_SORT = "div#sidebar ul li a[value=languages_count]"
    _VIEWS_TODAY_SORT = "div#sidebar ul li a[value=today_views]"
    _VIEWS_WEEK_SORT = "div#sidebar ul li a[value=week_views]"
    _VIEWS_MONTH_SORT = "div#sidebar ul li a[value=month_views]"
    _VIEWS_TOTAL_SORT = "div#sidebar ul li a[value=total_views]"
    _FIRST_SEARCH_RESULT = "ul.video_list li a"

    def search_has_no_results(self):
        time.sleep(5)
        self.wait_for_element_not_visible(self._SEARCHING_INDICATOR)
        if self.is_text_present(self._NO_RESULTS, "No videos found ..."):
            return True
        else:
            return False

    def search_has_results(self):
        self.wait_for_element_not_visible(self._SEARCHING_INDICATOR)
        if self.wait_for_element_present(self._FIRST_SEARCH_RESULT, wait_time=10):
            return True

    def click_search_result(self, result_element):
        self.click_by_css(result_element)
        return VideoPage(self.testcase)

    def click_first_search_result(self):
        self.click_by_css(self._FIRST_SEARCH_RESULT)
        return VideoPage(self.testcase)

    def sort_results(self, sort_by):
        pass

    def filter_original_languages(self, lang_code):
        pass

    def filter_translated_languages(self, lang_code):
        pass

    def page_heading_contains_search_term(self, search):
        self.wait_for_element_not_visible(self._SEARCHING_INDICATOR)
        self.wait_for_element_present(self._PAGE_HEADING)
        if search in self.get_text_by_css(self._PAGE_HEADING):
            return True

        
