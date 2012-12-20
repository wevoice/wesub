# -*- coding: utf-8 -*-
from apps.webdriver_testing.check_local.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages import auth_page
from apps.webdriver_testing.pages.site_pages.teams_dir_page import TeamsDirPage
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import UserFactory
 
from apps.teams.models import TeamMember

class TestCaseTeamSettings(WebdriverTestCase):
    """

        Videos:
            who can edit
            who can add

        Projects:
            add_project.pending
            edit_project (name / description)
            delete_project
        Languages:
            set preferred languages (auto-task creation)
            set blacklisted languages 
                not displayed
                can't blacklist preferred language
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
        self.team_dir_pg = TeamsDirPage(self)
        self.team = TeamMemberFactory.create(team__name='Roles Test',
                                             team__slug='roles-test',
                                             user__username='team_owner',
                                             )
        self.normal_user = TeamMemberFactory.create(team=self.team.team,
                                 user=UserFactory.create(username=
                                                         'normal_user'),
                                 role=TeamMember.ROLE_CONTRIBUTOR)
        TeamProjectFactory.create(team=self.team.team,
                                  name='my translation project',
                                  workflow_enabled=True,
                                  )




    def test_remove__no_link(self):
        """No remove link for users who can't remove videos.

        """







