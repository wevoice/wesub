import time
from django.core import mail
from django.core import management

from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages.teams.tasks_tab import TasksTab
from webdriver_testing.data_factories import TeamMemberFactory
from webdriver_testing.data_factories import TeamVideoFactory
from webdriver_testing.data_factories import TeamLangPrefFactory
from webdriver_testing.data_factories import UserLangFactory
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import VideoFactory
from webdriver_testing.data_factories import WorkflowFactory
from webdriver_testing import data_helpers

class TestCaseBulkApprove(WebdriverTestCase):    
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseBulkApprove, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.tasks_tab = TasksTab(cls)
        #Create a partner user to own the team.
        cls.owner = UserFactory.create(is_partner=True, 
                                       email='owner@example.com')

        #CREATE AN OPEN TEAM WITH WORKFLOWS and AUTOTASKS
        cls.team = TeamMemberFactory.create(
            team__workflow_enabled = True,
            user = cls.owner,
            ).team

        cls.workflow = WorkflowFactory.create(
            team = cls.team,
            autocreate_subtitle = True,
            autocreate_translate = True,
            review_allowed = 10,
            approve_allowed = 10)
        lang_list = ['en', 'ru', 'pt-br', 'de', 'sv', 'fr', 'it']
        for language in lang_list:
            TeamLangPrefFactory.create(
                team = cls.team,
                language_code = language,
                preferred = True)
        #Create a member of the team
        cls.contributor = TeamMemberFactory.create(role="ROLE_CONTRIBUTOR",
                team = cls.team,
                ).user
        cls.manager = TeamMemberFactory(role="ROLE_MANAGER",
                team = cls.team,
                ).user


    def setUp(self):
        self.tasks_tab.open_page('teams/%s/approvals/' %self.team.slug)


    def tearDown(self):
        self.browser.get_screenshot_as_file('%s.png' % self.id())


    def complete_review_tasks(self, tv):
        """Complete the review task, 20 for approve, 30 for reject.
 
        Making the assumtion that I have only 1 at a time.

        """
        tasks = list(tv.task_set.incomplete_review().all())
        for task in tasks: 
            task.assignee = self.manager
            task.approved = 20
            task.save()
            task.complete()


    def test_bulk_approve(self):
        """bulk accept approval tasks """
        self.tasks_tab.log_in(self.owner.username, 'password')
        self.tasks_tab.open_page('teams/%s/approvals/' %self.team.slug)
        lang_list = ('en', 'fr', 'de', 'it', 'hr', 'ro', 'ru', 'sv', 'es', 'pt')
        for x in range(100):
            video = self.data_utils.create_video()
            tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
            for lc in lang_list:
                defaults = {
                            'video': tv.video,
                            'language_code': lc,
                            'complete': True, 
                            'visibility': 'private',
                            'committer': self.owner
                           }

                self.data_utils.add_subs(**defaults)
                self.complete_review_tasks(tv)

        self.tasks_tab.open_page('teams/%s/approvals/' %self.team.slug)
        start = time.clock()
        self.tasks_tab.bulk_approve_tasks()
        elapsed = (time.clock() - start)
        self.logger.info(elapsed)
        self.assertLess(elapsed, 5)
