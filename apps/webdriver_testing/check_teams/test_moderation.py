# -*- coding: utf-8 -*-
import os

from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.data_factories import TeamMemberFactory
from webdriver_testing.data_factories import TeamVideoFactory
from webdriver_testing.data_factories import WorkflowFactory
from webdriver_testing.data_factories import UserFactory
from webdriver_testing import data_helpers
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing.pages.site_pages import video_language_page
from webdriver_testing.pages.editor_pages import dialogs


class TestCasePublishedVideos(WebdriverTestCase):    
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCasePublishedVideos, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.create_modal = dialogs.CreateLanguageSelection(cls)
        cls.user = UserFactory(username = 'user', is_partner=True)
        
        #Add a team with workflows, tasks and preferred languages
        cls.logger.info('setup: Create a team with tasks enabled')
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
        cls.member = TeamMemberFactory.create(role="ROLE_CONTRIBUTOR",
                team = cls.team,
                user = UserFactory(username='member')
                ).user
        cls.nonmember = UserFactory()

        #Add video to team with published subtitles
        cls.logger.info('Setup: Add video to team with published subs.')
        vid = cls.data_utils.create_video()
        cls.data_utils.add_subs(video=vid)
        cls.published = TeamVideoFactory.create(
                team=cls.team, 
                video=vid,
                added_by=cls.user).video

        cls.video_pg.open_video_page(cls.published.video_id)
        cls.video_pg.set_skiphowto()


    def setUp(self):
        if self.team.subtitle_policy != 20:
            self.team.subtitle_policy=20
            self.team.save()
        if self.team.translate_policy != 20:
            self.team.translate_policy=20
            self.team.save()

    def test_video_add_subtitles(self):
        """No Add Subtitles option in the video view for moderated videos"""

        self.video_pg.open_video_page(self.published.video_id)
        self.assertFalse(self.video_pg.displays_add_subtitles())

    def test_video_upload_subtitles(self):
        """No Upload Subtitles option in the video view for moderated videos"""

        self.video_pg.open_video_page(self.published.video_id)
        self.assertFalse(self.video_pg.displays_upload_subtitles())

    def test_video_add_translation(self):
        """No Add Translation in the video view for moderated videos"""
        self.video_pg.open_video_page(self.published.video_id)
        self.assertFalse(self.video_pg.displays_add_subtitles())

    def test_published_guest_display(self):
        """Published version is visible to guests in subtitle view"""
        self.video_pg.open_video_page(self.published.video_id)
        self.video_lang_pg.open_video_lang_page(self.published.video_id, 'en')
        self.assertTrue(self.video_lang_pg.displays_subtitles())

    def test_published_nonmember_display(self):
        """Published version is visible to non-members in subtitle view"""
        self.video_pg.open_video_page(self.published.video_id)
        self.video_pg.log_in(self.nonmember.username, 'password')
        self.video_lang_pg.open_video_lang_page(self.published.video_id, 'en')
        self.assertTrue(self.video_lang_pg.displays_subtitles())


class TestCaseDraftVideos(WebdriverTestCase):    
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseDraftVideos, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.create_modal = dialogs.CreateLanguageSelection(cls)
        cls.user = UserFactory(username = 'user', is_partner=True)
        #Add a team with workflows, tasks and preferred languages
        cls.logger.info('setup: Create a team with tasks enabled')
        cls.team = TeamMemberFactory.create(team__workflow_enabled=True,
                                            team__subtitle_policy=20,
                                            team__translate_policy=20,
                                            user = cls.user,
                                            ).team
        cls.team_workflow = WorkflowFactory(team = cls.team,
                                            autocreate_subtitle=True,
                                            autocreate_translate=True,
                                            approve_allowed = 10,
                                            review_allowed = 10,
                                           )
        cls.member = TeamMemberFactory.create(role="ROLE_CONTRIBUTOR",
                team = cls.team,
                user = UserFactory(username='member')
                ).user
        cls.nonmember = UserFactory()

        #Add video to team with draft subtitles
        cls.logger.info('Setup: Add video to team with draft subs.')
        cls.draft = TeamVideoFactory.create(
                team=cls.team, 
                video=cls.data_utils.create_video(),
                added_by=cls.user).video
        data = { 'visibility': 'private', 
                 'video': cls.draft,
                 'committer': cls.user }
        cls.data_utils.add_subs(**data)
        cls.video_pg.open_video_page(cls.draft.video_id)

    def setUp(self):
        self.team.translate_policy=20
        self.team.save()
        self.video_pg.open_video_page(self.draft.video_id)

    def test_video_add_subtitles(self):
        """No Add Subtitles option in the video view for moderated videos"""

        self.assertFalse(self.video_pg.displays_add_subtitles())

    def test_video_upload_subtitles(self):
        """No Upload Subtitles option in the video view for moderated videos"""

        self.assertFalse(self.video_pg.displays_upload_subtitles())

    def test_draft_guest_display(self):
        """Draft is not visible to guests in subtitle view."""
        self.video_lang_pg.open_video_lang_page(self.draft.video_id, 'en')
        self.assertIn('waiting to be moderated', self.video_lang_pg.displays_subtitles())

    def test_draft_nonmember_display(self):
        """Draft is not visible to non-members in subtitle view."""
        self.video_pg.log_in(self.nonmember.username, 'password')
        self.video_lang_pg.open_video_lang_page(self.draft.video_id, 'en')
        self.assertIn('waiting to be moderated', self.video_lang_pg.displays_subtitles())

    def test_draft_member_display(self):
        """Draft is visible to members in subtitle view."""
        self.video_pg.log_in(self.member.username, 'password')
        self.video_lang_pg.open_video_lang_page(self.draft.video_id, 'en')
        self.assertTrue(self.video_lang_pg.displays_subtitles())

