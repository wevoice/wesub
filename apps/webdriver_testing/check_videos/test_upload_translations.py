import os
import codecs
import time

from caching.tests.utils import assert_invalidates_model_cache
from utils.factories import *
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing.pages.site_pages import video_language_page
from webdriver_testing import data_helpers
from webdriver_testing.pages.site_pages import editor_page 

class TestCaseUploadTranslation(WebdriverTestCase):
    """TestSuite for uploading subtitles with untimed text.  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod 
    def setUpClass(cls):
        super(TestCaseUploadTranslation, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory()
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)
        cls.editor_pg = editor_page.EditorPage(cls)
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')
        cls.video_pg.open_page('videos/create/')
        cls.video_pg.log_in(cls.user.username, 'password')

    def setUp(self):
        self.video_pg.open_page('videos/create/')
        self.video_pg.handle_js_alert('accept')
        self.tv = VideoFactory(primary_audio_language_code='en')
        data = {'language_code': 'en',
                 'video': self.tv,
                 'subtitles': 'apps/webdriver_testing/subtitle_data/'
                               'Timed_text.en.srt',
                 'complete': True,
                 'author': self.user,
                 'committer': self.user 
                }
        self.data_utils.add_subs(**data) 
        self.video_pg.open_video_page(self.tv.video_id)

    def _upload_and_verify(self, tv, sub_file, language, lang_code):
        """Upload the subtitle file and confirm subs are stored.

        Checking the subtitle count of the expected value vs the
        value in the database for the latest version of the lang.

        """
        message = self.video_pg.upload_subtitles(language, sub_file, 
                                       translated_from='English')
        self.logger.info("MESSAGE: %s" %message)
        subtitle_lang = tv.subtitle_language(lang_code) 
        page_url = 'videos/{0}/{1}/'.format(tv.video_id, lang_code)
        self.video_pg.open_page(page_url)
        self.video_pg.handle_js_alert('accept')
        return subtitle_lang.get_subtitle_count()


    def test_new_translation(self):
        """Upload a new translation.

        """
        with assert_invalidates_model_cache(self.tv):
            test_file = 'Timed_text.sv.dfxp'
            sub_file = os.path.join(self.subs_data_dir, test_file)       
            sc = self._upload_and_verify(self.tv, sub_file, 'Swedish', 'sv')
            self.assertEqual(sc, 72)    


    def test_editable(self):
        """Uploaded translation can be opened in the editor.

        """
        test_file = 'Timed_text.sv.dfxp'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self._upload_and_verify(self.tv, sub_file, 'Swedish', 'sv')

        
        #Open the language page for the video and click Edit Subtitles 
        self.video_language_pg.open_video_lang_page(self.tv.video_id, 'sv')
        self.video_language_pg.edit_subtitles()
        self.assertEqual(u'Editing Swedish\u2026', self.editor_pg.working_language())

    def test_txt(self):
        """Upload translation (de) in a txt file.

        """
        test_file = 'Timed_text.en.txt'
        sub_file = os.path.join(self.subs_data_dir, test_file)
        sc = self._upload_and_verify(self.tv, sub_file, 'German', 'de')
        self.assertEqual(sc, 72) 

    def test_srt(self):
        """Upload translation (sv) in a srt file.

        """
        sub_file = os.path.join(self.subs_data_dir, 'Timed_text.sv.srt')
        sc = self._upload_and_verify(self.tv, sub_file, 'Swedish', 'sv')
        self.assertEqual(sc, 72) 
       
    def test_dfxp(self):
        """Upload translation (fr) in a dfxp file.

        """
        sub_file = os.path.join(self.subs_data_dir, 'Timed_text.sv.dfxp')
        sc = self._upload_and_verify(self.tv, sub_file, 'French', 'fr')
        self.assertEqual(sc, 72)

    def test_xml_entities(self):
        """Upload translation with ampersand in text.

        """
        sub_file = os.path.join(self.subs_data_dir, 'xml_entities.en.srt')
        sc = self._upload_and_verify(self.tv, sub_file, 'French', 'fr')
        self.assertEqual(sc, 5)

