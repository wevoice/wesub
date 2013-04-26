# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
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

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from apps.teams.models import Team, TeamMember, TeamVideo, Project
from apps.videos.models import Video, VideoUrl
from auth.models import CustomUser as User
from utils import test_factories
from utils.panslugify import pan_slugify

class ViewsTests(TestCase):
    def setUp(self):
        self.auth = {
            "username": u"admin",
            "password": u"admin"}
        self.user = test_factories.create_user(is_staff=True,
                                               is_superuser=True,
                                               **self.auth)

    def _create_base_team(self):
       self.team = Team(
           slug="new-team",
            membership_policy=4,
            video_policy =1,
           name="New-name")
       self.team.save()
       user, created = User.objects.get_or_create(
           username=self.auth["username"])
       TeamMember.objects.create_first_member(self.team, user)
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

    def test_team_edit(self):
        team = self._create_base_team()
        self.client.login(**self.auth)
        url = reverse("teams:settings_basic", kwargs={"slug": team.slug})

        member = self._create_member(team, TeamMember.ROLE_ADMIN)
        videos = [test_factories.create_video() for i in xrange(4)]

        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)

        for video in videos:
            test_factories.create_team_video(team, member.user, video)

        self.assertTrue(all([v.is_public for v in videos]))

        self.assertFalse(team.logo)

        data = {
            "name": u"New team",
            "is_visible": u"0",
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
        self.assertFalse(team.is_visible)
        self.assertTrue(all([v.is_public for v in videos]))

        data = {
            "name": u"New team",
            "is_visible": u"1",
            "description": u"testing",
        }

        url = reverse("teams:settings_basic", kwargs={"slug": team.slug})
        response = self.client.post(url, data)

        self.failUnlessEqual(response.status_code, 302)
        self.assertTrue(all([v.is_public for v in videos]))

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

    def test_remove_video(self):
        team = test_factories.create_team(slug="new-team",
                                          membership_policy=4,
                                          video_policy=1,
                                          name="New-name")

        def create_member(role):
            user = test_factories.create_user(username='test' + role,
                                              password='test' + role)
            return TeamMember.objects.create(user=user, role=role, team=team)

        admin = create_member(TeamMember.ROLE_ADMIN)
        contributor = create_member(TeamMember.ROLE_CONTRIBUTOR)
        manager = create_member(TeamMember.ROLE_MANAGER)
        owner = create_member(TeamMember.ROLE_OWNER)

        def create_team_video():
            return test_factories.create_team_video(team, owner.user)

        # The video policy determines who can remove videos from teams.
        for member in [contributor, manager, admin, owner]:
            self.client.login(username=member.user.username,
                              password=member.user.username)
            tv = create_team_video()
            video_url = tv.video.get_video_url()

            url = reverse("teams:remove_video", kwargs={"team_video_pk": tv.pk})
            response = self.client.post(url)

            self.assertEqual(response.status_code, 302)
            self.assertFalse(TeamVideo.objects.filter(pk=tv.pk).exists())
            self.assertTrue(VideoUrl.objects.get(url=video_url).video)

        # Only owners can delete videos entirely.
        for role in [owner]:
            self.client.login(username=role.user.username,
                              password=role.user.username)
            tv = create_team_video()
            video_url = tv.video.get_video_url()

            url = reverse("teams:remove_video", kwargs={"team_video_pk": tv.pk})
            response = self.client.post(url, {'del-opt': 'total-destruction'})

            self.assertEqual(response.status_code, 302)
            self.assertFalse(TeamVideo.objects.filter(pk=tv.pk).exists())
            self.assertFalse(VideoUrl.objects.filter(url=video_url).exists())

        for role in [contributor, manager, admin]:
            self.client.login(username=role.user.username,
                              password=role.user.username)
            tv = create_team_video()
            video_url = tv.video.get_video_url()

            url = reverse("teams:remove_video", kwargs={"team_video_pk": tv.pk})
            response = self.client.post(url, {'del-opt': 'total-destruction'})

            self.assertEqual(response.status_code, 302)
            self.assertTrue(TeamVideo.objects.filter(pk=tv.pk).exists())
            self.assertTrue(VideoUrl.objects.filter(url=video_url).exists())

        # POST request required
        tv = create_team_video()
        video_url = tv.video.get_video_url()
        url = reverse("teams:remove_video", kwargs={"team_video_pk": tv.pk})
        self.client.login(username=self.user.username,
                          password=self.user.username)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(TeamVideo.objects.filter(pk=tv.pk).exists())
        self.assertTrue(VideoUrl.objects.filter(url=video_url).exists())


    def test_move_video_allowed(self):
        # Check that moving works when the user has permission.
        video = test_factories.create_video()
        old_team = test_factories.create_team(video_policy=Team.VP_MANAGER)
        new_team = test_factories.create_team(video_policy=Team.VP_MANAGER)
        team_video = test_factories.create_team_video(old_team, self.user,
                                                      video)
        # Convenient functions for pulling models fresh from the DB.
        get_video = lambda: Video.objects.get(pk=video.pk)
        get_team_video = lambda: get_video().get_team_video()

        # Create a member that's an admin of BOTH teams.
        # This member should be able to move the video.
        member = self._create_member(old_team, TeamMember.ROLE_ADMIN)
        self._create_member(new_team, TeamMember.ROLE_ADMIN, member.user)

        self.assertEqual(get_team_video().team.pk, old_team.pk,
                         "Video did not start in the correct team.")

        # Move the video.
        self.client.login(username=member.user.username,
                          password=member.user.username)
        url = reverse("teams:move_video")
        response = self.client.post(url, {'team_video': get_team_video().pk,
                                          'team': new_team.pk,})
        self.assertEqual(response.status_code, 302)

        self.assertEqual(get_team_video().team.pk, new_team.pk,
                         "Video was not moved to the new team.")

        self.assertEqual(get_team_video().project.team, new_team,
                         "Video ended up with a project for the first team")

    def test_move_video_disallowed_old(self):
        # Check that moving does not work when the user is blocked by the old
        # team.
        video = test_factories.create_video()
        old_team = test_factories.create_team(video_policy=Team.VP_MANAGER)
        new_team = test_factories.create_team(video_policy=Team.VP_MANAGER)
        team_video = test_factories.create_team_video(old_team, self.user,
                                                      video)
        # Convenient functions for pulling models fresh from the DB.
        get_video = lambda: Video.objects.get(pk=video.pk)
        get_team_video = lambda: get_video().get_team_video()

        # Create a member that's a contributor to the old/current team.
        # This member should NOT be able to move the video because they cannot
        # remove it from the first team.
        member = self._create_member(old_team, TeamMember.ROLE_CONTRIBUTOR)
        self._create_member(new_team, TeamMember.ROLE_ADMIN, member.user)

        self.assertEqual(get_team_video().team.pk, old_team.pk,
                         "Video did not start in the correct team.")

        # Try to move the video.
        self.client.login(username=member.user.username,
                          password=member.user.username)
        url = reverse("teams:move_video")
        response = self.client.post(url, {'team_video': get_team_video().pk,
                                          'team': new_team.pk,})
        self.assertEqual(response.status_code, 302)

        self.assertEqual(get_team_video().team.pk, old_team.pk,
                         "Video did not stay in the old team.")

    def test_move_video_disallowed_new(self):
        # Check that moving does not work when the user is blocked by the new
        # team.
        video = test_factories.create_video()
        old_team = test_factories.create_team(video_policy=Team.VP_MANAGER)
        new_team = test_factories.create_team(video_policy=Team.VP_MANAGER)
        team_video = test_factories.create_team_video(old_team, self.user,
                                                      video)
        # Convenient functions for pulling models fresh from the DB.
        get_video = lambda: Video.objects.get(pk=video.pk)
        get_team_video = lambda: get_video().get_team_video()

        # Create a member that's a contributor to the new/target team.
        # This member should NOT be able to move the video because they cannot
        # add it to the second team.
        member = self._create_member(old_team, TeamMember.ROLE_ADMIN)
        self._create_member(new_team, TeamMember.ROLE_CONTRIBUTOR, member.user)

        self.assertEqual(get_team_video().team.pk, old_team.pk,
                         "Video did not start in the correct team.")

        # Try to move the video.
        self.client.login(username=member.user.username,
                          password=member.user.username)
        url = reverse("teams:move_video")
        response = self.client.post(url, {'team_video': get_team_video().pk,
                                          'team': new_team.pk,})
        self.assertEqual(response.status_code, 302)

        self.assertEqual(get_team_video().team.pk, old_team.pk,
                         "Video did not stay in the old team.")

    def test_team_permission(self):
        team = test_factories.create_team(slug="private-team",
                                          name="Private Team",
                                          is_visible=False)
        TeamMember.objects.create_first_member(team, self.user)
        video = test_factories.create_video()
        test_factories.create_team_video(team, self.user, video)

        url = reverse("videos:video", kwargs={"video_id": video.video_id})

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.client.login(**self.auth)

        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

        self.client.logout()

    def test_add_videos_via_feed(self):
        team = self._create_base_team()
        self.client.login(**self.auth)

        url = reverse("teams:add_videos", kwargs={"slug": team.slug})

        data = {
            'feed_url': u'http://blip.tv/coxman/rss'
        }

        old_video_count = Video.objects.count()
        old_team_video_count = TeamVideo.objects.filter(team=team).count()

        response = self.client.post(url, data)
        self.assertRedirects(response, team.get_absolute_url())

        self.assertNotEquals(old_video_count, Video.objects.count())
        self.assertNotEquals(old_team_video_count, TeamVideo.objects.filter(team=team).count())

    def test_add_videos_via_youtube_user(self):
        team = self._create_base_team()
        self.client.login(**self.auth)

        url = reverse("teams:add_videos", kwargs={"slug": team.slug})

        data = {
            'usernames': u'fernandotakai'
        }

        old_video_count = Video.objects.count()
        old_team_video_count = TeamVideo.objects.filter(team=team).count()

        response = self.client.post(url, data)
        self.assertRedirects(response, team.get_absolute_url())

        self.assertNotEquals(old_video_count, Video.objects.count())
        self.assertNotEquals(old_team_video_count, TeamVideo.objects.filter(team=team).count())

    def _create_member(self, team, role, user=None):
        if not user:
            user = User.objects.create(username='test' + role)
            user.set_password('test' + role)
            user.save()
        return TeamMember.objects.create(user=user, role=role, team=team)

