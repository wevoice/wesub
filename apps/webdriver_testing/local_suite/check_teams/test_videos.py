#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import time
import os
import filecmp
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages.teams import videos_tab
from apps.webdriver_testing.site_pages import watch_page
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamContributorMemberFactory
from apps.webdriver_testing.data_factories import TeamAdminMemberFactory
from apps.webdriver_testing.data_factories import TeamProjectFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import VideoFactory
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamLangPrefFactory
from apps.webdriver_testing.data_factories import WorkflowFactory
from apps.webdriver_testing import data_helpers
from apps.testhelpers.views import _create_videos
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
        
        self.manager_user = TeamAdminMemberFactory(
            team = self.team,
            user = UserFactory(username = 'TeamAdmin')).user

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

    def test_search__updated_title(self):
        """Team video search for title text after it has been updated.

        """
        #Create user and key for api update.
        self.user = TeamAdminMemberFactory(
            team = self.team,
            user = UserFactory(username = 'user')).user

        data_helpers.create_user_api_key(self, self.user)

        #Update the video title and description (via api)
        url_part = 'videos/%s' % self.test_video.video_id
        print url_part
        new_data = {'title': 'Please do not glance at my mother.',
                    'description': 'Title update for grammar and politeness.'
                   }
        data_helpers.put_api_request(self, url_part, new_data)

        #Update the solr index
        management.call_command('rebuild_index', interactive=False)

        #Open team videos page and search for updated title text.
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('mother')
        self.assertTrue(self.videos_tab.video_present(new_data['title']))


    def test_search__updated_description(self):
        """Team video search for description text after it has been updated.

        """
        #Create user and key for api update.
        self.user = TeamAdminMemberFactory(
            team = self.team,
            user = UserFactory(username = 'user')).user
        data_helpers.create_user_api_key(self, self.user)

        #Update the video title and description (via api)
        url_part = 'videos/%s' % self.test_video.video_id
        print url_part
        new_data = {'title': 'Please do not glance at my mother.',
                    'description': 'Title update for grammar and politeness.'
                   }
        data_helpers.put_api_request(self, url_part, new_data)

        #Update the solr index
        management.call_command('rebuild_index', interactive=False)

        #Open team videos page and search for updated title text.
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('grammar and politeness')
        self.assertTrue(self.videos_tab.video_present(new_data['title']))



    def test_search__subs(self):
        """Team video search for subtitle text.

        """
        management.call_command('update_index', interactive=False)

        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('show this text')
        self.assertTrue(self.videos_tab.video_present(self.video_title))

    def test_search__nonascii(self):
        """Team video search for non-ascii char strings.
 
        """
        #Search for: 日本語, by opening entering the text via javascript
        #because webdriver can't type those characters.
        self.videos_tab.open_videos_tab(self.team.slug)
        self.browser.execute_script("document.getElementsByName('q')[1].value='日本語'")
        self.assertTrue(self.videos_tab.video_present(self.video_title))

    def test_search__no_results(self):
        """Team video search returns no results.

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('TextThatShouldNOTExistOnTheVideoOrSubs')
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())


    def test_filter__clear(self):
        """Clear filters.

        """
        videos = data_helpers.create_several_team_videos_with_subs(self, 
            self.team, 
            self.manager_user)
        self.videos_tab.open_videos_tab(self.team.slug)

        #Filter so that no videos are present
        self.videos_tab.sub_lang_filter(language = 'French')
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())

        #Clear filters and verify videos are displayed.
        self.videos_tab.clear_filters()
        self.assertTrue(self.videos_tab.video_present('qs1-not-transback'))


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
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())


    def test_sort__name_ztoa(self):
        """Sort videos on team page reverse alphabet.

        """
        videos = data_helpers.create_several_team_videos_with_subs(self, 
            self.team, 
            self.manager_user)
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.video_sort(sort_option = 'name, z-a')
        self.videos_tab.videos_displayed()
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
        self.videos_tab.videos_displayed()
        self.assertEqual(self.videos_tab.first_video_listed(), 
            'X Factor Audition - Stop Looking At My Mom Rap - Brian Bradley')

    def test_remove(self):
        """Remove video from team, video stays on site.

        """
        videos = data_helpers.create_several_team_videos_with_subs(self, 
            self.team, 
            self.manager_user)
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search(self.video_title)
        self.videos_tab.remove_video(video=self.video_title)
        self.videos_tab.search('X Factor Audition')
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())

        self.videos_tab.open_videos_tab(self.team.slug)

    def test_remove__site(self):
        """Remove video from team and site, total destruction!

        Must be the team owner to get the team vs. site dialog.
        """

        self.videos_tab.log_in(self.team_owner.username, 'password')

        #Create a team video for removal.
        tv = TeamVideoFactory.create(
            team=self.team, 
            added_by=self.manager_user).video

        #Search for the video in team videos and remove it.
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search(tv.title)
        self.videos_tab.remove_video(video = tv.title, 
            removal_action='total-destruction')

        #Verify video no longer in teams
        self.videos_tab.search(tv.title)
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())

        #Verify video no longer on site
        watch_pg = watch_page.WatchPage(self)
        watch_pg.open_watch_page()
        results_pg = watch_pg.basic_search(tv.title)
        self.assertTrue(results_pg.search_has_no_results())


    def test_remove__team_only(self):
        """Remove video from team but NOT site.

        Must be the team owner to get the team vs. site dialog.
        """

        self.videos_tab.log_in(self.team_owner.username, 'password')

        #Create a team video for removal.
        tv = TeamVideoFactory.create(
            team=self.team, 
            added_by=self.manager_user).video

        #Search for the video in team videos and remove it.
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search(tv.title)
        self.videos_tab.remove_video(video = tv.title, 
            removal_action='team-removal')

        #Verify video no longer in teams
        self.videos_tab.search(tv.title)
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())

        #Verify video is present on the site
        watch_pg = watch_page.WatchPage(self)
        watch_pg.open_watch_page()
        results_pg = watch_pg.basic_search(tv.title)
        self.assertTrue(results_pg.search_has_results())


    def test_edit__thumbnail(self):
        """Upload a new thumbnail.

        """
        video_title = 'qs1-not-transback' 
        videos = data_helpers.create_several_team_videos_with_subs(self, 
            self.team, 
            self.manager_user)


        self.videos_tab.log_in(self.team_owner.username, 'password')
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search(video_title)
        new_thumb = os.path.join(os.getcwd(), 'media', 'images', 'seal.png')
        self.videos_tab.edit_video(video=video_title, thumb=new_thumb)
        site_thumb = os.path.join(os.getcwd(), 
                                     'user-data', 
                                     self.videos_tab.new_thumb_location())
        self.assertTrue(filecmp.cmp(new_thumb, site_thumb))
  
 
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
 
        self.manager_user = TeamAdminMemberFactory(
            team=self.team,
            user = UserFactory(username = 'TeamAdmin')).user

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

    def test_filter__projects(self):
        """Filter video view by project.

        """
        data = json.load(open('apps/videos/fixtures/teams-list.json'))
        videos = _create_videos(data, [])
        for video in videos:
            TeamVideoFactory.create(
                team=self.team, 
                video=video, 
                added_by=self.manager_user,
                project = self.project2)

        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.project_filter(project = self.project1.name)
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())


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
        self.videos_tab.videos_displayed()
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
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())


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

class TestCaseVideosDisplay(WebdriverTestCase):
    """Check actions on team videos tab that are specific to user roles.

    """
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.videos_tab = videos_tab.VideosTab(self)
        self.team_owner = UserFactory.create(username = 'team_owner')
        self.limited_access_team = TeamMemberFactory.create(
            team__name='limited access open team',
            team__slug='limited-access-open-team',
            team__membership_policy = 4, #open
            team__video_policy = 2, #manager and admin
            team__workflow_enabled = True,
            user = self.team_owner,
            ).team


    def turn_on_automatic_tasks(self):
        #Turn on task autocreation for the team.
        WorkflowFactory.create(
            team = self.limited_access_team,
            autocreate_subtitle = True,
            autocreate_translate = True,
            review_allowed = 10)

        #Add some preferred languages to the team.
        lang_list = ['en', 'ru', 'pt-br']
        for language in lang_list:
            TeamLangPrefFactory(
                team = self.limited_access_team,
                language_code = language,
                preferred = True)

    def test_edit__no_permission(self):
        """A contributor can't see edit links without edit permission.

        """

        #Add some test videos to the team.
        vids = data_helpers.create_several_team_videos_with_subs(self, 
            team = self.limited_access_team,
            teamowner = self.team_owner)

        #Create a user who is a contributor to the team.
        contributor = TeamContributorMemberFactory(
            team = self.limited_access_team,
            user = UserFactory(username = 'contributor')).user
        self.videos_tab.log_in(contributor.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Edit'))

    def test_tasks__non_member(self):
        """Non-members of the team do not see the task links.
        """
        
        self.turn_on_automatic_tasks()
        #Add some test videos to the team.
        vids = data_helpers.create_several_team_videos_with_subs(self, 
            team = self.limited_access_team,
            teamowner = self.team_owner)

        #Create a user who is not a member 
        non_member = UserFactory(username = 'non_member')
        self.videos_tab.log_out()
        self.videos_tab.log_in(non_member.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Tasks'))

    def test_tasks__anonymous(self):
        """Anonymous users do not see the task links. 

        """
        self.turn_on_automatic_tasks()

        #Add some test videos to the team.
        vids = data_helpers.create_several_team_videos_with_subs(self, 
            team = self.limited_access_team,
            teamowner = self.team_owner)

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Tasks'))



    def test_edit__admin_permission(self):
        """A admin has the Edit link for videos.

        """
        #Add some test videos to the team.
        vids = data_helpers.create_several_team_videos_with_subs(self, 
            team = self.limited_access_team,
            teamowner = self.team_owner)

        #Create a user who is a contributor to the team.
        admin_member = TeamAdminMemberFactory(
            team = self.limited_access_team,
            user = UserFactory(username = 'admin_member')).user
        self.videos_tab.log_in(admin_member.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertTrue(self.videos_tab.video_has_link(vids[0].title, 'Edit'))

    def test_task_link(self):
        """A task link opens the task page for the video.
        """

        #Turn on task autocreation for the team.
        self.turn_on_automatic_tasks()

        #Add some test videos to the team.
        vids = data_helpers.create_several_team_videos_with_subs(self, 
            team = self.limited_access_team,
            teamowner = self.team_owner)
        test_title = vids[0].title
        self.videos_tab.log_in(self.team_owner.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        tasks_tab = self.videos_tab.open_video_tasks(test_title)

        self.assertEqual(test_title, tasks_tab.filtered_video())

    def test_languages__no_tasks(self):
        """Without tasks, display number of completed languages for video.

        """
        #Add some test videos to the team.
        vids = data_helpers.create_several_team_videos_with_subs(self, 
            team = self.limited_access_team,
            teamowner = self.team_owner)
        test_title = 'c'
        self.videos_tab.log_in(self.team_owner.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)

        self.assertEqual('1 language', 
            self.videos_tab.displayed_languages(test_title))

    def test_languages__automatic_tasks(self):
        """With automatic tasks, display number of needed languages for video.

        """
        self.turn_on_automatic_tasks()

        #Add some test videos to the team.
        vids = data_helpers.create_several_team_videos_with_subs(self, 
            team = self.limited_access_team,
            teamowner = self.team_owner)
        test_title = 'c'
        self.videos_tab.log_in(self.team_owner.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)

        self.assertEqual('2 languages needed', 
            self.videos_tab.displayed_languages(test_title))

    def test_pagination__admin(self):
        """Check number of videos displayed per page for team admin.

        """
        for x in range(50):
            TeamVideoFactory.create(
                team=self.limited_access_team, 
                video=VideoFactory.create(), 
                added_by=self.team_owner)
        self.videos_tab.log_in(self.team_owner.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertEqual(8, self.videos_tab.num_videos())

    def test_pagination__user(self):
        """Check number of videos displayed per page for team contributor.

        """
        contributor = UserFactory(username = 'contributor')
        for x in range(50):
            TeamVideoFactory.create(
                team=self.limited_access_team, 
                video=VideoFactory.create(), 
                added_by=self.team_owner)
        self.videos_tab.log_in(contributor.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertEqual(16, self.videos_tab.num_videos())

