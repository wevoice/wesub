# -*- coding: utf-8 -*-
import os
import time
import itertools
import operator
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamContributorMemberFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import TeamLangPrefFactory
from apps.webdriver_testing.data_factories import WorkflowFactory
from apps.webdriver_testing.data_factories import VideoFactory
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.pages.site_pages.teams_dir_page import TeamsDirPage
from apps.webdriver_testing.pages.site_pages.teams import tasks_tab

class TestCaseTeamTaskResource(WebdriverTestCase):
    """TestSuite for getting and modifying video urls via api_v2.

       One can list, update, delete and add video urls to existing videos.
 	
    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseTeamTaskResource, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create(
            username='TestUser',
            is_superuser = True,
            is_staff = True,
            is_partner = True)
        cls.data_utils.create_user_api_key(cls.user)

        #Create a test video
        cls.test_video = VideoFactory.create()
        cls.test_video.get_or_create_for_url(
            'http://unisubs.example.com/testvid1.mp4')

        #CREATE AN OPEN TEAM WITH WORKFLOWS and AUTOTASKS
        cls.open_team = TeamMemberFactory.create(
            team__name='Literal Video Version',
            team__slug='literal-video-version',
            team__workflow_enabled = True,
            user = cls.user,
            ).team
        #Turn on Task Autocreation
        WorkflowFactory.create(
            team = cls.open_team,
            autocreate_subtitle = True,
            autocreate_translate = True,
            review_allowed = 10)

        #ADD SOME PREFERRED LANGUAGES TO THE TEAM
        lang_list = ['es', 'ru', 'pt-br']
        for language in lang_list:
            TeamLangPrefFactory.create(
                team = cls.open_team,
                language_code = language,
                preferred = True)

        #ADD SOME VIDEOS TO THE TEAM
        cls.videos = cls.data_utils.create_several_team_videos_with_subs(
            cls.open_team, 
            cls.user,
            data = 'apps/webdriver_testing/subtitle_data/few_vids_with_subs.json') 
        TeamVideoFactory.create(
            team=cls.open_team, 
            video=cls.test_video, 
            added_by=cls.user)

        #Login to display tasks tab
        cls.tasks_tab = tasks_tab.TasksTab(cls)
        cls.tasks_tab.open_tasks_tab(cls.open_team.slug)
        cls.tasks_tab.log_in(cls.user.username, 'password')

    def test_tasks__list(self):
        """List off the existing tasks. 

        GET /api2/partners/teams/[team-slug]/tasks/
        """
        url_part = 'teams/%s/tasks/' % self.open_team.slug
        status, response = self.data_utils.api_get_request(self.user,url_part) 
        task_objects =  response['objects']
        print task_objects
        tasks_list = []
        for k, v in itertools.groupby(task_objects, 
            operator.itemgetter('video_id')):
                tasks_list.append(k)
        self.assertEqual(4, len(tasks_list))


    def test_tasks__query_video_id(self):
        """Query for tasks of a video_id. 

        GET /api2/partners/teams/[team-slug]/tasks/
        """
        url_part = 'teams/{0}/tasks/?video_id={1}'.format(
            self.open_team.slug, self.test_video.video_id)
        status, response = self.data_utils.api_get_request(self.user,url_part) 
        
        task_objects =  response['objects']
        self.assertEqual(1, len(task_objects)) 


    def test_query__assignee(self):
        """Query for a subset of tasks.
       
        GET /api2/partners/teams/[team-slug]/tasks/
        """

        #Create a task assigned to a user
        url_part = 'teams/%s/tasks/' % self.open_team.slug
        task_data = {   "type": "Subtitle",
                        "video_id": self.test_video.video_id,
                        "language": "en",
                        "assignee": self.user.username
                    }

        status, response = self.data_utils.post_api_request(self.user, url_part,
            task_data)

        url_part = 'teams/%s/tasks/?assignee=TestUser' % self.open_team.slug

        status, response = self.data_utils.api_get_request(self.user,url_part) 
        
        task_objects =  response['objects']
        self.assertEqual(self.test_video.video_id, task_objects[0]['video_id'])

 
    def test_tasks__details(self):
        """Get the details of a taks.

        GET /api2/partners/teams/[team-slug]/tasks/[task-id]/
        """
        url_part = 'teams/%s/tasks/' % self.open_team.slug
        task_data = {   "type": "Subtitle",
                        "video_id": self.test_video.video_id,
                        "language": "en"
                    }
        status, response = self.data_utils.post_api_request(self.user, url_part,
            task_data)
        url_part = 'teams/{0}/tasks/{1}/'.format(self.open_team.slug, 
            response['id'])

        del task_data['language']
        status, response = self.data_utils.api_get_request(self.user,url_part) 
        
        for k, v in task_data.iteritems():
            self.assertEqual(v, response[k])



    def test_tasks__create(self):
        """Create a new task for a video.

        POST /api2/partners/teams/[team-slug]/tasks/
        """

        url_part = 'teams/%s/tasks/' % self.open_team.slug
        task_data = {   "type": "Subtitle",
                        "video_id": self.test_video.video_id,
                        "language": "en"
                    }
        status, response = self.data_utils.post_api_request(self.user, url_part,
            task_data)

        del task_data['language']

        self.tasks_tab.open_tasks_tab(self.open_team.slug)
        for k, v in task_data.iteritems():
            self.assertEqual(v, response[k])


    def test_tasks__update(self):
        """Update a task 

        PUT /api2/partners/teams/[team-slug]/tasks/[task-id]/
        """
        url_part = 'teams/%s/tasks/' % self.open_team.slug
        task_data = {   "type": "Subtitle",
                        "video_id": self.test_video.video_id,
                        "language": "en"
                    }
        status, response = self.data_utils.post_api_request(self.user, url_part,
            task_data)


        url_part = 'teams/{0}/tasks/{1}/'.format(self.open_team.slug, 
            response['id'])
 
        updated_info = {'priority': 3} 
        status, response = self.data_utils.put_api_request(self.user, url_part, 
            updated_info) 
        self.assertEqual(updated_info['priority'], response['priority'])

    def test_tasks__delete(self):
        """Delete a task.

           DELETE /api2/partners/teams/[team-slug]/tasks/[task-id]/
        """
        #Post a new task
        url_part = 'teams/%s/tasks/' % self.open_team.slug
        task_data = {   "type": "Subtitle",
                        "video_id": self.test_video.video_id,
                        "language": "en"
                    }
        status, response = self.data_utils.post_api_request(self.user, url_part,
            task_data)
        task_id = response['id']
        #Make the DELETE request
        url_part = 'teams/{0}/tasks/{1}/'.format(self.open_team.slug, task_id)

        status, response = self.data_utils.delete_api_request(self.user, url_part) 
        url_part = 'teams/%s/tasks/' % self.open_team.slug
        status, response = self.data_utils.api_get_request(self.user,url_part) 
        task_objects =  response['objects']
        task_ids = []
        for k, v in itertools.groupby(task_ids, 
            operator.itemgetter('id')):
                tasks_list.append(k)
        self.tasks_tab.open_tasks_tab(self.open_team.slug)
        self.assertNotIn(task_id, task_ids)

