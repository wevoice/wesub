import os

from django.core import mail

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages import video_page
from apps.webdriver_testing.pages.site_pages import video_language_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import VideoUrlFactory


class TestCaseRevisionNotifications(WebdriverTestCase):
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseRevisionNotifications, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create()
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)
        cls.subs_path = os.path.dirname(os.path.abspath(__file__))

    def tearDown(self):
        self.browser.get_screenshot_as_file('MYTMP/%s.png' % self.id())

    def test_notify_contributor(self):
        """Subtitle contributor gets an email when new revision added.

        """
        video = VideoUrlFactory().video
        self.video_pg.open_video_page(video.video_id)

        self.video_pg.log_in(self.user.username, 'password')
        rev1 = os.path.join(self.subs_path, 'rev1.dfxp')
        self.video_pg.open_video_page(video.video_id)
        self.video_pg.upload_subtitles('English', rev1)
        sl = video.subtitle_language('en')
        v1 = sl.get_tip().id

        user2 = UserFactory.create()
        self.video_pg.log_in(user2.username, 'password')
        rev2 = os.path.join(self.subs_path, 'rev2.dfxp')
        self.video_pg.open_video_page(video.video_id)
        mail.outbox = []
        self.video_pg.upload_subtitles('English', rev2)
        email_to = mail.outbox[-1].to     
        msg = str(mail.outbox[-1].message())
        #self.logger.info("MESSAGE: %s" % msg)
        v2 = sl.get_tip().id
        diffing_page = ('videos/diffing/{0}/{1}/'.format(v2, v1))
        self.video_pg.open_page(diffing_page)
        self.assertIn(diffing_page, msg)
        self.assertIn(self.user.email, email_to)

    def test_notify__language_follower(self):
        """Language follower gets an email when new revision added.

        """
        video = VideoUrlFactory().video

        self.video_pg.open_video_page(video.video_id)
        self.video_pg.log_in(self.user.username, 'password')
        rev1 = os.path.join(self.subs_path, 'rev1.dfxp')
        self.video_pg.open_video_page(video.video_id)
        self.video_pg.upload_subtitles('English', rev1)

        follower = UserFactory.create(email='follower@example.com')
        self.video_language_pg.open_video_lang_page(video.video_id, 'en')
        self.video_pg.log_in(follower.username, 'password')
        self.video_pg.page_refresh()
        self.video_pg.toggle_follow()
        mail.outbox = []
        self.video_pg.log_in(self.user.username, 'password')
        rev2 = os.path.join(self.subs_path, 'rev2.dfxp')
        self.video_pg.open_video_page(video.video_id)
        self.video_pg.upload_subtitles('English', rev2)

        email_to = mail.outbox[-1].to     
        msg = str(mail.outbox[-1].message())
        self.logger.info("MESSAGE: %s" % msg)
        self.assertIn(follower.email, email_to)
        wrong_text = ('were changed by <b><a href="http://localhost:8081/'
                      'profiles/profile/TestUser0/"></a></b>. These changes '
                      'went live immediately.  of the timing was changed.')
        self.assertNotIn(wrong_text, msg)

    def test_notify__video_follower_revisions(self):
        """Video follower gets an email when new revision added.

        """
        video = VideoUrlFactory().video
        follower = UserFactory.create(email='follower@example.com')
        self.video_pg.open_video_page(video.video_id)
        self.video_pg.log_in(follower.username, 'password')
        self.video_pg.page_refresh()
        self.video_pg.toggle_follow()
        mail.outbox = []

        self.video_pg.open_video_page(video.video_id)
        self.video_pg.log_in(self.user.username, 'password')
        self.video_pg.page_refresh()
        rev1 = os.path.join(self.subs_path, 'rev1.dfxp')
        self.video_pg.open_video_page(video.video_id)
        self.video_pg.upload_subtitles('English', rev1)

        rev2 = os.path.join(self.subs_path, 'rev2.dfxp')
        self.video_pg.open_video_page(video.video_id)
        self.video_pg.upload_subtitles('English', rev2)
        self.video_pg.page_refresh()

        email_to = mail.outbox[-1].to     
        msg = str(mail.outbox[-1].message())
        self.logger.info("MESSAGE: %s" % msg)
        self.assertIn(follower.email, email_to)

    def test_notify__video_follower_initial(self):
        """Video follower gets an email when first revision of subtitles added.

        """
        self.skipTest('needs https://unisubs.sifterapp.com/issues/2220 fixed')
        video = VideoUrlFactory().video
        follower = UserFactory.create(email='follower@example.com')
        self.video_pg.open_video_page(video.video_id)
        self.video_pg.log_in(follower.username, 'password')
        self.video_pg.page_refresh()
        self.video_pg.toggle_follow()
        self.assertEqual(self.FOLLOWING, self.video_pg.follow_text())
        mail.outbox = []

        self.video_pg.open_video_page(video.video_id)
        self.video_pg.log_in(self.user.username, 'password')
        self.video_pg.page_refresh()
        rev1 = os.path.join(self.subs_path, 'rev1.dfxp')
        self.video_pg.open_video_page(video.video_id)
        self.video_pg.upload_subtitles('English', rev1)
        self.assertEqual(1, len(mail.outbox))
        email_to = mail.outbox[-1].to     
        msg = str(mail.outbox[-1].message())
        self.logger.info("MESSAGE: %s" % msg)
        self.assertIn(follower.email, email_to)

