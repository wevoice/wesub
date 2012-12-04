# -*- coding: utf-8 -*-

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import a_team_page 
from apps.webdriver_testing.site_pages import my_teams
from apps.webdriver_testing.site_pages.teams import members_tab
from apps.webdriver_testing.site_pages import auth_page
from apps.webdriver_testing.data_factories import *
from apps.teams.models import TeamMember


class TestCaseOpenTeamPage(WebdriverTestCase):
    """TestSuite for Open teams.

    """
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.team = TeamMemberFactory.create(
            team__name='my team',
            team__slug='my-team',
            user__username='open team owner',
            )
        self.a_team_pg = a_team_page.ATeamPage(self)
        self.auth_pg = auth_page.AuthPage(self)
        self.team_slug = self.team.team.get_absolute_url()

    def test_join__guest(self):
        """Guest user sees Sign in message when visiting a team page.

        """
        self.a_team_pg.open_page('teams/my-team')
        self.assertIn('This team is invitation only.', 
                      self.dashboard_welcome_message())

    def test_join__authenticated(self):
        """Logged in user can join an open team.

        """
        username = 'teamjoiner'
        passw = 'password'
        self.user = UserFactory.create(username=username)
        self.auth_pg.login(username, passw)
        self.a_team_pg.open_page('teams/my-team')
        self.a_team_pg.join()

        # Verify team page displays
        self.assertTrue(self.a_team_pg.is_team('my team'))

        # Verify the join button is no longer displayed
        self.assertFalse(self.a_team_pg.join_exists()) 

        #Verify the user is a member of team in db.
        team = TeamFactory.build(pk=self.team.team.pk)
        self.assertEqual(username, team.users.get(username=username).username)


class TestCaseApplicationTeamPage(WebdriverTestCase):
    """TestSuite for Application-Only teams.

    """
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.auth_pg = auth_page.AuthPage(self)

        self.team = TeamMemberFactory.create(team__name='my application-only team',
                                             team__slug='application-only',
                                             team__membership_policy=1,
                                             user__username='application_team_owner',
                                             ).team
        self.a_team_pg = a_team_page.ATeamPage(self)
        self.members_tab = members_tab.MembersTab(self)

    def test_join__guest(self):
        """Guest user sees Sign in message when visiting a team page.

        """
        self.a_team_pg.open_page('teams/'+self.team.slug)
        self.assertTrue(self.a_team_pg.join_exists())

    def test_join__apply(self):
        """User can apply to join team and is a member after approval.

        """
        username = 'teamjoiner'
        passw = 'password'
        test_user = UserFactory.create(username=username)
        self.auth_pg.login(username, passw)
        self.a_team_pg.open_page('teams/application-only/')
        self.a_team_pg.apply()
        self.a_team_pg.submit_application()
        user_app = ApplicationFactory.build(
            team=self.team,
            user=test_user,
            pk=1)
        user_app.approve(
            author = 'application_team_owner', 
            interface = "web UI")
        self.members_tab.member_search('application-only', 'teamjoiner')
        self.assertEqual(self.members_tab.user_role(), 'Contributor')


class TestCaseInvitationTeamPage(WebdriverTestCase):
    """Test Suite for Invitation-only teams.

    """
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.my_team_pg = my_teams.MyTeam(self)
        self.a_team_pg = a_team_page.ATeamPage(self)
        self.members_tab = members_tab.MembersTab(self)
        self.team_owner = UserFactory.create(username='invitation_team_owner')
        self.team = TeamMemberFactory.create(team__name='manage invitation team',
                                             team__slug='invitation-only',
                                             team__membership_policy=2,
                                             user = self.team_owner).team
        self.auth_pg = auth_page.AuthPage(self)

    def test_join__guest(self):
        """Guest user sees Sign in message when visiting a team page.

        """
        self.a_team_pg.open_page('teams/invitation-only/')
        self.assertTrue(self.a_team_pg.join_exists())

    def test_join__authenticated(self):
        """Authenticated user can't join application-only team.

        """
        UserFactory.create(username='UninvitedUser')
        self.auth_pg.login('UninvitedUser', 'password')
        self.a_team_pg.open_page('teams/invitation-only/')
        self.assertFalse(self.a_team_pg.join_exists(), 
            'Invite-only team should not display join button')

    def test_join__contributer_invitation(self):
        """User is added to team as contributor after accepting invitation.

        """

        usr = UserFactory.create(username='InvitedUser')
        invitation = TeamInviteFactory.create(
            team=self.team,
            user=usr,
            note="Please come join this great team!",
            author=self.team_owner,
            )
        invitation.accept()
        self.auth_pg.login('InvitedUser', 'password')
        self.my_team_pg.open_my_teams_page()
        self.assertTrue(self.my_team_pg.team_displayed(
            'manage invitation team'))

    def test_join__admin_invitation(self):
        """User is added to team as admin after accepting invitation.

        """
        usr = UserFactory.create(username='InvitedUser')
        invitation = TeamInviteFactory.create(
            team=self.team,
            user=usr,
            note="Please come join this great team!",
            author=self.team_owner,
            role=TeamMember.ROLE_ADMIN
            )
        invitation.accept()
        self.auth_pg.login('InvitedUser', 'password')
        self.members_tab.member_search('invitation-only', 'InvitedUser')
        self.assertEqual(self.members_tab.user_role(), 'Admin')
        self.assertTrue(self.members_tab.settings_tab_visible(), 
            "Did not find the settings tab on the page")
 
    def test_join__manager_invitation(self):
        """User is added to team as manager after accepting invitation.

        """

        usr = UserFactory.create(username='InvitedUser')
        invitation = TeamInviteFactory.create(
            team=self.team,
            user=usr,
            note="Please come join this great team!",
            author=self.team_owner,
            role=TeamMember.ROLE_MANAGER
            )
        invitation.accept()
        self.auth_pg.login('InvitedUser', 'password')
        self.members_tab.member_search('invitation-only', 'InvitedUser')
        self.assertEqual(self.members_tab.user_role(), 'Manager')
        self.assertFalse(self.members_tab.settings_tab_visible(), 
            "Settings tab present for manager role")
