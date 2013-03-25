import os
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages import video_language_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory

class TestCaseVideoLangResource(WebdriverTestCase):
    """TestSuite for uploading subtitles via the api.

    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseVideoLangResource, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create()
        cls.data_utils.create_user_api_key(cls.user)
      
        #Create some test data and set subtitle data dir
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
                                         'webdriver_testing', 'subtitle_data')
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)

    def test_complete(self):
        """Set a language as complete via the api
        """

        #Create the language for the test video
        test_video = self.data_utils.create_video()

        create_url = ('videos/%s/languages/'  % test_video.video_id)
        create_data = {'language_code': 'en',
                       'is_complete': True 
                      }
        status, response = self.data_utils.post_api_request(self.user,  
            create_url, 
            create_data)
        self.assertEqual(201, status)
        self.logger.info(response)

    def test_original(self):
        """Set a language as original via the api
        """
        test_video = self.data_utils.create_video()
        
        #Create the language for the test video
        create_url = ('videos/%s/languages/'  % test_video.video_id)
        create_data = {'language_code': 'fr',
                       'is_original': True 
                      }
        status, response = self.data_utils.post_api_request(self.user,  
            create_url, 
            create_data)
        self.assertEqual(201, status)
        url_part = 'videos/%s/' % test_video.video_id
        s, r = self.data_utils.api_get_request(self.user, url_part)
        self.assertEqual('fr', r['original_language'])
