# -*- coding: utf-8 -*-
import json

from utils.factories import *

from rest_framework.test import APILiveServerTestCase, APIClient
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing import data_helpers
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import TeamMemberFactory
from webdriver_testing.pages.site_pages import user_messages_page


class TestCaseMessages(APILiveServerTestCase, WebdriverTestCase):
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
        cls.messages_pg = user_messages_page.UserMessagesPage(cls)
        cls.messages_pg.open_messages()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory()
        cls.staff = UserFactory(is_staff=True, is_superuser=True)
        cls.admin = UserFactory()
        cls.manager = UserFactory()
        cls.member = UserFactory()
        cls.team = TeamFactory(admin=cls.admin,
                               manager=cls.manager,
                               member=cls.member,
                              )

        cls.client = APIClient

    def _post(self, url='/api/message/', data=None, user=None):
        self.client.force_authenticate(user)
        response = self.client.post(url, data)
        response.render()
        r = (json.loads(response.content))
        return r
    
    def test_message_user(self):
        """Send a message to a user.
        """
        
        #create a second team with 'second_member' as a member.
        user = UserFactory() 
        data = { "user": user.username,
                 "subject": "Subject of the message",
                 "content": "The message content" } 
        self._post(user=self.member, data=data)
        self.messages_pg.open_messages() 
        self.messages_pg.log_in(user.username, 'password')
        self.messages_pg.open_messages() 
        self.assertEqual(data['content'], 
            self.messages_pg.message_text())
        self.assertEqual(data['subject'], 
            self.messages_pg.message_subject())

    def test_message_team(self):
        """Send a message to a team.
        """
        user = UserFactory()         
        data = { "team": self.team.slug,
                 "subject": "Subject of the team message",
                 "content": "The team message content" } 
        #Nonmember the team
        r = self._post(user=user, data=data)
        self.assertEqual({u'detail': u'Permission denied'}, r)
        self.messages_pg.log_in(self.member.username, 'password')
        #Regular member the team
        r = self._post(user=self.member, data=data)
        self.assertEqual({u'detail': u'Permission denied'}, r)
        self.messages_pg.log_in(self.member.username, 'password')
        #Manager can't message team
        r = self._post(user=self.manager, data=data)
        self.assertEqual({u'detail': u'Permission denied'}, r)
        r = self._post(user=self.admin, data=data)
        self.logger.info(r)
        self.messages_pg.open_messages() 
        self.assertEqual(data['content'], 
            self.messages_pg.message_text())
        self.assertEqual(data['subject'], 
            self.messages_pg.message_subject())

