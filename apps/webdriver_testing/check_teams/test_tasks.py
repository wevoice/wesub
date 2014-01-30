# -*- coding: utf-8 -*-
import os
import time
from django.core import mail
from django.core import management

from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages.teams_dir_page import TeamsDirPage
from webdriver_testing.pages.site_pages.teams.tasks_tab import TasksTab
from webdriver_testing.pages.site_pages.teams.videos_tab import VideosTab
from webdriver_testing.data_factories import TeamMemberFactory
from webdriver_testing.data_factories import TeamVideoFactory
from webdriver_testing.data_factories import TeamLangPrefFactory
from webdriver_testing.data_factories import UserLangFactory
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import VideoFactory
from webdriver_testing.data_factories import WorkflowFactory
from webdriver_testing.pages.editor_pages import unisubs_menu
from webdriver_testing.pages.editor_pages import dialogs
from webdriver_testing.pages.editor_pages import subtitle_editor
from webdriver_testing import data_helpers
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing.pages.site_pages import video_language_page
from webdriver_testing.pages.site_pages import editor_page


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
        cls.contributor = TeamMemberFactory.create(role="ROLE_CONTRIBUTOR",
            team = cls.team,
            user = UserFactory.create()
            ).user


        #Create a test video and add it to the team
        cls.test_video = cls.data_utils.create_video()

        #cls.test_video = VideoFactory.create()
        TeamVideoFactory.create(
            team=cls.team, 
            video=cls.test_video,
            added_by=cls.user)
        cls.videos_tab.open_videos_tab(cls.team.slug)


    def setUp(self):
        management.call_command('update_index', interactive=False)
        self.videos_tab.open_videos_tab(self.team.slug)



    def test_create(self):
        """Create a manual transcription task
        
        """
        #Configure workflow with autocreate tasks set to False 
        self.videos_tab.log_in(self.user.username, 'password')
        self.videos_tab.open_videos_tab(self.team.slug)

        self.videos_tab.open_video_tasks(self.test_video.title)
        self.tasks_tab.add_task(task_type = 'Transcribe')
