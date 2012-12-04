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
from apps.webdriver_testing.site_pages import a_team_page

class TestCaseTeamProjectResource(WebdriverTestCase):
    """TestSuite for getting and modifying video urls via api_v2.

       One can list, update, delete and add video urls to existing videos.
    """

    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'TestUser', is_partner=True)
        self.team_owner = UserFactory.create(username = 'team_owner')
        data_helpers.create_user_api_key(self, self.user)

        #create an open team with description text and 2 members
        self.open_team = TeamMemberFactory.create(
            team__name="Cool team",
            team__slug='team-with-projects',
            team__description='this is the coolest, most creative team ever',
            user = self.team_owner,
            ).team
        TeamAdminMemberFactory(team=self.open_team, 
            user = self.user)
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

        self.team_pg = a_team_page.ATeamPage(self)
        self.team_pg.open_team_page(self.open_team.slug)

    def test_projects__list(self):
        """List off the teams projects.

        GET /api2/partners/teams/[team-slug]/projects/
        """
        expected_projects = ['team project one', 'team project two'] 
        url_part = 'teams/%s/projects/' % self.open_team.slug
        status, response = data_helpers.api_get_request(self, url_part) 
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
        _, response = data_helpers.api_get_request(self, url_part) 

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
        status, response = data_helpers.post_api_request(self, url_part,
            project_data)
        self.team_pg.open_team_page(self.open_team.slug)
        print response

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
        status, response = data_helpers.put_api_request(self, url_part, 
            updated_info) 
        print response
        self.assertEqual(updated_info['description'], response['description'])

    def test_projects__delete(self):
        """Delete a team project.

           DELETE /api2/partners/teams/[team-slug]/projects/[project-slug]/
        """
        url_part = 'teams/{0}/projects/{1}/'.format(self.open_team.slug,
           self.project1.slug)
        
        data_helpers.delete_api_request(self, url_part) 
        self.team_pg.open_team_page(self.open_team.slug)

        #Verify project 1 is still present
        self.assertTrue(self.team_pg.has_project(self.project2.slug)) 

        #Verify project2 is deleted
        self.assertFalse(self.team_pg.has_project(self.project1.slug)) 
