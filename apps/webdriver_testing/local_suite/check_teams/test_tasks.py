# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import my_teams
from apps.webdriver_testing.site_pages.teams import tasks_tab
from apps.webdriver_testing.site_pages.teams import videos_tab
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamContributorMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import VideoFactory
from apps.webdriver_testing.data_factories import WorkflowFactory

class TestCaseTeamTasks(WebdriverTestCase):
    """Verify tasks creation, modification, assignment.

        Assign a task
        Create a manual task
        Automatic task creation
        Filter tasks
        Perform task
        Remove a task from a team
Tasks link opens the page with the tasks for the video 
- Non-members and anon users do not see Tasks links
- Just added, non-subtitled video has tag "1 language needed" (if a task is created automatically) or "0 languages" (otherwise), the tag has an appropriate link 
    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.tasks_tab = tasks_tab.TasksTab(self)
        self.videos_tab = videos_tab.VideosTab(self)


        #Create a partner user to own the team.
        self.user = UserFactory.create(
            username='TestUser',
            is_superuser = True,
            is_partner = True)


        #CREATE AN OPEN TEAM WITH WORKFLOWS and AUTOTASKS
        self.open_team = TeamMemberFactory.create(
            team__name='Literal Video Version',
            team__slug='literal-video-version',
            team__workflow_enabled = True,
            user = self.user,
            ).team

        #Create a member of the team
        self.contributor = TeamContributorMemberFactory.create(
            team = self.open_team,
            user = UserFactory.create()
            ).user


        #Create a test video and add it to the team
        self.test_video = VideoFactory.create()

        TeamVideoFactory.create(
            team=self.open_team, 
            video=self.test_video,
            added_by=self.user)


    def test_create(self):
        """Create a manual transcription task
        
        """
        #Configure workflow with autocreate tasks set to False 
        WorkflowFactory.create(
            team = self.open_team,
            autocreate_subtitle = False,
            autocreate_translate = False,
            review_allowed = 10)

        self.videos_tab.log_in(self.user.username, 'password')
        self.videos_tab.open_videos_tab(self.open_team.slug)
        self.videos_tab.open_video_tasks(self.test_video.title)
        self.tasks_tab.add_task(task_type = 'Transcribe')
        self.assertTrue(self.tasks_tab.task_present('Transcribe', 
            self.test_video.title))


