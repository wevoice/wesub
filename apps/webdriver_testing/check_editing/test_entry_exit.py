#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from django.test import TestCase
from django.core import management

from videos.models import Video

from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing import data_helpers
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing.pages.site_pages import video_language_page
from webdriver_testing.pages.site_pages import editor_page
from webdriver_testing.pages.editor_pages import dialogs
from webdriver_testing.pages.editor_pages import unisubs_menu
from webdriver_testing.pages.editor_pages import subtitle_editor 
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import TaskFactory
from webdriver_testing.data_factories import WorkflowFactory
from webdriver_testing.pages.site_pages.teams.tasks_tab import TasksTab
from webdriver_testing.data_factories import TeamVideoFactory
from webdriver_testing.data_factories import TeamMemberFactory


class TestCaseEntryExit(WebdriverTestCase):
    """Entry and Exit points to New Editor. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseEntryExit, cls).setUpClass()
        cls.create_modal = dialogs.CreateLanguageSelection(cls)
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)
        cls.unisubs_menu = unisubs_menu.UnisubsMenu(cls)
        cls.editor_pg = editor_page.EditorPage(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.tasks_tab = TasksTab(cls)
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create()
        cls.video_pg.open_page('auth/login/')
        cls.video_pg.log_in(cls.user.username, 'password')
        cls.user = UserFactory.create()

    @classmethod
    def tearDownClass(cls):
        super(TestCaseEntryExit, cls).tearDownClass()

    def test_timed_to_new_and_back(self):
        """From timed editor to beta, reference and working langs are same.

        """
        data = {'url': 'http://www.youtube.com/watch?v=WqJineyEszo',
                 'video__title': ('X Factor Audition - Stop Looking At My '
                                  'Mom Rap - Brian Bradley'),
                                  'type': 'Y'
               }
        video = self.data_utils.create_video(**data)
        self.data_utils.add_subs(video=video)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.edit_subtitles()
        self.sub_editor.open_in_beta_editor()
        self.assertEqual('English', self.editor_pg.selected_ref_language())
        self.assertEqual(u'Editing English\u2026', 
                          self.editor_pg.working_language())
        self.editor_pg.exit_to_full_editor()
        self.assertEqual('Typing', self.sub_editor.dialog_title())




class TestCaseTaskEntry(WebdriverTestCase):

    """Entry and Exit points to New Editor. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseTaskEntry, cls).setUpClass()
        cls.create_modal = dialogs.CreateLanguageSelection(cls)
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)
        cls.unisubs_menu = unisubs_menu.UnisubsMenu(cls)
        cls.editor_pg = editor_page.EditorPage(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.tasks_tab = TasksTab(cls)
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create()
        cls.video_pg.open_page('auth/login/')
        cls.video_pg.log_in(cls.user.username, 'password')

        #Create a workflow enabled team to check review/approve dialog switching.
        cls.team = TeamMemberFactory.create(team__workflow_enabled=True,
                                            team__translate_policy=20, #any team
                                            team__subtitle_policy=20, #any team
                                            team__task_assign_policy=10, #any team
                                            user = cls.user,
                                            ).team
        cls.workflow = WorkflowFactory(team = cls.team,
                                       autocreate_subtitle=True,
                                       autocreate_translate=True,
                                       approve_allowed = 10, # manager
                                       review_allowed = 10, # peer
                                       )
        cls.user = UserFactory.create()



        cls.logger.info('creating video and adding to team')
        data = {'url': 'http://www.youtube.com/watch?v=WqJineyEszo',
                'video__primary_audio_language_code': 'en',
                'video__title': ('X Factor Audition'),
                'type': 'Y'
               }
        cls.video = cls.data_utils.create_video(**data)
        for x in range(3):
            cls.data_utils.add_subs(video=cls.video)
        cls.member = TeamMemberFactory(team=cls.team).user

        #Add video to team and create some review / approve tasks
        
        tv = TeamVideoFactory(team=cls.team, added_by=cls.user, video=cls.video)
        langs = ('sv', 'de', 'fr', 'es', 'pt')
        for lang in langs:
            translate_task = TaskFactory.create(type = 20, 
                                               team = cls.team, 
                                               team_video = tv, 
                                               language = lang, 
                                               assignee = cls.member)

            translate_task.save()
            data = {
                    'language_code': lang,
                    'complete': False, 
                    'visibility': 'private'
                   }
  
            cls.data_utils.add_subs(video=cls.video, **data)
            task = translate_task.complete()
            cls.tasks_tab.open_tasks_tab(cls.team.slug)
            cls.tasks_tab.log_in(cls.member.username, 'password')

    def setUp(self):
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.handle_js_alert('accept')

    def test_review_to_new(self):
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone&lang=sv' % self.team.slug) 
        self.tasks_tab.perform_and_assign_task('Review Swedish Subtitles',
                                                self.video.title)
        self.sub_editor.open_in_beta_editor()
        self.assertEqual('English', self.editor_pg.selected_ref_language())
        self.assertEqual('Version 3', self.editor_pg.selected_ref_version())
        self.assertEqual(u'Editing Swedish\u2026', 
                          self.editor_pg.working_language())
        self.editor_pg.exit()


    def test_review_to_new_approve(self):
        """Start Review task, switch to new editor and endorse 

        """

        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone&lang=es' % self.team.slug) 
        self.tasks_tab.perform_and_assign_task('Review Spanish Subtitles',
                                                self.video.title)
        self.sub_editor.open_in_beta_editor()
        self.assertEqual(u'Editing Spanish\u2026', 
                          self.editor_pg.working_language())
        self.editor_pg.approve_task()
        self.assertEqual(self.video.title, 
                         self.video_pg.video_title())
        self.assertEqual(1, len(list(self.video.teamvideo.task_set.all_approve().filter(language='es'))))


    def test_edit_approve_version(self):
        """Edit then and approve review task save new version.

        """
        self.tasks_tab.open_page('teams/%s/tasks/?assignee=anyone&lang=de' % self.team.slug) 
        self.tasks_tab.perform_and_assign_task('Review German Subtitles',
                                                self.video.title)
        self.sub_editor.open_in_beta_editor()
        self.assertEqual(u'Editing German\u2026', 
                          self.editor_pg.working_language())
        self.editor_pg.edit_sub_line('12345 chars', 1)
        self.editor_pg.save('Resume editing')
        self.editor_pg.approve_task()
        de_tag, _ = self.video_pg.language_status('German')
        self.assertEqual('needs approval', de_tag) 
        de = self.video.subtitle_language('de').get_tip(full=True)
        self.assertEqual(3, de.version_number)
        

    def test_save_back_to_old(self):
        """Open in new editor, then save and go back to old editor.

        """
        self.editor_pg.open_editor_page(self.video.video_id, 'fr')
        self.editor_pg.edit_sub_line('12345 chars', 1)
        self.editor_pg.save('Back to full editor')
        self.assertEqual('Typing', self.sub_editor.dialog_title())

    def test_save_resume(self):
        """Open in new editor, then save and resume editing.

        """
        self.editor_pg.open_editor_page(self.video.video_id, 'fr')
        self.editor_pg.edit_sub_line('12345 chars', 1)
        self.editor_pg.save('Resume editing')
        self.assertEqual(self.video.title,
                         self.editor_pg.video_title())
        self.editor_pg.exit()

    def test_save_exit(self):
        self.editor_pg.open_editor_page(self.video.video_id, 'pt')
        self.editor_pg.edit_sub_line('12345 chars', 1)
        self.editor_pg.save('Exit')
        self.assertEqual(self.video.title, 
                         self.video_pg.video_title())
