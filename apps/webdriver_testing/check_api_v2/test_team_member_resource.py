import os
import time
import itertools
import operator
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import TeamMemberFactory
from webdriver_testing.data_factories import TeamVideoFactory
from webdriver_testing import data_helpers
from webdriver_testing.pages.site_pages.teams_dir_page import TeamsDirPage
from webdriver_testing.pages.site_pages.teams import members_tab
from webdriver_testing.pages.site_pages import user_messages_page

class TestCaseTeamMemberResource(WebdriverTestCase):
    """TestSuite for getting and modifying video urls via api_v2.

       One can list, update, delete and add video urls to existing videos.
    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseTeamMemberResource, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create(username = 'TestUser', is_partner=True)
        cls.team_member = UserFactory.create(username = 'team_member')
        

        #create an open team with description text and 2 members
        cls.open_team = TeamMemberFactory.create(
            team__name="A1 Waay Cool team",
            team__slug='a1-waay-cool-team',
            team__description='this is the coolest, most creative team ever',
            user = cls.user,
            ).team

        TeamMemberFactory.create(role="ROLE_CONTRIBUTOR", team=cls.open_team, 
                user = UserFactory.create(username = 'member'))

        #Open to the teams page so you can see what's there.
        cls.teams_dir_pg = TeamsDirPage(cls)
        cls.teams_dir_pg.open_teams_page()

    def test_members_list(self):
        """List off the existing team members.

        GET /api2/partners/teams/[team-slug]/members/
        """
        expected_members = ['TestUser', 'member'] 
        url_part = 'teams/%s/members/' % self.open_team.slug
        r = self.data_utils.make_request(self.user, 'get', url_part)
        self.logger.info(r.json)
        response = r.json
        member_objects =  response['objects']
        members_list = []
        for k, v in itertools.groupby(member_objects, operator.itemgetter('username')):
            members_list.append(k)
        self.assertEqual(sorted(expected_members), sorted(members_list))


    def test_members_update(self):
        """Update a team members role.

        PUT /api2/partners/teams/[team-slug]/members/[username]/
        """

        updated_info = {
            'role': 'admin' 
            } 

        url_part = 'teams/%s/members/member/' % self.open_team.slug
        self.data_utils.make_request(self.user, 'put', url_part, **updated_info)
        
        self.teams_dir_pg.open_page('teams/%s/members/' % self.open_team.slug)
        self.teams_dir_pg.log_in(self.user.username, 'password')
        members_tb = members_tab.MembersTab(self)
        members_tb.member_search(self.open_team.slug, 'member')
        self.assertEqual(members_tb.user_role(), 'Admin')

    def test_member_create_contributor(self):
        """Verify video urls for a particular video are listed.
          
          POST /api2/partners/teams/[team-slug]/members/
        """
        
        #create a second team with 'second_member' as a member.
        second_user = UserFactory.create(username = 'second_member')
        second_team = TeamMemberFactory.create(
            team__name="normal team",
            team__slug='normal-team',
            team__description='this is the junior team',
            user = self.user,
            ).team
        TeamMemberFactory.create(role="ROLE_CONTRIBUTOR", 
                                 team=second_team, 
                                 user = second_user)
        
        user_details = {"username": second_user.username,
                        "role": "admin"
                       } 
        url_part = 'teams/%s/members/' % self.open_team.slug
        self.data_utils.make_request(self.user, 'post', url_part, **user_details)
        self.teams_dir_pg.open_page('teams/%s/members/' % self.open_team.slug)
        self.teams_dir_pg.log_in(self.user.username, 'password')
       
        url_part = 'teams/%s/members/' % self.open_team.slug
        r = self.data_utils.make_request(self.user, 'get', url_part)
        self.logger.info(r.status_code)
        response = r.content
        self.assertNotEqual(None, response, "Got a None response")

    def test_member_safe_invite(self):
        """Use safe-members api to invite user from 1 team to anther.
          
          POST /api2/partners/teams/[team-slug]/safe-members/
        """
        
        #create a second team with 'second_member' as a member.
        second_user = UserFactory.create(username = 'secondMember')
        second_team = TeamMemberFactory.create(
            team__name="normal team",
            team__slug='normal-team',
            team__description='this is the junior team',
            user = self.user,
            ).team
        TeamMemberFactory.create(role="ROLE_CONTRIBUTOR", team=second_team, user = second_user)
        
        #Create a post the request 
        user_details = {"username": second_user.username,
                        "role": "admin",
                        "note": "we need you on our team"
                       } 
        url_part = 'teams/%s/safe-members/' % self.open_team.slug
        self.data_utils.make_request(self.user, 'post', url_part, **user_details)

        #Login in a verify invitation message is displayed 
        usr_messages_pg = user_messages_page.UserMessagesPage(self)
        usr_messages_pg.log_in(second_user.username, 'password')
        usr_messages_pg.open_messages()
        invite_subject = ("You've been invited to team %s on Amara" 
                          % self.open_team.name)
        self.assertEqual(invite_subject, usr_messages_pg.message_subject())


    def test_member_safe_create(self):
        """Use the safe-members api to create a new user to invite.
          
          POST /api2/partners/teams/[team-slug]/safe-members/
        """
        user_details = {"username": 'MakeMe',
                        "email": 'makeme@example.com',
                        "role": "contributor"
                       } 
        url_part = 'teams/%s/safe-members/' % self.open_team.slug
        self.data_utils.make_request(self.user, 'post', url_part, **user_details)
        r = self.data_utils.make_request(self.user, 'get', 'users/')
        response = r.json        
        users_objects =  response['objects']
        users_list = []
        for k, v in itertools.groupby(users_objects, 
                                      operator.itemgetter('username')):
            users_list.append(k)
        self.assertIn(user_details['username'], users_list)

       

    def test_members_delete(self):
        """Team is deleted by the owner.

           DELETE /api2/partners/teams/[team-slug]/members/[username]/
        """
        url_part = 'teams/%s/members/member' % self.open_team.slug
        r = self.data_utils.make_request(self.user, 'delete', url_part)
        
        url_part = 'teams/%s/members/' % self.open_team.slug
        r = self.data_utils.make_request(self.user, 'get', url_part)
        response = r.json
        member_objects =  response['objects']

        self.teams_dir_pg.open_page('teams/%s/members/' % self.open_team.slug)
        self.teams_dir_pg.log_in(self.user.username, 'password')
        members_list = []
        for k, v in itertools.groupby(member_objects, operator.itemgetter('username')):
            members_list.append(k)
        self.assertNotIn('member', members_list)
 
