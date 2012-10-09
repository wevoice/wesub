from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory

class WebdriverTestCaseSubtitlesUpload(WebdriverTestCase):
    """TestSuite for uploading subtitles via the api.
    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user')
        data_helpers.create_user_api_key(self, self.user)

    def api_create_user(self, **kwargs):
        """Create a user via the api.
           Creating Users:
           POST /api2/partners/users/
        """

        create_url = 'users'
        create_data = {'username': None,
                       'email': None, 
                       'password': 'password',
                       'first_name': None, 
                       'last_name': None, 
                       'create_login_token': None
                       }
        create_data.update(kwargs)
        status, response = data_helpers.post_api_request(self, 
            create_url, 
            create_data)
        print status
        return response 


 

    def test_create(self):
        new_user = {'username': 'newuser',
                    'email': 'newuser@example.com',
                    'first_name': 'New', 
                    'last_name': 'User_1',
                    }
        user_data = self.api_create_user(**new_user)
        users = user_data['objects']
        print '#######'
        for x in users:
            print x['username']
 


