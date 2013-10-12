import time
import datetime
import itertools
import operator
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing import data_helpers
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import TeamMemberFactory
from webdriver_testing.data_factories import ApplicationFactory
from webdriver_testing.pages.site_pages.teams import ATeamPage 



class TestCaseApplications(WebdriverTestCase):
    """TestSuite for managing applications via the api.

    GET /api2/partners/teams/[team-slug]/applications
    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseApplications, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create(
            is_partner = True)
        
        cls.joiner = UserFactory.create(username='teamjoiner')

        #Create the application only team
        cls.team = TeamMemberFactory.create(
            team__name='my application-only team',
            team__slug='application-only',
            team__membership_policy=1,
            user = cls.user).team

        #Create a user who has a pending application
        cls.joiner_app = ApplicationFactory.create(
            team = cls.team,
            user = cls.joiner,
            status = 0, 
            note = 'let me in')

        # Create some additional applications the various status
        cls.joiners_list = []
        for x in range(0,5):
            team_joiner = ApplicationFactory.create(team = cls.team,
                                               user = UserFactory.create(),
                                               status = x, 
                                               note = 'let me in, too').user
            cls.joiners_list.append(team_joiner.username)
        cls.joiners_list.append(cls.joiner.username)

        cls.a_team_pg = ATeamPage(cls)

    def test_list_applications(self):
        """List all applications for a team.

        """
        url_part = 'teams/%s/applications/' % self.team.slug
        r = self.data_utils.make_request(self.user, 'get', url_part) 
        response = r.json
        self.logger.info(response)
        applicants_objects =  response['objects']
        applicants_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                applicants_list.append(k)
        self.a_team_pg.open_page('teams/%s/applications/' % self.team.slug)
        self.assertEqual(sorted(self.joiners_list), sorted(applicants_list))


    def test_application_details(self):
        """List details of an application.

           GET /api2/partners/teams/[team-slug]/application/[application-id]/
        """
        url_part = 'teams/%s/applications/' % self.team.slug
        r = self.data_utils.make_request(self.user, 'get', url_part) 
        response = r.json
        self.logger.info(response)

        expected_details = {'user': response['objects'][0]['user'], 
                            'status': response['objects'][0]['status']}
 
        url_part = response['objects'][0]['resource_uri']

        r = self.data_utils.make_request(self.user, 'get', url_part) 
        response = r.json
        self.logger.info(response)
        self.a_team_pg.open_page('teams/%s/applications/' % self.team.slug)

        for k, v in expected_details.iteritems():
            self.assertEqual(v, response[k])



    def test_query_status(self):
        """List applications with 'pending' status.
 
           GET /api2/partners/teams/[team-slug]/applications
        """

        pending_applicants = [self.joiner.username,
                               'TestUser0']
 
        query = '?status=Pending'
        url_part = 'teams/{0}/applications/{1}'.format(self.team.slug, query)
        r = self.data_utils.make_request(self.user, 'get', url_part)
        response = r.json
        applicants_objects =  response['objects']
        applicants_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                applicants_list.append(k)
        self.a_team_pg.open_page('teams/%s/applications/' % self.team.slug)
        self.assertEqual(2, len(applicants_list))
        self.assertIn(self.joiner.username, applicants_list)


    def test_application_update(self):
        """Update an application status.

        PUT /api2/partners/teams/[team-slug]/application/[application-id]/

        """  
        data = { 'status': 'Approved' } 
        url_part = 'teams/{0}/applications/{1}/'.format(
            self.team.slug, 
            self.joiner_app.pk)

        r = self.data_utils.make_request(self.user, 'put', url_part, **data)
        resp = r.json
        self.logger.info(resp)
 
        #Query for approved applicants.
 
        query = '?status=Approved'
        url_part = 'teams/{0}/applications/{1}'.format(self.team.slug, query)
        r = self.data_utils.make_request(self.user, 'get', url_part)
        response = r.json
        applicants_objects =  response['objects']
        approved_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                approved_list.append(k)
        self.a_team_pg.open_page('teams/%s/members/' % self.team.slug)

        self.assertIn(self.joiner.username, approved_list) 


    def test_application_delete(self):
        """Delete an application.

        DELETE /api2/partners/teams/[team-slug]/application/[application-id]/
        """
        url_part = 'teams/{0}/applications/{1}/'.format(
            self.team.slug, 
            self.joiner_app.pk)

        self.data_utils.make_request(self.user, 'delete', url_part)
       
        #Get the list and verify application is deleted.
        url_part = 'teams/%s/applications/' % self.team.slug
        r = self.data_utils.make_request(self.user, 'get', url_part)
        response = r.json

        applicants_objects =  response['objects']
        applicants_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                applicants_list.append(k)
        self.a_team_pg.open_page('teams/%s/applications/' % self.team.slug)
        self.assertNotIn(self.joiner.username, applicants_list)

