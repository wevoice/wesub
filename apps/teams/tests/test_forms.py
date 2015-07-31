# Amara, universalsubtitles.org
#
# Copyright (C) 2015 Participatory Culture Foundation
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

from __future__ import absolute_import
import os

from django.test import TestCase
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from haystack import site
from haystack.query import SearchQuerySet
from nose.tools import *
import mock

from teams import forms
from teams.models import TeamVideo
from teams.permissions import *
from utils.factories import *
from utils.test_utils import patch_for_test, reload_obj
from videos.models import Video, VideoUrl

class EditMemberFormTest(TestCase):
    @patch_for_test('teams.permissions.get_edit_member_permissions')
    def setUp(self, mock_permission_check):
        self.mock_permission_check = mock_permission_check
        self.mock_permission_check.return_value = EDIT_MEMBER_ALL_PERMITTED
        self.team = TeamFactory()
        self.member = TeamMemberFactory(team=self.team)
        self.contributor = TeamMemberFactory(team=self.team,
                                             role=ROLE_CONTRIBUTOR)
        self.manager = TeamMemberFactory(team=self.team,
                                         role=ROLE_MANAGER)
        self.admin = TeamMemberFactory(team=self.team,
                                       role=ROLE_ADMIN)
        self.owner = TeamMemberFactory(team=self.team,
                                       role=ROLE_OWNER)

    def make_form(self, data=None):
        return forms.EditMembershipForm(self.member, data=data)

    def check_choices(self, form, member_choices, role_choices):
        assert_equal(
            [c[0] for c in form.fields['member'].choices],
            [m.id for m in member_choices]
        )
        assert_equal(
            [c[0] for c in form.fields['role'].choices],
            role_choices
        )
        assert_items_equal(form.editable_member_ids,
                           [m.id for m in member_choices])


    def test_all_permitted(self):
        form = self.make_form()
        self.check_choices(
            form,
            [ self.contributor, self.manager, self.admin, self.owner, ],
            [ ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ],
        )

        assert_true('remove' in form.fields)

    def test_cant_edit_admin(self):
        self.mock_permission_check.return_value = EDIT_MEMBER_CANT_EDIT_ADMIN
        form = self.make_form()
        self.check_choices(
            form,
            [ self.contributor, self.manager, ],
            [ ROLE_CONTRIBUTOR, ROLE_MANAGER, ],
        )
        assert_true('remove' in form.fields)

    def test_not_pemitted(self):
        self.mock_permission_check.return_value = EDIT_MEMBER_NOT_PERMITTED
        form = self.make_form()
        self.check_choices(form, [], [])
        assert_false('remove' in form.fields)

    def test_update_role(self):
        form = self.make_form(data={
            'member': self.contributor.id,
            'role': ROLE_MANAGER,
        })
        assert_true(form.is_valid())
        form.save()
        assert_equal(reload_obj(self.contributor).role, ROLE_MANAGER)

    def test_remove(self):
        form = self.make_form(data={
            'member': self.contributor.id,
            'role': ROLE_MANAGER,
            'remove': 1,
        })
        assert_true(form.is_valid())
        form.save()
        assert_false(
            TeamMember.objects.filter(id=self.contributor.id).exists()
        )

def test_thumbnail_file():
    p = os.path.join(settings.PROJECT_ROOT,
                     'media/images/video-no-thumbnail-wide.png')
    content = open(p).read()
    return SimpleUploadedFile('thumb.png', content)

class AddTeamVideoFormTest(TestCase):
    @patch_for_test('teams.permissions.can_add_video')
    def setUp(self, mock_can_add_video):
        self.mock_can_add_video = mock_can_add_video
        self.mock_can_add_video.return_value = True

        self.team = TeamFactory()
        self.user = TeamMemberFactory(team=self.team).user
        self.url = 'http://example.com/video.mp4'

    def make_form(self, data=None, files=None):
        return forms.NewAddTeamVideoForm(self.team, self.user,
                                         data=data, files=files)

    def test_add(self):
        form = self.make_form({'video_url': self.url})
        assert_true(form.is_valid(), form.errors.as_text())
        team_video = form.save()
        assert_equal(team_video.team, self.team)
        assert_equal(team_video.video.get_primary_videourl_obj().added_by,
                     self.user)

    @patch_for_test('utils.amazon.fields.S3ImageFieldFile.save')
    def test_add_with_thumbnail(self, mock_save):
        thumb_file = test_thumbnail_file()
        form = self.make_form({
            'video_url': self.url,
        }, {
            'thumbnail': thumb_file,
        })
        assert_true(form.is_valid(), form.errors.as_text())
        form.save()
        assert_equal(mock_save.call_args,
                     mock.call(thumb_file.name, thumb_file))

    def test_add_with_project(self):
        project = ProjectFactory.create(team=self.team)
        form = self.make_form({
            'video_url': self.url,
            'project': project.id,
        })
        assert_true(form.is_valid(), form.errors.as_text())
        team_video = form.save()
        assert_equal(team_video.project, project)

    def test_add_non_team_video(self):
        existing_video = VideoFactory.create(video_url__url=self.url)
        form = self.make_form({'video_url': self.url})
        assert_true(form.is_valid(), form.errors.as_text())
        team_video = form.save()
        assert_equal(team_video.team, self.team)
        assert_equal(team_video.video, existing_video)

    def test_cant_add_team_video(self):
        existing_video = TeamVideoFactory.create(
            video__video_url__url=self.url
        )
        form = self.make_form({'video_url': self.url})
        assert_false(form.is_valid())

    def test_permissions_check(self):
        self.mock_can_add_video.return_value = False
        form = self.make_form({'video_url': self.url})
        assert_equal(
            self.mock_can_add_video.call_args,
            mock.call(self.team, self.user)
        )
        assert_false(form.enabled)
        assert_false(form.is_valid())

