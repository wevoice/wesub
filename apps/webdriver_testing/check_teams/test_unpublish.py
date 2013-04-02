import os
import time

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages import video_page
from apps.webdriver_testing.pages.site_pages import video_language_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import VideoUrlFactory
from apps.webdriver_testing.pages.editor_pages import subtitle_editor
from apps.webdriver_testing.pages.editor_pages import unisubs_menu 
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import WorkflowFactory
from apps.webdriver_testing.data_factories import TeamLangPrefFactory
from apps.webdriver_testing.pages.site_pages.teams.tasks_tab import TasksTab
from apps.webdriver_testing.pages.editor_pages import dialogs

class TestCaseDelete(WebdriverTestCase):
    """TestSuite for download subtitles from the video's lanugage page   """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseDelete, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)

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
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)
        cls.create_modal = dialogs.CreateLanguageSelection(cls)

        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')
        cls.user_creds = dict(username=cls.user.username, 
                          password='password')



    def _create_source_with_multiple_revisions(self):
        self.logger.info("Create a video that has this revision structure:")
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
        rev1_data = {'language_code': 'en',
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
                     'draft': open(rev1_subs)
                    }
        self.data_utils.upload_subs(video, rev1_data, user=self.user_creds)
        self.logger.info(video.subtitle_language('en').get_tip(full=True))

        #REV2
        rev2_subs = os.path.join(self.subs_data_dir, 'Timed_text.rev2.en.srt')
        rev2_data = {'language_code': 'en',
                     'video': video.pk,
                     'draft': open(rev2_subs)
                    }
        self.data_utils.upload_subs(video, rev2_data, user=self.user_creds)
        self.logger.info(video.subtitle_language('en').get_tip(full=True))

        #REV3
        rev3_subs = os.path.join(self.subs_data_dir, 'Timed_text.rev3.en.srt')
        rev3_data = {'language_code': 'en',
                     'video': video.pk,
                     'draft': open(rev3_subs),
                     'is_complete': True,
                     'complete': 1,
                    }
        self.data_utils.upload_subs(video, rev3_data, user=self.user_creds)
        self.logger.info("PRE APPROVE REV3")
        self.logger.info(video.subtitle_language('en').get_tip(full=True)) 
        time.sleep(2)
        self.data_utils.complete_review_task(tv, 20, self.user)
        self.data_utils.complete_approve_task(tv, 20, self.user)
        time.sleep(2)
        self.logger.info("POST APPROVE REV3")
        self.logger.info(video.subtitle_language('en').get_tip(full=True)) 

        #REV 4
        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.log_in(**self.user_creds)
        self.video_lang_pg.page_refresh()
        self.video_lang_pg.edit_subtitles()
        self.sub_editor.edit_subs()
        self.sub_editor.continue_to_next_step() #to syncing
        self.sub_editor.continue_to_next_step() #to description
        self.sub_editor.continue_to_next_step() #to review
        self.sub_editor.submit(complete=True)
        time.sleep(8)
        #rev4_subs = os.path.join(self.subs_data_dir, 'Timed_text.rev4.en.srt')
        #rev4_data = {'language_code': 'en',
        #             'video': video.pk,
        #             'draft': open(rev4_subs),
        #             'is_complete': True,
        #             'complete': 1,
        #            }
        #self.data_utils.upload_subs(video, rev4_data, user=self.user_creds)
        self.logger.info("REVISION 4")
        self.logger.info(video.subtitle_language('en').get_tip(full=True))
        #self.data_utils.complete_review_task(tv, 20, self.user)
        #self.data_utils.complete_approve_task(tv, 20, self.user)
        time.sleep(2)
        self.logger.info("POST APPROVE REV4")
        self.logger.info(video.subtitle_language('en').get_tip(full=True)) 


        return video, tv

    def tearDown(self):
        self.browser.get_screenshot_as_file('MYTMP/%s.png' % self.id())

    def upload_translation(self, video, lang):
        data = {'language_code': lang,
                'video': video.pk,
                'from_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.sv.dfxp'),
                'is_complete': True,
                'complete': 1
           }
        self.data_utils.upload_subs(
                video, 
                data=data,
                user=self.user_creds)

    def test_unpublish__updates_translation_source(self):
        """Unpublishing updates translation source to prior public rev.

        """
        video, tv = self._create_source_with_multiple_revisions()
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.log_in(self.user.username, 'password')
       
        self.upload_translation(video, 'sv')
        sv = video.subtitle_language('sv')
        self.logger.info("sv lineage - pre unpublish")
        self.logger.info(sv.get_tip().lineage)

        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.unpublish(delete=True)
        time.sleep(8)
        self.logger.info("en public rev post-unpublish")
        self.logger.info(video.subtitle_language('en').get_tip(public=True))

        self.upload_translation(video, 'de')
        de = video.subtitle_language('de')
        self.logger.info("Post unpublish german translation lineage")
        self.logger.info(de.get_tip().lineage)

