import time
import datetime
import itertools
import operator
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import ApplicationFactory
from apps.webdriver_testing.pages.site_pages.teams import ATeamPage 



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
        cls.data_utils.create_user_api_key(cls.user)
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

    def test_list__applications(self):
        """List all applications for a team.

        """
        url_part = 'teams/%s/applications/' % self.team.slug
        _, response = self.data_utils.api_get_request(self.user,  url_part) 
        applicants_objects =  response['objects']
        applicants_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                applicants_list.append(k)
        self.a_team_pg.open_page('teams/%s/applications/' % self.team.slug)
        self.assertEqual(sorted(self.joiners_list), sorted(applicants_list))


    def test_application__details(self):
        """List details of an application.

           GET /api2/partners/teams/[team-slug]/application/[application-id]/
        """
        expected_details = {'user': self.joiner.username, 
                            'status': 'Pending',}
 
        url_part = 'teams/{0}/applications/{1}'.format(self.team.slug, 
            self.joiner_app.pk)
        _, response = self.data_utils.api_get_request(self.user,  url_part) 
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
        _, response = self.data_utils.api_get_request(self.user,  url_part) 
        applicants_objects =  response['objects']
        applicants_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                applicants_list.append(k)
        self.a_team_pg.open_page('teams/%s/applications/' % self.team.slug)
        self.assertEqual(2, len(applicants_list))
        self.assertIn(self.joiner.username, applicants_list)

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

        _, response = self.data_utils.api_get_request(self.user,  url_part) 
        
        applicants_objects =  response['objects']
        applicants_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                applicants_list.append(k)
                
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

        _, response = self.data_utils.put_api_request(self.user,  url_part, data)
 
        #Query for approved applicants.
 
        query = '?status=Approved'
        url_part = 'teams/{0}/applications/{1}'.format(self.team.slug, query)
        status, response = self.data_utils.api_get_request(self.user,  url_part) 
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

        self.data_utils.delete_api_request(self.user,  url_part)
       
        #Get the list and verify application is deleted.
        url_part = 'teams/%s/applications/' % self.team.slug
        _, response = self.data_utils.api_get_request(self.user,  url_part) 
        applicants_objects =  response['objects']
        applicants_list = []
        for k, v in itertools.groupby(applicants_objects, 
            operator.itemgetter('user')):
                applicants_list.append(k)
        self.a_team_pg.open_page('teams/%s/applications/' % self.team.slug)
        self.assertNotIn(self.joiner.username, applicants_list)

