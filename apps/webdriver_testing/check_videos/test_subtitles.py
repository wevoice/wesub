import codecs
import os

from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing.pages.site_pages import video_language_page
from utils.factories import *
from webdriver_testing import data_helpers
from webdriver_testing.pages.editor_pages import subtitle_editor


class TestCaseSubtitles(WebdriverTestCase):
    """TestSuite for download subtitles from the video's lanugage page   """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseSubtitles, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory()
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')

    def test_subs_with_markdown(self):
        """Subtitles are available for subtitles with markdown formatting.

        """
        sub_file = os.path.join(self.subs_data_dir, 'subs_with_markdown.dfxp')
        video = VideoFactory(primary_audio_language_code='en')
        data = {'language_code': 'en',
                 'video': video,
                 'subtitles': sub_file,
                 'complete': True,
                 'author': self.user,
                 'committer': self.user
                }
        self.data_utils.add_subs(**data)
        self.video_pg.open_video_page(video.video_id)
        self.assertIn('English', self.video_pg.subtitle_languages())


    def test_misordered_subs(self):
        """Subtitles are displayed in sub lang page in order of time.

        """
        sub_file = os.path.join(self.subs_data_dir, 'misordered_subs.dfxp')
        video = VideoFactory(primary_audio_language_code='en')
        data = {'language_code': 'en',
                 'video': video,
                 'subtitles': sub_file,
                 'complete': True,
                 'author': self.user,
                 'committer': self.user
                }
        self.data_utils.add_subs(**data)
        self.video_language_pg.open_video_lang_page(video.video_id, 'en')
        expected_lines = [u'Line 1 \xb6', 'Line 2', 'Line 3', 'Line 4', 'Line 5', 'Line 6']
        self.assertEqual(expected_lines, self.video_language_pg.displayed_lines())

