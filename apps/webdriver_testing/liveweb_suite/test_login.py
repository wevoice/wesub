from setup_base import WebdriverRemote
from ..site_pages.unisubs_page import UnisubsPage


class TestLogin(WebdriverRemote):
    """TestSuite for site video searches.

    """
    def setUp(self):
        WebdriverRemote.setUp(self)
        self.unisubs_pg = UnisubsPage(self)

    def test_login__site(self):
        """Open the site and login as site user.

        """
        self.unisubs_pg.open_page('')
        self.unisubs_pg.log_in('sub_writer', 'sub.writer')

