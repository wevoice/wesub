import os
import simplejson
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers

class WebdriverTestCaseLanguagesFetch(WebdriverTestCase):
    """TestSuite for fetching the list of available languages via the api.
    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')

    def test_fetch__languages(self):
        """Fetch the list of available languages.
        """
        url_part = 'languages/'
        status, response = data_helpers.api_get_request(self, url_part) 
        self.assertEqual(200, status)
        langs = response['languages']
        lang_checks = {"hr": "Croatian", 
                      "zh-cn": "Chinese, Simplified",
                      "zh-hk": "Chinese, Traditional (Hong Kong)",
                      "swa": "Swahili",
                      "es-ar": "Spanish, Argentinian"}
        for lang_code, lang in lang_checks.iteritems():
            self.assertEqual(langs[lang_code], lang)

