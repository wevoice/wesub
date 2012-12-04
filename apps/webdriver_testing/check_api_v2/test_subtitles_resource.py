import os
import time
import codecs
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import video_language_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import WorkflowFactory
from apps.webdriver_testing.data_factories import TaskFactory
from apps.webdriver_testing.editor_pages import subtitle_editor 
from apps.webdriver_testing.site_pages.teams import tasks_tab
class TestCaseSubtitlesUpload(WebdriverTestCase):
    """TestSuite for uploading subtitles via the api.

    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)

        #Create the test user and api key
        self.user = UserFactory.create(username = 'user')
        data_helpers.create_user_api_key(self, self.user)
      
        #Create some test data and set subtitle data dir
        self.test_video = data_helpers.create_video(self, 
            'http://www.example.com/upload_test.mp4')
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')

        self.video_language_pg = video_language_page.VideoLanguagePage(self)



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
        status, response = data_helpers.post_api_request(self, 
            create_url, 
            create_data)
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
        status, response = data_helpers.post_api_request(self, 
            upload_url, 
            upload_data)
        self.assertNotEqual(500, status)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            test_lang_code)
        subtitle_lang = self.test_video.subtitle_language(test_lang_code) 
        return subtitle_lang


    def test_upload__display(self):
        #Create the language for the test video
        create_url = ( 'videos/%s/languages/'  % self.test_video.video_id  )
        create_data = { 'language_code': 'en', 'is_original': True }
        status, response = data_helpers.post_api_request(self, 
            create_url, 
            create_data)

        #Upload the subtitles via api request
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )
        sub_data =  open(os.path.join(self.subs_data_dir, 'Untimed_text.srt'))
        upload_data = { 'subtitles': sub_data.read(), 'sub_format': 'srt' } 
        status, response = data_helpers.post_api_request( self, 
            upload_url, 
            upload_data )
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            'en')
        verification_file = os.path.join(self.subs_data_dir,'Untimed_lines.txt')
        expected_list = [line.strip() for line in codecs.open(
        verification_file, encoding='utf-8')]
        displayed_list = self.video_language_pg.displayed_lines()
        self.assertEqual(expected_list, displayed_list) 

    def test_upload__resource_uri(self):
        #Create the language for the test video
        create_url = ( 'videos/%s/languages/'  % self.test_video.video_id  )
        create_data = { 'language_code': 'en', 'is_original': True }
        status, response = data_helpers.post_api_request(self, 
            create_url, 
            create_data)

        #Upload the subtitles via api request
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )
        sub_data =  open(os.path.join(self.subs_data_dir, 'Untimed_text.srt'))
        upload_data = { 'subtitles': sub_data.read(), 'sub_format': 'srt' } 
        status, response = data_helpers.post_api_request( self, 
            upload_url, 
            upload_data )
        print response
        #Compare the returned uri
        expected_uri = '/api2/partners/videos/%s/languages/en/subtitles/' % self.test_video.video_id
        self.assertEqual(expected_uri, response['resource_uri'])


    def test_upload__srt(self):
        test_lang_code = 'en'
        test_format = 'srt'
        subtitle_language = self.api_upload_subs(test_format, 
           test_lang_code)
        self.assertEqual(72, subtitle_language.get_subtitle_count())


    def test_upload__ssa(self):
        test_lang_code = 'hu'
        test_format = 'ssa'
        subtitle_language = self.api_upload_subs(test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            test_lang_code)

        self.assertEqual(243, subtitle_language.get_subtitle_count())


    def test_upload__sbv(self):
        test_lang_code = 'zh-cn'
        test_format = 'sbv'
        subtitle_language = self.api_upload_subs(test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            test_lang_code)

        self.assertEqual(243, subtitle_language.get_subtitle_count())

    def test_upload__ttml(self):
        test_lang_code = 'ar'
        test_format = 'ttml'
        subtitle_language = self.api_upload_subs(test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            test_lang_code)

        self.assertEqual(243, subtitle_language.get_subtitle_count())

    def test_upload__dfxp(self):
        test_lang_code = 'sv'
        test_format = 'dfxp'
        subtitle_language = self.api_upload_subs(test_format, 
           test_lang_code)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            test_lang_code)
        self.assertEqual(72, subtitle_language.get_subtitle_count())

    def test_upload__edit(self):
        """Subs uploaded via api are editable in the subtitle editor.

        """
        #Create the language for the test video
        create_url = ('videos/%s/languages/'  % self.test_video.video_id)
        create_data = { 'language_code': 'en', 'is_original': True }
        status, response = data_helpers.post_api_request(self, 
            create_url, 
            create_data)

        #Upload the subtitles via api request
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )
        sub_data =  open(os.path.join(self.subs_data_dir, 'Untimed_text.srt'))
        upload_data = { 'subtitles': sub_data.read(), 'sub_format': 'srt' } 
        status, response = data_helpers.post_api_request(self, 
            upload_url, 
            upload_data)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            'en')
        #Open the language page for the video and click Edit Subtitles 
        verification_file = os.path.join(self.subs_data_dir, 
            'Untimed_lines.txt')
        expected_list = [line.strip() for line in codecs.open(
            verification_file, encoding='utf-8')]

        self.video_language_pg.open_video_lang_page(
            self.test_video.video_id, 'en')
        self.video_language_pg.edit_subtitles()
        sub_editor = subtitle_editor.SubtitleEditor(self)
        sub_editor.continue_past_help()
        editor_sub_list = sub_editor.subtitles_list()

        #Verify uploaded subs are displayed in the Editor
        self.assertEqual(expected_list, editor_sub_list)
        typed_subs = sub_editor.type_subs()
        sub_editor.save_and_exit()
        self.video_language_pg.open_video_lang_page(
            self.test_video.video_id, 'en')
        displayed_list = self.video_language_pg.displayed_lines()

        #Verify the edited text is in the sub list
        self.assertIn("I'd like to be under the sea", displayed_list)

        #Verify the origal unedited text is still present in the sub list.
        self.assertIn(expected_list[9], displayed_list)


class TestCaseSubtitlesFetch(WebdriverTestCase):
    """TestSuite for fetching subtitle information via the api.

    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)

        #Create the user and get the api key.
        self.user = UserFactory.create(username = 'user')
        data_helpers.create_user_api_key(self, self.user)

        #Create teh test video and path to the sub data directory.
        self.test_video = data_helpers.create_video_with_subs(self)
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')

        #Open the video language page for the test video.
        self.video_language_pg = video_language_page.VideoLanguagePage(self)
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            'en')

    def test_fetch__language(self):
        """Fetch the subtitle data for the specified language.

        If no version is specified, the latest public version will be 
        returned. 
        """
        video_id = self.test_video.video_id
        lang_code = 'en'

        #Set the url for fetching.
        url_part = 'videos/{0}/languages/{1}/'.format(
            video_id, lang_code)

        #Verify we get matching lang code in the response data.
        status, response = data_helpers.api_get_request(self, url_part)
        self.assertEqual(lang_code, response['language_code'])
        

    def test_fetch__srt(self):
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

        status, response = data_helpers.api_get_request(self, url_part, 
            output_type = 'content') 

        self.assertTrue(response is not None)

        #Verify returned subs are valid - by uploading back to system
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )

        upload_data = { 'subtitles': response, 'sub_format': 'srt' } 
        status, response = data_helpers.post_api_request(self, 
            upload_url, 
            upload_data)

        #Open the language page on the site.        
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            'en')

        self.assertEqual(2, response['version_number'])


    def test_fetch__dfxp(self):
        """Fetch the subtitle data in dfxp format.
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'dfxp'

        url_part = 'videos/{0}/languages/{1}/subtitles/?format={2}'.format(
            video_id, lang_code, output_format)
        status, response = data_helpers.api_get_request(self, url_part, 
            output_type = 'content')  
        self.assertNotEqual(404, status)
        
        #Verify returned subs are valid - by uploading back to system
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )

        upload_data = { 'subtitles': response, 'sub_format': 'dfxp' } 
        status, response = data_helpers.post_api_request(self, 
            upload_url, 
            upload_data)

        #Open the language page on the site.        
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            'en')

        self.assertEqual(2, response['version_number'])

    def test_fetch__ssa(self):
        """Fetch the subtitle data in ssa format.
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'ssa'

        url_part = 'videos/{0}/languages/{1}/subtitles/?format={2}'.format(
            video_id, lang_code, output_format)
        status, response = data_helpers.api_get_request(self, url_part, 
            output_type = 'content') 

        self.assertNotEqual(404, status)

        #Verify returned subs are valid - by uploading back to system
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )

        upload_data = { 'subtitles': response, 'sub_format': 'ssa' } 
        status, response = data_helpers.post_api_request(self, 
            upload_url, 
            upload_data)

        #Open the language page on the site.        
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            'en')

        self.assertEqual(2, response['version_number'])

    def test_fetch__sbv(self):
        """Fetch the subtitle data in sbv format'
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'sbv'

        url_part = 'videos/{0}/languages/{1}/subtitles/?format={2}'.format(
            video_id, lang_code, output_format)
        status, response = data_helpers.api_get_request(self, url_part, 
            output_type = 'content') 

        self.assertNotEqual(404, status)

        #Verify returned subs are valid - by uploading back to system
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )

        upload_data = { 'subtitles': response, 'sub_format': 'sbv' } 
        status, response = data_helpers.post_api_request(self, 
            upload_url, 
            upload_data)

        #Open the language page on the site.        
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            'en')

        self.assertEqual(2, response['version_number'])


    def test_fetch__txt(self):
        """Fetch the subtitle data in txt format.
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'txt'

        url_part = 'videos/{0}/languages/{1}/subtitles/?format={2}'.format(
            video_id, lang_code, output_format)
        status, response = data_helpers.api_get_request(self, url_part, 
            output_type = 'content') 

        self.assertNotEqual(404, status)

        #Verify returned subs are valid - by uploading back to system
        upload_url = ( 'videos/%s/languages/en/subtitles/' 
            % self.test_video.video_id )

        upload_data = { 'subtitles': response, 'sub_format': 'txt' } 
        status, response = data_helpers.post_api_request(self, 
            upload_url, 
            upload_data)
        self.assertEqual(2, response['version_number'])


    def test_fetch__version(self):
        """Fetch a specific version of a video subtitles.

        Versions are listed in the VideoLanguageResouce request.
        GET /api2/partners/videos/asfssd/languages/en/subtitles/
            ?version=<version_no>


        """
        url = 'http://www.youtube.com/watch?v=WqJineyEszo' 
        video_id = self.test_video.video_id
        lang_code = 'en'
        version = 2
        output_format = 'json'
        data = {
            'language_code': lang_code,
            'video_language': lang_code,
            'video': self.test_video.pk,
            'draft': open('apps/webdriver_testing/subtitle_data/'
                          'Timed_text.en.srt'),
            'is_complete': True
            }
        data_helpers.create_video_with_subs(self, url, data)
        url_part = ('videos/{0}/languages/{1}/subtitles/?format={2}'
                    '&version={3}'.format(video_id, 
					  lang_code, 
                                          output_format, 
                                          version))
        status, response = data_helpers.api_get_request(self, url_part) 
        self.assertNotEqual(404, status)
        self.assertIs(2, response['version_number'])



