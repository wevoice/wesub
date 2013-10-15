import os

from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing import data_helpers
from webdriver_testing.pages.site_pages import video_language_page
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing.pages.site_pages import diffing_page
from webdriver_testing.data_factories import TeamVideoFactory
from webdriver_testing.data_factories import TeamMemberFactory

from webdriver_testing.data_factories import TeamManagerLanguageFactory


from webdriver_testing.data_factories import WorkflowFactory
from webdriver_testing.data_factories import TeamLangPrefFactory
from webdriver_testing.data_factories import UserFactory


class TestCaseApprovalWorkflow(WebdriverTestCase):
    """TestSuite for display of Rollback button on a revision. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseApprovalWorkflow, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.diffing_pg = diffing_page.DiffingPage(cls)
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
        cls.admin = TeamMemberFactory(role="ROLE_ADMIN",team=cls.team).user
        cls.manager = TeamMemberFactory(role="ROLE_MANAGER",team=cls.team).user
        cls.contributor = TeamMemberFactory(team=cls.team, role="ROLE_CONTRIBUTOR").user
        cls.contributor2 = TeamMemberFactory(team=cls.team, role="ROLE_CONTRIBUTOR").user
        cls.subs_dir = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                    'subtitle_data') 

    @classmethod
    def _upload_en_draft(cls, video, subs, user, complete=False):
        data = {'language_code': 'en',
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
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
    
    @classmethod
    def _create_two_drafts(cls, video, user):
        rev1 = os.path.join(cls.subs_dir, 'Timed_text.en.srt')
        rev2 = os.path.join(cls.subs_dir, 'Timed_text.rev2.en.srt')

        cls._upload_en_draft(video, rev1, user)
        en = video.subtitle_language('en')
        en_v1 = en.get_tip()
        cls._upload_en_draft(video, rev2, user)
        en_v2 = en.get_tip()
        return en_v1, en_v2

    @classmethod
    def _create_complete_rev(cls, video, user):
        rev1 = os.path.join(cls.subs_dir, 'Timed_text.en.srt')
        rev2 = os.path.join(cls.subs_dir, 'Timed_text.rev2.en.srt')

        cls._upload_en_draft(video, rev1, user)
        en = video.subtitle_language('en')
        en_v1 = en.get_tip()
        cls._upload_en_draft(video, rev2, user, complete=True)
        en_v2 = en.get_tip()
        return en_v1, en_v2


    def test_rollback_draft__assignee(self):
        """Rollback available for task assignee.

        """
        video, tv = self._add_team_video()
        v1, _ = self._create_two_drafts(video, self.contributor)
        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists())

    def test_diffing_rollback_draft__assignee(self):
        """Rollback available for task assignee.

        """
        video, tv = self._add_team_video()
        v1, v2 = self._create_two_drafts(video, self.contributor)
        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.diffing_pg.open_diffing_page(v1.id, v2.id)
        self.assertTrue(self.diffing_pg.rollback_exists())

    def test_review_reject__assignee(self):
        """Rollback available for assignee after transcript fails review.

        """
        video, tv = self._add_team_video()
        v1, _ = self._create_complete_rev(video, self.contributor)

        #Reject transcript in review phase
        self.data_utils.complete_review_task(tv, 30, self.admin)
        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists())

    def test_diffing_rollback_review_reject__assignee(self):
        """Rollback on diffing page for assignee, if transcript fails review.

        """
        video, tv = self._add_team_video()
        v1, v2 = self._create_complete_rev(video, self.contributor)

        #Reject transcript in review phase
        self.data_utils.complete_review_task(tv, 30, self.admin)
        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.diffing_pg.open_diffing_page(v1.id, v2.id)
        self.assertTrue(self.diffing_pg.rollback_exists())


    def test_approve_reject__assignee(self):
        """Rollback NOT available for transcriber when approve fails.

        """
        video, tv = self._add_team_video()
        v1, _ = self._create_complete_rev(video, self.contributor)
        #Accept transcript in review phase
        self.data_utils.complete_review_task(tv, 20, self.admin)
        #Reject transcript in the approve phase
        self.data_utils.complete_approve_task(tv, 30, self.owner)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists())

    def test_review_unstarted__transcriber(self):
        """No Rollback for transcriber when waiting review.

        """
        video, tv = self._add_team_video()
        v1, _ = self._create_complete_rev(video, self.contributor)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists())

    def test_diffing_rollback_review_unstarted__transcriber(self):
        """No Rollback on diffing page for transcriber when waiting review.

        """
        video, tv = self._add_team_video()
        v1, v2 = self._create_complete_rev(video, self.contributor)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.diffing_pg.open_diffing_page(v1.id, v2.id)
        self.assertFalse(self.diffing_pg.rollback_exists())


    def test_approver_sent_back__reviewer(self):
        """Rollback active for reviewer after transcript fails approve.

        """
        reviewer = TeamMemberFactory(role="ROLE_CONTRIBUTOR",team=self.team).user
        video, tv = self._add_team_video()
        v1, _ = self._create_complete_rev(video, self.contributor)

        #Accept transcript in review phase
        self.data_utils.complete_review_task(tv, 20, reviewer)
        #Reject transcript in the approve phase
        self.data_utils.complete_approve_task(tv, 30, self.owner)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(reviewer.username, 'password')
        self.video_lang_pg.open_page(v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists())


    def test_draft__not_task_assignee(self):
        """Rollback not active for member not assigned with task.

        """
        member2 = TeamMemberFactory(role="ROLE_CONTRIBUTOR",team=self.team).user
        video, tv = self._add_team_video()
        v1, _ = self._create_two_drafts(video, self.contributor)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(member2.username, 'password')
        self.video_lang_pg.open_page(v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists())

    def test_diffing_page__not_task_assignee(self):
        """Rollback not active for member not assigned with task.

        """
        member2 = TeamMemberFactory(role="ROLE_CONTRIBUTOR",team=self.team).user
        video, tv = self._add_team_video()
        v1, v2 = self._create_two_drafts(video, self.contributor)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(member2.username, 'password')

        self.diffing_pg.open_diffing_page(v1.id, v2.id)
        self.assertFalse(self.diffing_pg.rollback_exists())


    def test_draft__team_admin(self):
        """Rollback not active for admin when task started by member.

        """
        video, tv = self._add_team_video()
        v1, _ = self._create_two_drafts(video, self.contributor)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.admin.username, 'password')

        self.video_lang_pg.open_page(v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists())


class TestCaseWorkflowPermissions(WebdriverTestCase):
    """TestSuite for display of Rollback button based on approval permissions. 

       gh-483 changed to used approval permission for post-edit permissions.
    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseWorkflowPermissions, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.diffing_pg = diffing_page.DiffingPage(cls)
        cls.user = UserFactory.create()
        cls.owner = UserFactory.create()
        cls.team = TeamMemberFactory.create(team__workflow_enabled=True,
                                            team__translate_policy=20, #any team
                                            team__subtitle_policy=20, #any team
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
        cls.admin = TeamMemberFactory(role="ROLE_ADMIN",team=cls.team).user
        cls.manager = TeamMemberFactory(role="ROLE_MANAGER",team=cls.team).user
        cls.contributor = TeamMemberFactory(team=cls.team, role="ROLE_CONTRIBUTOR").user
        cls.contributor2 = TeamMemberFactory(team=cls.team, role="ROLE_CONTRIBUTOR").user


        cls.site_user = UserFactory.create()
        cls.en_lc = TeamMemberFactory(role="ROLE_MANAGER",team=cls.team)
        TeamManagerLanguageFactory(member = cls.en_lc,
                                   language = 'en')
        cls.de_lc = TeamMemberFactory(role="ROLE_MANAGER",team=cls.team)
        TeamManagerLanguageFactory(member = cls.de_lc,
                                   language = 'de')
        cls.site_staff = TeamMemberFactory(team=cls.team, role="ROLE_CONTRIBUTOR").user
        cls.site_staff.is_staff = True
        cls.site_staff.save()


        cls.subs_dir = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                    'subtitle_data') 
        cls.video, cls.tv = cls._add_team_video()
        cls._create_complete_rev(cls.video, cls.contributor)
        cls._review_and_approve(cls.tv)
        en = cls.video.subtitle_language('en')
        en.clear_tip_cache()
        cls.v1 = en.version(public_only=False, version_number=1)        

    @classmethod
    def _upload_en_draft(cls, video, subs, user, complete=False):
        data = {'language_code': 'en',
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
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

    @classmethod
    def _review_and_approve(cls, tv):
        """Review and approve version.

        """
        if cls.workflow.review_enabled:
            cls.data_utils.complete_review_task(tv, 20, cls.owner)
        if cls.workflow.approve_enabled:
            cls.data_utils.complete_approve_task(tv, 20, cls.owner)

    @classmethod
    def _create_complete_rev(cls, video, user):
        rev1 = os.path.join(cls.subs_dir, 'Timed_text.en.srt')
        rev2 = os.path.join(cls.subs_dir, 'Timed_text.rev2.en.srt')

        cls._upload_en_draft(video, rev1, user)
        en = video.subtitle_language('en')
        en_v1 = en.get_tip()
        cls._upload_en_draft(video, rev2, user, complete=True)
        en_v2 = en.get_tip()
        return en_v1, en_v2


    def test_public_admin_approve(self):
        """Rollback available to admin and above when Admin must approve.

        """

        self.workflow.approve_allowed = 20 # admin
        self.workflow.review_allowed = 10 # peer
        self.workflow.save()
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')

        #site staff
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'site staff rollback check failed')

        #team admin
        self.video.clear_language_cache()
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin rollback check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team manager rollback check failed')

        #en lang coordinator
        self.video_lang_pg.log_in(self.en_lc.user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'lc same lang rollback check failed')


        #team member
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member rollback check failed')


        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user rollback check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user rollback check failed')

    def test_public_manager_approve(self):
        """Rollback available to manager and above when Manager must approve.
        """

        self.workflow.approve_allowed = 10 # manager
        self.workflow.review_allowed = 10 # peer
        self.workflow.save()
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')

        #site staff
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'site staff rollback check failed')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin rollback check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team manager rollback check failed')

        #en lang coordinator
        self.video_lang_pg.log_in(self.en_lc.user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'lc same lang rollback check failed')


        #de lang coordinator
        self.video_lang_pg.log_in(self.de_lc.user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'lc same diff lang rollback check failed')

        #team member
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member rollback check failed')


        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user rollback check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user rollback check failed')

    def test_public_admin_review(self):
        """Rollback for admin and above when Admin must review (no approve).
        """

        self.workflow.approve_allowed = 00 # not required
        self.workflow.review_allowed = 30 # admin
        self.workflow.save()
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')

        #site staff
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'site staff rollback check failed')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin rollback check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team manager rollback check failed')

        #en lang coordinator
        self.video_lang_pg.log_in(self.en_lc.user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'lc same lang rollback check failed')


        #de lang coordinator
        self.video_lang_pg.log_in(self.de_lc.user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'lc same diff lang rollback check failed')

        #team member
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member rollback check failed')


        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user rollback check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user rollback check failed')

    def test_public_manager_review(self):
        """Rollback for mnager and above when Manager must review (no approve).
        """

        self.workflow.approve_allowed = 00 # not required
        self.workflow.review_allowed = 20 # manager
        self.workflow.save()
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')

        #site staff
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'site staff rollback check failed')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin rollback check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team manager rollback check failed')

        #en lang coordinator
        self.video_lang_pg.log_in(self.en_lc.user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'lc same lang rollback check failed')


        #de lang coordinator
        self.video_lang_pg.log_in(self.de_lc.user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'lc same diff lang rollback check failed')

        #team member 
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member rollback check failed')


        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user rollback check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user rollback check failed')


    def test_public_peer_review(self):
        """Rollback for peer and above when Peer must review (no approve).
        """

        self.workflow.approve_allowed = 0 # not required
        self.workflow.review_allowed = 10 # peer
        self.workflow.save()
        self.logger.info(self.workflow.review_allowed)
        self.video_lang_pg.open_video_lang_page(self.video.video_id, 'en')

        #site staff
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'site staff rollback check failed')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin rollback check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team manager rollback check failed')
        #team member peer
        self.video_lang_pg.log_in(self.contributor2.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team peer rollback check failed')
      
        #team member draft author
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team draft author rollback check failed')

        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user rollback check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user rollback check failed')


class TestCaseNoReviews(WebdriverTestCase):
    """TestSuite for Rollback of No-Review / Approve team. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseNoReviews, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.video_pg = video_page.VideoPage(cls)

        cls.user = UserFactory.create()
        cls.owner = UserFactory.create()
        cls.team = TeamMemberFactory.create(team__workflow_enabled=True,
                                            team__translate_policy=20, #any team
                                            team__subtitle_policy=20, #any team
                                            user = cls.owner,
                                            ).team
        cls.workflow = WorkflowFactory(team = cls.team,
                                       autocreate_subtitle=True,
                                       autocreate_translate=True,
                                       approve_allowed = 00, # none
                                       review_allowed = 00, # none
                                       )
        lang_list = ['en', 'ru', 'pt-br', 'de', 'sv']
        for language in lang_list:
            TeamLangPrefFactory.create(team=cls.team, language_code=language,
                                       preferred=True)
        
        cls.admin = TeamMemberFactory(role="ROLE_ADMIN",team=cls.team).user
        cls.manager = TeamMemberFactory(role="ROLE_MANAGER",team=cls.team).user
        cls.contributor = TeamMemberFactory(team=cls.team, role="ROLE_CONTRIBUTOR").user
        cls.contributor2 = TeamMemberFactory(team=cls.team, role="ROLE_CONTRIBUTOR").user

        cls.subs_dir = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                    'subtitle_data')
        cls.site_user = UserFactory.create()

        cls.draft_video, cls.draft_tv = cls._add_team_video()
        cls.draft_v1, _ = cls._create_two_drafts(cls.draft_video, cls.contributor)
        cls.public_video, cls.public_tv = cls._add_team_video()
        cls.public_v1, _ = cls._create_complete_rev(cls.public_video, cls.contributor)


    @classmethod
    def _upload_en_draft(cls, video, subs, user, complete=False):
        data = {'language_code': 'en',
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
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

    @classmethod
    def _create_two_drafts(cls, video, user):
        rev1 = os.path.join(cls.subs_dir, 'Timed_text.en.srt')
        rev2 = os.path.join(cls.subs_dir, 'Timed_text.rev2.en.srt')

        cls._upload_en_draft(video, rev1, user)
        en = video.subtitle_language('en')
        en_v1 = en.get_tip()
        cls._upload_en_draft(video, rev2, user)
        en_v2 = en.get_tip()
        return en_v1, en_v2

    @classmethod
    def _create_complete_rev(cls, video, user):
        rev1 = os.path.join(cls.subs_dir, 'Timed_text.en.srt')
        rev2 = os.path.join(cls.subs_dir, 'Timed_text.rev2.en.srt')

        cls._upload_en_draft(video, rev1, user)
        en = video.subtitle_language('en')
        en_v1 = en.get_tip()
        cls._upload_en_draft(video, rev2, user, complete=True)
        en_v2 = en.get_tip()
        return en_v1, en_v2



    def test_draft_any_team_subtitle_permissions(self):
        """Rollback only active for member assigned to task on draft.
        """
        self.team.translate_policy = 20
        self.team.subtitle_policy = 20
        self.team.save()  
        self.video_lang_pg.open_video_lang_page(self.draft_video.video_id, 'en')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team admin draft check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team manager draft check failed')

        #team member task assignee
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team member draft check failed')

        #team member not task assignee
        self.video_lang_pg.log_in(self.contributor2.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member, not assignee draft check failed')

        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user check failed')

    def test_public_any_team_subtitle_permissions(self):
        """Rollback active Public version when subtitle perms any team.

        """
        self.team.translate_policy = 20
        self.team.subtitle_policy = 20
        self.team.save()  
        self.video_lang_pg.open_video_lang_page(self.public_video.video_id, 'en')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin draft check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team manager draft check failed')

        #team member task assignee
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team member draft check failed')

        #team member not task assignee
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team member, not assignee draft check failed')

        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user check failed')


class TestCaseNoWorkflow(WebdriverTestCase):
    """TestSuite for Rollback of No Workflow team. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseNoWorkflow, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.video_pg = video_page.VideoPage(cls)

        cls.user = UserFactory.create()
        cls.owner = UserFactory.create()
        cls.team = TeamMemberFactory.create( team__translate_policy=20, #any team
                                            team__subtitle_policy=20, #any team
                                            user = cls.owner,
                                            ).team
        cls.admin = TeamMemberFactory(role="ROLE_ADMIN",team=cls.team).user
        cls.manager = TeamMemberFactory(role="ROLE_MANAGER",team=cls.team).user
        cls.contributor = TeamMemberFactory(team=cls.team, role="ROLE_CONTRIBUTOR").user
        cls.contributor2 = TeamMemberFactory(team=cls.team, role="ROLE_CONTRIBUTOR").user
        cls.site_user = UserFactory.create()
        cls.subs_dir = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                    'subtitle_data')
        cls.draft_video, cls.draft_tv = cls._add_team_video()
        cls.draft_v1, _ = cls._create_two_drafts(cls.draft_video, cls.contributor)
        cls.public_video, cls.public_tv = cls._add_team_video()
        cls.public_v1, _ = cls._create_complete_rev(cls.public_video, cls.contributor)


    @classmethod
    def _upload_en_draft(cls, video, subs, user, complete=False):
        data = {'language_code': 'en',
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
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
    @classmethod
    def _create_two_drafts(cls, video, user):
        rev1 = os.path.join(cls.subs_dir, 'Timed_text.en.srt')
        rev2 = os.path.join(cls.subs_dir, 'Timed_text.rev2.en.srt')

        cls._upload_en_draft(video, rev1, user)
        en = video.subtitle_language('en')
        en_v1 = en.get_tip()
        cls._upload_en_draft(video, rev2, user)
        en_v2 = en.get_tip()
        return en_v1, en_v2

    @classmethod
    def _create_complete_rev(cls, video, user):
        rev1 = os.path.join(cls.subs_dir, 'Timed_text.en.srt')
        rev2 = os.path.join(cls.subs_dir, 'Timed_text.rev2.en.srt')

        cls._upload_en_draft(video, rev1, user)
        en = video.subtitle_language('en')
        en_v1 = en.get_tip()
        cls._upload_en_draft(video, rev2, user, complete=True)
        en_v2 = en.get_tip()
        return en_v1, en_v2


    def test_incomplete_video_admin_permissions(self):
        """Rollback inactive for below admin permissions.

        """
        self.team.subtitle_policy = 40
        self.team.translate_policy = 40
        self.team.save()

        self.video_lang_pg.open_video_lang_page(self.draft_video.video_id, 'en')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin draft check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team manager draft check failed')

        #team member task assignee
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member draft author check failed')

        #team member not task assignee
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member, not draft author check failed')

        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user check failed')



    def test_complete_video_admin_permissions(self):
        """Rollback inactive for below admin permissions.

        """
        self.team.subtitle_policy = 40
        self.team.translate_policy = 40
        self.team.save()
        self.video_lang_pg.open_video_lang_page(self.public_video.video_id, 'en')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin draft check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team manager draft check failed')

        #team member draft author
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member draft check failed')

        #team member not draft author
        self.video_lang_pg.log_in(self.contributor2.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member, not assignee draft check failed')

        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user check failed')


    def test_incomplete_video_manager_permissions(self):
        """Rollback inactive for below manager permissions.

        """
        self.team.subtitle_policy = 30
        self.team.translate_policy = 30
        self.team.save()

        self.video_lang_pg.open_video_lang_page(self.draft_video.video_id, 'en')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin draft check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team manager draft check failed')

        #team member draft author
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member draft author check failed')

        #team member not draft author
        self.video_lang_pg.log_in(self.contributor2.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member, not draft author check failed')

        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user check failed')



    def test_complete_video_manager_permissions(self):
        """Rollback inactive for below manager permissions.

        """
        self.team.subtitle_policy = 30
        self.team.translate_policy = 30
        self.team.save()
        self.video_lang_pg.open_video_lang_page(self.public_video.video_id, 'en')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin draft check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team manager draft check failed')

        #team member draft author
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member draft check failed')

        #team member not draft author
        self.video_lang_pg.log_in(self.contributor2.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                        'team member, not assignee draft check failed')

        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user check failed')

    def test_incomplete_video_manager_permissions(self):
        """Rollback inactive for below manager permissions.

        """
        self.team.subtitle_policy = 20
        self.team.translate_policy = 20
        self.team.save()

        self.video_lang_pg.open_video_lang_page(self.draft_video.video_id, 'en')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin draft check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team manager draft check failed')

        #team member draft author 
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team member draft author check failed')

        #team member not author
        self.video_lang_pg.log_in(self.contributor2.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team member, not draft author check failed')

        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.draft_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user check failed')



    def test_complete_video_manager_permissions(self):
        """Rollback inactive for below manager permissions.

        """
        self.team.subtitle_policy = 20
        self.team.translate_policy = 20
        self.team.save()
        self.video_lang_pg.open_video_lang_page(self.public_video.video_id, 'en')

        #team admin
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team admin draft check failed')
 
        #team manager
        self.video_lang_pg.log_in(self.manager.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team manager draft check failed')

        #team member draft author
        self.video_lang_pg.log_in(self.contributor.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team member draft check failed')

        #team member not draft author
        self.video_lang_pg.log_in(self.contributor2.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback_exists(),
                        'team member, not assignee draft check failed')

        #site user has no button
        self.video_lang_pg.log_in(self.site_user.username, 'password')
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'site user check failed')

        # Guest user has no button
        self.video_lang_pg.log_out()
        self.video_lang_pg.open_page(self.public_v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists(),
                         'Guest user check failed')

class TestCaseRollbackRevision(WebdriverTestCase):
    """TestSuite for clicking Rollback button on a revision. """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseRollbackRevision, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.diffing_pg = diffing_page.DiffingPage(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.user = UserFactory.create()

        cls.owner = UserFactory.create()
        cls.team = TeamMemberFactory.create(team__workflow_enabled=True,
                                            team__translate_policy=20, #any team
                                            team__subtitle_policy=20, #any team
                                            team__task_assign_policy=10, #any team
                                            user = cls.owner,
                                            ).team
        cls.team_workflow = WorkflowFactory(team = cls.team,
                                            autocreate_subtitle=True,
                                            autocreate_translate=True,
                                            approve_allowed = 10, # manager
                                            review_allowed = 10, # peer
                                           )
        lang_list = ['en', 'ru', 'pt-br', 'de', 'sv']
        for language in lang_list:
            TeamLangPrefFactory.create(team=cls.team, language_code=language,
                                       preferred=True)

        cls.admin = TeamMemberFactory(role="ROLE_ADMIN",team=cls.team).user
        cls.contributor = TeamMemberFactory(team=cls.team, role="ROLE_CONTRIBUTOR").user
        cls.subs_dir = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                    'subtitle_data')  

    def _add_team_video(self):
        video = self.data_utils.create_video()
        tv = TeamVideoFactory(team=self.team, added_by=self.owner, video=video)
        return video, tv

    def _upload_en_draft(self, video, subs, user, complete=False):
        data = {'language_code': 'en',
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
                     'draft': open(subs),
                     'complete': int(complete),
                     'is_complete': complete,
                    }
        self.data_utils.upload_subs(user, **data)

    def _create_two_drafts(self, video, user):
        rev1 = os.path.join(self.subs_dir, 'Timed_text.en.srt')
        rev2 = os.path.join(self.subs_dir, 'Timed_text.rev2.en.srt')

        self._upload_en_draft(video, rev1, user)
        en = video.subtitle_language('en')
        en_v1 = en.get_tip()
        self._upload_en_draft(video, rev2, user)
        en_v2 = en.get_tip()
        return en_v1, en_v2

    def _create_complete_rev(self, video, user):
        rev1 = os.path.join(self.subs_dir, 'Timed_text.en.srt')
        rev2 = os.path.join(self.subs_dir, 'Timed_text.rev2.en.srt')

        self._upload_en_draft(video, rev1, user)
        en = video.subtitle_language('en')
        en_v1 = en.get_tip()
        self._upload_en_draft(video, rev2, user, complete=True)
        en_v2 = en.get_tip()
        return en_v1, en_v2



    def test_unstarted_review__transcriber_rollback(self):
        """No rollback for transcriber on revision when draft in review.


        """
        video, tv = self._add_team_video()
        v1, _ = self._create_complete_rev(video, self.contributor)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.contributor.username, 'password')

        self.video_lang_pg.open_page(v1.get_absolute_url())
        self.assertFalse(self.video_lang_pg.rollback_exists())

    
    def test_unstarted_review__diffing_page_rollback(self):
        """No Rollback for transcriber when draft in review.

        """
        video, tv = self._add_team_video()
        v1, v2 = self._create_complete_rev(video, self.contributor)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.contributor.username, 'password')

        self.diffing_pg.open_diffing_page(v1.id, v2.id)
        self.assertFalse(self.diffing_pg.rollback_exists())

    def test_failed_approve__reviewer_rollback(self):
        """Reviewer can rollback after transcript fails approve.

        """
        reviewer = TeamMemberFactory(role="ROLE_CONTRIBUTOR",team=self.team).user
        video, tv = self._add_team_video()
        v1, _ = self._create_complete_rev(video, self.contributor)

        #Accept transcript in review phase
        self.data_utils.complete_review_task(tv, 20, reviewer)
        #Reject transcript in the approve phase
        self.data_utils.complete_approve_task(tv, 30, self.owner)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(reviewer.username, 'password')
        self.video_lang_pg.open_page(v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback())
        en = video.subtitle_language('en')
        en.clear_tip_cache() 
        en_v3 = en.get_tip()
        
        self.video_lang_pg.open_page(en_v3.get_absolute_url())
        self.assertTrue(self.video_lang_pg.is_draft())
        self.assertIn('Revision 3', self.video_lang_pg.view_notice())


    def test_rolledback_draft_is_public(self):
        """Post-approval rollback to draft produces public version.

        """
        video, tv = self._add_team_video()
        v1, _ = self._create_complete_rev(video, self.contributor)
        #Accept transcript in review phase
        self.data_utils.complete_review_task(tv, 20, self.admin)
        #Reject transcript in the approve phase
        self.data_utils.complete_approve_task(tv, 20, self.owner)
        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(v1.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback())
        en = video.subtitle_language('en')
        en.clear_tip_cache() 
        en_v3 = en.get_tip()
        
        self.video_lang_pg.open_page(en_v3.get_absolute_url())
        self.assertFalse(self.video_lang_pg.is_draft())
        self.assertIn('Revision 3', self.video_lang_pg.view_notice())

    def test_diffing_page_rolledback_draft_is_public(self):
        """Post-approval diffing page rollback to draft produces public 

           version.

        """
        video, tv = self._add_team_video()
        v1, v2 = self._create_complete_rev(video, self.contributor)
        #Accept transcript in review phase
        self.data_utils.complete_review_task(tv, 20, self.admin)
        #Reject transcript in the approve phase
        self.data_utils.complete_approve_task(tv, 20, self.owner)
        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.admin.username, 'password')

        self.diffing_pg.open_diffing_page(v1.id, v2.id)
        self.assertTrue(self.diffing_pg.rollback())
        en = video.subtitle_language('en')
        en.clear_tip_cache() 
        en_v3 = en.get_tip()
        
        self.video_lang_pg.open_page(en_v3.get_absolute_url())
        self.assertFalse(self.video_lang_pg.is_draft())
        self.assertIn('Revision 3', self.video_lang_pg.view_notice())



    def test_unpublished__rollback(self):
        """Rollback to unpublished version produce new public version.
        
        """
        video, tv = self._add_team_video()
        self._create_complete_rev(video, self.contributor)
        rev3 = os.path.join(self.subs_dir, 'Timed_text.rev3.en.srt')
        self._upload_en_draft(video, rev3, self.admin, complete=True)
        #Accept transcript in review phase
        self.data_utils.complete_review_task(tv, 20, self.admin)
        #Reject transcript in the approve phase
        self.data_utils.complete_approve_task(tv, 20, self.owner)
        rev4 = os.path.join(self.subs_dir, 'Timed_text.rev4.en.srt')
        self._upload_en_draft(video, rev4, self.admin, complete=True)

        #set v3 visibilility_override to private
        en_v3 = video.subtitle_language('en').version(version_number=3)
        en_v3.visibility_override = 'private'
        en_v3.save() 

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.admin.username, 'password')
        self.video_lang_pg.open_page(en_v3.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback())
        en_v5 = video.subtitle_language('en').version(version_number=5)
        self.video_lang_pg.open_page(en_v5.get_absolute_url())
        self.assertFalse(self.video_lang_pg.is_draft())
        self.assertIn('Revision 5', self.video_lang_pg.view_notice())

    def test_diffing_page_unpublished__rollback(self):
        """Rollback to unpublished version (diffing page) => new public version.
        
        """
        video, tv = self._add_team_video()
        self._create_complete_rev(video, self.contributor)
        rev3 = os.path.join(self.subs_dir, 'Timed_text.rev3.en.srt')
        self._upload_en_draft(video, rev3, self.admin, complete=True)
        #Accept transcript in review phase
        self.data_utils.complete_review_task(tv, 20, self.admin)
        #Reject transcript in the approve phase
        self.data_utils.complete_approve_task(tv, 20, self.owner)
        rev4 = os.path.join(self.subs_dir, 'Timed_text.rev4.en.srt')
        self._upload_en_draft(video, rev4, self.admin, complete=True)

        #set v3 visibilility_override to private
        en_v3 = video.subtitle_language('en').version(version_number=3)
        en_v3.visibility_override = 'private'
        en_v3.save() 
        en_v4 = video.subtitle_language('en').version(version_number=4)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(self.admin.username, 'password')

        self.diffing_pg.open_diffing_page(en_v3.id, en_v4.id)
        self.assertTrue(self.diffing_pg.rollback())

        self.video_lang_pg.open_page(en_v3.get_absolute_url())
        self.assertTrue(self.video_lang_pg.rollback())
        en_v5 = video.subtitle_language('en').version(version_number=5)
        self.video_lang_pg.open_page(en_v5.get_absolute_url())
        self.assertFalse(self.video_lang_pg.is_draft())
        self.assertIn('Revision 5', self.video_lang_pg.view_notice())

