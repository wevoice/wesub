#!/usr/bin/env python
from video_listings import VideoListings
from search_results_page import SearchResultsPage
import time

class WatchPage(VideoListings):
    """
     Unisubs page contains common web elements found across
     all Universal Subtitles pages. Every new page class is derived from
     UnisubsPage so that every child class can have access to common web
     elements and methods that pertain to those elements.
    """

    _URL = "videos/watch/"
    _SEARCH = "form.search-form div#watch_search input#id_q"
    _SEARCH_PULLDOWN = "a#advanced_search"
    _SEARCH_ORIG_LANG = "select#id_video_lang"
    _SEARCH_TRANS_LANG = "select#id_langs"
    _SEARCH_SUBMIT = "div#advanced_menu button"
    _VIDEO_SECTION = "div#%s_videos"
    _SECTION_VIDEOS = "div#%s_videos ul.video_list li.Video_list_item"  
    _MORE_VIDEOS = ".btn_more_videos"

    #Popular Sort
    _POPULAR_SORT = "a#popular_sort"
    _CURRENT_SORT = "span.current-sort"

    def open_watch_page(self):
        self.open_page(self._URL)

    def basic_search(self, search_term):
        self.logger.info('Searching for %s' %search_term)
        self.submit_form_text_by_css(self._SEARCH, search_term)
        return SearchResultsPage(self.testcase)

    def advanced_search(self, search_term=None, orig_lang=None, trans_lang=None):
        self.logger.info('Opening advanced search')
        self.click_by_css(self._SEARCH_PULLDOWN)
        if orig_lang:
            self.logger.info('specifying the orig lang to search')
            self.select_option_by_value(self._SEARCH_ORIG_LANG, orig_lang)
        if trans_lang:
            self.logger.info('specifying the translated language to search')
            self.select_option_by_value(self._SEARCH_TRANS_LANG, trans_lang)
               
        if search_term:
            self.logger.info('entering the search term %s' % search_term)
            self.submit_form_text_by_css(self._SEARCH, search_term)
        else:
            self.logger.info('submitting the search')
            elem = self.wait_for_element_present(self._SEARCH)
            elem.submit()

        return SearchResultsPage(self.testcase)

       
    def _valid_section_name(self, section):
        sections = ['popular', 'latest', 'featured']
        if section not in sections:
            raise ValueError('%s is not a valid section name')


    def section_empty(self, section):
        self.logger.info('Checking if %s section is empty' % section)
        self._valid_section_name(section)
        el = (self._VIDEO_SECTION + ' ' + p.empty) % section
        if self.is_element_present(el):
            return True

    def _videos_in_section(self, section):
        self._valid_section_name(section)
        section_css = self._SECTION_VIDEOS % section
        video_els = self.get_elements_list(section_css)
        return video_els


    def _video_list_item(self, title, section='latest'):
        """Return the element of video by title in the given section.

        """
        video_elements = self._videos_in_section(section)
        try:
            for el in video_elements:
                vid_title = el.find_element_by_css_selector("a").get_attribute(
                    'title')
                if title == vid_title:
                    return el
                else:
                    self.record_error("title %s not found on the page" % title)
        except Exception as e:
            self.record_error(e)

    def section_has_video(self, title, section='latest'):
        self.logger.info('Checking if %s section has videos' % section)
        if self._video_list_item(title, section):
            return True

    def section_videos(self, section):
        self.logger.info('Getting the titles from the %s section' % section)
        video_els = self._videos_in_section(section)
        title_list = []
        for el in video_els:
            vid_title = el.find_element_by_css_selector("a").get_attribute(
                    'title')
            title_list.append(vid_title)
        if 'About Amara' in title_list:
            title_list.remove('About Amara') #Video isn't always present in index.
        return title_list

    def display_more(self, section):
        self.logger.info('Clicking More for the %s section' % section)
        more_css = (self._VIDEO_SECTION + ' ' + self._MORE_VIDEOS) % section
        self.click_by_css(more_css)
        self.search_complete()

    def popular_current_sort(self):
        self.wait_for_element_present(self._CURRENT_SORT)
        return self.get_text_by_css(self._CURRENT_SORT)

    def popular_sort(self, sort_param):
        """Sort the popular videos by date parameter.

        valid values are: today, week, month, year, total.
        """
        self.logger.info('Sorting by %s' % sort_param)
        sort_el_css = "div#sort_menu ul li[val='%s']" % sort_param
        self.click_item_from_pulldown(self._CURRENT_SORT, sort_el_css)

    def popular_more_link(self):
        self.logger.info('Getting the url for the popular section More link')
        more_css = (self._VIDEO_SECTION + ' ' + self._MORE_VIDEOS) % 'popular'
        more_link = self.get_element_attribute(more_css, 'href')
        return more_link




        
    

        
        