#        self.assertTrue(self.tasks_tab.task_present('Transcribe Subtitles', 
#                        self.test_video.title))

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
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)
        cls.video_pg = video_page.VideoPage(cls)


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
        cls.contributor = TeamMemberFactory.create(role="ROLE_CONTRIBUTOR",
                team = cls.team,
                user = UserFactory.create()
                ).user
        cls.manager = TeamMemberFactory(role="ROLE_MANAGER",
                team = cls.team,
                user = UserFactory.create()
                ).user

        user_langs = ['en', 'ru', 'pt-br']
        for lang in user_langs:
            UserLangFactory(user=cls.contributor, language=lang)
        cls.subs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)
                                     ), 'oneline.txt')
        cls.tasks_tab.open_team_page(cls.team.slug)

    def tearDown(self):
        if self.team.subtitle_policy > 10:
            self.team.subtitle_policy = 10
            self.team.save() 
        if self.team.translate_policy > 10:
            self.team.translate_policy = 10
            self.team.save()
        self.tasks_tab.open_team_page(self.team.slug)
        self.tasks_tab.handle_js_alert('accept')


    def test_transcription_perform(self):
        """Starting a Transcription task opens the subtitling dialog."""
        tv = self.data_utils.create_video()
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Transcribe Subtitles', tv.title)
        self.create_modal.lang_selection(video_language='English')
        self.assertEqual('Typing', self.sub_editor.dialog_title())



    def test_task_search_speaker_metadata(self):
        tv = self.data_utils.create_video()
        #Update the video title and description (via api)
        url_part = 'videos/%s/' % tv.video_id
        new_data = {'metadata': {'speaker-name': 'Ronaldo', 
                                 'location': 'Portugal'}
                   }

        self.data_utils.make_request(self.owner, 'put', 
                                     url_part, **new_data)

        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)

        #Update the solr index
        management.call_command('update_index', interactive=False)

        #Open team tasks page and search for metadata.
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)

        self.tasks_tab.search('Ronaldo')
        self.assertTrue(self.tasks_tab.task_present('Transcribe Subtitles', tv.title))

    def test_task_search_location_metadata(self):
        tv = self.data_utils.create_video()
        #Update the video title and description (via api)
        url_part = 'videos/%s/' % tv.video_id
        new_data = {'metadata': {'speaker-name': 'Ronaldo', 
                                 'location': 'Portugal'}
                   }

        self.data_utils.make_request(self.owner, 'put', 
                                     url_part, **new_data)

        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)

        #Update the solr index
        management.call_command('update_index', interactive=False)

        #Open team tasks page and search for metadata.
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)

        self.tasks_tab.search('Portugal')
        self.assertTrue(self.tasks_tab.task_present('Transcribe Subtitles', tv.title))


    def test_transcription_save(self):
        """Incomplete transcription task exists, is assigned to the same user.

        """
        tv = self.data_utils.create_video()
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Transcribe Subtitles', tv.title)
        self.create_modal.lang_selection(video_language='English')
        self.sub_editor.type_subs(self.subs_file)
        self.sub_editor.save_and_exit()
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=me&/' 
                                 % self.team.slug)
        task = self.tasks_tab.task_present('Transcribe English Subtitles',
                                           tv.title)
        self.assertEqual(task['assignee'], 'Assigned to me')


    def test_transcription_resume(self):
        """Saved transcription task can be resumed. """
        tv = self.data_utils.create_video()
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Transcribe Subtitles', tv.title)
        self.create_modal.lang_selection(video_language='English')
        self.sub_editor.type_subs(self.subs_file)
        self.sub_editor.save_and_exit()
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=me'
                                 % self.team.slug)
        self.tasks_tab.perform_assigned_task('Transcribe English Subtitles', 
                                             tv.title)
        self.assertEqual('Typing', self.sub_editor.dialog_title())
        self.video_pg.open_video_page(tv.video_id)
        self.tasks_tab.handle_js_alert(action='accept')
        en_tag, _ = self.video_pg.language_status('English')
        self.assertEqual('original | incomplete', en_tag) 

    def test_transcription_permissions(self):
        """User must have permission to start a transcription task. 
        """
        self.team.subtitle_policy = 30
        self.team.save()
        tv = self.data_utils.create_video()
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertEqual(self.tasks_tab.disabled_task('Transcribe Subtitles', 
                         tv.title), 
                         "You don't have permission to perform this task.")


    def test_transcription_complete(self):
        """Translation tasks are created for preferred languages, on complete.

        """
        tv = self.data_utils.create_video()
        t = TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        data = {
                      'language_code': 'en',
                      'video': tv.pk,
                      'primary_audio_language_code': 'en',
                      'draft': open('apps/webdriver_testing/subtitle_data/'
                              'less_lines.ssa'),
                      'complete': False
               }

        self.data_utils.upload_subs(self.contributor, **data)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)

        self.tasks_tab.perform_assigned_task('Transcribe English Subtitles', tv.title)
        sub_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                'oneline.txt')
        self.sub_editor.edit_subs(sub_file)
        self.sub_editor.continue_to_next_step() #to syncing
        self.sub_editor.continue_to_next_step() #to description
        self.sub_editor.continue_to_next_step() #to review
        self.sub_editor.submit(complete=True)
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)

        self.assertTrue(self.tasks_tab.task_present(
                        'Translate Subtitles into Russian', tv.title))


    def test_translation_perform(self):
        """Starting a translation task opens the translation dialog."""
        data = { 'video__primary_audio_language_code': 'en' }
        tv = self.data_utils.create_video(**data)
        self.data_utils.add_subs(video=tv)
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone&lang=ru'
                                 % self.team.slug)
        #self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Translate Subtitles into ' 
                                               'Russian', tv.title)
        self.create_modal.lang_selection()
        self.assertEqual('Adding a New Translation', 
                         self.sub_editor.dialog_title())


    def test_translation_save(self):
        """Incomplete translation task exists, is assigned to the same user.

        """
        self.tasks_tab.log_out()
        data = { 'video__primary_audio_language_code': 'en' }
        tv = self.data_utils.create_video(**data)
        self.data_utils.add_subs(video=tv)
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone&lang=ru' 
                                 % self.team.slug)
        self.tasks_tab.perform_and_assign_task('Translate Subtitles into ' 
                                               'Russian', tv.title)
        self.create_modal.lang_selection()
        self.sub_editor.type_translation()
        self.sub_editor.save_translation()
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=me&lang=ru' 
                                 % self.team.slug)
        task = self.tasks_tab.task_present('Translate Subtitles into '
                                           'Russian', tv.title)
        self.assertEqual(task['assignee'], 'Assigned to me')

    def test_translation_permission(self):
        """User must have permission to start a transcription task. 
        """
        self.team.translate_policy = 30
        self.team.save()
        tv = self.data_utils.create_video()
        self.data_utils.add_subs(video=tv)
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertEqual(self.tasks_tab.disabled_task('Translate Subtitles '
                         'into Russian', tv.title), 
                         "You don't have permission to perform this task.")

    def test_available_tasks_filter(self):
        """Available tasks are for any project"""
        self.tasks_tab.log_in(self.contributor, 'password')
        tv = self.data_utils.create_video()
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.available_tasks()
        self.assertIn("?project=any", self.tasks_tab.current_url())
        self.assertTrue(self.tasks_tab.task_present('Transcribe Subtitles',
                                                     tv.title))

    def test_your_tasks_filter(self):
        """Your tasks shows all assigned to you. """
        video = self.data_utils.create_video()
        video.primary_audio_language_code = 'pt-br'
        video.save()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, video=video)
        task = list(tv.task_set.incomplete_subtitle().filter(language='pt-br'))[0]
        task.assignee = self.contributor
        task.save()
        management.call_command('index_team_videos', self.team.slug)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.your_tasks()
        self.assertIn("assignee=me&project=any&lang=all", 
                      self.tasks_tab.current_url())
        self.assertTrue(self.tasks_tab.task_present(
                'Transcribe Portuguese, Brazilian Subtitles', video.title))

    def test_members_assignment_filter(self):
        """Assignment filters by user, lang all and any project. """
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_page('teams/%s/members' % self.team.slug)
        self.tasks_tab.click_link_partial_text('Assignments')
        self.assertIn("?assignee=", self.tasks_tab.current_url())
        self.assertIn("&project=any&lang=all", self.tasks_tab.current_url())

 
    def test_video_langs_needed_filter(self):
        """Video XX langs needed filters by lang all and any assignee and tv. """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, video=video)
        management.call_command('index_team_videos', self.team.slug)
        management.call_command('update_index', interactive=False)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_page('teams/%s/videos' % self.team.slug)
        self.tasks_tab.click_link_partial_text('language needed')
        self.assertIn("?team_video=", self.tasks_tab.current_url())
        self.assertIn("&lang=all&assignee=anyone", self.tasks_tab.current_url())



    def test_video_tasks_filter(self):
        """Video task link filters by lang all and any assignee and tv. """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, video=video)
        management.call_command('index_team_videos', self.team.slug)
        management.call_command('update_index', interactive=False)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_page('teams/%s/videos' % self.team.slug)
        self.tasks_tab.click_by_css('a[title="Manage tasks"]')
        self.assertIn("?team_video=", self.tasks_tab.current_url())


    def test_video_page_tasks_link(self):
        """Tasks link on video page filters to that video."""
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, video=video)
        management.call_command('index_team_videos', self.team.slug)
        management.call_command('update_index', interactive=False)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_page('videos/%s' % video.video_id)
        self.tasks_tab.click_link_text('tasks for this video')
        self.assertIn("?team_video=", self.tasks_tab.current_url())

