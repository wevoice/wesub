#!/usr/bin/python

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import video_page
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing import data_helpers
import os

class TestCaseUploadSubs(WebdriverTestCase):
    """TestSuite for uploading subtitles to team videos

    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user')
        self.video_pg = video_page.VideoPage(self)
        self.video_pg.log_in(self.user.username, 'password')
        self.test_video = data_helpers.create_video(self, 
            'http://www.example.com/upload_test.mp4')
        self.team = TeamMemberFactory.create(
            team__name='Video Test',
            team__slug='video-test',
            user = self.user).team

        TeamVideoFactory.create(
            team = self.team,
            video = self.test_video, 
            added_by = self.user)

        self.video_pg.open_video_page(self.test_video.video_id)
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')

    def test_upload__open_team(self):
        """Upload subtitles to a video that belongs to an open team.

        """
        test_file = 'Timed_text.en.srt'
        sub_file = os.path.join(self.subs_data_dir, test_file) 
        message = self.video_pg.upload_subtitles('English', sub_file)
        self.video_pg.open_video_page(self.test_video.video_id)
        self.assertEqual(message, self.video_pg.UPLOAD_SUCCESS_TEXT)
        
      
