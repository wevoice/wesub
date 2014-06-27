#!/usr/bin/env python

import time
from webdriver_testing.pages.site_pages import UnisubsPage


class AddFeedPage(UnisubsPage):
    """
     Feed Page for adding video feeds to teams
    """

    _INPUT_PREFOCUS = "input#submit_video_field.prefocus"
    _URL = "teams/add/videos/%s/"
    _SUBMIT = "button span"
    _YOUTUBE_USER_FIELD = "input#id_usernames"
    _YOUTUBE_PAGE_FIELD = "input#id_youtube_user_url"
    _FEED_URL = "input#id_feed_url"
    _SUBMIT_ERROR = "ul.errorlist li"

    def open_feed_page(self, team):
        self.logger.info('Opening the team %s add feed page' % team)
        self.open_page(self._URL % team)


    def submit_youtube_users_videos(self, youtube_usernames):
        """Submit 1 or several youtube user names.
        Type 1 or several youtube user names in hte Youtube usernames field.

        """
        self.logger.info('Submitting youtube users videos: '
                         '%s' %youtube_usernames)
        self.type_by_css(self._YOUTUBE_USER_FIELD, youtube_usernames)
        self.submit_by_css(self._SUBMIT)

    def submit_youtube_user_page(self, youtube_user_url):
        """Submit videos from youtube user page url.

        """
        self.logger.info('Submitting youtube user page %s' %youtube_user_url)
        self.type_by_css(self._YOUTUBE_PAGE_FIELD, youtube_user_url)
        self.submit_by_css(self._SUBMIT)

    def submit_feed_url(self, feed_url):
        """Submit videos from a supported feed type.

        """
        self.logger.info('Submitting the feed %s' % feed_url)
        self.type_by_css(self._FEED_URL, feed_url)
        self.submit_by_css(self._SUBMIT)

    def submit_successful(self):
        self.wait_for_element_present(self._SUCCESS_MESSAGE, wait_time=20)
        if self.is_text_present(self._SUCCESS_MESSAGE,
                                ("The videos are being added in the "
                                 "background. If you are logged in, you "
                                 "will receive a message when it's done")):
            return True
        else:
            self.logger.info(self.get_text_by_css(self._SUCCESS_MESSAGE))

    def submit_failed(self):
        if self.is_element_present(self._ERROR_MESSAGE):
            return True

    def submit_error(self):
        return self.get_text_by_css(self._SUBMIT_ERROR)
