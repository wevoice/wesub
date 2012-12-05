# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import a_team_page, my_teams
from apps.webdriver_testing.data_factories import TeamMemberFactory 
from apps.webdriver_testing.data_factories import UserFactory
from apps.teams.models import TeamMember


class TestCaseLeaveTeam(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.my_teams_pg = my_teams.MyTeam(self)
        self.team = TeamMemberFactory.create(
            team__name='manage invitation team',
            team__slug='invitation-only',
            team__membership_policy=2,  # manager invite-only
            user__username='invitation_team_owner',
            ).team

    def test_leave__contributor(self):
        """A contributor can leave a team.

        """
        TeamMemberFactory.create(
            team=self.team,
            user=UserFactory.create(username='tester'),
            role=TeamMember.ROLE_CONTRIBUTOR)

        self.my_teams_pg.log_in('tester', 'password')
        self.my_teams_pg.leave_team('invitation-only')
        self.assertTrue(self.my_teams_pg.leave_team_successful())

    def test_leave__second_to_last_owner(self):
        """Second to last owner can leave the team.

        """
        TeamMemberFactory.create(
            team=self.team,
            user=UserFactory.create(username='testOwner'),
            role=TeamMember.ROLE_OWNER)

        self.my_teams_pg.log_in('testOwner', 'password')
        self.my_teams_pg.leave_team('invitation-only')
        self.assertTrue(self.my_teams_pg.leave_team_successful())

    def test_leave__admin(self):
        """An admin can leave the team.

        """
        TeamMemberFactory.create(
            team=self.team,
            user=UserFactory.create(username='testAdmin'),
            role=TeamMember.ROLE_ADMIN)

        self.my_teams_pg.log_in('testAdmin', 'password')
        self.my_teams_pg.leave_team('invitation-only')
        self.assertTrue(self.my_teams_pg.leave_team_successful())

    def test_leave__last_owner(self):
        """The last owner can not leave the team.

        """
        self.my_teams_pg.log_in('invitation_team_owner', 'password')
        self.my_teams_pg.leave_team('invitation-only')
        self.assertTrue(self.my_teams_pg.leave_team_failed())

    def test_leave__last_owner_ui(self):
        """The last owner has no leave button on hover.
        """
        self.my_teams_pg.log_in('invitation_team_owner', 'password')
        self.my_teams_pg.open_my_teams_page()
        self.assertFalse(self.my_teams_pg.leave_present(self.team.name))

    def test_leave__ui(self):
        """A contributor leaves team by clicking leave link.

        """
        TeamMemberFactory.create(
            team=self.team,
            user=UserFactory.create(username='tester'),
            role=TeamMember.ROLE_CONTRIBUTOR)

        self.my_teams_pg.log_in('tester', 'password')
        self.my_teams_pg.open_my_teams_page()
        self.my_teams_pg.click_leave_link(self.team.name)
        self.assertTrue(self.my_teams_pg.leave_team_successful())

