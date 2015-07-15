from externalsites.syncing import youtube
from subtitles import pipeline
from utils.factories import *
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages import video_language_page
from webdriver_testing.pages.site_pages import video_page


class TestCaseUserSyncing(WebdriverTestCase):
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseUserSyncing, cls).setUpClass()
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.vid_owner = UserFactory()
        cls.account = YouTubeAccountFactory(user=cls.vid_owner,
                                            channel_id='test-channel-id')
        cls.video = YouTubeVideoFactory()
        version = pipeline.add_subtitles(cls.video, 'en', SubtitleSetFactory())
        cls.language = version.subtitle_language
        cls.video_url = cls.video.get_primary_videourl_obj()

    def setUp(self):
        self.video_pg.open_video_page(self.video.video_id)

    def test_sync_permissions(self):
        """Only site admin sees sync history tab for user videos."""
        admin = UserFactory(is_staff=True, is_superuser=True)
        self.video_pg.log_in(self.vid_owner.username, 'password') 
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertNotIn('Sync History', self.video_lang_pg.visible_tabs())

        self.video_pg.log_in(admin.username, 'password') 
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertIn('Sync History', self.video_lang_pg.visible_tabs())

    def test_linked_urls(self):
        """Resync button active for linked urls only."""
        admin = UserFactory(is_staff=True, is_superuser=True)
        self.video_pg.log_in(admin.username, 'password') 
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.video_lang_pg.open_sync_history()
        self.assertTrue(self.video_lang_pg.has_resync())




