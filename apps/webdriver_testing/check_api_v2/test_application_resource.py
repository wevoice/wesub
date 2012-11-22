import time
import datetime
import itertools
import operator
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import ApplicationFactory
from apps.webdriver_testing.site_pages import a_team_page 
from apps.webdriver_testing.site_pages import auth_page



class TestCaseApplications(WebdriverTestCase):
    """TestSuite for managing applications via the api.

    GET /api2/partners/teams/[team-slug]/applications

    Query Parameters
    status: Denied, Approved, Pending, Member Removed, Member Left
    before: A unix timestamp in seconds
    after: A unix timestamp in seconds
    user: The username applying for the team
       
    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user', is_partner=True)
        data_helpers.create_user_api_key(self, self.user)
        self.joiner = UserFactory.create(username='teamjoiner')

        #Create the application only team
        self.team = TeamMemberFactory.create(
            team__name='my application-only team',
            team__slug='application-only',
            team__membership_policy=1,
            user = self.user).team

        #Create a user who has a pending application
        self.joiner_app = ApplicationFactory.create(
            team = self.team,
            user = self.joiner,
            status = 0, 
            note = 'let me in')

        # Create some additional applications the various status
        for x in range(0,5):
            test_username = 'TestUser'+str(x)
            ApplicationFactory.create(
            team = self.team,
            user = UserFactory.create(username = test_username),
            status = x, 
            note = 'let me in, too')

        self.a_team_pg = a_team_page.ATeamPage(self)
        self.auth_pg = auth_page.AuthPage(self)

    def test_list__applications(self):
        """List all applications for a team.

           GET /api2/partners/teams/[team-slug]/applications
        """
        
        expected_applicants = [self.joiner.username,
                               'TestUser0',
                               'TestUser1',
                               'TestUser2',
                               'TestUser3',
                               'TestUser4']

        url_part = 'teams/%s/applications/' % self.team.slug
        _, response = data_helpers.api_get_request(self, url_part) 
        applicants_objects =  response['objects']
        applicants_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                applicants_list.append(k)
        self.a_team_pg.open_page('teams/%s/applications/' % self.team.slug)
        self.assertEqual(expected_applicants, applicants_list)


    def test_application__details(self):
        """List details of an application.

           GET /api2/partners/teams/[team-slug]/application/[application-id]/
        """
        expected_details = {'user': self.joiner.username, 
                            'status': 'Pending',}
 
        url_part = 'teams/{0}/applications/{1}'.format(self.team.slug, 
            self.joiner_app.pk)
        _, response = data_helpers.api_get_request(self, url_part) 
        self.a_team_pg.open_page('teams/%s/applications/' % self.team.slug)

        for k, v in expected_details.iteritems():
            self.assertEqual(v, response[k])



    def test_query__status(self):
        """List applications with 'pending' status.
 
           GET /api2/partners/teams/[team-slug]/applications
        """

        pending_applicants = [self.joiner.username,
                               'TestUser0']
 
        query = '?status=Pending'
        url_part = 'teams/{0}/applications/{1}'.format(self.team.slug, query)
        _, response = data_helpers.api_get_request(self, url_part) 
        applicants_objects =  response['objects']
        applicants_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                applicants_list.append(k)
        self.a_team_pg.open_page('teams/%s/applications/' % self.team.slug)
        self.assertEqual(pending_applicants, applicants_list)

    def test_query__time(self):
        """List applications created after a timestamp

           GET /api2/partners/teams/[team-slug]/applications
        """
        self.skipTest("Needs work")
        time_now = datetime.datetime.now()
        time.sleep(3)
        late_application = ApplicationFactory.create(
           team = self.team,
           user = UserFactory.create(username = 'late_joiner'),
           status = 0, 
           note = 'let me in, too',
           )
 

        query_time = int(time_now.strftime("%s")) 
        url_part = 'teams/{0}/applications/?after={1}'.format(
            self.team.slug, 
            query_time)

        _, response = data_helpers.api_get_request(self, url_part) 
        print response
        applicants_objects =  response['objects']
        applicants_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                applicants_list.append(k)
                print k
        self.a_team_pg.open_page('teams/%s/members/' % self.team.slug)
        self.assertEqual('late_joiner', applicants_list)


    def test_application__update(self):
        """Update an application status.

        PUT /api2/partners/teams/[team-slug]/application/[application-id]/

        """  
        data = { 'status': 'Approved' } 
        # TODO: Consider using get_resource_uri when constructing urls
        url_part = 'teams/{0}/applications/{1}/'.format(
            self.team.slug, 
            self.joiner_app.pk)

        _, response = data_helpers.put_api_request(self, url_part, data)
 
        #Query for approved applicants.
 
        query = '?status=Approved'
        url_part = 'teams/{0}/applications/{1}'.format(self.team.slug, query)
        status, response = data_helpers.api_get_request(self, url_part) 
        applicants_objects =  response['objects']
        approved_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                approved_list.append(k)
        self.a_team_pg.open_page('teams/%s/members/' % self.team.slug)

        self.assertIn(self.joiner.username, approved_list) 


    def test_application__delete(self):
        """Delete an application.

        DELETE /api2/partners/teams/[team-slug]/application/[application-id]/
        """
        url_part = 'teams/{0}/applications/{1}/'.format(
            self.team.slug, 
            self.joiner_app.pk)

        data_helpers.delete_api_request(self, url_part)
       
        #Get the list and verify application is deleted.
        url_part = 'teams/%s/applications/' % self.team.slug
        _, response = data_helpers.api_get_request(self, url_part) 
        applicants_objects =  response['objects']
        applicants_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                applicants_list.append(k)
        self.a_team_pg.open_page('teams/%s/applications/' % self.team.slug)
        self.assertNotIn(self.joiner.username, applicants_list)

