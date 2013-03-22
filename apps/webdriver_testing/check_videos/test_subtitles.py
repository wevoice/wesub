import codecs
import os

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages import video_page
from apps.webdriver_testing.pages.site_pages import video_language_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import VideoUrlFactory
from apps.webdriver_testing.pages.editor_pages import subtitle_editor
from apps.webdriver_testing.pages.editor_pages import unisubs_menu 


class TestCaseSubtitles(WebdriverTestCase):
    """TestSuite for download subtitles from the video's lanugage page   """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseSubtitles, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.menu = unisubs_menu.UnisubsMenu(cls)

        cls.user = UserFactory.create()
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')

    def _add_video_and_subs(self, sub_file, lang_code, title):
        """Create the test videos and add subtitles to it.
  
        """
        video = VideoUrlFactory(
            url = 'http://example.unisubs.com/download-test.mp4',
            video__title = title
            ).video
        data = {'language_code': lang_code,
                'video': video.pk,
                'primary_audio_language_code': lang_code,
                'draft': open(sub_file),
                'is_complete': True,
                'complete': 1
                }

        self.data_utils.upload_subs(video, data)
        return video



    def test_subs_with_markdown(self):
        """Subtitles are available for subtitles with markdown formatting.

        """

        #Specify subtitle file, language and download formats.
        test_file = 'subs_with_markdown.dfxp'
        video_title = 'Subs have markdown'
        lang_code = 'en'
        sub_file = os.path.join(self.subs_data_dir, test_file)

        #Create a video and upload subtitles
        test_video = self._add_video_and_subs(sub_file, lang_code, video_title)
        self.video_pg.open_video_page(test_video.video_id)
        self.assertEqual('English', self.menu.visible_menu_text())

