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
        self.skipTest('needs https://unisubs.sifterapp.com/issues/2162 resolved')
        self.logger.info('Create a video with an approved "en" transcript')
        video, tv = self._create_video_with_approved_transcript()
        self._unpublish_source_with_delete(video)
        self.logger.info('Check that new translations can not be started.')
        self.tasks_tab.log_in(self.user.username, 'password')
        self.tasks_tab.open_page('teams/{0}/tasks/?team_video={1}'
                                 '&assignee=anyone&lang=sv'.format(
                                 self.team.slug, tv.pk))
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
        self.tasks_tab.open_page('teams/{0}/tasks/?team_video={1}'
                                 '&assignee=anyone&lang=sv'.format(
                                 self.team.slug, tv.pk))

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
                                 '&assignee=anyone&lang=sv'.format(
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

class TestCaseEditSubtitlesButton(WebdriverTestCase):
    """Edit Subtitles button display on a revision after latest version set private. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseEditSubtitlesButton, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.video_pg = video_page.VideoPage(cls)

        cls.user = UserFactory.create()
        cls.owner = UserFactory.create()
        cls.team = TeamMemberFactory.create(team__workflow_enabled=True,
                                            team__translate_policy=20, #any team
                                            team__subtitle_policy=20, #any team
                                            team__task_assign_policy=10, #any team
                                            user = cls.owner,
                                            ).team
        cls.workflow = WorkflowFactory(team = cls.team,
                                       autocreate_subtitle=True,
                                       autocreate_translate=True,
                                       approve_allowed = 10, # manager
                                       review_allowed = 10, # peer
                                       )
        lang_list = ['en', 'ru', 'pt-br', 'de', 'sv']
        for language in lang_list:
            TeamLangPrefFactory.create(team=cls.team, language_code=language,
                                       preferred=True)

        cls.admin = TeamAdminMemberFactory(team=cls.team).user
        cls.contributor = TeamMemberFactory(team=cls.team).user
        cls.subs_dir = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                    'subtitle_data') 
        cls.video, cls.tv = cls._create_source_with_multiple_revisions()


    def tearDown(self):
        self.browser.get_screenshot_as_file('MYTMP/%s.png' % self.id())
        if self.team.task_assign_policy > 10: #reset to default start value
            self.team.task_assign_policy = 10
            self.team.save()

    @classmethod
    def _upload_en_draft(cls, video, subs, user, complete=False):
        auth_creds = dict(username=user.username, password='password')
        draft_data = {'language_code': 'en',
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
                     'draft': open(subs),
                     'complete': int(complete),
                     'is_complete': complete,
                    }
        cls.data_utils.upload_subs(video, draft_data, user=auth_creds)

    @classmethod
    def _add_team_video(cls):
        video = cls.data_utils.create_video()
        tv = TeamVideoFactory(team=cls.team, added_by=cls.owner, video=video)
        return video, tv

    @classmethod
    def _create_source_with_multiple_revisions(cls):
        cls.logger.info("Create a team video with 4 revisions:")
        cls.logger.info("""
                            v1: private (draft version only)
                            v2: private (draft version only)
                            v3: public 
                            v4: public 
                        """)
        video, tv = cls._add_team_video()

        #REV1 (draft)
        rev1_subs = os.path.join(cls.subs_dir, 'Timed_text.en.srt')
        cls._upload_en_draft(video, rev1_subs, user=cls.contributor)

        #REV2 (draft)
        rev2_subs = os.path.join(cls.subs_dir, 'Timed_text.rev2.en.srt')
        cls._upload_en_draft(video, rev2_subs, user=cls.contributor, complete=True)

        #REV3, reviewed and approved (public)
        rev3_subs = os.path.join(cls.subs_dir, 'Timed_text.rev3.en.srt')
        cls._upload_en_draft(video, rev3_subs, user=cls.admin, complete=True)
        cls.data_utils.complete_review_task(tv, 20, cls.admin)

        #REV4, reviewed and approved (public)
        rev4_subs = os.path.join(cls.subs_dir, 'Timed_text.rev4.en.srt')
        cls._upload_en_draft(video, rev4_subs, user=cls.owner, complete=True)
        cls.data_utils.complete_approve_task(tv, 20, cls.owner)
        cls.en = video.subtitle_language('en')
        en_v4 = cls.en.get_tip(full=True)
        en_v4.visibility_override = 'private'
        en_v4.save() 
        cls.video_lang_pg.open_video_lang_page(video.video_id, 'en')

        return video, tv


    def test_unpublished__member_with_create_tasks(self):
        self.logger.info(self.en.get_tip(full=True).visibility_override)
        """Unpublished version has Edit Subtitles active for member with permission.

        """
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertEqual('active', self.video_lang_pg.edit_subtitles_active())

    def test_unpublished__admin(self):
        """Admin can always edit unpublished version.

        """
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertEqual('active',
                         self.video_lang_pg.edit_subtitles_active())

    def test_unpublished__owner(self):
        """Owner can always edit unpublished version.

        """
        self.video_lang_pg.log_in(self.owner.username, 'password')
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertEqual('active',
                         self.video_lang_pg.edit_subtitles_active())

    def test_unpublished__member_with_no_create_tasks(self):
        """Member can't edit unpublished version when create tasks is manager level.

        """
        self.team.task_assign_policy = 30
        self.team.save()
        member2 = TeamContributorMemberFactory(team=self.team).user
        self.video_lang_pg.log_in(member2.username, 'password')
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertEqual(self.video_lang_pg.EDIT_INACTIVE_TEXT,
                         self.video_lang_pg.edit_subtitles_active())

    def test_unpublished__guest_sees_no_button(self):
        """Guest sees no Edit Subtitles button after version unpublished.

        """
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertFalse(self.video_lang_pg.edit_subtitles_exists())

    def test_unpublished__non_member_sees_no_button(self):
        """Edit Subtitles not visible for non-member.
        """
        siteuser = UserFactory.create()
        self.video_lang_pg.log_in(siteuser.username, 'password')
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')
        self.assertFalse(self.video_lang_pg.edit_subtitles_exists())

