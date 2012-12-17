from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.site_pages.profiles import profile_account_page 


class TestCaseUserResource(WebdriverTestCase):
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

        create_url = 'users/'
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
        print user_data
        self.assertEqual('newuser', user_data['username'])

    def test_create__login_token(self):
        new_user = {'username': 'newuser',
                    'email': 'newuser@example.com',
                    'first_name': 'New', 
                    'last_name': 'User_1',
                    'create_login_token': True
                    }
        user_data = self.api_create_user(**new_user)
        api_key = user_data['api_key']
        login_url = user_data['auto_login_url']
        print api_key, login_url
        profile_account_pg = profile_account_page.ProfileAccountPage(self)
        profile_account_pg.open_page(login_url)
        profile_account_pg.open_account_tab()
        
        self.assertEqual(api_key, profile_account_pg.current_api_key())

        

    def test_create__invalid_email(self):
        new_user = {'username': 'newuser',
                    'email': 'stone-throwing-giants@yahoo',
                    'first_name': 'New', 
                    'last_name': 'User_1',
                    }
        user_data = self.api_create_user(**new_user)
        self.assertEqual('Enter a valid e-mail address.', user_data['email'][0])

    def test_create__invalid_username(self):
        new_user = {'username': 'new user',
                    'email': 'newuser@example.com',
                    'first_name': 'New', 
                    'last_name': 'User_1',
                    }
        user_data = self.api_create_user(**new_user)
        self.assertEqual('This value may contain only letters, numbers and @/./+/-/_ characters.', 
                         user_data['username'][0])

    
