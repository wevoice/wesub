# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from nose.tools import assert_true
from apps.webdriver_testing.site_pages import js_test_page
from apps.webdriver_testing.webdriver_base import WebdriverTestCase


class TestCaseJavascriptUnittest(WebdriverTestCase):
    def setUp(self):
        self.skipTest("These tests are old and not maintained.")
        WebdriverTestCase.setUp(self)
        self.jstest_pg = js_test_page.JsTestPage(self)

    def test_javascript_unittest(self):
        self.jstest_pg.open_js_page()
        self.jstest_pg.click_start()
        assert_true(0 == self.jstest_pg.num_failed_tests())
