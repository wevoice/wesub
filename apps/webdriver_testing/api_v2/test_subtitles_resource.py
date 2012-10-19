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

class WebdriverTestCaseSubtitlesUpload(WebdriverTestCase):
    """TestSuite for uploading subtitles via the api.
    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user')
        self.video_language_pg = video_language_page.VideoLanguagePage(self)
        data_helpers.create_user_api_key(self, self.user)
        self.test_video = data_helpers.create_video(self, 
            'http://www.example.com/upload_test.mp4')
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')


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
        #Upload the subtitles via api request
        upload_url = ('videos/{0}/languages/{1}/subtitles/'.format(
            self.test_video.video_id, test_lang_code))
        if test_format == 'ttml':
            sub_data = codecs.open(os.path.join(self.subs_data_dir, 
                'Timed_text.{0}.{1}'.format(test_lang_code, 'xml')),
                encoding = 'utf-8'
                )
        else:
            sub_data = codecs.open(os.path.join(self.subs_data_dir, 
                'Timed_text.{0}.{1}'.format(test_lang_code, test_format)),
                encoding = 'utf-8')

        upload_data = {'subtitles': sub_data.read(), 
                       'sub_format': test_format} 

        status, response = data_helpers.post_api_request(self, 
            upload_url, 
            upload_data)
        print '####'
        print status, response
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
        sub_data =  open(os.path.join( self.subs_data_dir, 'Untimed_text.srt'))
        upload_data = { 'subtitles': sub_data.read(), 'sub_format': 'txt' } 
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
        subtitle_language = self.api_upload_subs( test_format, 
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
        upload_data = { 'subtitles': sub_data.read(), 'sub_format': 'txt' } 
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
        editor_sub_list = subtitle_editor.subtitles_list()
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


class WebdriverTestCaseSubtitlesFetch(WebdriverTestCase):
    """TestSuite for fetching subtitle information via the api.
    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user')
        self.video_language_pg = video_language_page.VideoLanguagePage(self)
        data_helpers.create_user_api_key(self, self.user)
        self.test_video = data_helpers.create_video_with_subs(self)
        time.sleep(2)
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')
        self.video_language_pg.open_video_lang_page(self.test_video.video_id, 
            'en')

    def test_fetch__language(self):
        """Fetch the subtitle data for the specified language.

        If no version is specified, the latest public version will be 
        returned. 
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        subtitle_lang = self.test_video.subtitle_language(lang_code)
        print subtitle_lang

        url_part = 'videos/{0}/languages/{1}/'.format(video_id, lang_code)
        status, response = data_helpers.api_get_request(self, url_part) 
        print status, response
        self.assertNotEqual(404, status)

        self.assertFalse('Needs verification steps added here')


    def test_fetch__rst(self):
        """Fetch the subtitle data for the specfied lang and format.
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'rst'

        url_part = 'videos/{0}/languages/{1}/?format={2}'.format(
            video_id, lang_code, output_format)
        status, response = data_helpers.api_get_request( self, url_part ) 
        print status, response
        self.assertNotEqual(404, status)

        self.assertFalse('Needs verification steps added here')

    def test_fetch__srt(self):
        """Fetch the subtitle data for the specfied lang and format.
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'srt'

        url_part = 'videos/{0}/languages/{1}/?format={2}'.format(
            video_id, lang_code, output_format)
        status, response = data_helpers.api_get_request( self, url_part ) 
        print status, response
        self.assertNotEqual(404, status)

        self.assertFalse('Needs verification steps added here')

    def test_fetch__ttml(self):
        """Fetch the subtitle data for the specfied lang and format.
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'ttml'

        url_part = 'videos/{0}/languages/{1}/?format={2}'.format(
            video_id, lang_code, output_format)
        status, response = data_helpers.api_get_request(self, url_part) 
        print status, response
        self.assertNotEqual(404, status)
        self.assertFalse('Needs verification steps added here')

    def test_fetch__sbv(self):
        """Fetch the subtitle data for the specfied lang and format.
        
        GET /api2/partners/videos/[video-id]/languages/[lang-identifier]/
            subtitles/?format=srt
        """
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'sbv'

        url_part = 'videos/{0}/languages/{1}/?format={2}'.format(
            video_id, lang_code, output_format)
        status, response = data_helpers.api_get_request(self, url_part) 
        print status, response
        self.assertNotEqual(404, status)

        self.assertFalse('Needs verification steps added here')


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
        output_format = 'srt'
        data = {
            'language': lang_code,
            'video_language': lang_code,
            'video': self.test_video.pk,
            'draft': open('apps/webdriver_testing/subtitle_data/'
                          'Timed_text.en.srt'),
            'is_complete': True
            }
        data_helpers.create_video_with_subs(self, url, data)
        url_part = 'videos/{0}/languages/{1}/?format={2}&version={3}'.format(
            video_id, lang_code, output_format, version)
        status, response = data_helpers.api_get_request(self, url_part) 
        print status, response
        self.assertNotEqual(404, status)
        self.assertFalse('Needs verification steps added here')


    def test_fetch__moderated_public(self):
        """Return public subtitles of a moderated video.

        For videos under moderation only the latest published version is returned. 
        """
        # Setup data for the test
        video_id = self.test_video.video_id
        lang_code = 'en'
        output_format = 'srt'
        ## self.team_video already has a set of subtitles.
        ## Create a team with moderation settings
        my_team = TeamMemberFactory.create(
            team__name='Video Test',
            team__slug='video-test',
            user = self.user, 
            team__is_moderated = True,
            team__workflow_enabled = True,
            ).team
        ## Set the team workflow to peer review required.
        workflow = WorkflowFactory(team = my_team)
        workflow.review_allowed = 10
        workflow.save()
        ##  Add test_video to the team and create a transcription task.
        tv = TeamVideoFactory.create(
            team=my_team, 
            video=self.test_video, 
            added_by=self.user)
        subtitle_lang = self.test_video.subtitle_language(lang_code)
        task = TaskFactory(type = 10, team = my_team, team_video = tv, 
            language = lang_code)
        #FIXME Perform the task so there is a new set of complete subs that
        # are unreviewd.
        # Probably easiest to upload a draft, then review it.
       
        # Make a get request for the video language.  Version returned should 
        #be 1, the  original uploaded subtitles 
        url_part = 'videos/{0}/languages/{1}/?format={2}'.format(
            video_id, lang_code, output_format, 
            #version
            )
        status, response = data_helpers.api_get_request(self, url_part) 
        print status, response
        self.assertFalse('Needs verification steps added here. '
                         'Verify the returned version number and '
                         'the sub content.')


    def test_fetch__moderated_none(self):
        """Fetch nothing if moderated and no version has been accepted in review.
        """
        test_video = data_helpers.create_video(self)
        video_id = test_video.video_id
        lang_code = 'en'
        output_format = 'srt'
        #FIXME  Create a moderated team video with 1 published and 1 unpublished version.
        ## self.team_video already has a set of subtitles.
        ## Create a team with moderation settings
        my_team = TeamMemberFactory.create(
            team__name='Video Test',
            team__slug='video-test',
            user = self.user, 
            team__is_moderated = True,
            team__workflow_enabled = True,
            ).team
        ## Set the team workflow to peer review required.
        workflow = WorkflowFactory(team = my_team)
        workflow.review_allowed = 10
        workflow.save()
        ##  Add test_video to the team and create a transcription task.
        tv = TeamVideoFactory.create(team = my_team, 
            video = test_video,
            added_by = self.user)
        task = TaskFactory(type = 10, team = my_team, team_video = tv, 
            language = lang_code)
        #FIXME Perform the task so there is a new set of complete subs that are unreviewed.
       
        # Make a get request for the video language.  Version returned should
        # be None, since there are no approved subs.
        url_part = 'videos/{0}/languages/{1}/?format={2}'.format(
            video_id, lang_code, output_format) 
            
        status, response = data_helpers.api_get_request(self, url_part) 
        print status, response
        self.assertFalse('Needs verification steps added here. '
                         'Verify nothing is returned.')


