# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import auth_page
from apps.webdriver_testing.site_pages import my_teams
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import UserFactory
 
from apps.teams.models import TeamMember

class WebdriverTestCaseTeamTasks(WebdriverTestCase):
    """Verify tasks creation, modification, assignment.

        Feature: Assign a task
	As a team member with permission to assign tasks
	I want to assign an unassigned task
	So that the task may be completed

	Scenario: Assign a Feature: Filter tasks by language
	As a visitor or user
	I want to view tasks for a specific language
	So that I can find ways to contribute given my skills

	Scenario: 
		Given I am on the team tasks page
		And the language filter list contains all languages with active tasks
		When I select a language in the list
		Then I see only the tasks for that languageFeature:

        Scenario:  Filter tasks by language - results
        Scenario: Filter tasks by language - no results
        Scenario: Perform task

        Filter tasks by type - results
        Filter tasks by type - no results


        Feature: Remove a task from a team
	As a team member with permission to assign tasks
	I want to remove a task from the team
	So that it is no longer shown for the team

	Scenario: Remove a task
		Given I am on the team tasks page
		When I click the remove button on a task
		Then that task is removed from the team and I don't see it listed 
        Scenario: Create a task manually
        Scenario: Create tasks automatically

    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.auth_pg = auth_page.AuthPage(self)
        self.my_teams_pg = my_teams.MyTeam(self)
        self.team = TeamMemberFactory.create(team__name='Roles Test',
                                             team__slug='roles-test',
                                             user__username='team_owner',
                                             )
        self.manager_test_user = TeamMemberFactory.create(team=self.team.team,
                                 user=UserFactory.create(username=
                                                         'promotedToManager'),
                                 role=TeamMember.ROLE_CONTRIBUTOR)
        self.admin_test_user = TeamMemberFactory.create(team=self.team.team,
                                 user=UserFactory.create(username=
                                                         'promotedToAdmin'),
                                 role=TeamMember.ROLE_CONTRIBUTOR)
        TeamProjectFactory.create(team=self.team.team,
                                  name='my translation project',
                                  workflow_enabled=True,
                                  )




    def test_assign__manager_project_lang_restrictions(self):
        """Assign a manager with project restrictions.

           Verify the display of the roles in the members tab.
        """
        self.auth_pg.login('team_owner', 'password')




