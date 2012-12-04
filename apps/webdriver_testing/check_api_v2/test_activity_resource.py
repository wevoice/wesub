# -*- coding: utf-8 -*-
import os
import time
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory

from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.site_pages import video_page
from apps.webdriver_testing.site_pages import teams_page


class TestCaseActivity(WebdriverTestCase):
    """TestSuite for listing things that happened.

    GET /api2/partners/activity/
    Query Parameters:
        team – Show only items related to a given team (team slug)
        video – Show only items related to a given video (video id)
        type – Show only items with a given activity type (int, see below)
        language – Show only items with a given language (language code)
        before – A unix timestamp in seconds
        after – A unix timestamp in seconds

    Activity types:

    Add video
    Change title
    Comment
    Add version
    Add video URL
    Add translation
    Subtitle request
    Approve version
    Member joined
    Reject version
    Member left
    Review version
    Accept version
    Decline version
    Delete video

Activity item detail:

GET /api2/partners/activity/[activity-id]/

   """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'TestUser', is_partner=True)
        data_helpers.create_user_api_key(self, self.user)
        
        #create an open team with description text and 2 members
        self.open_team = TeamMemberFactory.create(
            team__name="A1 Waay Cool team",
            team__slug='a1-waay-cool-team',
            team__description='this is the coolest, most creative team ever',
            user = self.user
            ).team

        TeamMemberFactory.create(team=self.open_team,
             user=UserFactory.create())
        TeamVideoFactory.create(team=self.open_team, added_by=self.user)

    def test_list__video_update(self):
        """Verify 
        GET /api2/partners/activity/[activity-id]/

        """
        url_data = { 'video_url': ('http://qa.pculture.org/amara_tests/'
                                   'Birds_short.webmsd.webm'),
                     'title': 'Test video created via api',
                     'duration': 37,
                      }
        url_part = 'videos/'
        status, response = data_helpers.post_api_request(self, 
            url_part, url_data)
        print response
        vid_id = response['id']

        url_part = 'videos/%s' % vid_id
        new_data = {'title': 'MVC webM output sample',
                    'description': ('This is a sample vid converted to webM '
                                   '720p using Miro Video Converter')
                   }
        status, response = data_helpers.put_api_request(self, url_part, 
            new_data)
        print response


        url_part = 'activity/%d/' % 2
        status, response = data_helpers.api_get_request(self, url_part) 
        print status, response
        self.assertEqual(200, status)




    def test_team__video_added(self):
        """Verify 
        GET /api2/partners/activity/[activity-id]/

        """
        url_data = { 'video_url': ('http://qa.pculture.org/amara_tests/'
                                   'Birds_short.webmsd.webm'),
                     'title': 'Test video created via api',
                     'duration': 37,
                     'team': self.open_team.slug }
        url_part = 'videos/'
        status, response = data_helpers.post_api_request(self, 
            url_part, url_data)
        new_vid_id = response['id']


        activity_query = '?team={0}&type={1}'.format(
            self.open_team.slug, 1)
        url_part = 'activity/%s' % activity_query
        status, response = data_helpers.api_get_request(self, url_part) 
        print status, response
        self.assertEqual(new_vid_id, response['objects'][0]['video'])
    
