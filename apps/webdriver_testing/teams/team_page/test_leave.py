# -*- coding: utf-8 -*-

from nose.tools import assert_true, assert_false, assert_equal
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import a_team_page, my_teams
from apps.webdriver_testing.site_pages import auth_page
from apps.webdriver_testing.site_pages.teams import members
from apps.webdriver_testing.testdata_factories import *
from apps.teams.models import TeamMember


class WebdriverTestCaseLeaveTeam(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.auth_pg = auth_page.AuthPage(self)
        self.my_teams_pg = my_teams.MyTeam(self)
        self.team = TeamMemberFactory.create(team__name='manage invitation team', 
                                             team__slug='invitation-only',
                                             team__membership_policy=2,  #manager invite-only
                                             user__username='invitation_team_owner', 
                                             )


    def test_leave__contributer(self):
        TeamMemberFactory.create(team=self.team.team, 
                                 user=UserFactory.create(username='tester'),
                                 role = TeamMember.ROLE_CONTRIBUTOR)

        self.auth_pg.login('tester', 'password')
        self.my_teams_pg.leave_team('invitation-only')
        assert_true(self.my_teams_pg.leave_team_successful())

    def test_leave__second_to_last_owner(self):
        TeamMemberFactory.create(team=self.team.team, 
                                 user=UserFactory.create(username='testOwner'),
                                 role = TeamMember.ROLE_OWNER)

        self.auth_pg.login('testOwner', 'password')
        self.my_teams_pg.leave_team('invitation-only')
        assert_true(self.my_teams_pg.leave_team_successful())

    def test_leave__admin(self):
        TeamMemberFactory.create(team=self.team.team, 
                                 user=UserFactory.create(username='testAdmin'),
                                 role = TeamMember.ROLE_ADMIN)

        self.auth_pg.login('testAdmin', 'password')
        self.my_teams_pg.leave_team('invitation-only')
        assert_true(self.my_teams_pg.leave_team_successful())


    def test_leave__last_owner(self):
        self.auth_pg.login('invitation_team_owner', 'password')
        self.my_teams_pg.leave_team('invitation-only')
        assert_true(self.my_teams_pg.leave_team_failed())

        
