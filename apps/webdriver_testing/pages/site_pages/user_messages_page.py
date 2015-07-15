#!/usr/bin/env python

from webdriver_testing.pages.site_pages import UnisubsPage


class UserMessagesPage(UnisubsPage):
    """
     Search page is the main search page stub.  Watch Page and Search Results page
    """

    _URL = "messages/"
    _MESSAGE = 'li.message p:nth-child(3)'
    _MESSAGE_SUBJECT = 'li.message h3'
    _MESSAGE_FROM = 'li.message p:nth-child(2) a'
    _NO_MESSAGES = 'p.empty'

    #SENT MESSAGES


    def open_messages(self):
        self.open_page(self._URL)

    def open_sent_messages(self):
        self.open_page(self._URL+'sent/')

    def message_text(self):
        return self.get_text_by_css(self._MESSAGE)

    def message_subject(self):
        return self.get_text_by_css(self._MESSAGE_SUBJECT)

    def message_from(self):
        return self.get_text_by_css(self._MESSAGE_FROM)

    def no_messages(self):
        return self.get_text_by_css(self._NO_MESSAGES)

