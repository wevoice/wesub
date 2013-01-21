# -*- coding: utf-8 -*-

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages.teams import ATeamPage 
from apps.webdriver_testing.pages.site_pages.teams_dir_page import TeamsDirPage
from apps.webdriver_testing.pages.site_pages.teams import members_tab
from apps.webdriver_testing.data_factories import *
from apps.teams.models import TeamMember


class TestCaseOpenTeamPage(WebdriverTestCase):
    """TestSuite for Open teams.

    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseOpenTeamPage, cls).setUpClass()
        cls.team_owner = UserFactory.create()
        cls.team = TeamMemberFactory.create(
            user = cls.team_owner).team
        cls.a_team_pg = ATeamPage(cls)
        cls.a_team_pg.open_team_page(cls.team.slug)


    def test_join__guest(self):
        """Guest user sees Sign in message when visiting a team page.

        """
        self.a_team_pg.open_team_page(self.team.slug)
        self.assertIn("We've got lots of great content that we'd love your ", 
                      self.a_team_pg.dashboard_welcome_message())

    def test_join__authenticated(self):
        """Logged in user can join an open team.

        """

        user = UserFactory.create()
        self.a_team_pg.log_in(user.username, 'password')
        self.a_team_pg.open_team_page(self.team.slug)
        self.a_team_pg.join()

        # Verify team page displays
        self.assertTrue(self.a_team_pg.is_team(self.team.name))

        # Verify the join button is no longer displayed
        self.assertFalse(self.a_team_pg.join_exists()) 

        #Verify the user is a member of team in db.
        team = TeamFactory.build(pk=self.team.pk)
        self.assertEqual(user.username, team.users.get(username=user.username).username)


class TestCaseApplicationTeamPage(WebdriverTestCase):
    """TestSuite for Application-Only teams.  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseApplicationTeamPage, cls).setUpClass()
        cls.team_owner = UserFactory.create()
        cls.team = TeamMemberFactory.create(team__membership_policy=1,
                                            user = cls.team_owner).team
        cls.a_team_pg = ATeamPage(cls)
        cls.members_tab = members_tab.MembersTab(cls)
        cls.a_team_pg.open_team_page(cls.team.slug)


    def test_join__guest(self):
        """Guest user sees Sign in message when visiting a team page.

        """
        self.a_team_pg.open_team_page(self.team.slug)
        self.assertTrue(self.a_team_pg.join_exists())

    def test_join__apply(self):
        """User can apply to join team and is a member after approval.

        """
        test_joiner = UserFactory.create()
        self.a_team_pg.log_in(test_joiner.username, 'password')
        self.a_team_pg.open_team_page(self.team.slug)
        self.a_team_pg.apply()
        self.a_team_pg.submit_application()
        user_app = ApplicationFactory.build(
            team=self.team,
            user=test_joiner,
            pk=1)
        user_app.approve(
            author = self.team_owner.username, 
            interface = "web UI")
        self.members_tab.member_search(self.team.slug, test_joiner.username)
        self.assertEqual(self.members_tab.user_role(), 'Contributor')


class TestCaseInvitationTeamPage(WebdriverTestCase):
    """Test Suite for Invitation-only teams.

    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseInvitationTeamPage, cls).setUpClass()
        cls.team_dir_pg = TeamsDirPage(cls)
        cls.a_team_pg = ATeamPage(cls)
        cls.members_tab = members_tab.MembersTab(cls)
        cls.team_owner = UserFactory.create()
        cls.team = TeamMemberFactory.create(team__membership_policy=2,
                                             user = cls.team_owner).team
        cls.a_team_pg.open_team_page(cls.team.slug)


    def test_join__guest(self):
        """Guest user sees Sign in message when visiting a team page.

        """
        self.a_team_pg.open_team_page(self.team.slug)
        self.assertIn('This team is invitation only.', 
                      self.a_team_pg.dashboard_welcome_message())

    def test_join__authenticated(self):
        """Authenticated user can't join application-only team.

        """
        user = UserFactory.create()
        self.a_team_pg.log_in(user.username, 'password')
        self.a_team_pg.open_page(self.team.slug)
        self.assertFalse(self.a_team_pg.join_exists(), 
            'Invite-only team should not display join button')

    def test_join__contributer_invitation(self):
        """User is added to team as contributor after accepting invitation.

        """

        user = UserFactory.create()
        invitation = TeamInviteFactory.create(
            team=self.team,
            user=user,
            note="Please come join this great team!",
            author=self.team_owner,
            )
        invitation.accept()
        self.team_dir_pg.log_in(user.username, 'password')
        self.team_dir_pg.open_my_teams_page()
        self.assertTrue(self.team_dir_pg.team_displayed(self.team.name))

    def test_join__admin_invitation(self):
        """User is added to team as admin after accepting invitation.

        """
        user = UserFactory.create()
        invitation = TeamInviteFactory.create(
            team=self.team,
            user=user,
            note="Please come join this great team!",
            author=self.team_owner,
            role=TeamMember.ROLE_ADMIN
            )
        invitation.accept()
        self.members_tab.log_in(user.username, 'password')
        self.members_tab.member_search(self.team.slug, user.username)
        self.assertEqual(self.members_tab.user_role(), 'Admin')
        self.assertTrue(self.members_tab.settings_tab_visible(), 
            "Did not find the settings tab on the page")
 
    def test_join__manager_invitation(self):
        """User is added to team as manager after accepting invitation.

        """

        user = UserFactory.create()
        invitation = TeamInviteFactory.create(
            team=self.team,
            user=user,
            note="Please come join this great team!",
            author=self.team_owner,
            role=TeamMember.ROLE_MANAGER
            )
        invitation.accept()
        self.members_tab.log_in(user.username, 'password')
        self.members_tab.member_search(self.team.slug, user.username)
        self.assertEqual(self.members_tab.user_role(), 'Manager')
        self.assertFalse(self.members_tab.settings_tab_visible(), 
            "Settings tab present for manager role")
