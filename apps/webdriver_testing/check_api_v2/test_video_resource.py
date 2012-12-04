import time
import itertools
import operator
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.site_pages import video_page 
from apps.webdriver_testing.site_pages.teams import videos_tab

class TestCaseVideoResource(WebdriverTestCase):
    """TestSuite for videos via the api

    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user')
        data_helpers.create_user_api_key(self, self.user)
        self.test_video = data_helpers.create_video(self, 
            'http://www.example.com/upload_test.mp4')
        self.open_team = TeamMemberFactory.create(
            team__name="Cool team",
            team__slug='team-with-projects',
            team__description='this is the coolest, most creative team ever',
            user = self.user,
            ).team
        #Open to the teams page so you can see what's there.
        self.project1 = TeamProjectFactory(
            team=self.open_team,
            name='team project one',
            slug = 'team-project-one',
            description = 'subtitle project number 1',
            guidelines = 'do a good job',
            workflow_enabled=False)
        
        self.project2 = TeamProjectFactory(
            team=self.open_team,
            name='team project two',
            workflow_enabled=True)

        self.video_pg = video_page.VideoPage(self)

    def test_video__list(self):
        """List the available videos.

        GET /api2/partners/videos/
        video_url 
        team  
        project
        order_by 
            title: ascending
            -title: descending
            created: older videos first
            -created : newer videos
        """
        for x in range(5):
            TeamVideoFactory.create(team=self.open_team, 
                added_by=self.user,
                project = self.project1)
        url_part = 'videos/'
        status, response = data_helpers.api_get_request(self, url_part)
        video_objects =  response['objects']
        videos_list = []
        for k, v in itertools.groupby(video_objects, 
            operator.itemgetter('id')):
                videos_list.append(k)
        self.assertIn(self.test_video.video_id, videos_list)

    def test_query__project(self):
        """List the available videos.

        GET /api2/partners/videos/
        video_url 
        team  
        project
        order_by 
            title: ascending
            -title: descending
            created: older videos first
            -created : newer videos
        """
        for x in range(5):
            TeamVideoFactory.create(team=self.open_team, 
                added_by=self.user,
                project = self.project1)
        url_part = 'videos/?project=%s' %self.project1.slug
        status, response = data_helpers.api_get_request(self, url_part)
        video_objects =  response['objects']
        videos_list = []
        for k, v in itertools.groupby(video_objects, 
            operator.itemgetter('id')):
                videos_list.append(k)
        self.assertEqual(5, len(videos_list))

    def test_query__team(self):
        """List the available videos.

        GET /api2/partners/videos/team=<team slug>
        """
        for x in range(5):
            TeamVideoFactory.create(team=self.open_team, 
                added_by=self.user,
                project = self.project1)
        url_part = 'videos/?team=%s' %self.open_team.slug
        status, response = data_helpers.api_get_request(self, url_part)
        video_objects =  response['objects']
        videos_list = []
        for k, v in itertools.groupby(video_objects, 
            operator.itemgetter('id')):
                videos_list.append(k)
        self.assertEqual(5, len(videos_list))

    def test_sort__newest(self):
        """List the available videos.

        GET /api2/partners/videos/
        """
        team_vid_list = []
        for x in range(3):
            vid = TeamVideoFactory.create(team=self.open_team, 
                added_by=self.user,
                project = self.project1).video
            team_vid_list.append(vid.title)
            
            time.sleep(1)
        url_part = 'videos/?order_by=-created' 
        status, response = data_helpers.api_get_request(self, url_part)
        video_objects =  response['objects']
        videos_list = []
        for k, v in itertools.groupby(video_objects, 
            operator.itemgetter('title')):
                videos_list.append(k)

        self.assertEqual(team_vid_list[-1], videos_list[0])

    def test_sort__title(self):
        """List the available videos sorted by title (desc)

        GET /api2/partners/videos/
        """
        for x in range(3):
            TeamVideoFactory.create(team=self.open_team, 
                added_by=self.user,
                project = self.project1)
        TeamVideoFactory.create(team=self.open_team, 
                added_by=self.user,
                project = self.project1,
                video__title = 'Zzz-test-video')


        url_part = 'videos/?order_by=-title' 
        status, response = data_helpers.api_get_request(self, url_part)
        print response
        video_objects =  response['objects']
        videos_list = []
        for k, v in itertools.groupby(video_objects, 
            operator.itemgetter('title')):
                videos_list.append(k)
        self.assertEqual('Zzz-test-video', videos_list[0])

    def test_video__create(self):
        """Add a new video.

        POST /api2/partners/videos/
        """

        url_data = { 'video_url': ('http://qa.pculture.org/amara_tests/'
                                   'Birds_short.webmsd.webm'),
                     'title': 'Test video created via api',
                     'duration': 37 }
        url_part = 'videos/'
        status, response = data_helpers.post_api_request(self, 
            url_part, url_data)
        self.video_pg.open_video_page(response['id'])
        #Check response metadata
        for k, v in url_data.iteritems():
            self.assertEqual(v, response[k])

        #Check video displays on the site
        self.assertTrue(self.video_pg.video_embed_present())


    def test_video__details(self):
        """Get video details.

        GET /api2/partners/videos/[video-id]/
        """

        expected_data = {
            'all_urls': ['http://www.youtube.com/watch?v=WqJineyEszo'], 
            'title': ('X Factor Audition - Stop Looking At My Mom Rap -'
                      ' Brian Bradley'),
            'languages': [], 
            'thumbnail': 'http://i.ytimg.com/vi/WqJineyEszo/0.jpg', 
            'duration': 121, 
            }
        
        test_video = data_helpers.create_video(self)
        url_part = 'videos/%s' % test_video.video_id
        status, response = data_helpers.api_get_request(self, url_part)
        self.video_pg.open_video_page(response['id'])
        for k, v in expected_data.iteritems():
            self.assertEqual(v, response[k])

        
    def test_update__metatdata(self):
        """Update video metadata, title, description.

        PUT /api2/partners/videos/[video-id]/
        """

        url_data = { 'video_url': ('http://qa.pculture.org/amara_tests/'
                                   'Birds_short.webmsd.webm'),
                     'title': 'Test video created via api',
                     'duration': 37 }
        url_part = 'videos/'
        status, response = data_helpers.post_api_request(self, 
            url_part, url_data)
        vid_id = response['id']

        url_part = 'videos/%s' % vid_id
        new_data = {'title': 'MVC webM output sample',
                    'description': ('This is a sample vid converted to webM '
                                   '720p using Miro Video Converter')
                   }
        status, response = data_helpers.put_api_request(self, url_part, 
            new_data)
        self.video_pg.open_video_page(vid_id)

        #Check response metadata
        for k, v in new_data.iteritems():
            self.assertEqual(v, response[k])

        #Check video displays on the site
        self.assertEqual(new_data['description'], 
            self.video_pg.description_text())

    def test_update__team(self):
        """Update the video metadata, add to team and edit video description.

        PUT /api2/partners/videos/[video-id]/
        """

        url_data = { 'video_url': ('http://qa.pculture.org/amara_tests/'
                                   'Birds_short.webmsd.webm'),
                     'title': 'Test video created via api',
                     'duration': 37 }
        url_part = 'videos/'
        status, response = data_helpers.post_api_request(self, 
            url_part, url_data)
        vid_id = response['id']

        url_part = 'videos/%s' % vid_id
        new_data = {'team': self.open_team.slug,
                    'description': ('This is a sample vid converted to webM '
                                   '720p using Miro Video Converter')
                   }
        status, response = data_helpers.put_api_request(self, url_part, 
            new_data)
        self.video_pg.open_video_page(vid_id)

        #Check response metadata
        for k, v in new_data.iteritems():
            self.assertEqual(v, response[k])

        #Check the team is listed on the video page 
        self.assertTrue(self.video_pg.team_slug(self.open_team.slug))

    def test_update__project(self):
        """Edit video, add it to a team and project.

        PUT /api2/partners/videos/[video-id]/
        """
        #Create the initial video via api and get the id
        url_data = { 'video_url': ('http://qa.pculture.org/amara_tests/'
                                   'Birds_short.webmsd.webm'),
                     'title': 'Test video created via api',
                     'duration': 37 }
        url_part = 'videos/'
        status, response = data_helpers.post_api_request(self, 
            url_part, url_data)
        vid_id = response['id']

        #Update the video setting the team and project and new description.
        url_part = 'videos/%s' % vid_id
        new_data = {'team': self.open_team.slug,
                    'project': self.project2.slug,
                    'description': ('This is a sample vid converted to webM '
                                   '720p using Miro Video Converter')
                   }
        status, response = data_helpers.put_api_request(self, url_part, 
            new_data)
        self.video_pg.open_video_page(vid_id)

        #Check response metadata
        for k, v in new_data.iteritems():
            self.assertEqual(v, response[k])

        #Open the projects page on the site and verify video in project.
        team_videos_tab = videos_tab.VideosTab(self)
        team_videos_tab.log_in(self.user.username, 'password')
        team_videos_tab.open_team_project(self.open_team.slug, 
                                          self.project2.slug)
        self.assertTrue(team_videos_tab.video_present(url_data['title']))


