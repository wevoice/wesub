import os
import time
import codecs
from rest_framework.test import APILiveServerTestCase, APIClient
from videos.models import *
from utils.factories import *
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages import video_language_page
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing import data_helpers
from webdriver_testing.pages.site_pages import editor_page


class TestCaseSubtitles(APILiveServerTestCase, WebdriverTestCase):
    """TestSuite for site video searches.  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseSubtitles, cls).setUpClass()
        cls.user = UserFactory()
        #Create some test data and set subtitle data dir
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
                'webdriver_testing', 'subtitle_data')
        cls.video_pg = video_page.VideoPage(cls)
        cls.editor_pg = editor_page.EditorPage(cls)
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)

    def _get (self, url):
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        response.render()
        r = (json.loads(response.content))
        return r

    def _post(self, url, data=None):
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)
        status = response.status_code
        response.render()
        r = (json.loads(response.content))
        return r, status

    def _post_subs(self, url, data=None):
        self.client.force_authenticate(self.user)
        response = self.client.post(url, json.dumps(data), 
                                    content_type="application/json;  charset=utf-8")
        status = response.status_code
        response.render()
        r = (json.loads(response.content))
        return r, status

    def test_add_language(self):
        """Set a language as complete via the api
        """
        video = VideoFactory()

        url = '/api/videos/%s/languages/' % video.video_id
        data = {'language_code': 'en',
               }
        r, status = self._post(url, data)
        self.assertEqual(201, status)


    def test_add_original_language(self):
        """Set a language as original via the api
        """
        video = VideoFactory()
        url = '/api/videos/%s/languages/' % video.video_id
        #Create the language for the test video
        data = {'language_code': 'fr',
                'is_primary_audio_language': True,
                'subtitles_complete': False
                 }

        r, status  = self._post(url, data)
        self.assertEqual(201, status)
        self.video_pg.open_video_page(video.video_id)
        self.video_pg.add_subtitles()
        self.assertTrue(self.video_pg.is_text_present("th", "This video is in French"))

    def test_upload_untimed_subtitles(self):
        """Upload untimed subtitles via api """
        #Create the language for the test video

        video = VideoFactory()
        url = '/api/videos/%s/languages/' % video.video_id
        data = {'language_code': 'en',
                'is_original': True 
                 }
        r, status = self._post(url, data)

        url = '/api/videos/%s/languages/en/subtitles/' % video.video_id 
        subtitles = open(os.path.join(self.subs_data_dir, 'Untimed_text.srt'))
        data = { 'subtitles': subtitles.read(),
                 'sub_format': 'srt',
                  } 

        r, status = self._post_subs(url, data)
        self.video_pg.open_video_page(video.video_id)
        self.video_language_pg.open_video_lang_page(video.video_id, 'en')
         
        verification_file = os.path.join(self.subs_data_dir,'Untimed_lines.txt')
        expected_list = [line.strip() for line in codecs.open(
                verification_file, encoding='utf-8')]
        displayed_list = self.video_language_pg.displayed_lines()
        self.assertEqual(expected_list, displayed_list) 
        self.video_language_pg.log_in(self.user.username, 'password')
        self.video_language_pg.open_video_lang_page(
            video.video_id, 'en')
        self.video_language_pg.edit_subtitles()
        editor_sub_list = self.editor_pg.working_text() 

        #Verify uploaded subs are displayed and editable
        self.assertLess(0, len(editor_sub_list))
        typed_line = "I'd like to be"
        self.editor_pg.edit_sub_line(typed_line, 1) 
        self.editor_pg.save('Exit') 
        self.video_language_pg.open_video_lang_page(
            video.video_id, 'en')
        displayed_list = self.video_language_pg.displayed_lines()

        #Verify the edited text is in the sub list
        self.assertIn(typed_line, displayed_list[0])

        #Verify the origal unedited text is still present in the sub list.
        self.assertEqual(expected_list[-1], displayed_list[-1])


    def test_formats_and_langs(self):
        """Upload subs via api.

        """
        errors = []
        video = VideoFactory()
        testdata = {
                    "srt": "en",
                    "ssa": "hu",
                    'sbv': 'zh-cn',
                    'dfxp': 'sv',
                    'txt': 'en-gb',
                    'vtt': 'es-mx'
                   }
        for sub_format, lc in testdata.iteritems():

            #Post the language
            url = '/api/videos/%s/languages/' % video.video_id
            data = {'language_code': lc,
                     }
            try: 
                r, status = self._post(url, data)
                self.logger.info(status)
                self.assertEqual(201, status) 
            except Exception as e:
                errors.append('failed adding language code: {0} error: {1}'.format(lc, e))
            
            #Post the subtitles
            try:
                url = '/api/videos/{0}/languages/{1}/subtitles/'.format(video.video_id, lc)
                subfile = os.path.join(self.subs_data_dir, 'Timed_text.{0}.{1}'.format(lc, sub_format))
                self.logger.info(subfile) 
                #subtitles =  codecs.open(subfile, encoding='utf-8')
                subtitles =  open(subfile)
                data = { "subtitles": subtitles.read(),
                         "sub_format": sub_format, 
                         } 
 
                r, status = self._post_subs(url, data)
                self.assertEqual(201, status) 
            except Exception as e: 
                errors.append('failed adding format: {0}, error {1}'.format(sub_format,e))
            
        self.assertEqual(errors, [])

    def test_false_subtitles(self):
        """Return error when 'false' passed for subtitles'

        """
        video = VideoFactory()
        url = '/api/videos/%s/languages/' % video.video_id
        data = {'language_code': 'en', }
        r, status = self._post(url, data)
        url = '/api/videos/{0}/languages/en/subtitles/'.format(video.video_id)
        data = { "subtitles": False,
                 "sub_format": 'json', 
                } 
 
        r, status = self._post_subs(url, data)
        self.logger.info(r)
        self.assertEqual({u'subtitles': [u'Invalid subtitle data']}, r)

    def test_invalid_videoid(self):
        """Return error when video id is None'

        """
        video = VideoFactory()
        url = '/api/videos/None/languages/en/subtitles/'
        r = self._get(url)
        self.logger.info(r)
        self.assertEqual({u'detail': u'Not found'}, r)
