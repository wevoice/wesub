# -*- coding: utf-8 -*-

from nose.tools import assert_true, assert_false, assert_equal
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import a_team_page, my_teams
from apps.webdriver_testing.site_pages.teams import members
from apps.webdriver_testing.site_pages import auth_page
from apps.webdriver_testing.testdata_factories import *
from apps.teams.models import TeamMember
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
        self.auth_pg = auth_page.AuthPage(self)

        self.team = TeamMemberFactory.create(team__name='my application-only team', 
                                             team__slug='application-only',
                                             team__membership_policy=1,
                                             user__username='application_team_owner', 
                                             )
        self.a_team_pg = a_team_page.ATeamPage(self)
        self.members_tab = members.MembersTab(self)


    def test_join__guest(self):
        """Guest (unauthenticated user) sees Sign in message when visiting a team page.

	"""
        team_slug = self.team.team.get_absolute_url()
        self.a_team_pg.open_page(team_slug)
        assert_true(self.a_team_pg.join_exists())

    def test_join__apply(self):
        username = 'teamjoiner'
        passw = 'password'
        self.user = UserFactory.create(username=username)
        self.auth_pg.login(username, passw)
        self.a_team_pg.open_page('teams/application-only/')
        self.a_team_pg.apply()
        self.a_team_pg.submit_application()
        user_app = ApplicationFactory.build(team = self.team.team,
                                       user = self.user,
                                       pk = 1)
        user_app.approve()
        self.members_tab.member_search('application-only', 'teamjoiner')
        assert_true(self.members_tab.user_role() == 'Contributor')


        

class WebdriverTestCaseInvitationTeamPage(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.my_team_pg = my_teams.MyTeam(self)
        self.a_team_pg = a_team_page.ATeamPage(self)
        self.members_tab = members.MembersTab(self)

        self.team = TeamMemberFactory.create(team__name='manage invitation team', 
                                             team__slug='invitation-only',
                                             team__membership_policy=2,  #manager invite-only
                                             user__username='invitation_team_owner', 
                                             )
        self.auth_pg = auth_page.AuthPage(self)


    def test_join__guest(self):
        """Guest (unauthenticated user) sees Sign in message when visiting a team page.

	"""
        self.a_team_pg.open_page('teams/invitation-only/')
        assert_true(self.a_team_pg.join_exists())

    def test_join__authenticated(self):
        """Authenticated user can't join application-only
	"""
        UserFactory.create(username='UninvitedUser')
        self.auth_pg.login('UninvitedUser', 'password')
        self.a_team_pg.open_page('teams/invitation-only/')
        assert_false(self.a_team_pg.join_exists(), 'Invite-only team should not display join button')


    def test_join__contributer_invitation(self):
        usr=UserFactory.create(username='InvitedUser')
        invitation = TeamInviteFactory.create(team=self.team.team,
                                              user=usr,
                                              note="Please come join this great team!",
                                              author=self.team.user,
                                              )
        invitation.accept()
        self.auth_pg.login('InvitedUser', 'password')
        self.my_team_pg.open_my_teams_page()
        assert_true(self.my_team_pg.team_displayed('manage invitation team'))

    def test_join__admin_invitation(self):
        usr=UserFactory.create(username='InvitedUser')
        invitation = TeamInviteFactory.create(team=self.team.team,
                                              user=usr,
                                              note="Please come join this great team!",
                                              author=self.team.user,
                                              role = TeamMember.ROLE_ADMIN
                                              )
        invitation.accept()
        self.auth_pg.login('InvitedUser', 'password')
        self.members_tab.member_search('invitation-only', 'InvitedUser')
        assert_true(self.members_tab.user_role() == 'Admin')
        assert_true(self.members_tab.settings_tab_visible(), "Did not find the settings tab on the page")


    def test_join__manager_invitation(self):
        usr=UserFactory.create(username='InvitedUser')
        invitation = TeamInviteFactory.create(team=self.team.team,
                                              user=usr,
                                              note="Please come join this great team!",
                                              author=self.team.user,
                                              role = TeamMember.ROLE_MANAGER
                                              )
        invitation.accept()
        self.auth_pg.login('InvitedUser', 'password')
        self.members_tab.member_search('invitation-only', 'InvitedUser')
        assert_true(self.members_tab.user_role() == 'Manager')
        assert_false(self.members_tab.settings_tab_visible(), "Settings tab present for manager role")








 
        
