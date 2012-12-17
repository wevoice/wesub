# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import a_team_page
from apps.webdriver_testing.site_pages.teams import messages_tab
from apps.webdriver_testing.site_pages.teams import members_tab
from apps.webdriver_testing.site_pages import user_messages_page
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import UserFactory
from apps.teams.models import TeamMember

class TestCaseTeamMessages(WebdriverTestCase):    

    _TEST_MESSAGES = {
        'INVITATION': ('I hear you are an awesome translator, please join '
                       'my team.'),
        'APPLICATION': ('Thank you for applying to the team, we will review ' 
                        'your qualifications and get back to you.'),
        'NEW_MANAGER': ('Congrats, you have been promoted to Manager.'),
        'NEW_ADMIN': ('Congrats, you have been promoted to Admin status.')
        }




    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.a_team_pg = a_team_page.ATeamPage(self)
        self.members_tab = members_tab.MembersTab(self)
        self.messages_tab = messages_tab.MessagesTab(self)
        self.user_message_pg = user_messages_page.UserMessagesPage(self)


        self.non_member = UserFactory.create(username='NonMember')
        self.team_owner = UserFactory.create(
            username='TeamOwner',
            is_superuser = True,
            is_staff = True)

        #CREATE AN APPLICATION-ONLY TEAM 
        self.team = TeamMemberFactory.create(
            team__name='Literal Video Version',
            team__slug='literal-video-version',
            team__membership_policy = 1,
            user = self.team_owner,
            ).team

        self.team_member = TeamMemberFactory.create(
            team=self.team,
            user=UserFactory.create(username='TeamMember'),
            role=TeamMember.ROLE_CONTRIBUTOR).user

        

        #ADD THE TEST MESSAGES TO THE TEST TEAM
        self.members_tab.log_in(self.team_owner.username, 'password')
        self.messages_tab.open_messages_tab(self.team.slug)
        self.messages_tab.edit_messages(self._TEST_MESSAGES)

    def test_messages__edit(self):
        """Change the default messages via the UI and verify they are stored.

        """
        self.assertEqual(self._TEST_MESSAGES, 
            self.messages_tab.stored_messages())


    def test_messages__invitation(self):
        """Invited user see the custom message.

        """
        self.members_tab.open_members_page(self.team.slug)
        self.members_tab.invite_user_via_form(
            username = self.non_member.username,
            message = 'Join my team',
            role = 'Contributor')

        #Verify the user gets the message displayed.
        self.user_message_pg.impersonate(self.non_member.username)
        self.user_message_pg.open_messages()
        self.assertTrue(self._TEST_MESSAGES['INVITATION'] in 
            self.user_message_pg.message_text())

    def test_messages__application(self):
        self.user_message_pg.impersonate(self.non_member.username)
        self.a_team_pg.open_team_page(self.team.slug)
        self.a_team_pg.apply()
        self.assertTrue(self._TEST_MESSAGES['APPLICATION'] in 
            self.a_team_pg.application_custom_message())

    def test_messages__promoted_admin(self):
        self.members_tab.member_search(self.team.slug,
            self.team_member.username)
        self.members_tab.edit_user(role="Admin")

        #Verify the user gets the message displayed.
        self.user_message_pg.impersonate(self.team_member.username)
        self.user_message_pg.open_messages()
        self.assertTrue(self._TEST_MESSAGES['NEW_ADMIN'] in 
            self.user_message_pg.message_text())

    def test_messages__promoted_manager(self):
        self.members_tab.member_search(self.team.slug,
            self.team_member.username)
        self.members_tab.edit_user(role="Manager")

        #Verify the user gets the message displayed.
        self.user_message_pg.impersonate(self.team_member.username)
        self.user_message_pg.open_messages()
        self.assertTrue(self._TEST_MESSAGES['NEW_MANAGER'] in 
            self.user_message_pg.message_text())
 
        

        

       
     

         