class EditTeamVideoFormTest(TestCase):
    @patch_for_test('teams.permissions.can_edit_videos')
    def setUp(self, mock_can_edit_videos):
        self.mock_can_edit_videos = mock_can_edit_videos
        self.mock_can_edit_videos.return_value = True

        self.team = TeamFactory()
        self.user = TeamMemberFactory(team=self.team).user
        self.project = ProjectFactory(team=self.team)
        self.project2 = ProjectFactory(team=self.team)
        self.team_video = TeamVideoFactory(team=self.team,
                                           project=self.project)

    def make_form(self, data=None, files=None):
        return forms.NewEditTeamVideoForm(self.team, self.user, data=data,
                                          files=files)

    @patch_for_test('utils.amazon.fields.S3ImageFieldFile.save')
    def test_update(self, mock_save):
        thumb_file = test_thumbnail_file()
        form = self.make_form({
            'team_video': self.team_video.id,
            'primary_audio_language': 'en',
            'project': self.project2.id,
        }, {
            'thumbnail': thumb_file,
        })
        assert_true(form.is_valid(), form.errors.as_text())
        form.save()
        team_video = reload_obj(self.team_video)
        assert_equal(team_video.project, self.project2)
        assert_equal(team_video.video.primary_audio_language_code, 'en')
        assert_equal(mock_save.call_args,
                     mock.call(thumb_file.name, thumb_file))

    def delete_projects(self):
        self.team_video.project = self.team.default_project
        self.team_video.save()
        self.project.delete()
        self.project2.delete()

    def test_no_project_field_when_team_has_no_projects(self):
        self.delete_projects()
        form = self.make_form()
        assert_false('project' in form.fields)

    @patch_for_test('utils.amazon.fields.S3ImageFieldFile.save')
    def test_submit_with_no_projects(self, mock_save):
        self.delete_projects()
        thumb_file = test_thumbnail_file()
        form = self.make_form({
            'team_video': self.team_video.id,
        }, {
            'thumbnail': thumb_file,
        })
        assert_true(form.is_valid(), form.errors.as_text())
        form.save()
        assert_equal(mock_save.call_args,
                     mock.call(thumb_file.name, thumb_file))

    def test_permission_check_args(self):
        form = self.make_form()
        assert_equal(self.mock_can_edit_videos.call_args,
                     mock.call(self.team, self.user))

    def test_can_edit_videos_permissions_check(self):
        self.mock_can_edit_videos.return_value = False
        form = self.make_form()
        assert_equal(form.fields['team_video'].choices, [])
        assert_false(form.enabled)

class BulkTeamVideoFormTest(TestCase):
    def setUp(self):
        self.check_permissions = mock.Mock(return_value=True)
        self.perform_save = mock.Mock()
        self.user = UserFactory()
        self.team = TeamFactory(admin=self.user)
        self.team_videos = [
            TeamVideoFactory(team=self.team)
            for i in range(10)
        ]

    def make_form(self, *args, **kwargs):
        class FormClass(forms.BulkTeamVideoForm):
            check_permissions = self.check_permissions
            perform_save = self.perform_save
        return FormClass(self.team, self.user, *args, **kwargs)

    def test_permission_check_pass(self):
        assert_true(self.make_form().enabled)

    def test_permission_check_fail(self):
        self.check_permissions.return_value = False
        assert_false(self.make_form().enabled)

    def test_permission_check_fail_prevents_save(self):
        self.check_permissions.return_value = False
        bound_form = self.make_form(data={
            'team_videos': [self.team_videos[0].id],
        })
        with assert_raises(PermissionDenied):
            bound_form.save(self.team.teamvideo_set.all())

    def check_save(self, form, correct_videos):
        assert_true(form.is_valid(), form.errors.as_text())
        form.save(qs=self.team.teamvideo_set.all())
        assert_items_equal(
            form.perform_save.call_args[0][0],
            correct_videos,
        )

    def test_save_no_include_all(self):
        selected_videos = self.team_videos[:2]

        form = self.make_form(data={
            'team_videos': [tv.id for tv in selected_videos],
        })
        self.check_save(form, selected_videos)

    def test_save_with_include_all(self):
        form = self.make_form(data={
            'team_videos': [self.team_videos[0].id],
            'include_all': 1,
        })
        self.check_save(form, self.team_videos)

    def test_save_with_include_all_and_search_qs(self):
        search_index = site.get_index(TeamVideo)
        for tv in self.team_videos:
            search_index.update_object(tv)
        search_qs = (SearchQuerySet().models(TeamVideo)
                     .filter(team_id=self.team.id))
        form = self.make_form(data={
            'team_videos': [self.team_videos[0].id],
            'include_all': 1,
        })
        self.check_save(form, self.team_videos)