class TestCaseModeratedTasks(WebdriverTestCase):    
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseModeratedTasks, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.tasks_tab = TasksTab(cls)
        cls.videos_tab = VideosTab(cls)
        cls.video_pg = video_page.VideoPage(cls)

        cls.menu = unisubs_menu.UnisubsMenu(cls)
        cls.create_modal = dialogs.CreateLanguageSelection(cls)
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)

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
        lang_list = ['en', 'ru', 'pt-br', 'de', 'sv']
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

        user_langs = ['en', 'ru', 'de', 'sv', 'pt-br']
        for lang in user_langs:
            UserLangFactory(user=cls.contributor, language=lang)
            UserLangFactory(user=cls.manager, language=lang)
        cls.subs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)
                                     ), 'oneline.txt')

        cls.rejected_text = ('The subtitles have been returned to you for '
                             'additional work and/or corrections.')
        cls.accepted_review = ('The subtitles passed review and have been '
                               'submitted for approval.')
        cls.accepted_approve = 'and they are now published!'


    def setUp(self):
        self.tasks_tab.open_team_page(self.team.slug)
        self.tasks_tab.handle_js_alert(action='accept')

    def tearDown(self):
        if self.workflow.approve_allowed != 10:
            self.workflow.approve_allowed = 10
            self.workflow.save()

    def test_submit_transcript_creates_review_task(self):
        """Review task is created on transcription submission. """
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=self.data_utils.create_video()).video
        self.data_utils.upload_subs(self.contributor, 
                                    video=tv.pk, 
                                    primary_audio_language_code='en')
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)

        self.assertTrue(self.tasks_tab.task_present(
                'Review Original English Subtitles', tv.title))

    def test_submit_transcript_removes_transcribe_task(self):
        """Transcribe task removed when transcript is submitted.

        """
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=self.data_utils.create_video()).video
        self.data_utils.upload_subs(self.contributor, video=tv.pk)
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)
        self.assertFalse(self.tasks_tab.task_present(
                        'Transcribe Subtitles', tv.title))

    def test_review_accept_creates_approve_task(self):
        """Approve task is created when reviewer accept transcription. """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'How-to.en.srt'),
                'is_complete': True,
                'complete': 1
               }

        self.data_utils.upload_subs(self.contributor, **data)
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Review Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        self.sub_editor.complete_review(result='Accept')
        self.sub_editor.mark_subs_complete()
        self.sub_editor.click_saved_ok()
        self.assertTrue(self.tasks_tab.task_present(
                        'Approve Original English Subtitles', video.title))
        task = list(tv.task_set.all_approve().all())[0]

    def test_review_accept_removes_review_task(self):
        """Review task removed after reviewer accepts transcription. """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertFalse(self.tasks_tab.task_present(
                        'Review Original English Subtitles', video.title))

    def test_review_accept_email(self):
        """Review task removed after reviewer accepts transcription. """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        mail.outbox = []
        self.complete_review_task(tv, 20)
        email_to = mail.outbox[-1].to     
        msg = str(mail.outbox[-1].message())
        self.logger.info("MESSAGE: %s" % msg)
        self.assertIn(self.contributor.email, email_to)
        self.assertIn(self.accepted_review, msg)





    def test_review_reject_transcription_reassigned(self):
        """Transcription task is reassigned when rejected by reviewer """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }

        self.data_utils.upload_subs(self.contributor, **data)
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Review Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        self.sub_editor.complete_review(result='Send Back')
        self.sub_editor.click_saved_ok()
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)
        task = self.tasks_tab.task_present('Transcribe English Subtitles',
                                           video.title)
        self.assertEqual(task['assignee'], 
                         'Assigned to %s' %self.contributor.username)

    def test_review_reject_removes_review_task(self):
        """Review task is removed when transcription rejected by reviewer """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }

        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 30)
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)
        self.assertFalse(self.tasks_tab.task_present(
                        'Review Original English Subtitles', video.title))

    def test_approve_creates_translate_tasks(self):
        """Translation tasks created, when transcription approved by approver.

        """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Approve Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        self.sub_editor.complete_approve(result='Approve')
        self.sub_editor.mark_subs_complete()
        self.sub_editor.click_saved_ok()
        self.assertTrue(self.tasks_tab.task_present(
                        'Translate Subtitles into German', video.title))

    def test_approve_removes_approve_tasks(self):
        """Approve task removed when transcription is approved by approver.

        """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        self.complete_approve_task(tv, 20)
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertFalse(self.tasks_tab.task_present(
                        'Approve Original English Subtitles', video.title))

    def test_approve_accept_email_translator(self):
        """Email sent to reviewer when approver accepts transcription. """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        mail.outbox = []

        self.complete_approve_task(tv, 20)

        email_to = mail.outbox[-1].to     
        msg = str(mail.outbox[-1].message())
        self.logger.info("MESSAGE: %s" % msg)
        self.assertIn(self.contributor.email, email_to)
        self.assertIn(self.accepted_approve, msg)

    def test_approve_accept_email_reviewer(self):
        """Email sent to reviewer when approver accepts transcription. """
        self.skipTest("https://github.com/pculture/unisubs/issues/600")
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        mail.outbox = []

        self.complete_approve_task(tv, 20)

        email_to = mail.outbox[-1].to     
        msg = str(mail.outbox[-1].message())
        self.logger.info("MESSAGE: %s" % msg)
        self.assertIn(self.manager.email, email_to)
        self.assertIn(self.accepted_approve, msg)


    def test_approve_reject_removes_approve_tasks(self):
        """Approve task removed when transcription is rejected by approver.

        """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        self.complete_approve_task(tv, 30)

        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)
        self.assertFalse(self.tasks_tab.task_present(
                        'Approve Original English Subtitles', video.title))

    def test_approve_reject_reassigns_review(self):
        """Review task reassigned when, approver rejects transcription.

        """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Approve Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        self.sub_editor.complete_approve(result='Send Back')
        self.sub_editor.click_saved_ok()
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)
        t = self.tasks_tab.task_present('Review Original English Subtitles',
                                        video.title)
        self.assertEqual(t['assignee'], 'Assigned to %s' 
                         % self.manager.username)

    def test_approve_send_back_email(self):
        """Email sent to reviewer when approver rejects transcription.

        """
        self.skipTest('Needs https://github.com/pculture/unisubs/issues/600 '
                      ' fixed')
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        
        self.tasks_tab.perform_and_assign_task('Approve Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        mail.outbox = []

        self.sub_editor.complete_approve(result='Send Back')
        self.sub_editor.click_saved_ok()
        self.logger.info(mail.outbox)
        email_to = mail.outbox[-1].to     
        msg = str(mail.outbox[-1].message())

        self.assertIn(self.manager.email, email_to)
        self.assertIn(self.rejected_text, msg)




    def test_review_send_back_email(self):
        """Translator emailed when review sends-back transcript. """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        mail.outbox = []
        self.complete_review_task(tv, 20)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Approve Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        self.sub_editor.complete_approve(result='Send Back')
        self.sub_editor.click_saved_ok()
        email_to = mail.outbox[-1].to     
        msg = str(mail.outbox[-1].message())
        self.logger.info("MESSAGE: %s" % msg)
        self.assertIn(self.contributor.email, email_to)
        self.assertIn(self.rejected_text, msg)



    def make_video_with_approved_transcript(self):
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                              video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
           }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        if self.workflow.approve_enabled:
            self.complete_approve_task(tv, 20)
        return video, tv

    def upload_translation(self, video):
        data = {'language_code': 'sv',
                'video': video.pk,
                'from_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
           }
        self.data_utils.upload_subs(self.contributor, **data)

    def complete_review_task(self, tv, status_code):
        """Complete the review task, 20 for approve, 30 for reject.
 
        Making the assumtion that I have only 1 at a time.

        """
        task = list(tv.task_set.incomplete_review().all())[0]
        task.assignee = self.manager
        task.approved = status_code
        task.save()
        task.complete()

    def complete_approve_task(self, tv, status_code):
        """Complete the approve task, 20 for approve, 30 for reject.
 
        Making the assumtion that I have only 1 at a time.

        """
        task = list(tv.task_set.incomplete_approve().all())[0]
        task.assignee = self.owner
        task.approved = status_code
        task.save()
        task.complete()

    def test_submit_translation_displays_as_draft(self):
        """Unreviewed translations are marked as drafts on site. """
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)

        self.tasks_tab.log_in(self.manager, 'password')
        sl = video.subtitle_language('sv')
        self.tasks_tab.open_page(sl.get_absolute_url()[4:])
        self.assertTrue(self.video_lang_pg.is_draft())


    def test_submit_translation_creates_review_task(self):
        """Review task is created when translation is submitted. """
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)

        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertTrue(self.tasks_tab.task_present(
                'Review Swedish Subtitles', video.title))

    def test_submit_translation_removes_translate_task(self):
        """Translation task removed when translation submitted. """
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)

        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertFalse(self.tasks_tab.task_present(
                'Translate Subtitles into Swedish', video.title))

    def test_translation_review_accept_creates_approve_task(self):
        """Approve task is created when translation accepted by reviewer.

        """
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)
        self.complete_review_task(tv, 20)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertTrue(self.tasks_tab.task_present(
                'Approve Swedish Subtitles', video.title))

    def test_translation_review_accept_removes_review_task(self):
        """Review task removed when translation accepted by reviewer.

        """
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)
        self.complete_review_task(tv, 20)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertFalse(self.tasks_tab.task_present(
                'Review Swedish Subtitles', video.title))

    def test_translation_review_reject_reassigns_translate(self):
        """Translation reassigned when translation is rejected by reviewer. """
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)
        self.complete_review_task(tv, 30)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)
        t = self.tasks_tab.task_present('Translate Subtitles into Swedish',
                                        video.title)
        self.assertEqual(t['assignee'], 'Assigned to %s' 
                         % self.contributor.username)


    def test_translation_review_reject_removes_review(self):
        """Review task removed when translation rejected by reviewer.

        """
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)
        self.complete_review_task(tv, 30)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertFalse(self.tasks_tab.task_present(
                'Review Swedish Subtitles', video.title))

    def test_translation_approve_removes_approve(self):
        """Approve task removed when accepted by approver.

        """
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)
        self.complete_review_task(tv, 20)
        self.complete_approve_task(tv, 20)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertFalse(self.tasks_tab.task_present(
                'Approve Swedish Subtitles', video.title))

    def test_translation_approve_published(self):
        """Translation is published when approved.

        """
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)
        self.complete_review_task(tv, 20)
        self.complete_approve_task(tv, 20)
        sl = video.subtitle_language('sv')
        self.assertEqual('public', sl.get_tip().get_visibility_display())
        self.tasks_tab.open_page(sl.get_absolute_url()[4:])
        self.assertFalse(self.video_lang_pg.is_draft())

    def test_translation_approve_reject_reassigns_review(self):
        """Review reassigned when translation review is rejected by approver.

        """
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)
        self.complete_review_task(tv, 20)
        self.complete_approve_task(tv, 30)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)
        t = self.tasks_tab.task_present('Review Swedish Subtitles',
                                        video.title)
        self.assertEqual(t['assignee'], 'Assigned to %s' 
                         % self.manager.username)


    def test_translation_approve_reject_removes_approve(self):
        """Approve task removed when translation review rejected by approver.

        """
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)
        self.complete_review_task(tv, 20)
        self.complete_approve_task(tv, 30)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertFalse(self.tasks_tab.task_present(
                'Approve Swedish Subtitles', video.title))

    def test_draft_guest_translate(self):
        """Translate policy: members, guest has no new translation in menu."""

        """Guest can not translate published subtitles."""
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }

        self.data_utils.upload_subs(self.contributor, **data)
        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.assertFalse(self.video_lang_pg.displays_add_subtitles())

    def test_transcription_resume_original_lang(self):
        """Resuming task does not reset originl language. """
        tv = self.data_utils.create_video()
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Transcribe Subtitles', tv.title)
        self.create_modal.lang_selection(video_language='English')
        self.sub_editor.type_subs(self.subs_file)
        self.sub_editor.save_and_exit()
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=me'
                                 % self.team.slug)
        self.tasks_tab.perform_assigned_task('Transcribe English Subtitles', 
                                             tv.title)
        self.assertEqual('Typing', self.sub_editor.dialog_title())
        self.video_pg.open_video_page(tv.video_id)
        self.tasks_tab.handle_js_alert(action='accept')
        en_tag, _ = self.video_pg.language_status('English')
        self.assertEqual('original | incomplete', en_tag) 



