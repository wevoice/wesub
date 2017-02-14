#!/usr/bin/env python

from webdriver_testing.pages.site_pages import UnisubsPage

class EditVideoPage(UnisubsPage):
    """Billing page, available only to is_superuser users.

    """

    _URL = "admin/videos/video/%s/"
    _META1 = 'select#id_meta_1_type'
    _META1_DATA = 'input#id_meta_1_content'

    def open_edit_video_page(self, video_id):
        self.open_page(self._URL % video_id)

    def add_speaker_name(self, speaker_data=None):
        self.select_option_by_text(self._META1, 'Speaker Name')
        self.submit_form_text_by_css(self._META1_DATA, speaker_data)
