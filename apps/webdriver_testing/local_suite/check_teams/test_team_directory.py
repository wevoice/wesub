# -*- coding: utf-8 -*-

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import teams_page
from apps.webdriver_testing.site_pages import a_team_page

from apps.webdriver_testing.data_factories import TeamMemberFactory, TeamVideoFactory, UserFactory


def setup_teams():
    """Create a user and some teams for the tests.

    """
    #CREATE A USER
    cool_user = UserFactory.create(username='Wicked Cool', password='password')

    print "creating some teams for testing"
    #create 5 open teams
    for x in range(5):
        TeamMemberFactory.create(
            team__name='my team ' + str(x),
            team__slug='my-team-' + str(x),
            user__username='open team owner' + str(x),
            user__password='password'
            )

    #create an open team with description text and 2 members
    team = TeamMemberFactory.create(
        team__name="A1 Waay Cool team",
        team__slug='a1-waay-cool-team',
        team__description='this is the coolest, most creative team ever',
        user__username='cool guy',
        user__password='password'
        ).team
    TeamMemberFactory.create(team=team, user=cool_user)
    TeamVideoFactory.create(team=team, added_by=cool_user)

    #create an application team with 3 members and 5 videos
    app_team = TeamMemberFactory.create(
        team__name='the application-only team',
        team__slug='the-application-only-team',
        team__membership_policy=1,
        user__username='application owner',
        user__password='password'
        ).team
    TeamMemberFactory.create(team=app_team, user=UserFactory.create())
    TeamMemberFactory.create(team=app_team, user=cool_user)
    for x in range(5):
        TeamVideoFactory.create(team=app_team, added_by=cool_user)

    #create 1 private team
    priv_team = TeamMemberFactory.create(
        team__name='my own private idaho ',
        team__slug='private-idaho',
        team__membership_policy=1,
        team__is_visible=False,
        user__username='Id A Read',
        user__password='password').team

    return team, app_team, priv_team


class TestCaseTeamsPage(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.COOL_TEAM_NAME = "A1 Waay Cool team"

        self.team, self.app_team, self.priv_team = setup_teams()  # ADD TEST DATA
        self.teams_pg = teams_page.TeamsPage(self)
        self.a_team_pg = a_team_page.ATeamPage(self)
        self.teams_pg.open_teams_page()

    def test_directory__search_name(self):
        """Search for a team by parital name text, has results.

        """
        self.teams_pg.team_search('waay cool')
        self.assertTrue(self.COOL_TEAM_NAME in self.teams_pg.teams_on_page())

    def test_directory__num_members(self):
        """Verify the number of videos displayed for a team is correct.

        """
        self.teams_pg.team_search('waay cool')
        self.assertEqual(2, self.teams_pg.members(self.COOL_TEAM_NAME))

    def test_directory__num_videos(self):
        """Verify the number of videos displayed for a team is correct.

        """
        self.teams_pg.team_search('waay cool')
        self.assertEqual(1, self.teams_pg.videos(self.COOL_TEAM_NAME))

    def test_directory__search_description(self):
        """Search for team description text has results.

        """
        self.teams_pg.team_search('creative')
        self.assertTrue(self.COOL_TEAM_NAME in self.teams_pg.teams_on_page())

    def test_directory__search_private_non_member(self):
        """Non-member search for a private team, get's no results.

        """
        self.teams_pg.team_search('private idaho')
        self.assertTrue(self.teams_pg.search_has_no_matches())

    def test_directory__open_team_page(self):
        """open a team page from the directory.

        """
        cool_team_pg = self.teams_pg.open_team_with_link(self.team.slug)
        self.assertTrue(cool_team_pg.is_team(self.team.name))

    def test_directory__sort_by_members_default(self):
        """Sort by number of members.

        """
        self.assertEqual('the application-only team', 
            self.teams_pg.first_team())

    def test_directory__sort_by_newest(self):
        """sort teams list by newest.

        """
        TeamMemberFactory.create(team__name='new team',
                                 team__slug='new-team',
                                 user=UserFactory.create()
                                 )
        self.teams_pg.sort("date")
        self.assertEqual('new team', self.teams_pg.first_team())

    def test_directory__sort_by_name(self):
        """Sort by team names.

        """
        self.teams_pg.sort("name")
        self.assertEqual(self.COOL_TEAM_NAME, self.teams_pg.first_team())