class TestCaseAutomaticTasksBetaEditor(WebdriverTestCase): 
    """Automatic task tests the require actions from the New editor."""
   
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseAutomaticTasksBetaEditor, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.tasks_tab = TasksTab(cls)
        cls.videos_tab = VideosTab(cls)
        cls.menu = unisubs_menu.UnisubsMenu(cls)
        cls.create_modal = dialogs.CreateLanguageSelection(cls)
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.editor_pg = editor_page.EditorPage(cls)


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
        cls.contributor = TeamMemberFactory.create(role="ROLE_CONTRIBUTOR",
                team = cls.team,
                user = UserFactory.create()
                ).user
        cls.manager = TeamMemberFactory(role="ROLE_MANAGER",
                team = cls.team,
                user = UserFactory.create()
                ).user

        user_langs = ['en', 'ru', 'pt-br']
        for lang in user_langs:
            UserLangFactory(user=cls.contributor, language=lang)
        cls.subs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)
                                     ), 'oneline.txt')
        cls.tasks_tab.open_team_page(cls.team.slug)


    def setUp(self):
        self.tasks_tab.open_page('teams/%s' % self.team.slug, True)


    def test_transcription_save(self):
        """Beta editor save, incomplete task exists, assigned to same user.

        """
        tv = self.data_utils.create_video()
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Transcribe Subtitles',
                                               tv.title)
        self.create_modal.lang_selection(video_language='English')
        self.sub_editor.open_in_beta_editor(mark_complete=False)
        subs = ['line 1', 'line 2', 'THE END']
        self.editor_pg.edit_sub_line(subs, 0)


        self.editor_pg.save('Exit')
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=me' 
                                 % self.team.slug)
        task = self.tasks_tab.task_present('Transcribe English Subtitles',
                                           tv.title)
        self.assertEqual(task['assignee'], 'Assigned to me')



    def test_transcription_complete(self):
        """Beta editor, complete taks, preferred translation tasks created. """
        tv = self.data_utils.create_video()
        t = TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        data = {'language_code': 'en',
                'video': tv.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'less_lines.ssa'),
                'complete': False
               }

        self.data_utils.upload_subs(self.contributor, **data)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)

        self.tasks_tab.perform_assigned_task('Transcribe English Subtitles',
                                             tv.title)
        sub_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                'oneline.txt')
        self.sub_editor.edit_subs(sub_file)
        self.sub_editor.open_in_beta_editor()
        self.editor_pg.edit_sub_line('TEST EDITED TEXT', 1)
        self.assertEqual('Start reviewing', self.editor_pg.next_step())
        self.editor_pg.start_next_step()
        self.editor_pg.start_next_step()
        self.editor_pg.endorse_subs()
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)
        self.assertTrue(self.tasks_tab.task_present(
                        'Translate Subtitles into Russian', tv.title))


    def test_translation_save(self):
        """Beta editor, save incomplete translation task.

        Verify the task is assigned to the same user.

        """
        tv = self.data_utils.create_video()
        self.data_utils.add_subs(video=tv)
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?lang=ru'
                                 % self.team.slug)
        self.tasks_tab.perform_and_assign_task('Translate Subtitles into ' 
                                               'Russian', tv.title)
        self.create_modal.lang_selection(video_language='English')
        self.sub_editor.type_translation()
        self.sub_editor.open_in_beta_editor(mark_complete=False)
        self.editor_pg.edit_sub_line('TEST EDITED TEXT', 1, enter=False)
        self.editor_pg.save('Exit')

        self.tasks_tab.open_page('teams/%s/tasks/?assignee=me&lang=ru'
                                 % self.team.slug)
        task = self.tasks_tab.task_present('Translate Subtitles into '
                                           'Russian', tv.title)
        self.assertEqual(task['assignee'], 'Assigned to me')


    def test_translation_permission(self):
        """Open Beta editor, user must have permission to start a task. 
        """
        self.team.translate_policy = 30
        self.team.save()
        tv = self.data_utils.create_video()
        self.data_utils.add_subs(video=tv)
        TeamVideoFactory(team=self.team, added_by=self.owner, video=tv)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.editor_pg.open_editor_page(tv.video_id, 'ru')
        self.assertIn('Another user is currently performing', 
                      self.video_pg.get_message())


