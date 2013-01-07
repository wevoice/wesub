# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from django.core import management
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.pages.site_pages.teams import dashboard_tab
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import TeamContributorMemberFactory
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import UserLangFactory

from apps.teams.models import TeamMember

class TestCaseDashboard(WebdriverTestCase):
    """Verify team dashboard displays the videos and needs.

    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.dashboard_tab = dashboard_tab.DashboardTab(self)
        self.team_owner = UserFactory(username = 'team_owner')
        self.team = TeamMemberFactory.create(team__name='Dashboard Test',
                                             team__slug='dash-test',
                                             user = self.team_owner,
                                             ).team
        #Add some videos with various languages required.
        test_videos = [('jaws.mp4', 'fr', 'fr'),
                       ('Birds_short.oggtheora.ogg', None, None),
                       ('fireplace.mp4', 'en', 'en')
                       ]
        for vid in test_videos:
            video = data_helpers.create_video(self, 
                    'http://qa.pculture.org/amara_tests/%s' % vid[0])
            if vid[1] is not None:
                video_data = {'language_code': vid[1],
                              'video_language': vid[2],
                              'video': video.pk,
                              'draft': open('apps/videos/fixtures/test.srt'),
                              'is_complete': True
                              }
            
                data_helpers.upload_subs(self, video, video_data)
            TeamVideoFactory(video = video,
                             team = self.team,
                             added_by = self.team_owner)
        self.polly_glott = TeamContributorMemberFactory.create(
                team = self.team,
                user = UserFactory(username =  'PollyGlott')
                ).user

        self.mono_glot = TeamContributorMemberFactory.create(
                team = self.team,
                user = UserFactory(username =  'MonoGlot')
                ).user



    def test_members__generic_create_subs(self):
        """Dashboard displays generic create subs message when no orig lang specified.

        """
        #Create a user that's a member of a team with language preferences set.

        polly_speaks = ['en', 'cs', 'ru', 'ar']
        for lang in polly_speaks:
            UserLangFactory(user = self.polly_glott,
                            language = lang)



        #Login user and go to team dashboard page
        self.dashboard_tab.log_in(self.polly_glott.username, 'password')

        #Verify expected videos are displayed.
        self.dashboard_tab.open_team_page(self.team.slug)
        langs = self.dashboard_tab.languages_needed('Birds_short')
        self.assertEqual(['Create Subtitles'], langs)

    def test_members__no_languages(self):
        """Dashboard displays Create Subtitles when member has no langs specified.

        """
        #Create a user that's a member of a team with language preferences set.
        #Login user and go to team dashboard page
        self.dashboard_tab.log_in(self.mono_glot.username, 'password')

        #Verify expected videos are displayed.
        self.dashboard_tab.open_team_page(self.team.slug)
        langs = self.dashboard_tab.languages_needed('jaws')
        self.assertEqual(['Create Subtitles'], langs)



    def test_members__specific_langs_neded(self):
        """Dashboard displays videos matching members language preferences.     

        """
        #Create a user that's a member of a team with language preferences set.
        polly_speaks = ['en', 'cs', 'ru', 'ar']
        for lang in polly_speaks:
            UserLangFactory(user = self.polly_glott,
                            language = lang)



        #Login user and go to team dashboard page
        self.dashboard_tab.log_in(self.polly_glott.username, 'password')

        #Verify expected videos are displayed.
        expected_lang_list = ['Create English Subtitles', 
                              'Create Czech Subtitles',
                              'Create Russian Subtitles',
                              'Create Arabic Subtitles']
        self.dashboard_tab.open_team_page(self.team.slug)
        langs = self.dashboard_tab.languages_needed('fireplace.mp4')
        self.assertEqual(sorted(langs), sorted(expected_lang_list))
 






