# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import auth_page
from apps.webdriver_testing.site_pages import my_teams
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import UserFactory
 
from apps.teams.models import TeamMember

class TestCaseTeamTasks(WebdriverTestCase):
    """Verify tasks creation, modification, assignment.

        Assign a task
        Create a manual task
        Automatic task creation
        Filter tasks
        Perform task
        Remove a task from a team
Tasks link opens the page with the tasks for the video 
- Non-members and anon users do not see Tasks links
- Just added, non-subtitled video has tag "1 language needed" (if a task is created automatically) or "0 languages" (otherwise), the tag has an appropriate link 
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




    def test_create(self):
        """Create a manual transcription task
        
        """
        self.assertFalse('This test needs to be written.')
        self.auth_pg.login('team_owner', 'password')




