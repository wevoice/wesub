# -*- coding: utf-8 -*-
from utils.factories import *
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages.teams import messages_tab
from webdriver_testing.pages.site_pages.teams import tasks_tab
from webdriver_testing.data_factories import TeamLangPrefFactory
from webdriver_testing import data_helpers
import time

class TestCaseTeamGuidelines(WebdriverTestCase):    
    NEW_BROWSER_PER_TEST_CASE = False
    _TEST_GUIDELINES = {
        'SUBTITLE': ('The are the guidelines for subtitling for this team.'),
        'TRANSLATE': ('Do not just use google translate!'),
        'REVIEW': ('The Review process is very important. Check everything.')
        }


    @classmethod
    def setUpClass(cls):
        super(TestCaseTeamGuidelines, cls).setUpClass()
        cls.messages_tab = messages_tab.MessagesTab(cls)
        cls.tasks_tab = tasks_tab.TasksTab(cls)
        cls.admin = UserFactory.create()
        cls.team = TeamFactory(admin=cls.admin,
                               workflow_enabled=True,
                               translate_policy=20,
                               subtitle_policy=20,
                              )
        cls.team_workflow = WorkflowFactory(team = cls.team,
                                            autocreate_subtitle=True,
                                            autocreate_translate=True,
                                            review_allowed = 10,
                                           )

    def test_guidelines_edit(self):
        """Change the default guidelines and verify they are stored.

        """
        self.messages_tab.open_page('teams')

        self.messages_tab.log_in(self.admin.username, 'password')
        self.messages_tab.open_messages_tab(self.team.slug)
        self.messages_tab.edit_guidelines(self._TEST_GUIDELINES)

        self.assertEqual(self._TEST_GUIDELINES, 
            self.messages_tab.stored_guidelines())

