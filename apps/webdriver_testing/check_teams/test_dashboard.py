# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import auth_page
from apps.webdriver_testing.site_pages.teams import dashboard_tab
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import UserFactory
from apps.teams.models import TeamMember

class TestCaseTeamDashboard(WebdriverTestCase):
    """Verify team dashboard displays the videos and needs.

    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.auth_pg = auth_page.AuthPage(self)
        self.team = TeamMemberFactory.create(team__name='Roles Test',
                                             team__slug='roles-test',
                                             user__username='team_owner',
                                             )
    def test_assign__manager_project_lang_restrictions(self):
        """Assign a manager with project restrictions.

           Verify the display of the roles in the members tab.
        """
        self.auth_pg.login('team_owner', 'password')




