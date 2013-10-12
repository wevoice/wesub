import os
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.pages.site_pages import video_language_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import WorkflowFactory
from apps.webdriver_testing.data_factories import VideoUrlFactory


class TestCaseVideoLangResource(WebdriverTestCase):
    """TestSuite for uploading subtitles via the api.

    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseVideoLangResource, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create()
        
      
        #Create some test data and set subtitle data dir
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
                                         'webdriver_testing', 'subtitle_data')
        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)

    def test_complete(self):
        """Set a language as complete via the api
        """

        #Create the language for the test video
        test_video = self.data_utils.create_video()

        url_part = ('videos/%s/languages/'  % test_video.video_id)
        data = {'language_code': 'en',
                       'is_complete': True 
                      }
        r = self.data_utils.make_request(self.user, 'post', url_part, **data)
        self.assertEqual(201, r.status_code)

    def test_original(self):
        """Set a language as original via the api
        """
        test_video = self.data_utils.create_video()
        
        #Create the language for the test video
        url_part = ('videos/%s/languages/'  % test_video.video_id)
        data = {'language_code': 'fr',
                       'is_original': True 
                      }
        r = self.data_utils.make_request(self.user, 'post', url_part, **data)
        response = r.json

        self.assertEqual(201, r.status_code)
        url_part = 'videos/%s/' % test_video.video_id
        r = self.data_utils.make_request(self.user, 'get', url_part)
        response = r.json
        self.assertEqual('fr', response['original_language'])


    def _create_team_owner(self):
        return UserFactory.create()

    def _create_team(self):
        owner = UserFactory.create()

        team = TeamMemberFactory.create(team__workflow_enabled=True,
                                            team__translate_policy=20,
                                            team__subtitle_policy=20,
                                            user = owner,
                                            ).team
        team_workflow = WorkflowFactory(team = team,
                                            autocreate_subtitle=True,
                                            autocreate_translate=True,
                                            approve_allowed = 10,
                                            review_allowed = 10,
                                           )
        return team, owner

    def _create_video_with_complete_transcript(self, team, owner):
        sub_file = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                 'subtitle_data', 'Timed_text.en.srt')
        member = TeamMemberFactory(team=team, role='ROLE_CONTRIBUTOR').user

        video = VideoUrlFactory().video
        tv = TeamVideoFactory.create(
            team=team, 
            video=video, 
            added_by=owner)
        data = {
                     'language_code': 'en',
                     'video': video,
                     'visibility': 'private',
                     'complete': True,
                     'committer': member
                    }
        self.data_utils.add_subs(**data)
        return video, tv

    def test_response__reviewer(self):
        team, owner = self._create_team()
        member = TeamMemberFactory(team=team).user

        video, tv = self._create_video_with_complete_transcript(team, owner)
        self.data_utils.complete_review_task(tv, 20, member)
        self.data_utils.complete_approve_task(tv, 20, owner)

        url_part = ('videos/%s/languages/' % video.video_id)
        r = self.data_utils.make_request(self.user, 'get', url_part)
        response = r.json
        self.assertIn(member.username, response['objects'][0]['reviewer'])

    def test_response__approver(self):
        team, owner = self._create_team()
        video, tv = self._create_video_with_complete_transcript(team, owner)
        self.data_utils.complete_review_task(tv, 20, owner)
        self.data_utils.complete_approve_task(tv, 20, owner)
        url_part = ('videos/%s/languages/' % video.video_id)
        r = self.data_utils.make_request(self.user, 'get', url_part)
        response = r.json

        self.assertIn(owner.username, response['objects'][0]['approver'])

    def test_response__published(self):
        team, owner = self._create_team()
        video, tv = self._create_video_with_complete_transcript(team, owner)
        self.data_utils.complete_review_task(tv, 20, owner)
        self.data_utils.complete_approve_task(tv, 20, owner)
        url_part = ('videos/%s/languages/' % video.video_id)
        r = self.data_utils.make_request(self.user, 'get', url_part)
        response = r.json

        self.assertTrue(response['objects'][0]['versions'][0]['published'])

 
