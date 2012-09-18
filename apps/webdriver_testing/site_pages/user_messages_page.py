#!/usr/bin/env python

from unisubs_page import UnisubsPage


class UserMessagesPage(UnisubsPage):
    """
     Search page is the main search page stub.  Watch Page and Search Results page
    """

    _URL = "messages/"
    _MESSAGE = 'li.message'

    def open_messages(self):
        self.open_page(self._URL)


    def message_text(self):
        return self.get_text_by_css(self._MESSAGE)
