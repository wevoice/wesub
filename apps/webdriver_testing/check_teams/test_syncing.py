from externalsites.models import KalturaAccount
from subtitles import pipeline
from utils.factories import *
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages import video_language_page
from webdriver_testing.pages.site_pages import video_page


class TestCaseTeamSyncing(WebdriverTestCase):
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseTeamSyncing, cls).setUpClass()
        cls.admin = UserFactory()
        cls.manager = UserFactory()
        cls.member = UserFactory()
        cls.team = TeamFactory(admin=cls.admin,
                               manager=cls.manager,
                               member=cls.member)

        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.video = KalturaVideoFactory(name='video')
        TeamVideoFactory(video=cls.video, team=cls.team)
        cls.account = KalturaAccount.objects.create(
            team=cls.team, partner_id=1234, secret='abcd')
        version = pipeline.add_subtitles(cls.video, 'en', SubtitleSetFactory())
        cls.language = version.subtitle_language
        cls.video_url = cls.video.get_primary_videourl_obj()

    def setUp(self):
        self.video_pg.open_video_page(self.video.video_id)

    def test_sync_permissions(self):

        staff = UserFactory(is_staff=True, is_superuser=True)
        """Only site admin sees sync history tab for user videos."""
        self.video_pg.log_in(self.member.username, 'password') 
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertNotIn('Sync History', self.video_lang_pg.visible_tabs())

        self.video_pg.log_in(self.manager.username, 'password') 
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertNotIn('Sync History', self.video_lang_pg.visible_tabs())

        self.video_pg.log_in(staff.username, 'password') 
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertIn('Sync History', self.video_lang_pg.visible_tabs())

        self.video_pg.log_in(self.admin.username, 'password') 
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertIn('Sync History', self.video_lang_pg.visible_tabs())

    def test_linked_urls(self):
        """Resync button active for linked urls only."""
        self.video_pg.log_in(self.admin.username, 'password') 
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.video_lang_pg.open_sync_history()
        self.assertTrue(self.video_lang_pg.has_resync())




