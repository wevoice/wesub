import time
from externalsites.models import KalturaAccount, SyncHistory
from subtitles import pipeline
from utils.factories import *
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages import video_language_page
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing.pages.site_pages.teams import failed_sync_page

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
        cls.sync_pg = failed_sync_page.FailedSyncPage(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.account = KalturaAccount.objects.create(
            team=cls.team, partner_id=1492321, secret='abcd')
        cls.video = KalturaVideoFactory(name='video')
        TeamVideoFactory(video=cls.video, team=cls.team)
        cls.version = pipeline.add_subtitles(cls.video, 'en', SubtitleSetFactory(), complete=True)
        cls.language = cls.version.subtitle_language
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


    def test_user_sync_page(self):
        langs = ['en', 
                 'fr', 'de', 'hu' 
                 ]
        user = UserFactory()
        account = YouTubeAccountFactory(user=user,
                                        channel_id='test-channel-id')
        for x in range(2):
            video = YouTubeVideoFactory(user=user, video_url__owner_username='test-channel-id')
            for lc in langs:
                version = pipeline.add_subtitles(video, lc, SubtitleSetFactory(), complete=True)
                language = version.subtitle_language
                video_url = video.get_primary_videourl_obj()
                SyncHistory.objects.create_for_success(
                        account=account,
                        video_url=video_url, language=language,
                        version=version, action=SyncHistory.ACTION_UPDATE_SUBTITLES,
                    )
                if x > 0:
                    SyncHistory.objects.create_for_error(
                        ValueError("Fake Error"), account=account,
                        video_url=video_url, language=language,
                        version=version, action=SyncHistory.ACTION_UPDATE_SUBTITLES,
                        retry=False)

        self.video_pg.log_in(user.username, 'password') 
        self.sync_pg.open_user_sync_page()
        self.assertEqual(4, self.sync_pg.resync_count())
        self.sync_pg.submit_for_resync()
        history_qs = SyncHistory.objects.filter(retry=True)
        self.assertEqual(4, len(history_qs))

    def test_failed_sync_performance(self):
        langs = ['en', 'fr', 'de', 'hu', 'es', 'hr', 'pt-br', 'ro', 'cs', 'id']
        for x in range(10):
            video = KalturaVideoFactory(name='video_%s' % x)
            TeamVideoFactory(video=video, team=self.team)
            for lc in langs:
                for y in range(5):
                    version = pipeline.add_subtitles(video, lc, SubtitleSetFactory(), complete=True)
                    language = version.subtitle_language
                    video_url = video.get_primary_videourl_obj()
                    SyncHistory.objects.create_for_success(
                        account=self.account,
                        video_url=video_url, language=language,
                        version=version, action=SyncHistory.ACTION_UPDATE_SUBTITLES,
                    )
                if x > 8:
                    SyncHistory.objects.create_for_error(
                        ValueError("Fake Error"), account=self.account,
                        video_url=video_url, language=language,
                        version=version, action=SyncHistory.ACTION_UPDATE_SUBTITLES,
                        retry=False)

        self.video_pg.log_in(self.admin.username, 'password') 
        start = time.clock()
        try:
            self.sync_pg.open_failed_sync_page(self.team.slug)
            self.logger.info(self.sync_pg.resync_count())
        finally:
            elapsed = (time.clock() - start)
            self.logger.info(elapsed)
        self.assertLess(elapsed, 3)
