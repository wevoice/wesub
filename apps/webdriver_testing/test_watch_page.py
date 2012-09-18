from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import watch_page
from apps.webdriver_testing.site_pages import search_results_page
from apps.webdriver_testing.data_factories import UserFactory 
from apps.webdriver_testing.data_helpers import create_video_with_subs

class WebdriverTestCaseWatchPage(WebdriverTestCase):
    """TestSuite for site video searches.

    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.watch_pg = watch_page.WatchPage(self)
        self.results_pg = search_results_page.SearchResultsPage(self)
        self.watch_pg.open_watch_page()
        self.user = UserFactory.create(username='tester')
        self.auth = dict(username='tester', password='password')
        self.client.login(**self.auth)
        create_video_with_subs(self, 
            video_url = "http://www.youtube.com/watch?v=WqJineyEszo")

    def test_search__simple(self):
        """Search for text contained in video title.

        """
        test_text = 'X factor'
        self.watch_pg.open_watch_page()
        self.watch_pg.basic_search(test_text)
        self.assertTrue(
            self.results_pg.page_heading_contains_search_term(test_text),
                    ("Won't work until https://unisubs.sifterapp.com/issue/"
                    "1496 is fixed. ")
        )
        self.assertTrue(self.results_pg.search_has_results())
