# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages.teams_dir_page import TeamsDirPage
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import UserFactory
 
from apps.teams.models import TeamMember

class TestCaseTeamSettings(WebdriverTestCase):
    """Test suite for managing team settings. """

    def setUp(self):
        super(TestCaseTeamSettings, self).setUp()
        self.skipTest('Incomplete test suite')
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







