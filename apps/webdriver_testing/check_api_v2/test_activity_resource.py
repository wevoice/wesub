# -*- coding: utf-8 -*-
import os
import time
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import TeamMemberFactory

from webdriver_testing.data_factories import TeamVideoFactory

from webdriver_testing import data_helpers

class TestCaseActivity(WebdriverTestCase):
    """TestSuite for listing things that happened.

    GET /api2/partners/activity/
    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseActivity, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create(is_partner = True)
        
        
        #create an open team with description text and 2 members
        cls.open_team = TeamMemberFactory.create(
            team__name="A1 Waay Cool team",
            team__slug='a1-waay-cool-team',
            team__description='this is the coolest, most creative team ever',
            user = cls.user
            ).team

        TeamMemberFactory.create(team=cls.open_team,
             user=UserFactory.create())
        TeamVideoFactory.create(team=cls.open_team, added_by=cls.user)

    def test_list_video_update(self):
        """Verify video update activity.
        GET /api2/partners/activity/[activity-id]/

        """
        video = self.data_utils.create_video_with_subs(self.user)
        TeamVideoFactory.create(team=self.open_team, 
                                video=video, 
                                added_by=self.user)

        url_data = { 'video_url': ('http://qa.pculture.org/amara_tests/fireplace.mp4'),
                     'title': 'Test video created via api',
                     'duration': 37,
                     'team': self.open_team.slug }
        url_part = 'videos/'
        r = self.data_utils.make_request(self.user, 'post', 
                                         url_part, **url_data)
        response = r.json
        
        new_data = {'title': 'MVC webM output sample',
                    'description': ('This is a sample vid converted to webM '
                                   '720p using Miro Video Converter')
                   }
        r = self.data_utils.make_request(self.user, 'put', 
                                         response['resource_uri'], **new_data)
        response = r.json
        #activity_query = '?team={0}&type={1}'.format(
        #    self.open_team.slug, 2)
        activity_query = '?team=%s&type=4&team-activity=1' % self.open_team.slug
        url_part = 'activity/%s' % activity_query
        r = self.data_utils.make_request(self.user, 'get', url_part)
        self.assertEqual(200, r.status_code)




    def test_team_video_added(self):
        """Verify team video added activity.

        GET /api2/partners/activity/[activity-id]/

        """
        url_data = { 'video_url': ('http://qa.pculture.org/amara_tests/'
                                   'Birds_short.webmsd.webm'),
                     'title': 'Test video created via api',
                     'duration': 37,
                     'team': self.open_team.slug }
        url_part = 'videos/'
        r = self.data_utils.make_request(self.user, 'post',
            url_part, **url_data)
        resp = r.json
        new_vid_id = resp['id']

        activity_query = '?team={0}&type={1}&team-activity=1'.format(
            self.open_team.slug, 1)
        url_part = 'activity/%s' %activity_query
        r = self.data_utils.make_request(self.user, 'get', url_part)
        resp = r.json
        self.assertEqual(new_vid_id, resp['objects'][0]['video'])
    
