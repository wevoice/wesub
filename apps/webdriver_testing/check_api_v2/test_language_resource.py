import os
import simplejson
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.data_factories import UserFactory
from webdriver_testing import data_helpers

class TestCaseLanguagesFetch(WebdriverTestCase):
    """TestSuite for fetching the list of available languages via the api.
    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'TestUser', is_partner=True)
        self.data_utils = data_helpers.DataHelpers()
        


    def test_fetch__languages(self):
        """Fetch the list of available languages.
        """
        url_part = 'languages/'
        r = self.data_utils.make_request(self.user, 'get', url_part) 
        self.assertEqual(200, r.status_code)
        response = r.json
        langs = response['languages']
        lang_checks = {"hr": "Croatian", 
                      "zh-cn": "Chinese, Simplified",
                      "zh-hk": "Chinese, Traditional (Hong Kong)",
                      "swa": "Swahili",
                      "es-ar": "Spanish, Argentinian"}
        for lang_code, lang in lang_checks.iteritems():
            self.assertEqual(langs[lang_code], lang)

