# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.pages.site_pages import user_messages_page


class TestCaseMessages(WebdriverTestCase):
    """TestSuite for sending messages via the api.

        POST /api2/partners/message/
          subject – Subject of the message
          content – Content of the message
          user – Recipient’s username
          team – Team’s slug
    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseMessages, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
    
        cls.user = UserFactory.create()
        

        cls.open_team = TeamMemberFactory.create(
            team__name="A1 Waay Cool team",
            team__slug='a1-waay-cool-team',
            team__description='this is the coolest, most creative team ever',
            user = cls.user,
            ).team
        cls.team_member = UserFactory.create(username = 'team_member')
        TeamMemberFactory.create(
            role = "ROLE_CONTRIBUTOR",
            team=cls.open_team, 
            user = cls.team_member) 
        for x in range(3):
            TeamMemberFactory.create(
            role = "ROLE_CONTRIBUTOR",
            team = cls.open_team,
            user = UserFactory.create())

        cls.second_user = UserFactory.create(username = 'second_user')
        cls.messages_pg = user_messages_page.UserMessagesPage(cls)
        cls.messages_pg.open_messages() 


    def test_message__user(self):
        """Send a message to a user.
       
        POST /api2/partners/message/

        """
        
        #create a second team with 'second_member' as a member.
        
        message_details = { "user": self.second_user.username,
                            "subject": "Subject of the message",
                            "content": "The message content" } 
        url_part = 'message/' 
        self.data_utils.make_request(self.user, 'post', url_part, **message_details)
        self.messages_pg.log_in(self.second_user.username, 'password')
        self.messages_pg.open_messages() 
        self.assertEqual(message_details['content'], 
            self.messages_pg.message_text())
        self.assertEqual(message_details['subject'], 
            self.messages_pg.message_subject())

    def test_message__team(self):
        """Send a message to a team.
       
        POST /api2/partners/message/

        """
                
        message_details = { "team": self.open_team.slug,
                            "subject": "Subject of the team message",
                            "content": "The team message content" } 
        url_part = 'message/' 
        self.data_utils.make_request(self.user, 'post', url_part, **message_details)
        self.messages_pg.log_in(self.team_member.username, 'password')
        self.messages_pg.open_messages() 

        self.assertEqual(message_details['content'], 
            self.messages_pg.message_text())
        self.assertEqual(message_details['subject'], 
            self.messages_pg.message_subject())

    def test_message__team_nonmember(self):
        """Non-team members don't get team messages.
       
        POST /api2/partners/message/

        """
                
        message_details = { "team": self.open_team.slug,
                            "subject": "Subject of the team message",
                            "content": "The team message content" } 
        url_part = 'message/' 
        self.data_utils.make_request(self.user, 'post', url_part, **message_details)
        self.messages_pg.log_in(self.second_user.username, 'password')
        self.messages_pg.open_messages() 
        self.assertEqual('You have no messages.', 
            self.messages_pg.no_messages())


    def test_message__sender(self):
        """Verify the messae sender via api shows the message in sent box.       
        POST /api2/partners/message/

        """        
        message_details = { "team": self.open_team.slug,
                            "subject": "Subject of the team message",
                            "content": "The team message content" } 
        url_part = 'message/' 
        self.data_utils.make_request(self.user, 'post', url_part, **message_details)
        self.messages_pg.log_in(self.user.username, 'password')
        self.messages_pg.open_sent_messages() 

        self.assertEqual(message_details['content'], 
            self.messages_pg.message_text())
        self.assertEqual(message_details['subject'], 
            self.messages_pg.message_subject())
       
