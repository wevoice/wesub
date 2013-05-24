#!/usr/bin/env python

from apps.webdriver_testing.pages.site_pages import UnisubsPage


class EditorPage(UnisubsPage):
    """
     This is the NEW subtitle editor.
    """

    _URL = "subtitles/editor/{0}/{1}/"  # (video_id, lang_code)
    _VIDEO_TITLE = "span.video-title"
    _VIDEO_LANG = "span.subtitles-language"

    #LEFT COLUMN


    #CENTER COLUMN
    _EMBEDDED_VIDEO = "div#video"
    _VIDEO_SUBTITLE = 'div.amara-popcorn-subtitles div'

    #RIGHT COLUMN


    def open_editor_page(self, video_id, lang):
        self.open_page(self._URL.format(video_id, lang))