class TestCaseModeratedSubtitlesUpload(WebdriverTestCase):
    """TestSuite for uploading moderated subtitles via the api.

    """

    def setUp(self):
        WebdriverTestCase.setUp(self)

        #Create the test user and api key
        self.user = UserFactory.create(username = 'user')
        data_helpers.create_user_api_key(self, self.user)
      
        #Create some test data and set subtitle data dir
        self.test_video = data_helpers.create_video(self, 
            'http://www.example.com/upload_test.mp4')
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')


        # self.team_video already has a set of subtitles.
        # Create a team with moderation settings
        self.my_team = TeamMemberFactory.create(
            team__name='Video Test',
            team__slug='video-test',
            user = self.user, 
            team__is_moderated = True,
            team__workflow_enabled = True,
            ).team
        
        # Set the team workflow to peer review required.
        workflow = WorkflowFactory(team = self.my_team)
        workflow.review_allowed = 10
        workflow.save()

        #  Add test_video to the team and create a transcription task.
        self.lang_code = 'en'
        self.tv = TeamVideoFactory.create(
            team=self.my_team, 
            video=self.test_video, 
            added_by=self.user)
        subtitle_lang = self.test_video.subtitle_language(self.lang_code)
        task = TaskFactory(type = 10, team = self.my_team, team_video = self.tv, 
            language = self.lang_code)

        self.video_language_pg = video_language_page.VideoLanguagePage(self)
        self.tasks_pg = tasks_tab.TasksTab(self)




    def test_fetch__moderated_public(self):
        """Return public subtitles of a moderated video.

        For videos under moderation only the latest published version is returned. 
        """
        #FIXME Perform the task so there is a new set of complete subs that
        # are unreviewed.
        # Probably easiest to upload a draft, then review it.
       
        # Make a get request for the video language.  Version returned should 
        #be 1, the  original uploaded subtitles 

        self.tasks_pg.log_in(self.user.username, 'password')
        self.tasks_pg.open_tasks_tab(self.my_team.slug)
        self.assertFalse('Tasks are not done yet')
        #url_part = 'videos/{0}/languages/{1}/?format={2}'.format(
        #    self.test_video.video_id, self.lang_code, output_format, 
        #    #version
        #    )
        #status, response = data_helpers.api_get_request(self, url_part) 
        #print status, response
        #self.assertFalse('Needs verification steps added here. '
        #                 'Verify the returned version number and '
        #                 'the sub content.')


    def test_fetch__moderated_none(self):
        """Fetch nothing if moderated and no version has been accepted in review.
        """
        self.tasks_pg.log_in(self.user.username, 'password')
        self.tasks_pg.open_tasks_tab(self.my_team.slug)
        self.assertFalse('Tasks are not done yet')

        #FIXME Perform the task so there is a new set of complete subs that are unreviewed.
       
        # Make a get request for the video language.  Version returned should
        # be None, since there are no approved subs.
        url_part = 'videos/{0}/languages/{1}/?format={2}'.format(
            self.test_video.video_id, lang_code, output_format) 
            
        status, response = data_helpers.api_get_request(self, url_part) 
        print status, response
        self.assertFalse('Needs verification steps added here. '
                         'Verify nothing is returned.')


