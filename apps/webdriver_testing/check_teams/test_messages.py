# -*- coding: utf-8 -*-
from django.core import mail

from teams import tasks
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages.teams import ATeamPage
from webdriver_testing.pages.site_pages.teams import messages_tab
from webdriver_testing.pages.site_pages.teams import members_tab
from webdriver_testing.pages.site_pages import user_messages_page
from webdriver_testing.data_factories import TeamMemberFactory
from webdriver_testing.data_factories import TeamVideoFactory
from webdriver_testing import data_helpers
from webdriver_testing.data_factories import TeamProjectFactory
from webdriver_testing.data_factories import UserFactory

class TestCaseTeamMessages(WebdriverTestCase):
    """TestSuite for searching team videos """
    NEW_BROWSER_PER_TEST_CASE = False
    _TEST_MESSAGES = {
        'INVITATION': ('I hear you are an awesome translator, please join '
                       'my team.'),
        'APPLICATION': ('Thank you for applying to the team, we will review ' 
                        'your qualifications and get back to you.'),
        'NEW_MANAGER': ('Congrats, you have been promoted to Manager.'),
        'NEW_ADMIN': ('Congrats, you have been promoted to Admin status.')
        }

    @classmethod
    def setUpClass(cls):
        super(TestCaseTeamMessages, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.a_team_pg = ATeamPage(cls)
        cls.members_tab = members_tab.MembersTab(cls)
        cls.messages_tab = messages_tab.MessagesTab(cls)
        cls.user_message_pg = user_messages_page.UserMessagesPage(cls)
        cls.non_member = UserFactory.create(username='NonMember')
        cls.team_owner = UserFactory.create(is_partner = True)

        #CREATE AN APPLICATION-ONLY TEAM 
        cls.team = TeamMemberFactory.create(
            team__membership_policy = 1,
            user = cls.team_owner,
            ).team

        cls.team_member = TeamMemberFactory.create(role="ROLE_CONTRIBUTOR",
                                           user=UserFactory(),
                                           team=cls.team).user

        #ADD THE TEST MESSAGES TO THE TEST TEAM
        cls.members_tab.open_members_page(cls.team.slug)
        cls.members_tab.log_in(cls.team_owner.username, 'password')
        cls.messages_tab.open_messages_tab(cls.team.slug)
        cls.messages_tab.edit_messages(cls._TEST_MESSAGES)


    def test_videos_added_hourly(self):

        mail.outbox = []
        video = TeamVideoFactory.create(
                team=self.team, 
                video=self.data_utils.create_video())
        
        tasks.add_videos_notification_hourly.apply()
        msg = str(mail.outbox[-1].message())
        self.assertIn('team has added new videos, and they need your help:', 
                      msg)
        self.logger.info(msg)
        self.assertEqual(3,len(mail.outbox))

    def test_videos_added_daily(self):
        team2 = TeamMemberFactory(team__notify_interval='NOTIFY_DAILY').team
        mail.outbox = []
        video = TeamVideoFactory.create(
                team=team2, 
                video=self.data_utils.create_video())
        
        tasks.add_videos_notification_daily.apply()
        msg = str(mail.outbox[-1].message())
        self.logger.info(msg)
        self.assertIn('team has added new videos, and they need your help:', 
                      msg)

 
        
    def test_messages__edit(self):
        """Change the default messages via the UI and verify they are stored.

        """
        self.members_tab.log_in(self.team_owner.username, 'password')
        self.messages_tab.open_messages_tab(self.team.slug)

        self.assertEqual(self._TEST_MESSAGES, 
            self.messages_tab.stored_messages())

    def test_messages__invitation(self):
        """Invited user see the custom message.  """
        self.members_tab.log_in(self.team_owner.username, 'password')
        self.messages_tab.open_messages_tab(self.team.slug)

        self.members_tab.open_members_page(self.team.slug)
        self.members_tab.invite_user_via_form(
            username = self.non_member.username,
            message = 'Join my team',
            role = 'Contributor')

        #Verify the user gets the message displayed.
        self.user_message_pg.log_in(self.non_member.username, 'password')
        self.user_message_pg.open_messages()
        self.assertTrue(self._TEST_MESSAGES['INVITATION'] in 
            self.user_message_pg.message_text())

    def test_messages__application(self):
        """Custom message for user application.

        """
        self.user_message_pg.log_in(self.non_member.username, 'password')
        self.a_team_pg.open_team_page(self.team.slug)
        self.a_team_pg.apply()
        self.assertTrue(self._TEST_MESSAGES['APPLICATION'] in 
            self.a_team_pg.application_custom_message())

    def test_messages__promoted_admin(self):
        """Message for user promoted to admin.

        """
        self.skipTest('needs bugs fixed: i1541 and i438')
        self.members_tab.member_search(self.team.slug,
            self.team_member.username)
        self.members_tab.edit_user(role="Admin")

        #Verify the user gets the message displayed.
        self.user_message_pg.log_in(self.non_member.username, 'password')
        self.user_message_pg.open_messages()
        self.assertTrue(self._TEST_MESSAGES['NEW_ADMIN'] in 
            self.user_message_pg.message_text())

    def test_messages__promoted_manager(self):
        """Message for user promoted to manager.

        """
        self.skipTest('needs bugs fixed: i1541 and i438')
        self.members_tab.member_search(self.team.slug,
            self.team_member.username)
        self.members_tab.edit_user(role="Manager")

        #Verify the user gets the message displayed.
        self.user_message_pg.log_in(self.non_member.username, 'password')
        self.user_message_pg.open_messages()
        self.assertTrue(self._TEST_MESSAGES['NEW_MANAGER'] in 
            self.user_message_pg.message_text())
 