class TestCaseModeratedTasksBetaEditor(WebdriverTestCase):    
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseModeratedTasksBetaEditor, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.tasks_tab = TasksTab(cls)
        cls.videos_tab = VideosTab(cls)
        cls.video_pg = video_page.VideoPage(cls)

        cls.menu = unisubs_menu.UnisubsMenu(cls)
        cls.create_modal = dialogs.CreateLanguageSelection(cls)
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.editor_pg = editor_page.EditorPage(cls)

        #Create a partner user to own the team.
        cls.owner = UserFactory.create(is_partner=True)

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
        lang_list = ['en', 'ru', 'pt-br', 'de', 'sv']
        for language in lang_list:
            TeamLangPrefFactory.create(
                team = cls.team,
                language_code = language,
                preferred = True)
        #Create a member of the team
        cls.contributor = TeamMemberFactory.create(role="ROLE_CONTRIBUTOR",
                team = cls.team,
                user = UserFactory.create()
                ).user
        cls.manager = TeamMemberFactory(role="ROLE_MANAGER",
                team = cls.team,
                user = UserFactory.create()
                ).user

        user_langs = ['en', 'ru', 'de', 'sv', 'pt-br']
        for lang in user_langs:
            UserLangFactory(user=cls.contributor, language=lang)
            UserLangFactory(user=cls.manager, language=lang)
        cls.subs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)
                                     ), 'oneline.txt')
        cls.rejected_text = ('The subtitles have been returned to you for '
                             'additional work and/or corrections.')
        cls.accepted_review = 'The subtitles passed review and have been submitted for approval.'
        cls.accepted_approve = 'and they are now published!'

    def setUp(self):
        self.tasks_tab.open_team_page(self.team.slug)
        self.tasks_tab.handle_js_alert(action='accept')

    def tearDown(self):
        if self.workflow.approve_allowed != 10:
            self.workflow.approve_allowed = 10
            self.workflow.save()


    def test_review_accept_creates_approve_task(self):
        """Beta editor approve task is created when transcription accepted.

        """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'How-to.en.srt'),
                'is_complete': True,
                'complete': 1
               }

        self.data_utils.upload_subs(self.contributor, **data)
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Review Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        self.sub_editor.open_in_beta_editor()
        self.editor_pg.approve_task()
        en_tag, _ = self.video_pg.language_status('English')
        self.assertEqual('original | needs approval', en_tag) 
        self.tasks_tab.open_tasks_tab(self.team.slug)

        self.assertTrue(self.tasks_tab.task_present(
                        'Approve Original English Subtitles', video.title))
        task = list(tv.task_set.all_approve().all())[0]

    def test_review_notes_are_saved(self):
        """Notes added are saved. 

        """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }

        self.data_utils.upload_subs(self.manager, **data)
        self.tasks_tab.log_in(self.contributor, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.open_page('/subtitles/editor/%s/en/' % video.video_id)
        note_text = 'This is a note'
        self.editor_pg.add_note(note_text)
        self.editor_pg.save('Exit')
        task = list(tv.task_set.all_review().all())[0]
        self.logger.info(dir(task))
        self.assertEqual(note_text, task.body)


    def test_review_accept_email(self):
        """Email sent when task accepted, contains notes.

        """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'How-to.en.srt'),
                'is_complete': True,
                'complete': 1
               }

        self.data_utils.upload_subs(self.contributor, **data)
        self.tasks_tab.log_in(self.manager, 'password')
        mail.outbox = []
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Review Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        self.sub_editor.open_in_beta_editor()
        self.editor_pg.approve_task()
        self.logger.info(mail.outbox)
        email_to = mail.outbox[-1].to     
        msg = str(mail.outbox[-1].message())

        self.assertIn(self.contributor.email, email_to)
        self.assertIn(self.accepted_review, msg)



    def test_review_reject_transcription_reassigned(self):
        """Beta editor transcription task is reassigned when sent back """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }

        self.data_utils.upload_subs(self.contributor, **data)
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Review Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        self.sub_editor.open_in_beta_editor()
        self.editor_pg.send_back_task()
        en_tag, _ = self.video_pg.language_status('English')
        self.assertEqual('original | needs editing', en_tag) 
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)
        task = self.tasks_tab.task_present('Transcribe English Subtitles',
                                           video.title)
        self.assertEqual(task['assignee'], 
                         'Assigned to %s' %self.contributor.username)

    def test_review_send_back_email(self):
        """Beta editor transcription task is reassigned when sent back """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }

        self.data_utils.upload_subs(self.contributor, **data)
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?type=Review'
                                 % self.team.slug)

        self.tasks_tab.perform_and_assign_task('Review Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        self.sub_editor.open_in_beta_editor()
        mail.outbox = []
        self.editor_pg.send_back_task()
        self.logger.info(mail.outbox)
        email_to = mail.outbox[-1].to     
        msg = str(mail.outbox[-1].message())

        self.assertIn(self.contributor.email, email_to)
        self.assertIn(self.rejected_text, msg)

    


    def test_approve_creates_translate_tasks(self):
        """Translation tasks created, when transcription approved by approver.

        """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        self.tasks_tab.log_in(self.manager, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Approve Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        self.sub_editor.open_in_beta_editor()
        self.editor_pg.approve_task()
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertTrue(self.tasks_tab.task_present(
                        'Translate Subtitles into German', video.title))



    def test_approve_reject_reassigns_review(self):
        """Review task reassigned when, approver rejects transcription.

        """
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                         video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
               }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        self.tasks_tab.log_in(self.owner, 'password')
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Approve Original English ' 
                                               'Subtitles', video.title)
        self.sub_editor.continue_to_next_step() #to subtitle info 
        self.sub_editor.open_in_beta_editor()
        self.editor_pg.send_back_task()
        en_tag, _ = self.video_pg.language_status('English')
        self.assertEqual('original | needs review', en_tag) 
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone'
                                 % self.team.slug)
        t = self.tasks_tab.task_present('Review Original English Subtitles',
                                        video.title)
        self.assertEqual(t['assignee'], 'Assigned to %s' 
                         % self.manager.username)


    def make_video_with_approved_transcript(self):
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                              video=video)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
           }
        self.data_utils.upload_subs(self.contributor, **data)
        self.complete_review_task(tv, 20)
        if self.workflow.approve_enabled:
            self.complete_approve_task(tv, 20)
        return video, tv

    def upload_translation(self, video):
        data = {'language_code': 'sv',
                'video': video.pk,
                'from_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'is_complete': True,
                'complete': 1
           }
        self.data_utils.upload_subs(self.contributor, **data)

    def complete_review_task(self, tv, status_code):
        """Complete the review task, 20 for approve, 30 for reject.
 
        Making the assumtion that I have only 1 at a time.

        """
        task = list(tv.task_set.incomplete_review().all())[0]
        task.assignee = self.manager
        task.approved = status_code
        task.save()
        task.complete()

    def complete_approve_task(self, tv, status_code):
        """Complete the approve task, 20 for approve, 30 for reject.
 
        Making the assumtion that I have only 1 at a time.

        """
        task = list(tv.task_set.incomplete_approve().all())[0]
        task.assignee = self.owner
        task.approved = status_code
        task.save()
        task.complete()
