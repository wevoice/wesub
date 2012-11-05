#!/usr/bin/env python

from video_page import VideoPage


class VideoLanguagePage(VideoPage):
    """
     Video Page contains the common elements in the video page.
    """

    _URL = "videos/{0}/{1}/"  # format(video id, language code) 
    _VIDEO_TITLE = "li.title"
    _VIDEO_DESCRIPTION  = "li.description"
    _SUB_LINES = "div.translation-text p"

    #SUBTITLES TAB
    _EDIT_SUBTITLES = "a#edit_subtitles_button"
    _DOWNLOAD_SUBS = "span.sort_label strong"

    def open_video_lang_page(self, video_id, lang_code):
        self.open_page(self._URL.format(video_id, lang_code))

    def edit_subtitles(self):
        self.click_by_css(self._EDIT_SUBTITLES)

    def displayed_lines(self):
        displayed_subtitles = []
        line_elements = self.browser.find_elements_by_css_selector(
            self._SUB_LINES)
        for el in line_elements:
            #html_text = el.text
            #sublist = html_text.split('\n')
            #temp = [i for i in sublist if "<br>" not in i]
            #displayed_subtitles.append(" ".join(temp))
            displayed_subtitles.append(el.text)
        return displayed_subtitles


    def download_subtitles(self, output_format):
        """This probably won't work with selenium. Can't download.

        Be better to get the link and download it from the system, and verify
        or just make sure the link is created correct and doesn't return a 404
        """
        self.click_by_css(self._DOWNLOAD_SUBS)
        self.click_link_text(output_format)

