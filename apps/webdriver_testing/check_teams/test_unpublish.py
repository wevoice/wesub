import os
import time

from django.core import management

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages import video_page
from apps.webdriver_testing.pages.site_pages import video_language_page
from apps.webdriver_testing.pages.site_pages import watch_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import VideoUrlFactory
from apps.webdriver_testing.pages.editor_pages import subtitle_editor
from apps.webdriver_testing.pages.editor_pages import unisubs_menu 
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamAdminMemberFactory
from apps.webdriver_testing.data_factories import TeamContributorMemberFactory
from apps.webdriver_testing.data_factories import WorkflowFactory
from apps.webdriver_testing.data_factories import TeamLangPrefFactory
from apps.webdriver_testing.data_factories import UserLangFactory
from apps.webdriver_testing.pages.site_pages.teams.tasks_tab import TasksTab
from apps.webdriver_testing.pages.site_pages.teams.videos_tab import VideosTab
from apps.webdriver_testing.pages.editor_pages import dialogs

class TestCaseDelete(WebdriverTestCase):
    """TestSuite for Unapprove / Delete last version of language.  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseDelete, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.watch_pg = watch_page.WatchPage(cls)
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)
        cls.menu = unisubs_menu.UnisubsMenu(cls)
        cls.user = UserFactory.create()
        cls.tasks_tab = TasksTab(cls)

        cls.team = TeamMemberFactory.create(team__workflow_enabled=True,
                                            team__translate_policy=20,
                                            team__subtitle_policy=20,
                                            user = cls.user,
                                            ).team
        cls.team_workflow = WorkflowFactory(team = cls.team,
                                            autocreate_subtitle=True,
                                            autocreate_translate=True,
                                            approve_allowed = 10,
                                            review_allowed = 10,
                                           )
        lang_list = ['en', 'ru', 'pt-br', 'de', 'sv']
        for language in lang_list:
            TeamLangPrefFactory.create(
                team = cls.team,
                language_code = language,
                preferred = True)
        cls.team_admin = TeamAdminMemberFactory(team=cls.team).user
        cls.team_member = TeamMemberFactory(team=cls.team).user

        cls.video_pg = video_page.VideoPage(cls)
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)
        cls.create_modal = dialogs.CreateLanguageSelection(cls)


        user_langs = ['en', 'ru', 'sv']
        for lang in user_langs:
            UserLangFactory(user=cls.team_member, language=lang)
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')
        cls.member_creds = dict(username=cls.team_member.username, 
                          password='password')
        cls.admin_creds = dict(username=cls.team_admin.username, 
                          password='password')

        
    def setUp(self):
        self.video_pg.open_page('videos/create')
        self.video_pg.handle_js_alert('accept')

    def _create_video_with_approved_transcript(self):
        sub_file = os.path.join(self.subs_data_dir, 'Timed_text.en.srt')
        video = VideoUrlFactory().video
        tv = TeamVideoFactory.create(
            team=self.team, 
            video=video, 
            added_by=self.user)
        orig_data = {'language_code': 'en',
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
                     'draft': open(sub_file),
                     'is_complete': True,
                     'complete': 1,
                    }
        self.data_utils.upload_subs(video, orig_data, self.member_creds)
        self.data_utils.complete_review_task(tv, 20, self.team_admin)
        self.data_utils.complete_approve_task(tv, 20, self.team_admin)
        return video, tv

    def _upload_sv_translation(self, video, complete=False):
        data = {'language_code': 'sv',
                'video': video.pk,
                'from_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.sv.dfxp')}
        if complete:
            data['complete'] = 1
            data['is_complete'] = True
        self.data_utils.upload_subs(video, data=data, user=self.member_creds)

    def _unpublish_source_with_delete(self, video, rev=None):
        self.video_pg.open_video_page(video.video_id)
        self.video_language_pg.log_in(self.user.username, 'password')
        if rev:
            self.video_language_pg.open_lang_revision_page(video.video_id, 
                                                           'en', rev)
        else:
            self.video_language_pg.open_video_lang_page(video.video_id, 'en')
        self.video_language_pg.unpublish(delete=True)
        self.logger.info("After unpublish EN full() Revision")
        self.logger.info(video.subtitle_language('en').get_tip(full=True))
        self.logger.info("After unpublish EN public() Revision")
        self.logger.info(video.subtitle_language('en').get_tip(public=True)) 

    def test_delete_last_source__forks_translations(self):
        """Deleting last source forks in-progress translations.

        """
        video, tv = self._create_video_with_approved_transcript() 
        self.logger.info("Original EN Revision")
        self.logger.info(video.subtitle_language('en').get_tip(full=True)) 
        self._upload_sv_translation(video, complete=True)
        self._unpublish_source_with_delete(video)

        sl_sv = video.subtitle_language('sv')
        self.logger.info('SV IS_FORKED %s' % sl_sv.is_forked)
        self.assertTrue(sl_sv.is_forked)


    def test_delete_last_source__blocks_unstarted(self):
        """Deleting the last source blocks translation tasks.

        Ref: https://unisubs.sifterapp.com/issues/2005
        Ref: https://unisubs.sifterapp.com/issues/2162

        """
        self.logger.info('Create a video with an approved "en" transcript')
        video, tv = self._create_video_with_approved_transcript()
        self._unpublish_source_with_delete(video)
        self.logger.info('Check that new translations can not be started.')
        self.tasks_tab.log_in(self.user.username, 'password')

        self.tasks_tab.open_page('teams/%s/tasks/?lang=sv&assignee=anyone'
                                 % self.team.slug)
        task_text = 'Translate Subtitles into Swedish'
        self.tasks_tab.perform_and_assign_task(task_text, video.title)
        self.create_modal.lang_selection()
        if 'Typing' in self.sub_editor.dialog_title():
            self.assertFalse('these translations should not be forked')
        else:
            self.assertFalse('update test case with correct assertion')


    def test_delete_last_source__upload_version(self):
        """Upload source version after deleting last rev with dep translations.

        REF: https://unisubs.sifterapp.com/issues/2180
        """
        video, tv = self._create_video_with_approved_transcript() 
        en = video.subtitle_language('en')
        self._upload_sv_translation(video)
        self._unpublish_source_with_delete(video)

        sub_file = os.path.join(self.subs_data_dir, 'srt-full.srt')
        rev2_data = {'language_code': 'en',
                     'video': video.pk,
                     'draft': open(sub_file),
                     'is_complete': True,
                     'complete': 1,
                    }
        self.data_utils.upload_subs(video, rev2_data, self.member_creds)
        self.logger.info(en.get_tip(full=True).visibility)
        self.assertEqual(2, en.get_tip(full=True).version_number)



    def test_delete_last_source__language_ui(self):
        """Deleted last source language not displayed in video page list.


        """
        video, tv = self._create_video_with_approved_transcript() 
        en = video.subtitle_language('en')
        self._upload_sv_translation(video)
        self._unpublish_source_with_delete(video)
        self.video_pg.open_video_page(video.video_id)
        available_langs = self.video_pg.subtitle_languages()
        self.logger.info(available_langs)
        self.assertNotIn('English', available_langs)



    def test_delete_last_source__edit_forked_translation(self):
        """In-progress translations editable after last source deleted.

        """
        video, tv = self._create_video_with_approved_transcript() 
        en = video.subtitle_language('en')
        self._upload_sv_translation(video)
        self._unpublish_source_with_delete(video)
        self.tasks_tab.log_in(self.team_member.username, 'password')
        self.tasks_tab.open_page('teams/%s/tasks/?lang=sv&assignee=anyone'
                                 % self.team.slug)
        task_text = 'Translate Subtitles into Swedish'
        self.tasks_tab.perform_assigned_task(task_text, video.title)
        self.create_modal.lang_selection()
        self.assertEqual('Typing', self.sub_editor.dialog_title())


    def _upload_en_draft(self, video, subs, complete=False):
        draft_data = {'language_code': 'en',
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
                     'draft': open(subs)
                    }
        if complete:
            draft_data['complete'] = 1
            draft_data['is_complete'] = True
        self.logger.info(draft_data)
        self.data_utils.upload_subs(video, draft_data, user=self.member_creds)
        en = video.subtitle_language('en').get_tip(full=True)
        self.logger.info('EN revision: %s' % en)
        self.logger.info('EN visibility: %s' % en.visibility)

    def _create_source_with_multiple_revisions(self):
        self.logger.info("Create a team video that has this revision structure:")
        self.logger.info("""
                            v1: private (draft version only)
                            v2: private (draft version only)
                            v3: public 
                            v4: public 
                        """)
        video = VideoUrlFactory().video
        tv = TeamVideoFactory.create(
            team=self.team, 
            video=video, 
            added_by=self.user)
        #REV1
        rev1_subs = os.path.join(self.subs_data_dir, 'Timed_text.en.srt')
        self._upload_en_draft(video, rev1_subs)

        #REV2
        rev2_subs = os.path.join(self.subs_data_dir, 'Timed_text.rev2.en.srt')
        self._upload_en_draft(video, rev2_subs)

        #REV3
        rev3_subs = os.path.join(self.subs_data_dir, 'Timed_text.rev3.en.srt')
        self._upload_en_draft(video, rev3_subs, complete=True)
        #Rev 3 Review and Approve
        self.data_utils.complete_review_task(tv, 20, self.team_admin)
        self.data_utils.complete_approve_task(tv, 20, self.team_admin)
        self.logger.info("POST APPROVE REV3")
        self.logger.info(video.subtitle_language('en').get_tip(full=True)) 

        #REV 4
        rev4_subs = os.path.join(self.subs_data_dir, 'Timed_text.rev4.en.srt')
        self._upload_en_draft(video, rev4_subs, complete=True)

        return video, tv

    def tearDown(self):
        self.browser.get_screenshot_as_file('MYTMP/%s.png' % self.id())

    def upload_translation(self, video, lang):
        data = {'language_code': lang,
                'video': video.pk,
                'from_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.sv.dfxp'),
           }
        self.data_utils.upload_subs(video, data=data, user=self.member_creds)

    def test_unpublish__updates_translation_source(self):
        """Unpublishing updates translation source to prior public rev.

        """
        video, tv = self._create_source_with_multiple_revisions()
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.upload_translation(video, 'sv')
        sv = video.subtitle_language('sv')
        self.logger.info(sv.get_translation_source_language().get_tip(public=True))
        self._unpublish_source_with_delete(video)
        self.logger.info(sv.get_translation_source_language().get_tip(public=True))
        self.tasks_tab.log_in(self.team_member.username, 'password')
        self.tasks_tab.open_page('teams/{0}/tasks/?team_video={1}'
                                 '&assignee=anyone'.format(
                                 self.team.slug, tv.pk))

        self.tasks_tab.perform_assigned_task('Translate Subtitles into Swedish',
                                               video.title)
        self.create_modal.lang_selection()
        self.assertEqual('This is revision 3', 
                         self.sub_editor.translation_source()[0])

    def test_private_revision_not_searchable(self):
        """Unpublished (deleted) revision text doesn't show in search results.

        """
        video, tv = self._create_source_with_multiple_revisions()
        self.watch_pg.log_out()
        self._unpublish_source_with_delete(video)
        management.call_command('update_index', interactive=False)

        self.watch_pg.open_watch_page()
        test_text = 'REVISION4'
        results_pg = self.watch_pg.basic_search(test_text)
        self.assertTrue(results_pg.search_has_no_results())

    def test_delete_all_public_creates_approve_task(self):
        """Unpublishing (delete) all public versions creates approve task'
        
        v1 - private, v2 - private, v3 - public, v4 - public
        Delete v3 and all later create approve task at v2
        Ref: https://unisubs.sifterapp.com/issues/2005


        """
        video, tv = self._create_source_with_multiple_revisions()
        en = video.subtitle_language('en')
        self.logger.info(en.pk)
        self.logger.info(en.version().pk)
        self.logger.info(en.version(version_number=3).pk)
        sl_sv = '{0}/{1}'.format(en.pk, en.version(version_number=3).pk)
        self._unpublish_source_with_delete(video, rev=sl_sv)
        self.tasks_tab.open_page('teams/{0}/tasks/?team_video={1}'
                                 '&assignee=anyone&lang=en'.format(
                                 self.team.slug, tv.pk))
        task_text = 'Approve Original English Subtitles'
        self.assertTrue(self.tasks_tab.task_present(task_text, video.title))
        self.logger.info(en.get_tip(full=True).version_number)
        self.tasks_tab.perform_and_assign_task(task_text, video.title)
        self.assertEqual('Approve subtitles', self.sub_editor.dialog_title())
        self.assertEqual('This is revision 2', 
                         self.sub_editor.subtitles_list()[0])




class TestCaseSendBack(WebdriverTestCase):    
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseSendBack, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.tasks_tab = TasksTab(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)
        cls.watch_pg = watch_page.WatchPage(cls)

        cls.videos_tab = VideosTab(cls)
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.menu = unisubs_menu.UnisubsMenu(cls)
        cls.create_modal = dialogs.CreateLanguageSelection(cls)
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)

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
        cls.contributor = TeamContributorMemberFactory.create(
                team = cls.team,
                ).user

        user_langs = ['en', 'ru', 'de', 'sv']
        for lang in user_langs:
            UserLangFactory(user=cls.contributor, language=lang)
        cls.subs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)
                                     ), 'oneline.txt')
        cls.member_creds = dict(username=cls.contributor.username, 
                                password='password')
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
                            'webdriver_testing', 'subtitle_data')



    def tearDown(self):
        self.browser.get_screenshot_as_file('MYTMP/%s.png' % self.id())

    def setUp(self):
        self.tasks_tab.open_team_page(self.team.slug)

    def _unpublish_source_with_sendback(self, video, rev=None):
        self.video_pg.open_video_page(video.video_id)
        self.video_pg.log_in(self.owner.username, 'password')
        if rev:
            self.video_language_pg.open_lang_revision_page(video.video_id, 
                                                           'en', rev)
        else:
            self.video_language_pg.open_video_lang_page(video.video_id, 'en')
        self.video_language_pg.unpublish()
        self.logger.info("After unpublish EN full() Revision")
        self.logger.info(video.subtitle_language('en').get_tip(full=True))
        self.logger.info("After unpublish EN public() Revision")
        self.logger.info(video.subtitle_language('en').get_tip(public=True)) 



    def _upload_en_draft(self, video, subs, complete=False):
        draft_data = {'language_code': 'en',
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
                     'draft': open(subs)
                    }
        if complete:
            draft_data['complete'] = 1
            draft_data['is_complete'] = True
        self.logger.info(draft_data)
        self.data_utils.upload_subs(video, draft_data, user=self.member_creds)
        en = video.subtitle_language('en').get_tip(full=True)
        self.logger.info('EN revision: %s' % en)
        self.logger.info('EN visibility: %s' % en.visibility)

    def _create_source_with_multiple_revisions(self):
        self.logger.info("Create a team video that has this revision structure:")
        self.logger.info("""
                            v1: private (draft version only)
                            v2: private (draft version only)
                            v3: public 
                            v4: public 
                        """)
        video = VideoUrlFactory().video
        tv = TeamVideoFactory.create(
            team=self.team, 
            video=video, 
            added_by=self.contributor)

        #REV1
        rev1_subs = os.path.join(self.subs_data_dir, 'Timed_text.en.srt')
        self._upload_en_draft(video, rev1_subs)

        #REV2
        rev2_subs = os.path.join(self.subs_data_dir, 'Timed_text.rev2.en.srt')
        self._upload_en_draft(video, rev2_subs)

        #REV3
        rev3_subs = os.path.join(self.subs_data_dir, 'Timed_text.rev3.en.srt')
        self._upload_en_draft(video, rev3_subs, complete=True)
        #Rev 3 Review and Approve
        self.data_utils.complete_review_task(tv, 20, self.owner)
        self.data_utils.complete_approve_task(tv, 20, self.owner)
        self.logger.info("POST APPROVE REV3")
        en = video.subtitle_language('en').get_tip(full=True)
        self.logger.info(en)
        self.logger.info('EN visibility: %s' % en.visibility)
        #REV 4
        rev4_subs = os.path.join(self.subs_data_dir, 'Timed_text.rev4.en.srt')
        self._upload_en_draft(video, rev4_subs, complete=True)
        self.data_utils.complete_review_task(tv, 20, self.owner)
        self.data_utils.complete_approve_task(tv, 20, self.owner)
        en = video.subtitle_language('en').get_tip(full=True)
        self.logger.info(en)
        self.logger.info('EN visibility: %s' % en.visibility)
        return video, tv



    def make_video_with_approved_transcript(self, subs='Timed_text.en.srt'):
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, 
                              video=video)
        rev1_subs = os.path.join(self.subs_data_dir, subs)
        self._upload_en_draft(video, rev1_subs, complete=True)
        self.data_utils.complete_review_task(tv, 20, self.owner)
        if self.workflow.approve_enabled:
            self.data_utils.complete_approve_task(tv, 20, self.owner)
        return video, tv

    def upload_translation(self, video, complete=False):
        data = {'language_code': 'sv',
                'video': video.pk,
                'from_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.sv.dfxp')
                }
        if complete:
            data['is_complete'] = True
            data['complete'] = 1
        self.data_utils.upload_subs(video, data=data, user=self.member_creds)

    def test_unpublish_locks_inprogress(self):
        """In-progress translation task locked when transcript is unpublished.

        This is the case where the current public version is unpproved and
        no previous published versions exist to take it's place.

        """
        self.logger.info('Create a video with an approved "en" transcript')
        video, tv = self.make_video_with_approved_transcript()
        self.upload_translation(video)
        self._unpublish_source_with_sendback(video)
        self.logger.info('Check that incomplete translation task is locked')
        self.tasks_tab.open_page('teams/{0}/tasks/?team_video={1}'
                                 '&assignee=anyone'.format(
                                 self.team.slug, tv.pk))
        task_text = 'Translate Subtitles into Swedish'
        disabled = self.tasks_tab.disabled_task(task_text, video.title) 
        self.assertEqual(disabled, 'Locked until subtitles have been approved.')
        self.logger.info('Check the perform task is not displayed')
        task = self.tasks_tab.task_present(task_text, video.title)
        self.assertEqual(task['perform'], None)

    def test_unpublish_blocks_unstarted(self):
        """Unstarted translation task blocked when transcript is unpublished.

        This is the case where the current public version is unpproved and
        no previous published versions exist to take it's place. When user tries
        to edit they get a dialog that they can't translate incomplete.
        Ref: https://unisubs.sifterapp.com/issues/2162

        """
        self.logger.info('Create a video with an approved "en" transcript')
        video, tv = self.make_video_with_approved_transcript()
        self._unpublish_source_with_sendback(video)
        self.logger.info('Check that new translations can not be started.')
        self.tasks_tab.log_in(self.owner.username, 'password')
        self.tasks_tab.open_page('teams/{0}/tasks/?team_video={1}'
                                 '&assignee=anyone'.format(
                                 self.team.slug, tv.pk))
        task_text = 'Translate Subtitles into German'
        self.logger.info("Video title: %s" % video.title)
        self.tasks_tab.perform_and_assign_task(task_text, video.title)
        self.create_modal.lang_selection()
        if 'Typing' in self.sub_editor.dialog_title():
            self.assertFalse('these translations should not be forked')
        else:
            self.assertFalse('update test case with correct assertion')

    def test_unpublish__creates_approve(self):
        """Unpublishing transcript creates an approve task.

        REF: https://unisubs.sifterapp.com/issues/2199
        """
        self.tasks_tab.log_in(self.owner, 'password')
        video, tv = self.make_video_with_approved_transcript()
        self._unpublish_source_with_sendback(video)
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.assertTrue(self.tasks_tab.task_present(
                'Approve Original English Subtitles', video.title))

    def test_draft_revision_not_searchable(self):
        """Unpublished (sendback) draft rev text not in search results.

        """
        self.logger.info('Create a video with an approved "en" transcript')
        video, _ = self.make_video_with_approved_transcript(
                    subs='srt-full.srt')
        self._unpublish_source_with_sendback(video)

        self.watch_pg.log_out()
        management.call_command('update_index', interactive=False)

        self.watch_pg.open_watch_page()
        test_text = 'Universal Subtitles'
        results_pg = self.watch_pg.basic_search(test_text)
        self.assertTrue(results_pg.search_has_no_results())

    def test_unpublish_all_public_creates_approve_task(self):
        """Unpublishing (send back) all public versions creates approve task'

        v1 - private, v2 - private, v3 - public, v4 - public
        Send back v3 and all later create approve task at v4
        Ref: https://unisubs.sifterapp.com/issues/2005


        """
        video, tv = self._create_source_with_multiple_revisions()
        en = video.subtitle_language('en')
        self.logger.info(en.pk)
        self.logger.info(en.version().pk)
        self.logger.info(en.version(version_number=3).pk)
        sl_sv = '{0}/{1}'.format(en.pk, en.version(version_number=3).pk)
        self._unpublish_source_with_sendback(video, rev=sl_sv)
        self.tasks_tab.open_page('teams/{0}/tasks/?team_video={1}'
                                 '&assignee=anyone&lang=en'.format(
                                 self.team.slug, tv.pk))

        task_text = 'Approve Original English Subtitles'
        self.assertTrue(self.tasks_tab.task_present(task_text, video.title))
        self.logger.info(en.get_tip(full=True).version_number)
        self.tasks_tab.perform_and_assign_task(task_text, video.title)
        self.assertEqual('Approve subtitles', self.sub_editor.dialog_title())
        self.assertEqual('REVISION4-REVISION4', 
                         self.sub_editor.subtitles_list()[0])


