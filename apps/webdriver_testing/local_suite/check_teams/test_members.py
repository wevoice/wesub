# -*- coding: utf-8 -*-

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import auth_page
from apps.webdriver_testing.site_pages import my_teams
from apps.webdriver_testing.site_pages.teams import members_tab
from apps.webdriver_testing.site_pages import user_messages_page
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import UserFactory
from apps.teams.models import TeamMember

class TestCaseMembersTab(WebdriverTestCase):
    """Verify edit of member roles and restrictions.

       Scenario: Assign another admin with no restrictions
       Scenario: Assign an admin with project restrictions
       Scenario: Asign a manager with no restrictions
       Scenario: Assign a manager with project restrictions
       Scenario: Assign a manager with language restrictions
       Scenario: Assign a manager with project and language restrictions
       Scenario: Invite user via form


    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.my_teams_pg = my_teams.MyTeam(self)
        self.user_message_pg = user_messages_page.UserMessagesPage(self)

        self.members_tab = members_tab.MembersTab(self)
        self.team = TeamMemberFactory.create(team__name='Roles Test',
                                             team__slug='roles-test',
                                             user__username='team_owner',
                                             ).team
        self.manager_test_user = TeamMemberFactory.create(team=self.team,
                                 user=UserFactory.create(username=
                                                         'promotedToManager'),
                                 role=TeamMember.ROLE_CONTRIBUTOR)
        self.admin_test_user = TeamMemberFactory.create(team=self.team,
                                 user=UserFactory.create(username=
                                                         'promotedToAdmin'),
                                 role=TeamMember.ROLE_CONTRIBUTOR)
        TeamProjectFactory.create(team=self.team,
                                  name='my translation project',
                                  workflow_enabled=True,
                                  )


    def test_invitation_form(self):
        """Send an invitation via the form on the members tab.

        """
        user = UserFactory.create()
        self.members_tab.log_in('team_owner', 'password')
        self.members_tab.open_members_page('roles-test')
        self.members_tab.invite_user_via_form(username = user.username,
                                              message = 'Join my team',
                                              role = 'Contributor')
        self.members_tab.log_out()
        self.members_tab.log_in(user.username, 'password')
        self.assertEqual(1, user.team_invitations.count())
        self.assertEqual(1, self.team.invitations.count())
        #Verify the user gets the message displayed.
        self.user_message_pg.open_messages()
        self.assertTrue('team_owner has invited you' in 
            self.user_message_pg.message_text())


    def test_assign__manager(self):
        """Asign a manager with no restrictions.

           Verify the display of the roles in the members tab.
        """
 
        self.members_tab.log_in('team_owner', 'password')
        self.members_tab.member_search('roles-test', 'promotedToManager')
        self.members_tab.edit_user(role="Manager")
        self.members_tab.member_search('roles-test', 'promotedToManager')
        self.assertEqual(self.members_tab.user_role(), 
                      'Manager')

    def test_assign__manager_lang_restrictions(self):
        self.members_tab.log_in('team_owner', 'password')
        self.members_tab.member_search('roles-test', 'promotedToManager')
        self.members_tab.edit_user(
            role="Manager", languages=['English', 'French'])
        self.members_tab.member_search('roles-test', 'promotedToManager')

        self.assertEqual(self.members_tab.user_role(), 
                      'Manager for French, and English languages')

    def test_assign__manager_project_lang_restrictions(self):
        """Assign a manager with project restrictions.

           Verify the display of the roles in the members tab.
        """
        self.members_tab.log_in('team_owner', 'password')
        self.members_tab.member_search('roles-test', 'promotedToManager')
        self.members_tab.edit_user(
            role="Manager", projects=['my translation project'],
            languages=['English', 'French'])
        self.members_tab.member_search('roles-test', 'promotedToManager')
        self.assertEqual(self.members_tab.user_role(), 
                      ('Manager for my translation project project '
                       'and for French, and English languages'))


    def test_assign__manager_project_restrictions(self):
        """Assign a manager with project restrictions.

           Verify the display of the roles in the members tab.
        """
        self.members_tab.log_in('team_owner', 'password')
        self.members_tab.member_search('roles-test', 'promotedToManager')
        self.members_tab.edit_user(
            role="Manager", projects=['my translation project'])
        self.members_tab.member_search('roles-test', 'promotedToManager')
        self.assertEqual(self.members_tab.user_role(), 
                      'Manager for my translation project project')


    def test_assign__admin(self):
        """Assign another admin with no restrictions.

           Verify the display of the roles in the members tab.
        """
        self.members_tab.log_in('team_owner', 'password')
        self.members_tab.member_search('roles-test', 'promotedToAdmin')
        self.members_tab.edit_user(role="Admin")
        self.members_tab.member_search('roles-test', 'promotedToAdmin')
        self.assertEqual(self.members_tab.user_role(), 
                      'Admin')


    def test_assign__admin_project_restrictions(self):
        """Assign an admin with project restrictions.

           Verify the display of the roles in the members tab.
        """
        self.members_tab.log_in('team_owner', 'password')
        self.members_tab.member_search('roles-test', 'promotedToAdmin')
        self.members_tab.edit_user(
            role="Admin", projects=['my translation project'])
        self.members_tab.member_search('roles-test', 'promotedToAdmin')
        self.assertEqual(self.members_tab.user_role(), 
                      'Admin for my translation project project')

