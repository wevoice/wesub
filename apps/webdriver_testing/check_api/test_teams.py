from rest_framework.test import APILiveServerTestCase, APIClient
from django.core import mail

from caching.tests.utils import assert_invalidates_model_cache
from videos.models import *
from utils.factories import *
from webdriver_testing.data_factories import ApplicationFactory
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages.teams_dir_page import TeamsDirPage
from webdriver_testing.pages.site_pages.teams import members_tab
from webdriver_testing.pages.site_pages import user_messages_page
from webdriver_testing.pages.site_pages.teams import ATeamPage

class TestCaseTeams(APILiveServerTestCase, WebdriverTestCase):
    """TestSuite for teams api  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseTeams, cls).setUpClass()
        cls.team_pg = ATeamPage(cls)
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
        try:
            response.render()
            r = (json.loads(response.content))
            return r
        except:
            return response.status_code

    def test_create_team_user(self):
        """Regular user can not create a team

        """
        
        data = {
            'name': 'API TEAM',
            'description': 'new team created via the api',
            'slug': 'api-created-team1' 
            } 

        r = self._post(data=data, user=self.user)
        self.assertEqual(r, {u'detail': u'Permission denied'})

    def test_create_team_amara_staff(self):
        """ Staff can not create a team via the api

        """
        
        data = {
            'name': 'API TEAM',
            'description': 'new team created via the api',
            'slug': 'api-created-team2' 
            } 

        r = self._post(data=data, user=self.staff)
        self.assertEqual(r, {u'detail': u'Permission denied'})


    def test_team_partner_create(self):
        """ is_partner required to create a team via the api

        """
        data = {
                'name': 'API TEAM',
                'description': 'new team created via the api',
                'slug': 'api-created-team3' 
                } 

        r = self._post(data=data, user=self.partner)
        self.logger.info(r)
        for k, v in data.iteritems():
            self.assertEqual(v, r[k])
        url = '/api/teams/%s/members/' % r['slug']
        r = self._get(url, self.partner)
        self.logger.info(r)
        self.assertIn(self.partner.username, r['objects'][0]['username'])
        self.assertIn('owner', r['objects'][0]['role'])

    def test_list(self):
        """User can get public teams + their private teams
        """
        admin = UserFactory()
        member = UserFactory()
        for x in range(1,6):
            TeamFactory(admin=admin,
                        member=member,
                        membership_policy=x, 
                        is_visible=False)

        #create an open team         
        TeamFactory()

        #Verify member sees all teams + open team
        r = self._get(user=member)
        self.assertEqual(6,len(r['objects']))
       
        #Regular user sees open teams + application teams 
        r = self._get(user=self.user)
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
        self.assertEqual(r, {u'detail': u"Method 'DELETE' not allowed."})

        #check member can't delete the team
        r = self._delete(url=url, user=member)
        self.assertEqual(r, {u'detail': u"Method 'DELETE' not allowed."})

        #admin can't delete the team.
        r = self._delete(url=url, user=admin)
        self.assertEqual(r, {u'detail': u"Method 'DELETE' not allowed."})

        #owner can't delete the team.
        owner = TeamMemberFactory(team=team).user
        r = self._delete(url=url, user=owner)
        self.assertEqual(r, {u'detail': u"Method 'DELETE' not allowed."})

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

    def test_add_team_video(self):
        """add a video to a team and project""" 
        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member)
        project = ProjectFactory(team=team)
        url = "/api/videos/"

        data = {
                "video_url": "http://unisubs.example.com:8000/video.mp4", 
                "primary_audio_language_code": "en", 
                "title": "This is a test", 
                "description": "The description of the test video", 
                "duration": 320, 
                "thumbnail": "https://i.ytimg.com/vi/BXMPp0TLSEo/hqdefault.jpg",
                "team": team.slug,
                "project": project.slug
                }
        r = self._post(url=url, data=data, user=admin)

        #Check response content
        self.assertEqual(data['primary_audio_language_code'], r['primary_audio_language_code'])
        self.assertEqual(data['title'], r['title'])
        self.assertEqual(data['description'], r['description'])
        self.assertEqual(data['duration'], r['duration'])
        self.assertEqual(data['thumbnail'], r['thumbnail'])
        self.assertEqual(data['video_url'], r['all_urls'][0])
        self.assertEqual(project.slug, r['project'])
        self.assertEqual(team.slug, r['team'])
        self.assertEqual('en', r['original_language'])
        self.assertEqual({}, r['metadata'])

        #Check database content 
        video = Video.get(videourl__url=data['video_url'])
        self.assertEqual(data['primary_audio_language_code'], video.primary_audio_language_code)
        self.assertEqual(data['title'], video.title)
        self.assertEqual(data['description'], video.description)
        self.assertEqual(data['duration'], video.duration)


    def test_project_list(self):
        """List off the teams projects.
        """
        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member)
        for x in range(3):
            ProjectFactory(team=team)

        url = "/api/teams/%s/projects/" % team.slug
        r = self._get(url=url, user=admin)
        self.assertEqual(3, len(r))


    def test_project_details(self):
        """Get the details of a project.
        """
        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member)
        project = ProjectFactory(team=team, 
                       description='initial team project',
                       guidelines='these are guidelines')
        url = '/api/teams/{0}/projects/{1}/'.format(team.slug, project.slug)
        r = self._get(url=url, user=admin)
        self.assertEqual(r['description'], project.description)
        self.assertEqual(r['slug'], project.slug)

    def test_project_create(self):
        """Create a new project for the team.
        """

        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member)
        url = '/api/teams/%s/projects/' % team.slug
        data = {
                     "name": "Project name",
                     "slug": "project-slug",
                     "description": "This is an example project.",
                }
        r = self._post(url=url, data=data, user=admin)
        self.team_pg.open_page('/')
        self.team_pg.log_in(admin.username, 'password')
        self.team_pg.open_team_page(team.slug)
        self.assertTrue(self.team_pg.has_project(data['slug']))


    def test_project_update(self):
        """Update a projects information.
        """
        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member)
        project1 = ProjectFactory(team=team, 
                       description='initial team project',
                       guidelines='these are guidelines')
        url = '/api/teams/{0}/projects/{1}/'.format(team.slug, project1.slug)
        data = {
            'description': 'updated description' 
            } 
        r = self._put(url=url, data=data, user=admin)
        self.logger.info(r)
        self.team_pg.open_page('/')
        self.team_pg.log_in(admin.username, 'password')
        self.team_pg.open_page("/teams/{0}/settings/projects/{1}/edit/".format(team.slug, project1.slug))
        
        self.assertTrue(self.team_pg.is_text_present("textarea", data['description']))

    def test_project_delete(self):
        """Delete a team project.
        """
        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member)
        project1 = ProjectFactory(team=team, 
                       description='initial team project')
        project2 = ProjectFactory(team=team, 
                       description='project 2')
        url = '/api/teams/{0}/projects/{1}/'.format(team.slug, project2.slug)
        r = self._delete(url=url, user=admin)
        self.team_pg.open_page('/')
        self.team_pg.log_in(admin.username, 'password')
        self.team_pg.open_team_page(team.slug)
        #Verify project 1 is still present
        self.assertTrue(self.team_pg.has_project(project1.slug)) 
        #Verify project2 is deleted
        self.assertFalse(self.team_pg.has_project(project2.slug)) 



    def test_applications(self):
        """get update and delete team applications
        """

        admin = UserFactory()
        member = UserFactory()
        team = TeamFactory(admin=admin,
                           member=member,
                           workflow_enabled=False,
                           membership_policy=1, # application-only team
                           description="This is the description",
                           is_visible=True)

        for x in range(0,5):
            ApplicationFactory(team = team,
                               user = UserFactory.create(),
                               status = x,
                               note = 'let me in')
        url = '/api/teams/%s/applications/' % team.slug
        r = self._get(url=url, user=admin)
        self.assertEqual(5, r['meta']['total_count'])
        applications = r['objects']

        #check the details of an app
        pending_app = [app.get('id') for app in applications if app.get('status') == 'Pending'][0]
        app_url = url + '%d/' % pending_app
        r = self._get(url=app_url, user=admin)
        user = r['user']
        self.assertEqual("Pending", r['status'])
        #Update the pending application to approved.
        data = {'status': 'Approved' }
        r = self._put(url=app_url, user=admin, data=data)
        r = self._get(url=url, user=admin)
        members_url = "/api/teams/%s/members/" % team.slug
        r = self._get(url=members_url, user=admin)
        self.assertIn(user, [member['username'] for member in r['objects']])
        #Query for a specific user
        query_url = url + '?user=%s' % user
        r = self._get(url=query_url, user=admin)
        self.assertEqual(1, r['meta']['total_count'])
        #Query by status
        query_url = url + '?status=Approved'
        r = self._get(url=query_url, user=admin)
        self.assertEqual(2, r['meta']['total_count'])
