# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import auth_page
from apps.webdriver_testing.site_pages import my_teams
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import UserFactory
 
from apps.teams.models import TeamMember

class TestCaseTeamSettings(WebdriverTestCase):
    """
        Projects:
            add_project.pending
            edit_project (name / description)
            delete_project
        Languages:
            set preferred languages (auto-task creation)
            set blacklisted languages 
                not displayed
                can't blacklist preferred language
        Messages:
            edit_message_admin.pending
            edit_message_application.pending
            edit_message_invitation.pending
            edit_message_manager.pending
            edit_guidelines_review.pending
            edit_guidelines_subtitle.pending
            edit_guidelines_translation.pending
        Team Details:
            edit_description
            edit visibility (public / private)
            edit logo
             - too large > 940x235

        Workflows:
            edit_permissions_join.pending
            edit_permissions_subtitle.pending
            edit_permissions_task.pending
            edit_permissions_translation.pending
            edit_permissions_video_management.pending

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





