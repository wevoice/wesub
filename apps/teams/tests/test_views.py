# Universal Subtitles, universalsubtitles.org
#
# Copyright (C) 2010 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.
from os import path
from django.core.urlresolvers import reverse
from auth.models import CustomUser as User
from django.conf import settings
from django.test import TestCase
from utils.panslugify import pan_slugify

from apps.teams.models import Team, TeamMember, TeamVideo, Project
from apps.videos.models import Video, VIDEO_TYPE_YOUTUBE, VideoUrl

class ViewsTests(TestCase):

    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]

    def setUp(self):
        self.auth = {
            "username": u"admin",
            "password": u"admin"}
        self.user = User.objects.get(username=self.auth["username"])
  
    def _create_base_team(self):
       self.team = Team(
           slug="new-team",
            membership_policy=4,
            video_policy =1,
           name="New-name")
       self.team.save()
       user, created = User.objects.get_or_create(
           username=self.auth["username"])
       tm = TeamMember.objects.create_first_member(self.team, user)
       return self.team


    def test_team_create(self):


        self.client.login(**self.auth)

        #------- create ----------
        response = self.client.get(reverse("teams:create"))
        self.failUnlessEqual(response.status_code, 200)

        data = {
            "description": u"",
            "video_url": u"",
            "membership_policy": u"4",
            "video_policy": u"1",
            "logo": u"",
            "slug": u"new-team",
            "name": u"New team"
        }
        response = self.client.post(reverse("teams:create"), data)
        self.failUnlessEqual(response.status_code, 302)
        self.assertEqual(Team.objects.get(slug=data['slug']).slug, data["slug"])

    def test_team_edit(self ):
        team = self._create_base_team()
        self.client.login(**self.auth)
        url = reverse("teams:settings_basic", kwargs={"slug": team.slug})
        response = self.client.get(url)

        self.failUnlessEqual(response.status_code, 200)

        self.assertFalse(team.logo)

        data = {
            "name": u"New team",
            "is_visible": u"1",
            "description": u"testing",
            "logo": open(path.join(settings.MEDIA_ROOT, "test/71600102.jpg"), "rb")
        }
        url = reverse("teams:settings_basic", kwargs={"slug": team.slug})
        response = self.client.post(url, data)
        self.failUnlessEqual(response.status_code, 302)

        team = Team.objects.get(pk=team.pk)
        self.assertTrue(team.logo)
        self.assertEqual(team.name, u"New team")
        self.assertEqual(team.description, u"testing")
        self.assertTrue(team.is_visible)

    def test_create_project(self):
        team = self._create_base_team()
        self.client.login(**self.auth)

        url = reverse("teams:add_project", kwargs={"slug": team.slug})

        data = {
            "name": u"Test Project",
            "description": u"Test Project",
            "review_allowed": u"0",
            "approve_allowed": u"0",
        }

        response = self.client.post(url, data)
        self.failUnlessEqual(response.status_code, 302)

        slug = pan_slugify(data['name'])

        project = Project.objects.get(slug=slug)
        self.assertEqual(project.name, data['name'])
        self.assertEqual(project.description, data['description'])

        # creating a duplicated project results in error
        response = self.client.post(url, data)
        self.failUnlessEqual(response.status_code, 200)
        messages = [m.message for m in list(response.context['messages'])]
        self.assertIn(u"There's already a project with this name", messages)

    def test_delete_video(self):
        video_url = Video.objects.all()[0].get_video_url()
        team = Team(
           slug="new-team",
            membership_policy=4,
            video_policy =1,
           name="New-name")
        team.save()
        TeamMember.objects.create_first_member(
            team, User.objects.create(username='void'))
        def create_member(role):
            user = User.objects.create(username='test' + role)
            user.set_password('test' + role)
            user.save()
            return TeamMember.objects.create(user=user, role = role,
                                             team=team)
        admin = create_member(TeamMember.ROLE_ADMIN)
        contributor = create_member(TeamMember.ROLE_CONTRIBUTOR)
        manager = create_member(TeamMember.ROLE_MANAGER)
        owner = create_member(TeamMember.ROLE_OWNER)
        # none of this should be able to delete
        def create_team_video():
           v, c  = Video.get_or_create_for_url(video_url)
           tv, c = TeamVideo.objects.get_or_create(video=v, team=team,
           defaults= {'added_by':owner.user})
           return tv
        # these guys can touch this
        for role in [contributor, manager]:
            self.client.login(**{"username": role.user.username,
                               "password":role.user.username})
            tv = create_team_video()
            url = reverse("teams:delete_video", kwargs={"team_video_pk": tv.pk})
            response = self.client.post(url)
            self.assertEqual(response.status_code,403)
            self.assertTrue(TeamVideo.objects.filter(pk=tv.pk).exists())
            self.assertTrue(VideoUrl.objects.get(url=video_url).video)
        # these should be allowed to delete it
            
        tv.delete()
        next = reverse('teams:user_teams')
        for role in [owner, admin]:
            self.client.login(**{"username": role.user.username,
                               "password":role.user.username})
            tv = create_team_video()
            url = reverse("teams:delete_video", kwargs={"team_video_pk": tv.pk})
            response = self.client.post(url)
            self.assertRedirects(response, next)
            self.assertFalse(TeamVideo.objects.filter(pk=tv.pk).exists())
            self.assertFalse(VideoUrl.objects.filter(url=video_url).exists())
            
            
        tv = create_team_video()
        url = reverse("teams:delete_video", kwargs={"team_video_pk": tv.pk})
        self.client.login(**self.auth)
        response = self.client.post(url)
        # not a member, can't do it!'
        self.assertEqual(response.status_code,403)
        
        # post required
        tv = create_team_video()
        url = reverse("teams:delete_video", kwargs={"team_video_pk": tv.pk})
        self.client.login(**{"username": self.user.username,
                           "password":self.user.username})
        response = self.client.get(url)
        # not a member, can't do it!'
        self.assertEqual(response.status_code,403)
 
