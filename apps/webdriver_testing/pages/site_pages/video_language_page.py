#!/usr/bin/env python

from video_page import VideoPage
import requests

class VideoLanguagePage(VideoPage):
    """
     Video Page contains the common elements in the video page.
    """

    _URL = "videos/{0}/{1}/"  # format(video id, language code) 
    _VIDEO_TITLE = "li.title"
    _VIDEO_DESCRIPTION  = "li.description"
    _SUB_LINES = "div.translation-text"

    #SUBTITLES TAB
    _EDIT_SUBTITLES = "a#edit_subtitles_button"
    _DOWNLOAD_SUBS = "span.sort_label strong"
    _DOWNLOAD_OPTION = "div.sort_button ul li" 

    def open_video_lang_page(self, video_id, lang_code):
        self.logger.info('Opening {0} page for video: {1}'.format(
                         lang_code, video_id))
        self.open_page(self._URL.format(video_id, lang_code))

    def edit_subtitles(self):
        self.logger.info('Clicking edit subtitles')
        self.click_by_css(self._EDIT_SUBTITLES)

    def displayed_lines(self):
        self.logger.info('Getting display lines of sub text')
        displayed_subtitles = []
        line_elements = self.get_elements_list(self._SUB_LINES)
        for el in line_elements:
            displayed_subtitles.append(el.text)
        return displayed_subtitles


    def download_link(self, output_format):
        """Return the download link for specified format.

        """
        self.logger.info('Locating the download link element for the format')
        self.click_by_css(self._DOWNLOAD_SUBS)
        self.wait_for_element_present(self._DOWNLOAD_OPTION)
        format_els = self.get_elements_list(self._DOWNLOAD_OPTION)
        for el in format_els:
            if el.text == output_format:
                return el.find_element_by_css_selector('a').get_attribute('href')
                break
        else:
            raise ValueError('Did not find the link for %s format' % output_format)

    def check_download_link(self, link):
        self.logger.info('Getting content and headers of dl link')
        r = requests.get(link)
        self.logger.info(r.content)
        return r.headers


