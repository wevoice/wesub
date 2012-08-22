from nose.tools import assert_true, assert_false
from nose import with_setup

from webdriver_base import WebdriverTestCase 
from site_pages import watch_page
from site_pages import search_results_page
from testdata_factories import * 
from django.core.urlresolvers import reverse


class WebdriverTestCaseWatchPage(WebdriverTestCase):
    def _create_video_with_subs(self, videoURL=None):
        #ADD SOME VIDEOS with SUBS to test SEARCHING
        self.user = UserFactory.create(username='tester')
        video, created = Video.get_or_create_for_url(videoURL)
        self.client.login(**self.auth)
        data = {
            'language': 'en',
            'video_language': 'en',
            'video': video.pk,
            'draft': open('apps/videos/fixtures/test.srt'),
            'is_complete': True
            }
        self.client.post(reverse('videos:upload_subtitles'), data)
        return video

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.watch_pg = watch_page.WatchPage(self)
        self.results_pg = search_results_page.SearchResultsPage(self)
        self.watch_pg.open_watch_page()
        self.auth = dict(username='tester', password='password')
        self._create_video_with_subs(videoURL="http://www.youtube.com/watch?v=WqJineyEszo")


    def test_search__simple(self):
        test_text = 'X factor'
        self.watch_pg.open_watch_page()
        self.watch_pg.basic_search(test_text)
        assert_true(self.results_pg.page_heading_contains_search_term(test_text))   
        print self.watch_pg.current_url()
        assert_true(self.results_pg.search_has_results())