class TestCaseViewSubtitles(WebdriverTestCase):    
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseViewSubtitles, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_pg = video_page.VideoPage(cls)
        cls.user = UserFactory.create()
        cls.owner = UserFactory.create()
        cls.basic_team = TeamMemberFactory.create(team__workflow_enabled=False,
                                            team__translate_policy=20, #any team
                                            team__subtitle_policy=20, #any team
                                            user = cls.owner,
                                            ).team

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
        cls.contributor = TeamMemberFactory(team=cls.team, role="ROLE_CONTRIBUTOR").user
        cls.subs_dir = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                    'subtitle_data') 
        cls.rev1 = os.path.join(cls.subs_dir, 'Timed_text.en.srt')
        cls.rev2 = os.path.join(cls.subs_dir, 'Timed_text.rev2.en.srt')
        de = os.path.join(cls.subs_dir, 'Timed_text.rev3.en.srt')

        cls.sv = os.path.join(cls.subs_dir, 'Timed_text.sv.dfxp')

        #Create en source language 2 revisions - approved.
        cls.video, cls.tv = cls._add_team_video()
        cls._upload_subtitles(cls.video, 'en', cls.rev1, cls.contributor, 
                              complete=False)
        cls._upload_subtitles(cls.video, 'en', cls.rev2, cls.contributor)
        cls.data_utils.complete_review_task(cls.tv, 20, cls.owner)
        cls.data_utils.complete_approve_task(cls.tv, 20, cls.owner)
       
        #Add sv translation, reviewed
        cls._upload_translation(cls.video, 'sv', cls.sv, cls.contributor)
        cls.data_utils.complete_review_task(cls.tv, 20, cls.owner)

        #Add de translation complete waiting review
        cls._upload_translation(cls.video, 'de', cls.sv, cls.contributor)

        #Add ru translation, incomplete.
        cls._upload_translation(cls.video, 'ru', cls.sv, cls.contributor, 
                                complete=False)

    @classmethod
    def _upload_subtitles(cls, video, lc, subs, user, complete=True):
        data = {'language_code': lc,
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
                     'draft': open(subs),
                     'complete': int(complete),
                     'is_complete': complete,
                    }
        cls.data_utils.upload_subs(user, **data)

    @classmethod
    def _upload_translation(cls, video, lc, subs, user, complete=True):
        data = {'language_code': lc,
                     'video': video.pk,
                     'from_language_code': 'en',
                     'draft': open(subs),
                     'complete': int(complete),
                     'is_complete': complete,
                    }
        cls.data_utils.upload_subs(user, **data)

    @classmethod
    def _add_team_video(cls):
        video = cls.data_utils.create_video()
        tv = TeamVideoFactory(team=cls.team, added_by=cls.owner, video=video)
        return video, tv

    def setUp(self):
        self.video_pg.open_video_page(self.video.video_id)


    def test_status_img_original_complete(self):
        """Orignal lang complete, shows complete status button.

        """
        _, en_status = self.video_pg.language_status('English')
        self.assertIn('status-complete', en_status)

    def test_tags_original(self):
        """Orignal lang has original tag.

        """
        en_tag, _ = self.video_pg.language_status('English')
        self.assertEqual('original', en_tag)

    def test_tags_needs_approval(self):
        """Language awaiting approval, shows needs approval tag.

        """
        sv_tag, _ = self.video_pg.language_status('Swedish')
        self.assertEqual('needs approval', sv_tag)

    def test_tags_needs_review(self):
        """Language awaiting review, shows needs review tag.

        """
        de_tag, _ = self.video_pg.language_status('German')
        self.assertEqual('needs review', de_tag)

    def test_tags_incomplete(self):
        """Incomplete language, shows incomplete tag.

        """
        ru_tag, _ = self.video_pg.language_status('Russian')
        self.assertEqual('incomplete', ru_tag)

    def test_status_img_translation_review(self):
        """Translation lang complete, shows needs review status button.

        """
        _, sv_status = self.video_pg.language_status('Swedish')
        self.assertIn('status-needs-review', sv_status)


    def test_status_img_incomplete(self):
        """Incomplete translation displays incomplete status button.

        """
        _, ru_status = self.video_pg.language_status('Russian')
        self.assertIn('status-incomplete', ru_status)

    def test_tags_original_review(self):
        """Tag display for original language needs review."""

        vid, tv = self._add_team_video()
        self._upload_subtitles(vid, 'en', self.rev1, self.contributor, 
                              complete=True)
        self.video_pg.open_video_page(vid.video_id)
        en_tag, _ = self.video_pg.language_status('English')
        self.assertEqual('original | needs review', en_tag)

    def test_tags_original_approve(self):
        """Tag display for original language needs approval."""
        vid, tv = self._add_team_video()
        self._upload_subtitles(vid, 'en', self.rev1, self.contributor, 
                              complete=True)
        self.data_utils.complete_review_task(tv, 20, self.owner)

        self.video_pg.open_video_page(vid.video_id)
        en_tag, _ = self.video_pg.language_status('English')
        self.assertEqual('original | needs approval', en_tag)

    def test_tags_original_incomplete(self):
        vid, tv = self._add_team_video()
        self._upload_subtitles(vid, 'en', self.rev1, self.contributor, 
                              complete=False)
        self.video_pg.open_video_page(vid.video_id)
        en_tag, _ = self.video_pg.language_status('English')
        self.assertEqual('original | incomplete', en_tag)
