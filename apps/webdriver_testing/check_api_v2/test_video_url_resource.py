import os
import time
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.data_factories import UserFactory
from webdriver_testing import data_helpers
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing.pages.site_pages import watch_page


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
        
        cls.test_video = cls.data_utils.create_video()


    def test_list(self):
        """Verify video urls for a particular video are listed.

        GET /api2/partners/videos/[video-id]/urls/
        """
        video_id = self.test_video.video_id
        video_url = self.test_video.get_video_url() 
        url_part = 'videos/%s/urls/' % video_id

        r = self.data_utils.make_request(self.user, 'get', url_part)
        response = r.json
        video_pg = video_page.VideoPage(self)
        video_pg.open_video_page(video_id)

        self.assertEqual(video_url, response['objects'][0]['url'])

    def test_url_post(self):
        """Add an additional new url.

           POST /api2/partners/videos/[video-id]/urls/
        """
        video = self.data_utils.create_video()
        video_url = video.get_video_url()

        data = { 'url': 'http://unisubs.example.com/newurl8.mp4' }
        url_part = 'videos/%s/urls/' % video.video_id
        r = self.data_utils.make_request(self.user, 'post', url_part, **data)
        self.assertEqual(r.status_code, 201)



    def test_url_put(self):
        """Add a second url.

           PUT /api2/partners/videos/[video-id]/urls/[url-id]/
        """
        #Post an additional url to the video
        video_id = self.test_video.video_id
        video_url = self.test_video.get_video_url()
        data = { 'url': 'http://unisubs.example.com/newurl.mp4' }
        url_part = 'videos/%s/urls/' % video_id
        r = self.data_utils.make_request(self.user, 'post', url_part, **data)
        response = r.json

        #Put an updated url on the video and set it as primary 
        put_url = 'videos/{0}/urls/{1}/'.format(video_id, response['id'])
        put_data = { 'url': 'http://unisubs.example.com/newerurl.mp4'}
        r = self.data_utils.make_request(self.user, 'put', put_url, **put_data)
        response = r.json

        video_pg = video_page.VideoPage(self)
        video_pg.open_video_page(video_id)

        self.assertEqual('http://unisubs.example.com/newerurl.mp4', response['url'])

    def test_put_primary(self):
        """Verify video urls for a particular video are listed.

           PUT /api2/partners/videos/[video-id]/urls/[url-id]/
        """
        #Post an additional url to the video
        video_id = self.test_video.video_id
        video_url = self.test_video.get_video_url()
        data = { 'url': 'http://unisubs.example.com/newurl.mp4' }
        url_part = 'videos/%s/urls/' % video_id
        r = self.data_utils.make_request(self.user, 'post', url_part, **data)
        response = r.json

        #Put an updated url on the video and set it as primary 
        put_url = 'videos/{0}/urls/{1}/'.format(video_id, response['id'])
        put_data = { 'url': 'http://unisubs.example.com/newerurl.mp4', 
                      'primary': True }

        r = self.data_utils.make_request(self.user, 'put', put_url, **put_data)
        response = r.json
        
        self.assertEqual('http://unisubs.example.com/newerurl.mp4', response['url'])
        video_pg = video_page.VideoPage(self)
        video_pg.open_video_page(video_id)
        self.assertEqual('http://unisubs.example.com/newerurl.mp4', self.test_video.get_video_url())


    def test_url_delete(self):
        """Delete a url.

           POST /api2/partners/videos/[video-id]/urls/
           DELETE /api2/partners/videos/[video-id]/urls/[url-id]/
        """
        video = self.data_utils.create_video()
        video_url = video.get_video_url()

        data = { 'url': 'http://unisubs.example.com/newurl3.mp4'}
        url_part = 'videos/%s/urls/' % video.video_id
        r = self.data_utils.make_request(self.user, 'post', url_part, **data)
        response = r.json

        update_url = 'videos/{0}/urls/{1}/'.format(video.video_id, response['id'])
        self.data_utils.make_request(self.user, 'delete', update_url)
        self.assertEqual(r.status_code, 201)

    def test_url_delete_primary(self):
        """Delete the primary url. 

           POST /api2/partners/videos/[video-id]/urls/
           DELETE /api2/partners/videos/[video-id]/urls/[url-id]/
        """
        video_id = self.test_video.video_id
        video_url = self.test_video.get_video_url()
        self.logger.info(video_url)
        data = { 'url': 'http://unisubs.example.com/newurl.mp4',
                     'primary': True }
        url_part = 'videos/%s/urls/' % video_id
        r = self.data_utils.make_request(self.user, 'post', url_part, **data)
        response = r.json
        update_url = 'videos/{0}/urls/{1}/'.format(video_id, response['id'])
        r = self.data_utils.make_request(self.user, 'delete', update_url)
        self.logger.info(r.content)
        self.assertEqual(r.status_code, 204)
        self.assertNotEqual(self.test_video.get_video_url(), 'http://unisubs.example.com/newurl.mp4')

    def test_url_delete_last(self):
        """Can not delete the last (only) url.  

        If this is the only URL for a video, the request will fail. 
        A video must have at least one URL.  
        """
        video = self.data_utils.create_video()
        expected_url = video.get_video_url()

        #add a few more urls
        data = { 'url': 'http://unisubs.example.com/new1.mp4' }
        url_part = 'videos/%s/urls/' % video.video_id
        self.data_utils.make_request(self.user, 'post', url_part, **data)
        data = { 'url': 'http://unisubs.example.com/new2.mp4' }
        url_part = 'videos/%s/urls/' % video.video_id
        self.data_utils.make_request(self.user, 'post', url_part, **data)

 

        #Get a list of the current urls
        url_part = 'videos/%s/urls/' % video.video_id
        r = self.data_utils.make_request(self.user, 'get', url_part)
        self.logger.info(r.status_code)
        response = r.json

        url_objects = response['objects']
        id_list = []
        for url in url_objects:
            id_list.append(url['id'])
        for url_id in sorted(id_list, reverse=True):
            url_part = 'videos/%s/urls/' % url_id 
            update_url = 'videos/{0}/urls/{1}/'.format(video.video_id, url_id)
            r = self.data_utils.make_request(self.user, 'delete', update_url)
        self.assertEqual('The last video url cannot be deleted', r.content)
        #Open the video page on the ui - for the verification screenshot
        self.assertEqual(expected_url, video.get_video_url())







        
