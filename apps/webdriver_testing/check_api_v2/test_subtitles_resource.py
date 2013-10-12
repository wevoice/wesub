import os
import time
import codecs
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages import video_language_page
from webdriver_testing.pages.site_pages import video_page
from webdriver_testing import data_helpers
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import TeamMemberFactory
from webdriver_testing.data_factories import TeamVideoFactory
from webdriver_testing.data_factories import WorkflowFactory
from webdriver_testing.data_factories import TaskFactory
from webdriver_testing.pages.editor_pages import subtitle_editor 
from webdriver_testing.pages.site_pages.teams import tasks_tab

class TestCaseSubtitlesUpload(WebdriverTestCase):
    """TestSuite for uploading subtitles via the api.

    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseSubtitlesUpload, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory.create()
        
      
        #Create some test data and set subtitle data dir
        cls.test_video = cls.data_utils.create_video()
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')

        cls.video_pg = video_page.VideoPage(cls)

        cls.video_language_pg = video_language_page.VideoLanguagePage(cls)
        cls.video_language_pg.set_skiphowto()



    def api_upload_subs(self, test_format, test_lang_code):
        """Create the language and upload the subtitles.

        Return the subtitle_language object of the test video for verification.
        
        Tests assume that we are using the Timed_text.<lang>.<format> files
        in the subtitle_data directory.
        """

        #Create the language for the test video
        create_url = ('videos/%s/languages/'  % self.test_video.video_id)
        create_data = {'language_code': test_lang_code,
                       'is_complete': True 
                      }
        r = self.data_utils.make_request(self.user, 'post', 
                                         create_url, **create_data)
        response = r.json
        self.assertEqual(201, r.status_code)
        #Create the url for uploading subtitles of give format and lang.
        upload_url = ('videos/{0}/languages/{1}/subtitles/'.format(
            self.test_video.video_id, test_lang_code))

        #Get the appropriate subtitle data file.
        if test_format == 'ttml':
            sub_data = codecs.open(os.path.join(self.subs_data_dir, 
                'Timed_text.{0}.{1}'.format(test_lang_code, 'xml')),
                encoding = 'utf-8'
                )
            test_format = 'dfxp'
        else:
            sub_data = codecs.open(os.path.join(self.subs_data_dir, 
                'Timed_text.{0}.{1}'.format(test_lang_code, test_format)),
                encoding = 'utf-8')

        #Create the url for uploading subtitles of give format and lang.
        upload_url = ('videos/{0}/languages/{1}/subtitles/'.format(
            self.test_video.video_id, test_lang_code))

        upload_data = {'subtitles': sub_data.read(), 
                       'sub_format': test_format} 

        #Upload the subtitles via api post request
        r = self.data_utils.make_request(self.user, 'post', 
                                         upload_url, **upload_data)
        response = r.json
        self.assertEqual(202, r.status_code)

        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            test_lang_code)
        subtitle_lang = self.test_video.subtitle_language(test_lang_code) 
        return subtitle_lang


    def test_upload_fork_dependents(self):
        video = self.data_utils.create_video()
        subs_dir = os.path.join(os.getcwd(), 'apps', 'webdriver_testing', 
                                'subtitle_data') 
        en_rev1 = os.path.join(subs_dir, 'Timed_text.en.srt')
        en_rev2 = os.path.join(subs_dir, 'Timed_text.rev2.en.srt')
        sv = os.path.join(subs_dir, 'Timed_text.sv.dfxp')
        complete = True
        draft_data = {'language_code': 'en',
                     'video': video.pk,
                     'primary_audio_language_code': 'en',
                     'draft': open(en_rev1),
                     'complete': int(complete),
                     'is_complete': complete
                    }
        self.data_utils.upload_subs(video, self.user, draft_data)

        draft_data = {'language_code': 'sv',
                     'video': video.pk,
                     'from_language_code': 'en',
                     'draft': open(sv),
                     'complete': int(complete),
                     'is_complete': complete,
                    }
        self.data_utils.upload_subs(video, self.user, draft_data)
        sl_sv = video.subtitle_language('sv')
        self.assertFalse(sl_sv.is_forked)


        #Upload a new set of subs via the api
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % video.video_id )
        upload_data = { #'title': 'updated via api',
                        'subtitles': open(en_rev2).read(), 
                        'sub_format': 'srt',
                        'is_complete': True, 
                        'complete': 1 } 
        r = self.data_utils.make_request(self.user, 'post', 
                                         upload_url, **upload_data)
        video.clear_language_cache()
        sl_sv = video.subtitle_language('sv')
        self.assertTrue(sl_sv.is_forked)

    def test_upload_display(self):
        """Upload subs via api and check display on language page. """
        #Create the language for the test video
        create_url = ( 'videos/%s/languages/'  % self.test_video.video_id  )
        create_data = { 'language_code': 'en', 'is_original': True }
        r = self.data_utils.make_request(self.user, 'post', 
                                         create_url, **create_data)

        #Upload the subtitles via api request
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )
        sub_data =  open(os.path.join(self.subs_data_dir, 'Untimed_text.srt'))
        upload_data = { 'subtitles': sub_data.read(), 'sub_format': 'srt' } 

        r = self.data_utils.make_request(self.user, 'post', 
                                         upload_url, **upload_data)


        self.video_language_pg.open_video_lang_page(
                self.test_video.video_id, 'en')
         
        verification_file = os.path.join(self.subs_data_dir,'Untimed_lines.txt')
        expected_list = [line.strip() for line in codecs.open(
                verification_file, encoding='utf-8')]
        displayed_list = self.video_language_pg.displayed_lines()
        #f = codecs.open('myworkfile', 'w', encoding="utf-8")
        #for line in displayed_list:
        #    f.write(line)

        #f.close()
        self.logger.info([(i,j) for i,j in zip(expected_list, displayed_list) if i!=j])
        self.assertEqual(expected_list, displayed_list) 

    def test_upload_resource_uri(self):
        """Check we are returing the correct resource uri fo subs.

        """
        #Create the language for the test video
        create_url = ( 'videos/%s/languages/'  % self.test_video.video_id  )
        create_data = { 'language_code': 'en', 'is_original': True }
        r = self.data_utils.make_request(self.user, 'post', 
                                         create_url, **create_data)

        #Upload the subtitles via api request
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )
        sub_data =  open(os.path.join(self.subs_data_dir, 'Untimed_text.srt'))
        upload_data = { 'subtitles': sub_data.read(), 'sub_format': 'srt' } 
        r = self.data_utils.make_request(self.user, 'post', 
                                         upload_url, **upload_data)
        response = r.json
        #Compare the returned uri
        expected_uri = ('/api2/partners/videos/%s/languages/en/subtitles/' 
                        % self.test_video.video_id)
        self.assertEqual(expected_uri, response['resource_uri'])


    def test_upload_srt(self):
        """Upload srt format subs via api.

        """
        test_lang_code = 'en'
        test_format = 'srt'
        subtitle_language = self.api_upload_subs(test_format, 
           test_lang_code)
        self.assertEqual(72, subtitle_language.get_subtitle_count())


    def test_upload_ssa(self):
        """Upload ssa format subs via api.

        """

        test_lang_code = 'hu'
        test_format = 'ssa'
        subtitle_language = self.api_upload_subs(test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            test_lang_code)

        self.assertEqual(243, subtitle_language.get_subtitle_count())


    def test_upload_sbv(self):
        """Upload sbv format subs via api.

        """

        test_lang_code = 'zh-cn'
        test_format = 'sbv'
        subtitle_language = self.api_upload_subs(test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            test_lang_code)

        self.assertEqual(243, subtitle_language.get_subtitle_count())

    def test_upload_ttml(self):
        """Upload xml (ttml) format subs via api.

        """

        test_lang_code = 'ar'
        test_format = 'ttml'
        subtitle_language = self.api_upload_subs(test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            test_lang_code)

        self.assertEqual(243, subtitle_language.get_subtitle_count())

    def test_upload_dfxp(self):
        """Upload dfxp format subs via api.

        """

        test_lang_code = 'sv'
        test_format = 'dfxp'
        subtitle_language = self.api_upload_subs(test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            test_lang_code)
        self.assertEqual(72, subtitle_language.get_subtitle_count())

    def test_upload_edit(self):
        """Subs uploaded via api are editable in the subtitle editor.

        """
        #Create the language for the test video
        create_url = ('videos/%s/languages/'  % self.test_video.video_id)
        create_data = { 'language_code': 'en', 'is_original': True }
        r = self.data_utils.make_request(self.user, 'post', 
                                         create_url, **create_data)

        #Upload the subtitles via api request
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )
        sub_data =  open(os.path.join(self.subs_data_dir, 'Untimed_text.srt'))
        upload_data = { 'subtitles': sub_data.read(), 'sub_format': 'srt' } 
        r = self.data_utils.make_request(self.user, 'post', 
                                         upload_url, **upload_data)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            'en')
        #Open the language page for the video and click Edit Subtitles 
        verification_file = os.path.join(self.subs_data_dir, 
            'Untimed_lines.txt')
        expected_list = [line.strip() for line in codecs.open(
            verification_file, encoding='utf-8')]
        self.video_language_pg.log_in(self.user.username, 'password')
        self.video_language_pg.set_skiphowto()
        self.video_language_pg.open_video_lang_page(
            self.test_video.video_id, 'en')
        self.video_language_pg.edit_subtitles()
        sub_editor = subtitle_editor.SubtitleEditor(self)
        editor_sub_list = sub_editor.subtitles_list()

        #Verify uploaded subs are displayed and editable
        self.assertLess(0, len(editor_sub_list))
        typed_subs = sub_editor.edit_subs()
        sub_editor.save_and_exit()
        self.video_language_pg.open_video_lang_page(
            self.test_video.video_id, 'en')
        displayed_list = self.video_language_pg.displayed_lines()

        #Verify the edited text is in the sub list
        self.assertIn("I'd like to be", displayed_list[0])

        #Verify the origal unedited text is still present in the sub list.
        self.assertEqual(expected_list[-1], displayed_list[-1])


class TestCaseSubtitlesFetch(WebdriverTestCase):
    """TestSuite for fetching subtitle information via the api.

    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseSubtitlesFetch, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.user = UserFactory()
        
 
        #Create the test video and path to the sub data directory.
        cls.test_video = cls.data_utils.create_video_with_subs(cls.user)
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')

        #Open the video language page for the test video.

    def test_fetch_language(self):
        """Fetch the subtitle data for the specified language.

        If no version is specified, the latest public version will be 
        returned. 
        """
        video_id = self.test_video.video_id
        lang_code = 'en'

        #Set the url for fetching.
        url_part = 'videos/{0}/languages/{1}'.format(
            video_id, lang_code)

        #Verify we get matching lang code in the response data.
        r = self.data_utils.make_request(self.user, 'get', url_part)
        response = r.json
        self.assertEqual(lang_code, response['language_code'])
        

    def test_fetch_srt(self):
        """Fetch the subtitle data in srt format.
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        lang = self.test_video.subtitle_language(language_code=lang_code)
        self.assertTrue(lang is not None)
        output_format = 'srt'

        url_part = 'videos/{0}/languages/{1}/subtitles/?format={2}'.format(
            video_id, lang_code, output_format)

        r = self.data_utils.make_request(self.user, 'get', url_part)
        response = r.content

        self.assertTrue(response is not None)

        #Verify returned subs are valid - by uploading back to system
        url_part = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )

        data = { 'subtitles': response, 'sub_format': 'srt' } 
        r = self.data_utils.make_request(self.user, 'post', url_part, **data)
        response = r.json
        self.assertEqual(2, response['version_number'])


    def test_fetch_dfxp(self):
        """Fetch the subtitle data in dfxp format.
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'dfxp'
        url_part = 'videos/{0}/languages/{1}/subtitles/?format={2}'.format(
            video_id, lang_code, output_format)
        r = self.data_utils.make_request(self.user, 'get', url_part)
        self.assertNotEqual(404, r.status_code)
        response = r.content
        
        #Verify returned subs are valid - by uploading back to system
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )

        upload_data = { 'subtitles': response, 'sub_format': 'dfxp' } 
        r = self.data_utils.make_request(self.user, 'post',
                                         upload_url, **upload_data)
        response = r.json
        self.assertEqual(2, response['version_number'])

    def test_fetch_ssa(self):
        """Fetch the subtitle data in ssa format.
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'ssa'

        url_part = 'videos/{0}/languages/{1}/subtitles/?format={2}'.format(
            video_id, lang_code, output_format)
        r = self.data_utils.make_request(self.user, 'get', url_part)
        self.assertNotEqual(404, r.status_code)
        response = r.content

        #Verify returned subs are valid - by uploading back to system
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )

        upload_data = { 'subtitles': response, 'sub_format': 'ssa' } 
        r = self.data_utils.make_request(self.user, 'post', 
                                         upload_url, **upload_data)
        response = r.json
        self.assertEqual(2, response['version_number'])

    def test_fetch_sbv(self):
        """Fetch the subtitle data in sbv format'
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'sbv'

        url_part = 'videos/{0}/languages/{1}/subtitles/?format={2}'.format(
            video_id, lang_code, output_format)
        r = self.data_utils.make_request(self.user, 'get', url_part)
        self.assertNotEqual(404, r.status_code)
        response = r.content

        #Verify returned subs are valid - by uploading back to system
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )

        upload_data = { 'subtitles': response, 'sub_format': 'sbv' } 
        r = self.data_utils.make_request(self.user, 'post', 
                                         upload_url, **upload_data)
        response = r.json
        self.assertEqual(2, response['version_number'])


    def test_fetch_txt(self):
        """Fetch the subtitle data in txt format.
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'txt'

        url_part = 'videos/{0}/languages/{1}/subtitles/?format={2}'.format(
            video_id, lang_code, output_format)
        r = self.data_utils.make_request(self.user, 'get', url_part)
        self.assertNotEqual(404, r.status_code)
        response = r.content

        #Verify returned subs are valid - by uploading back to system
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )

        upload_data = { 'subtitles': response, 'sub_format': 'txt' } 
        r = self.data_utils.make_request(self.user, 'post', 
                                         upload_url, **upload_data)
        response = r.json
        self.assertEqual(2, response['version_number'])


    def test_fetch_version(self):
        """Fetch a specific version of a video subtitles.

        Versions are listed in the VideoLanguageResouce request.
        GET /api2/partners/videos/asfssd/languages/en/subtitles/
            ?version=<version_no>


        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        version = 2
        self.data_utils.add_subs(video=self.test_video)
        url_part = ('videos/{0}/languages/{1}/subtitles/'
                    '?version={2}'.format(video_id, 
					  lang_code, 
                                          version))
        r = self.data_utils.make_request(self.user, 'get', url_part)
        resp = r.json
        
        self.assertNotEqual(404, r.status_code)
        self.assertIs(2, resp['version_number'])

