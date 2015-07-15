#!/usr/bin/env python

import time
from webdriver_testing.pages.site_pages import UnisubsPage


class FailedSyncPage(UnisubsPage):
    """
     Feed Page for adding video feeds to teams
    """

    _URL = "teams/%s/settings/sync"
    _USER_URL = "profiles/sync/"
    _RESYNC_BOX = "td.box input"
    _SUBMIT = "input[value='Resync selected items']"

    def open_failed_sync_page(self, team):
        self.logger.info('Opening the sync failures page')
        self.open_page(self._URL % team)

    def open_user_sync_page(self):
        self.open_page(self._USER_URL)

    def resync_count(self):
        
        self.wait_for_element_present(self._RESYNC_BOX)
        els = self.get_elements_list(self._RESYNC_BOX)
        return len(els)

    def submit_for_resync(self):
        """Check failed items for resync"""
        self.wait_for_element_present(self._RESYNC_BOX)
        els = self.get_elements_list(self._RESYNC_BOX)
        for el in els:
            el.click()
        self.click_by_css(self._SUBMIT)
