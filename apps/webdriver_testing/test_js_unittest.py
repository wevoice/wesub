from nose.tools import assert_true, assert_false
from nose import with_setup

from webdriver_base import WebdriverTestCase 
from site_pages import js_test_page


class WebdriverTestCaseJavascriptUnittest(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.jstest_pg = js_test_page.JsTestPage(self)


    def test_javascript_unittest(self):
        self.jstest_pg.open_js_page() 
        self.jstest_pg.click_start()
        assert_true(0 == self.jstest_pg.num_failed_tests())
