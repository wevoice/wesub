#!/usr/bin/python
# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages.teams import videos_tab
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing import data_helpers
from apps.teams.models import TeamMember
from apps.testhelpers.views import _create_videos
import json
import time
from django.core import management

class TestCaseTeamVideos(WebdriverTestCase):
    """
    Main videos tab tests and Projects tab. 
    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.videos_tab = videos_tab.VideosTab(self)
        self.team_owner = UserFactory.create(username = 'team_owner')
        self.team = TeamMemberFactory.create(
            team__name='Video Test',
            team__slug='video-test',
            user = self.team_owner).team
        
        self.manager_user = TeamMemberFactory.create(
            team = self.team,
            user = UserFactory.create(username = 'TeamAdmin'),
            role = TeamMember.ROLE_ADMIN).user

        self.video_url = 'http://www.youtube.com/watch?v=WqJineyEszo'
        self.video_title = ('X Factor Audition - Stop Looking At My Mom Rap '
            '- Brian Bradley')
        self.videos_tab.log_in(self.manager_user.username, 'password')
        self.test_video = data_helpers.create_video_with_subs(self, 
            self.video_url)
        TeamVideoFactory.create(
            team=self.team, 
            video=self.test_video, 
            added_by=self.manager_user)


    def test_add__new(self):
        """Submit a new video for the team.

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.add_video(
            url = 'http://www.youtube.com/watch?v=MBfgEnIKQOY')
        self.videos_tab.open_videos_tab(self.team.slug)

        self.assertTrue(self.videos_tab.video_present(
            'Video Ranger Message (1950s) - Classic TV PSA'))


    def test_add__duplicate(self):
        """Submit a video that is already in amara.

        """
        dup_url = 'http://www.youtube.com/watch?v=WqJineyEszo'
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.add_video(dup_url)
        self.assertEqual(self.videos_tab.error_message(), 
            'This video already belongs to a team.')


    def test_add__team_duplicate(self):
        """Duplicate videos are not added again.

        """
        dup_url = 'http://www.youtube.com/watch?v=WqJineyEszo'

        #Create a second team.
        team2 = TeamMemberFactory.create(
            team__name = 'Second Test Team',
            team__slug = 'second-test-team',
            user = self.manager_user).team
        #Open the new team and try to submit the video 
        self.videos_tab.open_videos_tab(team2.slug)
        self.videos_tab.add_video(dup_url)
        self.assertEqual(self.videos_tab.error_message(), 
                         'This video already belongs to a team.')

    def test_search__title(self):
        """Team video search for title text.

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('X Factor')
        self.assertTrue(self.videos_tab.video_present(self.video_title))

    def test_search__subs(self):
        """Team video search for subtitle text.

        """
        management.call_command('rebuild_index', interactive=False)

        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('should be bold')
        self.assertTrue(self.videos_tab.video_present(self.video_title))

    def test_search__nonascii(self):
        """Team video search for non-ascii char strings.
 
        """
        #Search for: 日本語, by opening the url with query term.
        #Using url because webdriver can't type those characters.
        self.videos_tab.open_page('teams/' + self.team.slug + '/videos' +
            '/?q=日本語')
        self.assertTrue(self.videos_tab.video_present(self.video_title))
        #    "https://unisubs.sifterapp.com/issue/1498")

    def test_search__no_results(self):
        """Team video search returns no results.

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('TextThatShouldNOTExistOnTheVideoOrSubs')
        self.assertEqual(self.videos_tab.search_no_result(), 
            'Sorry, no videos here ...')


    def test_filter__languages(self):
        """Filter team videos by language.

        """
        videos = data_helpers.create_several_team_videos_with_subs(self, 
            self.team, 
            self.manager_user)
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.sub_lang_filter(language = 'Russian')
        self.assertTrue(self.videos_tab.video_present('qs1-not-transback'))

    def test_filter__no_incomplete(self):
        """Filter by language, incomplete subs are not in results. 

        """
        videos = data_helpers.create_several_team_videos_with_subs(self,
            self.team, 
            self.manager_user)

        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.sub_lang_filter(language = ['Portuguese'])
        self.assertEqual(self.videos_tab.search_no_result(), 
            'Sorry, no videos here ...')

    def test_sort__name_ztoa(self):
        """Sort videos on team page reverse alphabet.

        """
        videos = data_helpers.create_several_team_videos_with_subs(self, 
            self.team, 
            self.manager_user)
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.video_sort(sort_option = 'name, z-a')
        self.assertEqual(self.videos_tab.first_video_listed(), 
            'qs1-not-transback')

    def test_sort__time_oldest(self):
        """Sort videos on team page by oldest.

        """
        videos = data_helpers.create_several_team_videos_with_subs(self, 
            self.team, 
            self.manager_user)
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.video_sort(sort_option = 'time, oldest')
        self.assertEqual(self.videos_tab.first_video_listed(), 
            'X Factor Audition - Stop Looking At My Mom Rap - Brian Bradley')

    def test_remove(self):
        """Remove video from team, video stays on site.

        """
        video_title = ('X Factor Audition - Stop Looking At My Mom Rap '
                      '- Brian Bradley')
        videos = data_helpers.create_several_team_videos_with_subs(self, 
            self.team, 
            self.manager_user)
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search(video_title)
        self.videos_tab.remove_video(video=video_title)
        self.videos_tab.search('X Factor Audition')
        self.assertEqual(self.videos_tab.search_no_result(), 
            'Sorry, no videos here ...')
        self.videos_tab.open_videos_tab(self.team.slug)


    def test_edit__change_team(self):
        """Edit a video, changing it from 1 team to another.

        """
        video_title = 'qs1-not-transback'
        team2 = TeamMemberFactory.create(
            team__name='Team 2',
            team__slug='team-2',
            user = self.team_owner).team
        videos = data_helpers.create_several_team_videos_with_subs(self, 
            self.team, 
            self.manager_user)

        self.videos_tab.log_in(self.team_owner.username, 'password')
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search(video_title)
        self.videos_tab.edit_video(
            video=video_title,
            team = team2.name, 
            )
        self.videos_tab.open_videos_tab(team2.slug)
        self.assertTrue(self.videos_tab.video_present(video_title))



