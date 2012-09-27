from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import video_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
import codecs
import os
import time

class WebdriverTestCaseUploadSubsUntimedText(WebdriverTestCase):
    """TestSuite for uploading subtitles with untimed text.
    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user')
        self.video_pg = video_page.VideoPage(self)
        self.video_pg.log_in(self.user.username, 'password')
        self.test_video = data_helpers.create_video(self, 
            'http://www.example.com/upload_test.mp4')
        self.video_pg.open_video_page(self.test_video.video_id)
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')

    def test_untimed__txt(self):
        """Upload untimed subs in a txt file.

        """
        test_file = 'Untimed_text.txt'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('English', sub_file)
        subtitle_lang = self.test_video.subtitle_language('en')
        self.assertEqual(43, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

    def test_untimed__srt(self):
        """Upload untimed subs in a srt file.

        """
        test_file = 'Untimed_text.srt'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('English', sub_file)
        subtitle_lang = self.test_video.subtitle_language('en')
        self.assertEqual(43, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

    def test_untimed__sbv(self):
        """Upload untimed subs in a sbv file.

        """
        test_file = 'Untimed_text.sbv'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('English', sub_file)
        subtitle_lang = self.test_video.subtitle_language('en')
        self.assertEqual(43, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

    def test_untimed__ssa(self):
        """Upload untimed subs in a ssa file.

        """
        test_file = 'Untimed_text.ssa'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('English', sub_file)
        subtitle_lang = self.test_video.subtitle_language('en')
        self.assertEqual(43, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

    def test_untimed__ttml(self):
        """Upload untimed subs in a ttml file.

        """
        test_file = 'Untimed_text.xml'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('English', sub_file)
        subtitle_lang = self.test_video.subtitle_language('en')
        self.assertEqual(43, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

    def test_untimed__dfxp(self):
        """Upload untimed subs in a dfxp file.

        """
        test_file = 'Untimed_text.dxfp'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('English', sub_file)
        subtitle_lang = self.test_video.subtitle_language('en')
        self.assertEqual(43, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

    def test_version__existing_translation(self):
        """Uploading a new set of subs is created as a new version.

        Uploaded subs replace the existing version even if the existing
        version has subs created from it.
        """
        test_video3 = data_helpers.create_video(self, 
            'http://www.example.com/3.mp4')

        video_list = data_helpers.create_videos_with_fake_subs(self)
        sub_lang = test_video3.subtitle_language('ru')
        test_file = 'Untimed_text.srt'
        sub_file = os.path.join(self.subs_data_dir, test_file)
        self.video_pg.open_video_page(test_video3.video_id)
     
        message = self.video_pg.upload_subtitles('Russian', sub_file)
        self.assertEqual(self.video_pg.UPLOAD_SUCCESS_TEXT, message)
        self.assertEqual(1,
            test_video3.version(language=sub_lang).version_no)

    def test__version__overwrite_existing(self):
        """Uploading a new set of subs is created as a new version.

        Uploaded subs replace the existing version.
        """
        test_video4 = data_helpers.create_video(self, 
            'http://www.example.com/4.mp4')

        video_list = data_helpers.create_videos_with_fake_subs(self)
        test_file = 'Untimed_text.srt'
        sub_file = os.path.join(self.subs_data_dir, test_file) 
        self.video_pg.open_video_page(test_video4.video_id)
      
        message = self.video_pg.upload_subtitles('Arabic', sub_file)
        self.assertEqual(self.video_pg.UPLOAD_SUCCESS_TEXT, message)
        sub_lang = test_video4.subtitle_language('ar')
        self.video_pg.page_refresh()
        self.assertEqual(1,
            test_video4.version(language=sub_lang).version_no)
    
    def test__upload__additional_translation(self):
        """Uploading a new set of subs is created as a new version.

        Uploaded subs replace the existing version.
        """
        test_video4 = data_helpers.create_video(self, 
            'http://www.example.com/4.mp4')

        video_list = data_helpers.create_videos_with_fake_subs(self)
        test_file = 'Untimed_text.srt'
        sub_file = os.path.join(self.subs_data_dir, test_file) 
        self.video_pg.open_video_page(test_video4.video_id)
      
        message = self.video_pg.upload_subtitles('Swedish', sub_file)
        self.assertEqual(self.video_pg.UPLOAD_SUCCESS_TEXT, message)
        self.video_pg.page_refresh()
        self.assertEqual(0, test_video4.latest_version('sv').version_no)
        sv_subtitles = test_video4.subtitle_language('sv')
        self.assertEqual(43, int(sv_subtitles.subtitle_count))


        
class WebdriverTestCaseUploadSubsTimedText(WebdriverTestCase):
    """TestSuite for uploading subtitles with untimed text.
    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user')
        self.video_pg = video_page.VideoPage(self)
        self.video_pg.log_in(self.user.username, 'password')
        self.test_video = data_helpers.create_video(self, 
            'http://www.example.com/upload_test.mp4')
        self.video_pg.open_video_page(self.test_video.video_id)
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')



    def test_timed__txt(self):
        """Upload timed subs in a txt file.

        """
        test_file = 'Timed_text.en.txt'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('English', sub_file)
        subtitle_lang = self.test_video.subtitle_language('en')
        self.assertEqual(72, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

    def test_timed__srt(self):
        """Upload timed subs in a srt file.

        """
        test_file = 'Timed_text.sv.srt'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('Swedish', sub_file)
        subtitle_lang = self.test_video.subtitle_language('sv')
        self.assertEqual(72, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

    def test_timed__sbv(self):
        """Upload timed subs in a sbv file.

        """
        test_file = 'Timed_text.zh-cn.sbv'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('Chinese, Simplified', sub_file)
        subtitle_lang = self.test_video.subtitle_language('zh-cn')
        self.assertEqual(243, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

    def test_timed__ssa(self):
        """Upload timed subs in a ssa file.

        """
        test_file = 'Timed_text.hu.ssa'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('Hungarian', sub_file)
        subtitle_lang = self.test_video.subtitle_language('hu')
        self.assertEqual(243, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

    def test_timed__ttml(self):
        """Upload timed subs in a ttml file.

        """
        test_file = 'Timed_text.ar.xml'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('Arabic', sub_file)
        subtitle_lang = self.test_video.subtitle_language('ar')
        self.assertEqual(243, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

    def test_timed__dfxp(self):
        """Upload timed subs in a dfxp file.

        """
        test_file = 'Timed_text.sv.dxfp'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('Swedish', sub_file)
        subtitle_lang = self.test_video.subtitle_language('sv')
        self.assertEqual(43, int(subtitle_lang.subtitle_count))
        self.video_pg.page_refresh()

