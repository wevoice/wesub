# -*- coding: utf-8 -*-
import time
from nose.tools import assert_true, assert_false
from webdriver_base import WebdriverTestCase 
from site_pages import offsite_page

class WebdriverTestCaseOffsiteWidget(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.offsite_pg = offsite_page.OffsitePage(self)

    def test_search__nytimes_widget(self):
        url = "pagedemo/nytimes_youtube_embed"
        self.offsite_pg.open_page(url)
        self.offsite_pg.start_playback("0")
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()

    def test_search__hkhan_widgetizer(self):
        url = "pagedemo/khan_widgetizer"
        self.offsite_pg.open_page(url)
        self.offsite_pg.start_playback("0")
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()


#        | pagedemo/blog_youtube_embed | 0 |
#        | pagedemo/gapminder | 0 |
