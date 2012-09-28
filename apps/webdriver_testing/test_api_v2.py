import os
import simplejson
import requests
import time
import codecs
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import video_language_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.editor_pages import subtitle_editor 

class WebdriverTestCaseApiV2UploadSubtitles(WebdriverTestCase):
    """TestSuite for uploading subtitles via the api.
    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user')
        self.video_language_pg = video_language_page.VideoLanguagePage(self)
        data_helpers.create_user_api_key(self, self.user)
        self.test_video = data_helpers.create_video( self, 
            'http://www.example.com/upload_test.mp4' )
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')


    def post_api_request(self, url_part, data):
        url = self.base_url + 'api2/partners/' + url_part
        headers = { 'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-apikey': self.user.api_key.key,
                    'X-api-username': self.user.username,
                  } 
        r = requests.post( url, data=simplejson.dumps(data), headers=headers )
        return r.status_code, r.json


    def api_upload_subs(self, test_format, test_lang_code):
        """Create the language and upload the subtitles.

        Return the subtitle_language object of the test video for verification.
        
        Tests assume that we are using the Timed_text.<lang>.<format> files
        in the subtitle_data directory.
        """

        #Create the language for the test video
        create_url = ( 'videos/%s/languages/'  % self.test_video.video_id  )
        create_data = { 'language_code': test_lang_code }
        status, response = self.post_api_request(create_url, create_data)
        #Upload the subtitles via api request
        upload_url = ( 'videos/{0}/languages/{1}/subtitles/'.format(
            self.test_video.video_id, test_lang_code ))
        if test_format == 'ttml':
            sub_data = codecs.open( os.path.join( self.subs_data_dir, 
                'Timed_text.{0}.{1}'.format( test_lang_code, 'xml' ) ),
                encoding='utf-8' )
        else:
            sub_data = codecs.open( os.path.join( self.subs_data_dir, 
                'Timed_text.{0}.{1}'.format( test_lang_code, test_format ) ), 
                 encoding='utf-8' )

        upload_data = { 'subtitles': sub_data.read(), 'sub_format': test_format } 
        print '#########'
        print upload_data
        print '#########'

        status, response = self.post_api_request( upload_url, upload_data )
        print status, response
        self.video_language_pg.open_video_lang_page( self.test_video.video_id, 
            test_lang_code )
        subtitle_lang = self.test_video.subtitle_language(test_lang_code) 
        return subtitle_lang


    def test_upload__display(self):
        #Create the language for the test video
        create_url = ( 'videos/%s/languages/'  % self.test_video.video_id  )
        create_data = { 'language_code': 'en', 'is_original': True }
        status, response = self.post_api_request(create_url, create_data)

        #Upload the subtitles via api request
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )
        sub_data =  open( os.path.join( self.subs_data_dir, 'Untimed_text.srt' ) )
        upload_data = { 'subtitles': sub_data.read(), 'sub_format': 'txt' } 
        status, response = self.post_api_request( upload_url, upload_data )
        self.video_language_pg.open_video_lang_page( self.test_video.video_id, 
            'en' )
        verification_file = os.path.join(self.subs_data_dir,'Untimed_lines.txt')
        expected_list = [line.strip() for line in codecs.open(
        verification_file, encoding='utf-8')]
        displayed_list = self.video_language_pg.displayed_lines()
        self.assertEqual( expected_list, displayed_list ) 

    def test_upload__srt(self):
        test_lang_code = 'en'
        test_format = 'srt'
        subtitle_language = self.api_upload_subs( test_format, 
           test_lang_code)
        self.assertEqual(72, subtitle_language.get_subtitle_count() )


    def test_upload__ssa(self):
        test_lang_code = 'hu'
        test_format = 'ssa'
        subtitle_language = self.api_upload_subs( test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page( self.test_video.video_id, 
            test_lang_code )

        self.assertEqual(243, subtitle_language.get_subtitle_count() )


    def test_upload__sbv(self):
        test_lang_code = 'zh-cn'
        test_format = 'sbv'
        subtitle_language = self.api_upload_subs( test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page( self.test_video.video_id, 
            test_lang_code )

        self.assertEqual(243, subtitle_language.get_subtitle_count() )

    def test_upload__ttml(self):
        test_lang_code = 'ar'
        test_format = 'ttml'
        subtitle_language = self.api_upload_subs( test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page( self.test_video.video_id, 
            test_lang_code )

        self.assertEqual(243, subtitle_language.get_subtitle_count() )

    def test_upload__dfxp(self):
        test_lang_code = 'sv'
        test_format = 'dfxp'
        subtitle_language = self.api_upload_subs( test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page( self.test_video.video_id, 
            test_lang_code )

        self.assertEqual(72, subtitle_language.get_subtitle_count() )

    def test_upload__edit(self):
        #Create the language for the test video
        create_url = ( 'videos/%s/languages/'  % self.test_video.video_id  )
        create_data = { 'language_code': 'en', 'is_original': True }
        status, response = self.post_api_request(create_url, create_data)

        #Upload the subtitles via api request
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )
        sub_data =  open( os.path.join( self.subs_data_dir, 'Untimed_text.srt' ) )
        upload_data = { 'subtitles': sub_data.read(), 'sub_format': 'txt' } 
        status, response = self.post_api_request( upload_url, upload_data )
        self.video_language_pg.open_video_lang_page( self.test_video.video_id, 
            'en' )
        #Open the language page for the video and click Edit Subtitles 
        verification_file = os.path.join(self.subs_data_dir,'Untimed_lines.txt')
        expected_list = [line.strip() for line in codecs.open(
            verification_file, encoding='utf-8')]

        self.video_language_pg.open_video_lang_page(
            self.test_video.video_id, 'en')
        self.video_language_pg.edit_subtitles()
        sub_editor = subtitle_editor.SubtitleEditor(self)
        sub_editor.continue_past_help()
        editor_sub_list = subtitle_editor.subtitles_list()
        #Verify uploaded subs are displayed in the Editor
        self.assertEqual(expected_list, editor_sub_list)
        typed_subs = sub_editor.type_subs()
        sub_editor.save_and_exit()
        self.video_language_pg.open_video_lang_page(
            self.test_video.video_id, 'en')
        displayed_list = self.video_language_pg.displayed_lines()
        #Verify the edited text is in the sub list
        self.assertIn("I'd like to be under the sea", displayed_list)
        #Verify the origal unedited text is still present in the sub list.
        self.assertIn(expected_list[9], displayed_list)


