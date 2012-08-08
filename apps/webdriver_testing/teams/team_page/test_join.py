# -*- coding: utf-8 -*-

from nose.tools import assert_true, assert_false
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import a_team_page
from apps.webdriver_testing.site_pages import auth_page
from apps.webdriver_testing.testdata_factories import TeamMemberFactory, UserFactory


class WebdriverTestCaseOpenTeamPage(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.team = TeamMemberFactory.create(team__name='my team', 
                                             team__slug='my-team',
                                             user__username='open team owner', 
                                             user__password='password')
        self.a_team_pg = a_team_page.ATeamPage(self)
        self.auth_pg = auth_page.AuthPage(self)

    def test_join__guest(self):
        """Guest (unauthenticated user) sees Sign in message when visiting a team page.

	"""
        team_slug = self.team.team.get_absolute_url()
        self.a_team_pg.open_page(team_slug)
        assert_true(self.a_team_pg.join_exists())

    def test_join__authenticated(self):
        username = 'open team member'
        passw = 'password'
        self.user = UserFactory.create(username=username)
        self.user.set_password(passw)
        self.auth_pg.login(username, passw)
        self.a_team_pg.open_page(team_slug)
        self.a_team_pg.join()
        print dir(self.team)


class WebdriverTestCaseApplicationTeamPage(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.team = TeamMemberFactory.create(team__name='my application-only team', 
                                             team__slug='application-only',
                                             team__membership_policy=1,
                                             user__username='application team owner', 
                                             user__password='password')
        self.a_team_pg = a_team_page.ATeamPage(self)

    def test_join__guest(self):
        """Guest (unauthenticated user) sees Sign in message when visiting a team page.

	"""
        team_slug = self.team.team.get_absolute_url()
        self.a_team_pg.open_page(team_slug)
        assert_true(self.a_team_pg.join_exists())



class WebdriverTestCaseInvitationTeamPage(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.team = TeamMemberFactory.create(team__name='manage invitation team', 
                                             team__slug='application-only',
                                             team__membership_policy=2,  #manager invite-only
                                             user__username='invitation team owner', 
                                             user__password='password')
        self.a_team_pg = a_team_page.ATeamPage(self)

    def test_join__guest(self):
        """Guest (unauthenticated user) sees Sign in message when visiting a team page.

	"""
        team_slug = self.team.team.get_absolute_url()
        self.a_team_pg.open_page(team_slug)
        assert_true(self.a_team_pg.join_exists())
