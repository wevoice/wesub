from rest_framework.test import APILiveServerTestCase, APIClient
from django.core import mail

from caching.tests.utils import assert_invalidates_model_cache
from videos.models import *
from utils.factories import *
from subtitles import pipeline
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages.teams_dir_page import TeamsDirPage
from webdriver_testing.pages.site_pages.teams import members_tab
from webdriver_testing.pages.site_pages import user_messages_page

class TestCaseTeams(APILiveServerTestCase, WebdriverTestCase):
    """TestSuite for teams api  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseTeams, cls).setUpClass()

        cls.user = UserFactory()
        cls.staff = UserFactory(is_staff=True, is_superuser=True)
        cls.partner = UserFactory(is_partner=True)
        cls.client = APIClient

    def _get (self, url='/api/teams/', user=None):
        self.client.force_authenticate(user)
        response = self.client.get(url)
        response.render()
        r = (json.loads(response.content))
        return r

    def _post(self, url='/api/teams/', data=None, user=None):
        self.client.force_authenticate(user)
        response = self.client.post(url, data)
        response.render()
        r = (json.loads(response.content))
        return r

    def _put(self, url='/api/teams/', data=None, user=None):
        self.client.force_authenticate(user)
        response = self.client.put(url, data)
        response.render()
        r = (json.loads(response.content))
        return r

    def _delete(self, url='/api/teams/', user=None):
        self.client.force_authenticate(user)
        response = self.client.delete(url)
        response.render()
        r = (json.loads(response.content))
        return r

    def test_create_team_user(self):
        """Regular user can not create a team

        """
        
        data = {
            'name': 'API TEAM',
            'description': 'new team created via the api',
            'slug': 'api-created-team' 
            } 

        r = self._post(data=data, user=self.user)
        self.assertEqual(r, {u'detail': u'Permission denied'})

    def test_create_team_amara_staff(self):
        """ Staff can not create a team via the api

        """
        
        data = {
            'name': 'API TEAM',
            'description': 'new team created via the api',
            'slug': 'api-created-team' 
            } 

        r = self._post(data=data, user=self.staff)
        self.assertEqual(r, {u'detail': u'Permission denied'})


    def test_team_partner_create(self):
        """ is_partner required to create a team via the api

        """
        partner_user = UserFactory.create(username = 'team_creator', is_partner = True)
        
        data = {
                'name': 'API V2 TEAM',
                'description': 'new team created via the api',
                'slug': 'api-created-team' 
                } 

        r = self._post(data=data, user=self.partner)
        for k, v in data.iteritems():
            self.assertEqual(v, r[k])

    def test_list(self):
        """User can get public teams + their private teams
        """
        admin = UserFactory()
        member = UserFactory()
        for x in range(1,6):
            self.logger.info(x)
            TeamFactory(admin=admin,
                        member=member,
                        membership_policy=x, 
                        is_visible=False)

        #create an open team         
        TeamFactory()

        #Verify member sees all teams + open team
        r = self._get(user=member)
        self.logger.info(r)
        self.assertEqual(6,len(r['objects']))
       
        #Regular user sees open teams + application teams 
        r = self._get(user=self.user)
        self.logger.info(r)
        self.assertEqual(3,len(r['objects']))

    def test_details(self):
        """Get the details about a specific team.

        """


        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member,
                           workflow_enabled=True,
                           membership_policy=5, #invitation by admin
                           description="This is the description",
                           is_visible=False)
        WorkflowFactory(team=team, 
                        autocreate_subtitle=True,
                        autocreate_translate=True)


        
        expected_details = {
            'is_visible': False, 
            'description': 'This is the description',
            'membership_policy': 'Invitation by admin', 
            'slug': team.slug, 
            'name': team.name
            } 

        url = '/api/teams/%s/' % team.slug
        r = self._get(url=url, user=member)
        self.logger.info(r)
        for k, v in expected_details.iteritems():
            self.assertEqual(v, r[k])

    def test_update(self):
        """Update the team information

        """

        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member,
                           workflow_enabled=True,
                           membership_policy=5, #invitation by admin
                           description="This is the description",
                           is_visible=False)

        url = '/api/teams/%s/' % team.slug
        data = {
            'description': 'updated the team description',
            'membership_policy': 'Invitation by any team member', 
            'is_visible': True, 
            } 


        #check regular user can't update the team.
        r = self._put(url=url, data=data, user=self.user)
        self.assertEqual(r, {u'detail': u'Not found'})

        #check member can't update the team
        r = self._put(url=url, data=data, user=member)
        self.logger.info(r)
        self.assertEqual(r, {u'detail': u'Permission denied'})

        #admin can update the team.
        r = self._put(url=url, data=data, user=admin)
        for k, v in data.iteritems():
            self.assertEqual(v, r[k])

    def test_delete(self):
        """Delete the team (owner-level permissions)

        """

        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member,
                           workflow_enabled=True,
                           membership_policy=5, #invitation by admin
                           description="This is the description",
                           is_visible=False)

        url = '/api/teams/%s/' % team.slug
        #check regular user can't delete the team.
        r = self._delete(url=url, user=self.user)
        self.assertEqual(r, {u'detail': u'Not found'})

        #check member can't delete the team
        r = self._delete(url=url, user=member)
        self.assertEqual(r, {u'detail': u'Permission denied'})

        #admin can't delete the team.
        r = self._delete(url=url, user=admin)
        self.assertEqual(r, {u'detail': u'Permission denied'})

        #owner can delete the team.
        owner = TeamMemberFactory(team=team).user
        self.client.force_authenticate(owner)
        response = self.client.delete(url)
        response.render()
        self.logger.info(response.status_code)
        self.assertEqual(response.status_code, 204)

    def test_members_list(self):
        """List off the existing team members.
        """
        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member
                           )
        url = '/api/teams/%s/members/' % team.slug

        r = self._get(url=url, user=member)
        self.assertEqual(len(r), 2)


    def test_member_update(self):
        """Update a team members role.
        """
        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member
                           )
        data = {
            'role': 'manager' 
            } 

        url = '/api/teams/%s/members/%s/' % (team.slug, 
                                             member.username)
        r = self._put(url=url, data=data, user=member)
        self.assertEqual(r, {u'detail': u'Permission denied'}) 
        r = self._put(url=url, data=data, user=admin)
        self.assertEqual(r, {u'role': u'manager', u'username': member.username})


    def test_create_contributor(self):
        """Add a team member via the api.
          
        """
        user = UserFactory()
        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member
                           )
        data = { "username": user.username, "role": "contributor" }
        url = "/api/teams/%s/members/" % team.slug
        r = self._post(url=url, data=data, user=admin)
        self.assertEqual(r, {u'role': u'contributor', u'username': user.username})

    def test_safe_member(self):
        """Safe-members sends an invitation and email
        """
        
        user = UserFactory()
        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member
                           )
        mail.outbox = [] 

        #Create a post the request 
        data = {"username": user.username,
                "role": "contributor",
                "email": "tester@example.com"
                } 
        url = '/api/teams/%s/safe-members/' % team.slug
        r = self._post(url=url, data=data, user=admin)
        message = mail.outbox[0]
        self.assertEqual(message.subject, 
                         "You've been invited to team %s on Amara" % team.name
                        )
        self.assertIn(user.email, message.to)


    def test_safe_member_email(self):
        """email address is a required field for safe member """
        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member
                           )
        data = {"username": 'InviteMe',
                "role": "contributor"
               } 
        url= '/api/teams/%s/safe-members/' % team.slug
        
        r = self._post(url=url, data=data, user=admin)
        self.logger.info(r)
        self.assertEqual(r, {u'non_field_errors': [u'Email required to create user']})
       

    def test_delete_member(self):
        """Team member is deleted by the owner.
        """

        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member,
                           workflow_enabled=True,
                           membership_policy=5, #invitation by admin
                           description="This is the description",
                           is_visible=False)

        user = TeamContributorMemberFactory(team=team).user

        url = '/api/teams/{0}/members/{1}/'.format(team.slug, user.username)
        #check member can't delete the user
        r = self._delete(url=url, user=member)
        self.assertEqual(r, {u'detail': u'Permission denied'})

        #admin can delete the user
        self.client.force_authenticate(admin)
        response = self.client.delete(url)
        response.render()
        self.assertEqual(response.status_code, 204)

    def test_post(self):
        """post a new video with all metadata for public video""" 
        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member)
        url = "/api/videos/"

        data = {
                "video_url": "http://unisubs.example.com:8000/video.mp4", 
                "primary_audio_language_code": "en", 
                "title": "This is a test", 
                "description": "The description of the test video", 
                "duration": 320, 
                "thumbnail": "https://i.ytimg.com/vi/BXMPp0TLSEo/hqdefault.jpg",
                "team": team.slug
                }
        r = self._post(url=url, data=data, user=admin)

        #Check response content
        self.assertEqual(data['primary_audio_language_code'], r['primary_audio_language_code'])
        self.assertEqual(data['title'], r['title'])
        self.assertEqual(data['description'], r['description'])
        self.assertEqual(data['duration'], r['duration'])
        self.assertEqual(data['thumbnail'], r['thumbnail'])
        self.assertEqual(data['video_url'], r['all_urls'][0])
        self.assertEqual(None, r['project'])
        self.assertEqual(team.slug, r['team'])
        self.assertEqual('en', r['original_language'])
        self.assertEqual({}, r['metadata'])

        #Check database content 
        video, created = Video.get_or_create_for_url(data['video_url'])
        self.assertFalse(created) 
        self.assertEqual(data['primary_audio_language_code'], video.primary_audio_language_code)
        self.assertEqual(data['title'], video.title)
        self.assertEqual(data['description'], video.description)
        self.assertEqual(data['duration'], video.duration)
