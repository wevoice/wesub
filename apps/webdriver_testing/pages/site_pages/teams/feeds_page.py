#!/usr/bin/env python

from webdriver_testing.pages.site_pages import UnisubsPage


class FeedsPage(UnisubsPage):
    """
     Feed Page for adding video feeds to teams
    """

    _URL = "teams/%s/feeds"
    _DETAILS_URL = "teams/{0}/feeds/{1}"
    _ADD_FEED_LINK = ""

    _FEED_LISTING = ".feeds li"
    _FEED_URL = "a h3"


    #FEED DETAILS
    _VIDEO_THUMBS = "li.video a img"

    def open_feeds_page(self, team):
        self.logger.info('Opening the team %s feeds' % team)
        self.open_page(self._URL % team)

    def open_feed_details(self, team, feed_id):
        self.logger.info('Opening the feed details')
        self.open_page(self._DETAILS_URL.format(team, feed_id))
 
    def num_videos(self):
        self.logger.info('Getting the number of videos on the page')
        video_els = self.browser.find_elements_by_css_selector(self._VIDEO_THUMBS)
        return len(video_els)


