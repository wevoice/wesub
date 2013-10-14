import os

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages import video_language_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import VideoUrlFactory
from apps.webdriver_testing.pages.editor_pages import subtitle_editor 


class TestCaseEditUploaded(WebdriverTestCase):
    """TestSuite large subtitle sets  """
    NEW_BROWSER_PER_TEST_CASE = False 

    @classmethod
    def setUpClass(cls):
        super(TestCaseEditUploaded, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create(username = 'user')
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')


    def test_edit__large(self):
        """Upload a large set of subtitles then open for editing. """
        video =  self.data_utils.create_video()
        data = {'language_code': 'en',
                'video': video,
                'subtitles': ('apps/webdriver_testing/subtitle_data/'
                              'How-to.en.srt'),
           }
        r = self.data_utils.add_subs(**data)

        fr_data = {'language_code': 'fr',
                     'video': video,
                     'complete': False,
                     'parents': [video.subtitle_language('en').get_tip()],
                     'subtitles': ('apps/webdriver_testing/subtitle_data/'
                                   'srt-full.srt')
                    }
        r = self.data_utils.add_subs(**fr_data)
        self.video_language_pg.open_video_lang_page(video.video_id, 'fr')
        self.video_language_pg.log_in(self.user.username, 'password')
        self.video_language_pg.page_refresh()
        self.video_language_pg.edit_subtitles()
        self.assertEqual('Adding a New Translation', 
                         self.sub_editor.dialog_title())
