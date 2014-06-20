#!/usr/bin/env python

from webdriver_testing.pages.site_pages import UnisubsPage

class IntegrationsPage(UnisubsPage):
    """
    Accounts page for external integrations
    """
    _URL = "teams/%s/settings/accounts"

    #FEED DETAILS

    def open_integrations_page(self, team):
        self.logger.info('Opening the team %s integrations' % team)
        self.open_page(self._URL % team)

