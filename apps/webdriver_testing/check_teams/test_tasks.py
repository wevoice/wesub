# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages.teams_dir_page import TeamsDirPage
from apps.webdriver_testing.pages.site_pages.teams.tasks_tab import TasksTab
from apps.webdriver_testing.pages.site_pages.teams.videos_tab import VideosTab
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamContributorMemberFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import TeamLangPrefFactory
from apps.webdriver_testing.data_factories import UserLangFactory
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import VideoFactory
from apps.webdriver_testing.data_factories import WorkflowFactory
from apps.webdriver_testing.pages.editor_pages import unisubs_menu
from apps.webdriver_testing.pages.editor_pages import dialogs
from apps.webdriver_testing import data_helpers

class TestCaseManualTasks(WebdriverTestCase):    
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseManualTasks, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.tasks_tab = TasksTab(cls)
        cls.videos_tab = VideosTab(cls)
        cls.menu = unisubs_menu.UnisubsMenu(cls)
        cls.create_modal = dialogs.CreateLanguageSelection(cls)

        #Create a partner user to own the team.
        cls.user = UserFactory.create(is_partner = True)

        #CREATE AN OPEN TEAM WITH WORKFLOWS and AUTOTASKS
        cls.team = TeamMemberFactory.create(
            team__workflow_enabled = True,
            user = cls.user,
            ).team
        WorkflowFactory.create(
            team = cls.team,
            autocreate_subtitle = False,
            autocreate_translate = False,
            review_allowed = 10)
        #Create a member of the team
        cls.contributor = TeamContributorMemberFactory.create(
            team = cls.team,
            user = UserFactory.create()
            ).user

        #Create a test video and add it to the team
        cls.test_video = VideoFactory.create()
        TeamVideoFactory.create(
            team=cls.team, 
            video=cls.test_video,
            added_by=cls.user)
        cls.videos_tab.open_videos_tab(cls.team.slug)

    def tearDown(self):
        self.browser.get_screenshot_as_file('MYTMP/%s.png' % self.id())


    def setUp(self):
        self.videos_tab.open_videos_tab(self.team.slug)


    def test_create(self):
        """Create a manual transcription task
        
        """
        #Configure workflow with autocreate tasks set to False 
        self.videos_tab.log_in(self.user.username, 'password')
        self.videos_tab.open_videos_tab(self.team.slug)

        self.videos_tab.open_video_tasks(self.test_video.title)
        self.tasks_tab.add_task(task_type = 'Transcribe')
        self.assertTrue(self.tasks_tab.task_present('Transcribe', 
                        self.test_video.title))

class TestCaseAutomaticTasks(WebdriverTestCase):    
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseAutomaticTasks, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.tasks_tab = TasksTab(cls)
        cls.videos_tab = VideosTab(cls)
        cls.menu = unisubs_menu.UnisubsMenu(cls)
        cls.create_modal = dialogs.CreateLanguageSelection(cls)

        #Create a partner user to own the team.
        cls.owner = UserFactory.create(is_partner=True)

        #CREATE AN OPEN TEAM WITH WORKFLOWS and AUTOTASKS
        cls.team = TeamMemberFactory.create(
            team__workflow_enabled = True,
            user = cls.owner,
            ).team

        WorkflowFactory.create(
            team = cls.team,
            autocreate_subtitle = True,
            autocreate_translate = True)
        lang_list = ['en', 'ru', 'pt-br', 'fr', 'de', 'es']
        for language in lang_list:
            TeamLangPrefFactory.create(
                team = cls.team,
                language_code = language,
                preferred = True)
        #Create a member of the team
        cls.contributor = TeamContributorMemberFactory.create(
            team = cls.team,
            user = UserFactory.create()
            ).user
        user_langs = ['en', 'ru', 'pt-br']
        for lang in user_langs:
            UserLangFactory(user=cls.contributor, language=lang)


    def setUp(self):
        self.tasks_tab.open_team_page(self.team.slug)
        self.tasks_tab.set_skiphowto()


    def tearDown(self):
        self.browser.get_screenshot_as_file('MYTMP/%s.png' % self.id())


    def test_transcription__perform(self):
        """Starting a Transcription task opens the subtitling dialog."""
        tv = TeamVideoFactory(team=self.team, added_by=self.owner).video
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Transcribe', tv.title)
        self.create_modal.lang_selection(video_language='English')
        self.assertEqual('Typing', self.sub_editor.dialog_title())


    def test_transcription__save(self):
        """After saving without submission, Transcription task exists, is
           assigned to the same user.

        """
        self.skipTest('Needs to be completed') 

    def test_transcription__resume(self):
        """Saved trasncription task can be resumed. """
        self.skipTest('Needs to be completed') 

    def test_transcription__permissions(self):
        """User must have permission to start a transcription task. 
        """
        self.skipTest('Needs to be completed') 

    def test_transcription__complete(self):
        """When transcription is completed, translation tasks are created 
           for preferred languages.

        """
        tv = TeamVideoFactory(team=self.team, added_by=self.owner).video
        video_data = {'language_code': 'en',
                      'video': tv.pk,
                      'draft': open('apps/videos/fixtures/test.srt'),
                     }

        self.data_utils.upload_subs(
                tv,
                data=None, 
                user=dict(username=self.contributor.username, 
                password='password'))

        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Transcribe', tv.title)
        self.create_modal.lang_selection(video_language='English')
        self.assertEqual('Typing', self.sub_editor.dialog_title())
