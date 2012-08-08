# -*- coding: utf-8 -*-

from nose.tools import assert_true, assert_false
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import teams_page
from apps.webdriver_testing.testdata_factories import TeamMemberFactory, UserFactory


def setup_teams():
    print "creating some teams for testing"
    #create 5 open teams
    for x in range(5):
        team = TeamMemberFactory.create(team__name='my team '+ str(x),
                                        team__slug='my-team-' +str(x),
                                        user__username='open team owner' + str(x), 
                                        user__password='password')

    #create an open team with description text and 2 members
    cool_user = UserFactory.create(username='Wicked Cool', password='password')

    team = TeamMemberFactory.create(team__name='Waay Cool team ',
                                    team__slug='waay-cool-team',
                                    team__description='this is the coolest, most creative team ever created',
                                    user__username='cool guy', 
                                    user__password='password')
    TeamMemberFactory.create(team=team.team, user=cool_user)


    #create 2 application teams
    for x in range(20,22):
        team = TeamMemberFactory.create(team__name='application-only team '+ str(x), 
                                             team__slug='application-only-team-' + str(x),
                                             team__membership_policy=1,
                                             user__username='application owner-'+ str(x), 
                                             user__password='password')

    #create 1 private team
    team = TeamMemberFactory.create(team__name='my own private idaho ', 
                                             team__slug='private-idaho',
                                             team__membership_policy=1,
                                             team__is_visible=False,
                                             user__username='Id A Read', 
                                             user__password='password')

class WebdriverTestCaseTeamsPage(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        setup_teams()  #ADD TEST DATA
        self.teams_pg = teams_page.TeamsPage(self)
        self.teams_pg.open_teams_page()

    def test_directory__search_name(self):
        self.teams_pg.team_search('waay cool')
        assert_true('Waay Cool team' in self.teams_pg.teams_on_page())

    def test_directory__num_members(self):
        self.teams_pg.team_search('waay cool')
        assert_true(2 == self.teams_pg.members('Waay Cool team'))


    def test_directory__num_videos(self):
        pass
      

    def test_directory__search_description(self):
        """Search the teams page for a team, by description text.

        """
        self.teams_pg.team_search('creative')
        assert_true('Waay Cool team' in self.teams_pg.teams_on_page())

 


    def test_directory__search_private_non_member(self):
        self.teams_pg.team_search('private idaho')
        assert_true(self.teams_pg.search_has_no_matches())
 

    def test_directory__open_team_page(self):
        """open a team page from the directory.

        """
        pass

    def test_directory__sort_members(self):
        """sort teams list by members.

        """
        pass

    def test_directory__sort_newest(self):
        """sort teams list by members.

        """
        pass

    def test_directory__sort_name(self):
        """sort teams list by members.

        """
        pass


