import os
import simplejson
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing import data_helpers

class TestCaseLanguagesFetch(WebdriverTestCase):
    """TestSuite for fetching the list of available languages via the api.
    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'TestUser', is_partner=True)
        self.data_utils = data_helpers.DataHelpers()
        self.data_utils.create_user_api_key(self.user)


    def test_fetch__languages(self):
        """Fetch the list of available languages.
        """
        url_part = 'languages/'
        status, response = self.data_utils.api_get_request(self.user, url_part) 
        self.assertEqual(200, status)
        langs = response['languages']
        lang_checks = {"hr": "Croatian", 
                      "zh-cn": "Chinese, Simplified",
                      "zh-hk": "Chinese, Traditional (Hong Kong)",
                      "swa": "Swahili",
                      "es-ar": "Spanish, Argentinian"}
        for lang_code, lang in lang_checks.iteritems():
            self.assertEqual(langs[lang_code], lang)