class TestCaseTeamProjectVideos(WebdriverTestCase):

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.videos_tab = videos_tab.VideosTab(self)
        self.team_owner = UserFactory.create(username = 'team_owner')
        self.team = TeamMemberFactory.create(
            team__name='Video Test', 
            team__slug='video-test', 
            user = self.team_owner).team
 
        self.manager_user = TeamMemberFactory.create(
            team=self.team,
            user=UserFactory.create(username= 'TeamAdmin'),
            role=TeamMember.ROLE_ADMIN).user

        self.project1 = TeamProjectFactory.create(
            team=self.team,
            name='team project one',
            workflow_enabled=True,)
        
        self.project2 = TeamProjectFactory.create(
            team=self.team,
            name='team project two',
            workflow_enabled=True)

        self.videos_tab.log_in(self.manager_user.username, 'password')
        print '***'
        print self.project2.slug
        print self.project2.name
        print self.team.slug


    def test_add__new(self):
        """Submit a new video for the team and assign to a project.

        """
        project_page = 'teams/{0}/videos/?project={1}'.format(self.team.slug, 
            self.project2.slug)
        self.videos_tab.open_page(project_page)
        self.videos_tab.add_video(
            url = 'http://www.youtube.com/watch?v=MBfgEnIKQOY',
            project = self.project2.name)
        self.videos_tab.open_page(project_page)

        #Verify the video is present on the videos tab for that project.
        self.assertTrue(self.videos_tab.video_present(
            'Video Ranger Message (1950s) - Classic TV PSA'))    

    def test_search__simple(self):
        """Peform a basic search on the project page for videos.

        """
        video_url = 'http://www.youtube.com/watch?v=WqJineyEszo'
        video_title = ('X Factor Audition - Stop Looking At My Mom Rap '
                      '- Brian Bradley')
        project_page = 'teams/{0}/videos/?project={1}'.format(self.team.slug, 
            self.project2.slug)

        self.videos_tab.log_in(self.manager_user.username, 'password')
        test_video = data_helpers.create_video_with_subs(self, video_url)
        TeamVideoFactory.create(
            team=self.team, 
            video=test_video, 
            added_by=self.manager_user, 
            project = self.project2)
        
        self.videos_tab.open_page(project_page)
        self.videos_tab.search('X Factor')
        self.assertTrue(self.videos_tab.video_present(video_title))

    def test_filter__languages(self):
        """Filter on the project page by language.

        """
        project_page = 'teams/{0}/videos/?project={1}'.format(self.team.slug, 
            self.project2.slug)

        data = json.load(open('apps/videos/fixtures/teams-list.json'))
        videos = _create_videos(data, [])
        for video in videos[::2]:
            TeamVideoFactory.create(
                team=self.team, 
                video=video, 
                added_by=self.manager_user,
                project = self.project2)
        self.videos_tab.open_page(project_page)
        self.videos_tab.sub_lang_filter(language = 'English')
        self.assertTrue(self.videos_tab.video_present('c'))

    def test_sort__most_subtitles(self):
        """Sort on the project page by most subtitles.

        """
        project_page = 'teams/{0}/videos/?project={1}'.format(self.team.slug, 
            self.project2.slug)

        print project_page

        data = json.load(open('apps/videos/fixtures/teams-list.json'))
        videos1 = _create_videos(data, [])
        data2 = json.load(open(
            'apps/webdriver_testing/check_teams/lots_of_subtitles.json'))
        videos2 = _create_videos(data2, [])
        videos = videos1 + videos2
        for video in videos:
            TeamVideoFactory.create(
                team=self.team, 
                video=video, 
                added_by=self.manager_user,
                project = self.project2)

        self.videos_tab.open_page(project_page)
        self.videos_tab.video_sort(sort_option = 'most subtitles')
        self.assertEqual(self.videos_tab.first_video_listed(), 
            'lots of translations')
        



    def test_remove(self):
        """Remove a video from the team project.

        """
        project_page = 'teams/{0}/videos/?project={1}'.format(self.team.slug, 
            self.project2.slug)

        self.videos_tab.open_page(project_page)
        self.videos_tab.add_video(
            url = 'http://www.youtube.com/watch?v=MBfgEnIKQOY',
            project = self.project2.name)
        self.videos_tab.open_page(project_page)
        self.videos_tab.remove_video(
            video = 'Video Ranger Message (1950s) - Classic TV PSA')
        self.videos_tab.search('Video Ranger')
        self.assertEqual(self.videos_tab.search_no_result(), 
            'Sorry, no videos here ...')
     

    def test_edit__change_project(self):
        """Move a video from project2 to project 1.

        """
        video_title = 'Video Ranger Message (1950s) - Classic TV PSA'
        project1_page = 'teams/{0}/videos/?project={1}'.format(self.team.slug, 
            self.project1.slug)
        project2_page = 'teams/{0}/videos/?project={1}'.format(self.team.slug, 
            self.project2.slug)
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.add_video(
            url = 'http://www.youtube.com/watch?v=MBfgEnIKQOY',
            project = self.project2.name)
        self.videos_tab.open_page(project2_page)

        self.videos_tab.edit_video(
            video=video_title,
            project = self.project1.name, 
            )
        self.videos_tab.open_page(project1_page)
        self.assertTrue(self.videos_tab.video_present(video_title))


