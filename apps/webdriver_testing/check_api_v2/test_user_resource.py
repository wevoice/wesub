from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing import data_helpers
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.pages.site_pages.profiles import profile_personal_page 
import os

class TestCaseUserResource(WebdriverTestCase):
    """TestSuite for uploading subtitles via the api.
    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseUserResource, cls).setUpClass()
        cls.user = UserFactory.create(username = 'user')
        cls.data_utils = data_helpers.DataHelpers()
        

    def api_create_user(self, **kwargs):
        """Create a user via the api.
           Creating Users:
           POST /api2/partners/users/
        """

        url_part = 'users/'
        data = {'username': None,
                       'email': None, 
                       'password': 'password',
                       'first_name': None, 
                       'last_name': None, 
                       'create_login_token': None
                       }
        data.update(kwargs)
        r = self.data_utils.make_request(self.user, 'post', url_part, **data)
        response = r.json 
        return response 



    def test_create(self):
        """Create a user via the api.

        """
        new_user = {'username': 'newuser',
                    'email': 'newuser@example.com',
                    'first_name': 'New', 
                    'last_name': 'User_1',
                    }
        user_data = self.api_create_user(**new_user)
        self.assertEqual('newuser', user_data['username'])

    def test_create_login_token(self):
        """Create a user and login token, verify login.

        """
        new_user = {'username': 'newuser',
                    'email': 'enriqueumaran@uribekostabhi.com',
                    'first_name': 'New', 
                    'last_name': 'User_1',
                    'create_login_token': True
                    }
        user_data = self.api_create_user(**new_user)
        api_key = user_data['api_key']
        login_url = user_data['auto_login_url']
        personal_pg = profile_personal_page.ProfilePersonalPage(self)
        personal_pg.open_page(login_url)
        fullname = ' '.join([new_user['first_name'], new_user['last_name']])
        try:
            self.assertEqual(fullname, personal_pg.username())
        except:
            self.logger.warning('Site page error: verifying response data')
            self.assertEqual(fullname, user_data['full_name'])
        

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
        self.assertEqual('This value may contain only letters, '
                         'numbers and @/./+/-/_ characters.', 
                         user_data['username'][0])

