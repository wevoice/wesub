import os
import time
import itertools
import operator
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamAdminMemberFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory

from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.pages.site_pages.teams import ATeamPage

class TestCaseTeamProjectResource(WebdriverTestCase):
    """TestSuite for getting and modifying video urls via api_v2.

       One can list, update, delete and add video urls to existing videos.
    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseTeamProjectResource, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()

        cls.user = UserFactory.create(username = 'TestUser', is_partner=True)
        cls.team_owner = UserFactory.create(username = 'team_owner')
        cls.data_utils.create_user_api_key(cls.user)

        #create an open team with description text and 2 members
        cls.open_team = TeamMemberFactory.create(
            team__name="Cool team",
            team__slug='team-with-projects',
            team__description='this is the coolest, most creative team ever',
            user = cls.team_owner,
            ).team
        TeamAdminMemberFactory(team=cls.open_team, 
            user = cls.user)
        #Open to the teams page so you can see what's there.
        cls.project1 = TeamProjectFactory(
            team=cls.open_team,
            name='team project one',
            slug = 'team-project-one',
            description = 'subtitle project number 1',
            guidelines = 'do a good job',
            workflow_enabled=False)
        
        cls.project2 = TeamProjectFactory(
            team=cls.open_team,
            name='team project two',
            workflow_enabled=True)

        cls.team_pg = ATeamPage(cls)
        cls.team_pg.open_team_page(cls.open_team.slug)

    def test_projects__list(self):
        """List off the teams projects.

        GET /api2/partners/teams/[team-slug]/projects/
        """
        expected_projects = ['team project one', 'team project two'] 
        url_part = 'teams/%s/projects/' % self.open_team.slug
        status, response = self.data_utils.api_get_request(self.user, url_part) 
        self.assertNotEqual(None, response)
        project_objects = response['objects']
        projects_list = []
        for k, v in itertools.groupby(
            project_objects, 
            operator.itemgetter('name')):
                projects_list.append(k)
        self.assertEqual(expected_projects, projects_list)



    def test_projects__details(self):
        """Get the details of a project.

           GET /api2/partners/teams/[team-slug]/projects/[project-slug]/
        """
        expected_data = { 'description': 'subtitle project number 1',
                          'guidelines': 'do a good job',
                          'name': 'team project one',
                          'slug': 'team-project-one',
                          'workflow_enabled': False }

        url_part = 'teams/{0}/projects/{1}/'.format(self.open_team.slug,
            self.project1.slug)
        _, response = self.data_utils.api_get_request(self.user, url_part) 

        for k, v in expected_data.iteritems():
            self.assertEqual(v, response[k])


    def test_projects__create(self):
        """Create a new project for the team.

        POST /api2/partners/teams/[team-slug]/projects/
        """

        url_part = 'teams/%s/projects/' % self.open_team.slug
        project_data = {
                     "name": "Project name",
                     "slug": "project-slug",
                     "description": "This is an example project.",
                     "guidelines": "Only post family-friendly videos."
                    }
        status, response = self.data_utils.post_api_request(self.user, url_part,
            project_data)
        self.team_pg.open_team_page(self.open_team.slug)
        

        self.assertTrue(self.team_pg.has_project(project_data['slug']))



    def test_projects__update(self):
        """Update a projects information.

        PUT /api2/partners/teams/[team-slug]/projects/[project-slug]/
        """
        url_part = 'teams/{0}/projects/{1}/'.format(self.open_team.slug,
            self.project1.slug)
 
        updated_info = {
            'description': 'this a an updated test description' 
            } 
        status, response = self.data_utils.put_api_request(self.user, url_part, 
            updated_info) 
        
        self.assertEqual(updated_info['description'], response['description'])

    def test_projects__delete(self):
        """Delete a team project.

           DELETE /api2/partners/teams/[team-slug]/projects/[project-slug]/
        """
        url_part = 'teams/{0}/projects/{1}/'.format(self.open_team.slug,
           self.project1.slug)
        
        self.data_utils.delete_api_request(self.user, url_part) 
        self.team_pg.open_team_page(self.open_team.slug)

        #Verify project 1 is still present
        self.assertTrue(self.team_pg.has_project(self.project2.slug)) 

        #Verify project2 is deleted
        self.assertFalse(self.team_pg.has_project(self.project1.slug)) 
