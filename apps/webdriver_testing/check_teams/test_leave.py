# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages.teams_dir_page import TeamsDirPage
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamContributorMemberFactory
from apps.webdriver_testing.data_factories import TeamAdminMemberFactory
from apps.webdriver_testing.data_factories import TeamOwnerMemberFactory

from apps.webdriver_testing.data_factories import UserFactory
from apps.teams.models import TeamMember


class TestCaseLeaveTeam(WebdriverTestCase):
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseLeaveTeam, cls).setUpClass()

        cls.team_dir_pg = TeamsDirPage(cls)
        cls.team = TeamMemberFactory.create(
            team__membership_policy=2,  # manager invite-only
            user__username='invitation_team_owner',
            ).team
        cls.team_dir_pg.open_teams_page()


    def test_leave__contributor(self):
        """A contributor can leave a team.

        """
        contributor = TeamContributorMemberFactory(team = self.team).user

        self.team_dir_pg.log_in(contributor.username, 'password')
        self.team_dir_pg.leave_team(self.team.slug)
        self.assertTrue(self.team_dir_pg.leave_team_successful())

    def test_leave__second_to_last_owner(self):
        """Second to last owner can leave the team.

        """
        owner2 = TeamOwnerMemberFactory(team = self.team).user

        self.team_dir_pg.log_in(owner2.username, 'password')
        self.team_dir_pg.leave_team(self.team.slug)
        self.assertTrue(self.team_dir_pg.leave_team_successful())

    def test_leave__admin(self):
        """An admin can leave the team.

        """
        admin = TeamAdminMemberFactory(team = self.team).user

        self.team_dir_pg.log_in(admin.username, 'password')
        self.team_dir_pg.leave_team(self.team.slug)
        self.assertTrue(self.team_dir_pg.leave_team_successful())

    def test_leave__last_owner(self):
        """The last owner can not leave the team.

        """
        self.team_dir_pg.log_in('invitation_team_owner', 'password')
        self.team_dir_pg.leave_team(self.team.slug)
        self.assertTrue(self.team_dir_pg.leave_team_failed())

    def test_leave__last_owner_ui(self):
        """The last owner has no leave button on hover.
        """
        self.team_dir_pg.log_in('invitation_team_owner', 'password')
        self.team_dir_pg.open_my_teams_page()
        self.assertFalse(self.team_dir_pg.leave_present(self.team.name))

    def test_leave__ui(self):
        """A contributor leaves team by clicking leave link.

        """
        contributor = TeamContributorMemberFactory(team = self.team).user

        self.team_dir_pg.log_in(contributor.username, 'password')
        self.team_dir_pg.open_my_teams_page()
        self.team_dir_pg.click_leave_link(self.team.name)
        self.assertTrue(self.team_dir_pg.leave_team_successful())

