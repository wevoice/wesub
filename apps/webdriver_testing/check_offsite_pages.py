import time
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages import offsite_page
from apps.webdriver_testing.data_factories import UserFactory 
from apps.webdriver_testing.pages.site_pages import UnisubsPage
from apps.webdriver_testing.data_helpers import create_video_with_subs


class TestCaseOffsiteWidget(WebdriverTestCase):
    """Test suite for the widget demo pages.

    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.offsite_pg = offsite_page.OffsitePage(self)
        self.user = UserFactory.create()
        self.unisubs_pg = UnisubsPage(self)
        self.unisubs_pg.log_in(username=self.user.username, passw='password')

    def test_widget__nytimes(self):
        """Verify subs display on ny times demo page.

        """
        url = "pagedemo/nytimes_youtube_embed"
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()

    def test_widget__youtube(self):
        """Verify subs display on amara blog with youtube page.

        """

        url = "pagedemo/blog_youtube_embed"
        create_video_with_subs(self, video_url=
                           'http://www.youtube.com/watch?v=-RSjbtJHi_Q')
        time.sleep(10)
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()

    def test_widget__gapminder(self):
        """Verify subs display on gapminder page.

        """

        url = "pagedemo/gapminder"
        create_video_with_subs(self, 
            video_url='http://www.youtube.com/watch?v=jbkSRLYSojo')
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()

    def test_widget__aljazeera(self):
        """Verify subs display on al jazeera page.

        """
        url = "pagedemo/aljazeera_blog"
        create_video_with_subs(self, 
            video_url='http://www.youtube.com/watch?v=Oraas1O7DIc')
        self.offsite_pg.open_offsite_page(url)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()

    def test_widget__boingboing(self):
        """Verify subs display on boing boing page.

        """
        url = "pagedemo/boingboing_embed"
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()


class TestCaseOffsiteWidgetizer(WebdriverTestCase):
    """Test suite for the widgetizer demo pages.

    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.offsite_pg = offsite_page.OffsitePage(self)
        self.auth = dict(username='tester', password='password')

    def test_widgetizer__khan(self):
        """Verify subs display on khan widgetizer demo page.

        """

        url = "pagedemo/khan_widgetizer"
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()

    def test_widgetizer__boingboing(self):
        """Verify subs display on boing-boing widgetizer demo page.

        """
        self.skipTest("Boing-Boing pages don't load. ")
        url = "pagedemo/boingboing_widgetizer"
        self.offsite_pg.open_page(url)
        time.sleep(5)
        self.offsite_pg.start_playback(0)
        self.offsite_pg.pause_playback_when_subs_appear(0)
        self.offsite_pg.displays_subs_in_correct_position()
