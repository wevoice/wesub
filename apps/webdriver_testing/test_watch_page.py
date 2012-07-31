# -*- coding: utf-8 -*-

from nose.tools import assert_true, assert_false
from nose import with_setup

from webdriver_base import WebdriverTestCase 
from site_pages import watch_page
from site_pages import search_results_page
from testdata_factories import VideoFactory

class WebdriverTestCaseWatchPage(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.watch_pg = watch_page.WatchPage(self)
        self.results_pg = search_results_page.SearchResultsPage(self)
        self.watch_pg.open_watch_page() 

    def test_search__single_quote(self):
        test_text = "X factor"
        video1 = VideoFactory.create(title=test_text)
        self.watch_pg.basic_search(test_text) 
        assert_true(self.results_pg.search_has_results())
        assert_true(self.results_pg.page_heading_contains_search_term(search))   

#CREATE MORE TESTS HERE WITH DATA VARIATIONS
test_data = """
        | monkey |
        | I'd like to be under the sea |
        | Selbst wenn du das letzte Herbstblatt bist, das vom Baum hängt |
        | 我们开始通用字幕，因为我们相信 |
        """
 
