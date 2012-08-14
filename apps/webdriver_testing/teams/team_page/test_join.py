# -*- coding: utf-8 -*-

from nose.tools import assert_true, assert_false, assert_equal
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import a_team_page
from apps.webdriver_testing.site_pages import auth_page
from apps.webdriver_testing.testdata_factories import TeamMemberFactory, UserFactory, TeamFactory


class WebdriverTestCaseOpenTeamPage(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.team = TeamMemberFactory.create(team__name='my team', 
                                             team__slug='my-team',
                                             user__username='open team owner', 
                                             )
        self.a_team_pg = a_team_page.ATeamPage(self)
        self.auth_pg = auth_page.AuthPage(self)
        self.team_slug = self.team.team.get_absolute_url()
        print self.team_slug


    def test_join__guest(self):
        """Guest (unauthenticated user) sees Sign in message when visiting a team page.

	"""
        self.a_team_pg.open_page('teams/my-team')
        assert_true(self.a_team_pg.join_exists())


    def test_join__authenticated(self):
        username = 'teamjoiner'
        passw = 'password'
        self.user = UserFactory.create(username=username)
        self.auth_pg.login(username, passw)
        self.a_team_pg.open_page('teams/my-team')
        self.a_team_pg.join()
        assert_true(self.a_team_pg.is_team('my team')) #Verify team page displays
        assert_false(self.a_team_pg.join_exists())   #Verify the join button is no longer displayed

        #Verify the user is a member of team in db.
        team = TeamFactory.build(pk=self.team.team.pk)
        assert_equal(username, team.users.get(username=username).username)


class WebdriverTestCaseApplicationTeamPage(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.team = TeamMemberFactory.create(team__name='my application-only team', 
                                             team__slug='application-only',
                                             team__membership_policy=1,
                                             user__username='application team owner', 
                                             )
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
                                             team__slug='invitation-only',
                                             team__membership_policy=2,  #manager invite-only
                                             user__username='invitation team owner', 
                                             )
        self.a_team_pg = a_team_page.ATeamPage(self)

    def test_join__guest(self):
        """Guest (unauthenticated user) sees Sign in message when visiting a team page.

	"""
        team_slug = self.team.team.get_absolute_url()
        self.a_team_pg.open_page(team_slug)
        assert_true(self.a_team_pg.join_exists())
