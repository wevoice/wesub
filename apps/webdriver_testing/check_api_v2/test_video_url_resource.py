import os
import time
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.pages.site_pages import video_page
from apps.webdriver_testing.pages.site_pages import watch_page


class TestCaseVideoUrl(WebdriverTestCase):
    """TestSuite for getting and modifying video urls via api_v2.

       One can list, update, delete and add video urls to existing videos.
    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseVideoUrl, cls).setUpClass()
        cls.user = UserFactory.create(username = 'user')
        cls.data_utils = data_helpers.DataHelpers()
        cls.data_utils.create_user_api_key(cls.user)
        cls.test_video = cls.data_utils.create_video()


    def test_list(self):
        """Verify video urls for a particular video are listed.

        GET /api2/partners/videos/[video-id]/urls/
        """
        video_id = self.test_video.video_id
        video_url = self.test_video.get_video_url() 
        url_part = 'videos/%s/urls/' % video_id
        status, response = self.data_utils.api_get_request(self.user,url_part) 
        video_pg = video_page.VideoPage(self)
        video_pg.open_video_page(video_id)

        self.assertEqual(video_url, response['objects'][0]['url'])

    def test_url__post(self):
        """Add an additional new url.

           POST /api2/partners/videos/[video-id]/urls/
        """
        video_id = self.test_video.video_id
        video_url = self.test_video.get_video_url()
        url_data = { 'url': 'http://unisubs.example.com/newurl.mp4' }
        url_part = 'videos/%s/urls/' % video_id
        status, response = self.data_utils.post_api_request(self.user,url_part, 
            url_data) 

        vid_url = 'videos/%s' % video_id
        status, response = self.data_utils.api_get_request(self.user,vid_url) 
        video_pg = video_page.VideoPage(self)
        video_pg.open_video_page(video_id)

        self.assertIn(video_url, response['all_urls'], response)



    def test_url__put(self):
        """Add a second url.

           PUT /api2/partners/videos/[video-id]/urls/[url-id]/
        """
        #Post an additional url to the video
        video_id = self.test_video.video_id
        video_url = self.test_video.get_video_url()
        url_data = { 'url': 'http://unisubs.example.com/newurl.mp4' }
        url_part = 'videos/%s/urls/' % video_id
        status, response = self.data_utils.post_api_request(self.user,url_part, url_data)

        #Put an updated url on the video and set it as primary 
        put_url = 'videos/{0}/urls/{1}/'.format(video_id, response['id'])
        put_data = { 'url': 'http://unisubs.example.com/newerurl.mp4'}
        status, response = self.data_utils.put_api_request(self.user,put_url, put_data) 
        video_pg = video_page.VideoPage(self)
        video_pg.open_video_page(video_id)

        self.assertEqual('http://unisubs.example.com/newerurl.mp4', response['url'])

    def test_url__put_primary(self):
        """Verify video urls for a particular video are listed.

           PUT /api2/partners/videos/[video-id]/urls/[url-id]/
        """
        #Post an additional url to the video
        video_id = self.test_video.video_id
        video_url = self.test_video.get_video_url()
        url_data = { 'url': 'http://unisubs.example.com/newurl.mp4' }
        url_part = 'videos/%s/urls/' % video_id
        status, response = self.data_utils.post_api_request(self.user,url_part, url_data)

        #Put an updated url on the video and set it as primary 
        put_url = 'videos/{0}/urls/{1}/'.format(video_id, response['id'])
        put_data = { 'url': 'http://unisubs.example.com/newerurl.mp4', 
                      'primary': True }
        status, response = self.data_utils.put_api_request(self.user,put_url, put_data) 
        
        self.assertEqual('http://unisubs.example.com/newerurl.mp4', response['url'])
        video_pg = video_page.VideoPage(self)
        video_pg.open_video_page(video_id)
        self.assertEqual('http://unisubs.example.com/newerurl.mp4', self.test_video.get_video_url())


    def test_url__delete(self):
        """Delete a url.

           POST /api2/partners/videos/[video-id]/urls/
           DELETE /api2/partners/videos/[video-id]/urls/[url-id]/
        """
        video_id = self.test_video.video_id
        video_url = self.test_video.get_video_url()
        url_data = { 'url': 'http://unisubs.example.com/newurl.mp4'}
        url_part = 'videos/%s/urls/' % video_id
        status, response = self.data_utils.post_api_request(self.user,url_part, url_data)
        self.logger.info( self.test_video.get_video_url())
        update_url = 'videos/{0}/urls/{1}/'.format(video_id, response['id'])
        status, response = self.data_utils.delete_api_request(self.user, update_url) 
        self.assertEqual(status, 204)
        self.assertNotEqual(self.test_video.get_video_url(), 'http://unisubs.example.com/newurl.mp4')

    def test_url__delete_primary(self):
        """Delete the primary url. 

           POST /api2/partners/videos/[video-id]/urls/
           DELETE /api2/partners/videos/[video-id]/urls/[url-id]/
        """
        video_id = self.test_video.video_id
        video_url = self.test_video.get_video_url()
        self.logger.info( video_url)
        url_data = { 'url': 'http://unisubs.example.com/newurl.mp4',
                     'primary': True }
        url_part = 'videos/%s/urls/' % video_id
        status, response = self.data_utils.post_api_request(self.user,url_part, url_data)
        self.logger.info( self.test_video.get_video_url())
        update_url = 'videos/{0}/urls/{1}/'.format(video_id, response['id'])
        status, response = self.data_utils.delete_api_request(self.user, update_url) 
        self.assertEqual(status, 204)
        self.logger.info( self.test_video.get_video_url())
        self.assertNotEqual(self.test_video.get_video_url(), 'http://unisubs.example.com/newurl.mp4')

    def test_url__delete_last(self):
        """Can not delete the last (only) url.  

        If this is the only URL for a video, the request will fail. 
        A video must have at least one URL.  
        """
        video_id = self.test_video.video_id
        expected_url = self.test_video.get_video_url()
        #Get a list of the current urls
        url_part = 'videos/%s/urls/' % video_id
        status, response = self.data_utils.api_get_request(self.user,url_part) 
        

        url_objects = response['objects']
        id_list = []
        for url in url_objects:
            id_list.append(url['id'])
        for url_id in sorted(id_list, reverse=True):
            url_part = 'videos/%s/urls/' % url_id 
            update_url = 'videos/{0}/urls/{1}/'.format(video_id, url_id)
            status, response =  self.data_utils.delete_api_request(self.user, update_url) 

        #Open the video page on the ui - for the verification screenshot
        video_pg = video_page.VideoPage(self)
        video_pg.open_video_page(video_id)
        self.assertEqual(expected_url, self.test_video.get_video_url())







        
