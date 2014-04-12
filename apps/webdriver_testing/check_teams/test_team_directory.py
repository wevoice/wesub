# -*- coding: utf-8 -*-

from django.core import management

from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages.teams_dir_page import TeamsDirPage
from webdriver_testing.pages.site_pages.teams import ATeamPage

from webdriver_testing.data_factories import TeamMemberFactory, TeamVideoFactory, UserFactory

class TestCaseTeamsPage(WebdriverTestCase):
    """Test suite for the teams directory page. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseTeamsPage, cls).setUpClass()
        management.call_command('flush', interactive=False)
        cls.COOL_TEAM_NAME = "A1 Waay Cool team"

        #CREATE A USER
        cls.cool_user = UserFactory.create(username='Wicked Cool', 
                                           password='password')

        cls.logger.info("creating some teams for testing")
        #create 5 open teams
        for x in range(5):
            TeamMemberFactory.create(
                team__name='my team ' + str(x),
                team__slug='my-team-' + str(x),
                )

        #create an open team with description text and 2 members
        cls.team = TeamMemberFactory.create(
            team__name="A1 Waay Cool team",
            team__slug='a1-waay-cool-team',
            team__description='this is the coolest, most creative team ever',
            ).team
        TeamMemberFactory.create(team=cls.team, user=cls.cool_user)
        TeamVideoFactory.create(team=cls.team, added_by=cls.cool_user)

        #create an application team with 3 members and 5 videos
        cls.app_team = TeamMemberFactory.create(
            team__name='the application-only team',
            team__slug='the-application-only-team',
            team__membership_policy=1,
            ).team
        TeamMemberFactory.create(team=cls.app_team, user=UserFactory.create())
        TeamMemberFactory.create(team=cls.app_team, user=cls.cool_user)
        for x in range(5):
            TeamVideoFactory.create(team=cls.app_team, added_by=cls.cool_user)

        #create 1 private invitation team
        cls.priv_team = TeamMemberFactory.create(
            team__name='my own private idaho ',
            team__slug='private-idaho',
            team__membership_policy=2,
            team__is_visible=False,
            ).team


        #create 1 private application team
        cls.priv_team = TeamMemberFactory.create(
            team__name='private application',
            team__slug='private-application',
            team__membership_policy=1,
            team__is_visible=False,
            ).team

        cls.teams_dir_pg = TeamsDirPage(cls)
        cls.a_team_pg = ATeamPage(cls)

    def setUp(self):
        self.teams_dir_pg.open_teams_page()


    def test_directory__search_name(self):
        """Search for a team by parital name text, has results.

        """
        self.teams_dir_pg.team_search('waay cool')
        self.assertTrue(self.COOL_TEAM_NAME in self.teams_dir_pg.teams_on_page())

    def test_directory__num_members(self):
        """Verify the number of videos displayed for a team is correct.

        """
        self.teams_dir_pg.team_search('waay cool')
        self.assertEqual(2, self.teams_dir_pg.members(self.COOL_TEAM_NAME))

    def test_directory__num_videos(self):
        """Verify the number of videos displayed for a team is correct.

        """
        self.teams_dir_pg.team_search('waay cool')
        self.assertEqual(1, self.teams_dir_pg.videos(self.COOL_TEAM_NAME))

    def test_directory__search_description(self):
        """Search for team description text has results.

        """
        self.teams_dir_pg.team_search('creative')
        self.assertTrue(self.COOL_TEAM_NAME in self.teams_dir_pg.teams_on_page())

    def test_search_private_invitation_non_member(self):
        """Non-member search for a private invitation only team, get's no results.

        """
        self.teams_dir_pg.team_search('private idaho')
        self.assertTrue(self.teams_dir_pg.search_has_no_matches())

    def test_search_private_application_non_member(self):
        """Non-member search for a private application team, has results.

        """
        self.teams_dir_pg.team_search('private application')
        self.assertTrue('private application' in self.teams_dir_pg.teams_on_page())

    def test_directory__open_team_page(self):
        """open a team page from the directory.

        """
        self.teams_dir_pg.open_team_with_link(self.team.slug)
        self.assertTrue(self.a_team_pg.is_team(self.team.name))

    def test_directory__sort_by_members_default(self):
        """Sort by number of members.

        """
        self.assertEqual('the application-only team', 
            self.teams_dir_pg.first_team())

    def test_directory__sort_by_newest(self):
        """sort teams list by newest.

        """
        TeamMemberFactory.create(team__name='new team',
                                 team__slug='new-team',
                                 user=UserFactory.create()
                                 )
        self.teams_dir_pg.sort("date")
        self.assertEqual('new team', self.teams_dir_pg.first_team())

    def test_directory__sort_by_name(self):
        """Sort by team names.

        """
        self.teams_dir_pg.sort("name")
        self.assertEqual(self.COOL_TEAM_NAME, self.teams_dir_pg.first_team())
