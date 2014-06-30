from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages import watch_page
from webdriver_testing.data_factories import UserFactory 
from webdriver_testing import data_helpers
from django.core import management
import datetime


class TestCaseLogin(WebdriverTestCase):
    """TestSuite for site video searches.

    """

    def setUp(self):
        WebdriverTestCase.setUp(self)

    def test_login__site(self):
        """Open the site.

        """
        pass
        #self.watch_pg.open_watch_page()
         
        
