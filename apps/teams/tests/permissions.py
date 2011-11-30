# Universal Subtitles, universalsubtitles.org
#
# Copyright (C) 2011 Participatory Culture Foundation
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

import datetime
from django.test import TestCase
from apps.teams.models import Team, TeamVideo, TeamMember, Workflow, Task
from auth.models import CustomUser as User
from contextlib import contextmanager
from apps.testhelpers import views as helpers
from utils.translation import SUPPORTED_LANGUAGES_DICT

from apps.teams.permissions_const import *
from apps.teams.permissions import (
    remove_role, add_role, can_message_all_members, can_add_video,
    can_assign_tasks, can_assign_role, roles_user_can_assign,
    add_narrowing_to_member, can_rename_team, can_view_settings_tab,
    can_change_team_settings, can_view_tasks_tab, can_invite,
    can_change_video_settings, can_review, can_message_all_members,
    can_edit_project, can_create_and_edit_subtitles, can_create_task_subtitle,
    can_create_task_translate
)


TOTAL_LANGS = len(SUPPORTED_LANGUAGES_DICT)


def _set_subtitles(team_video, language, original, complete, translations=[]):
    translations = [{'code': lang, 'is_original': False, 'is_complete': True,
                     'num_subs': 1} for lang in translations]

    data = {'code': language, 'is_original': original, 'is_complete': complete,
            'num_subs': 1, 'translations': translations}

    helpers._add_lang_to_video(team_video.video, data, None)


class BaseTestPermission(TestCase):
    def setUp(self):
        self.auth = dict(username='admin', password='admin')
        self.team  = Team.objects.all()[0]
        self.team.video_policy = Team.MANAGER_REMOVE
        self.video = self.team.videos.all()[0]

        # TODO: Remove these magic queryset indexes
        self.user = User.objects.all()[0]

        self.owner, _ = TeamMember.objects.get_or_create(
            user= User.objects.all()[3], role=TeamMember.ROLE_OWNER, team=self.team)

        self.outsider = User.objects.get(username='outsider')

    @property
    def default_project(self):
        return self.team.project_set.get(pk=1)

    @property
    def test_project(self):
        return self.team.project_set.get(pk=2)


    @property
    def nonproject_video(self):
        return TeamVideo.objects.filter(project__pk=1)[0]

    @property
    def project_video(self):
        return TeamVideo.objects.filter(project__pk=2)[0]


    @contextmanager
    def role(self, r, project=None):
        add_role(self.team, self.user, self.owner, r, project=project)

        try:
            yield
        finally:
            remove_role(self.team, self.user, r, project=project)


class TestRules(BaseTestPermission):
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]

    def _login(self):
        self.client.login(**self.auth)


    # Testing specific permissions
    def test_roles_assignable(self):
        user = User.objects.filter(teams__isnull=True)[0]
        team = self.team

        # Owners can do anything.
        with self.role(ROLE_OWNER):
            self.assertItemsEqual(roles_user_can_assign(team, user, None), [
                ROLE_OWNER, ROLE_ADMIN, ROLE_MANAGER, ROLE_CONTRIBUTOR
            ])

        # Admins can do anything except assign owners and changing owners' roles.
        with self.role(ROLE_ADMIN):
            self.assertItemsEqual(roles_user_can_assign(team, user, None), [
                ROLE_ADMIN, ROLE_MANAGER, ROLE_CONTRIBUTOR
            ])
            self.assertItemsEqual(roles_user_can_assign(team, user, self.owner.user), [])

        # Restricted Admins can't assign roles at all.
        with self.role(ROLE_ADMIN, self.test_project):
            self.assertItemsEqual(roles_user_can_assign(team, user, None), [])

        # No one else can assign roles.
        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER]:
            with self.role(r):
                self.assertItemsEqual(roles_user_can_assign(team, user, None), [])

    def test_can_rename_team(self):
        user = self.user
        team = self.team

        # Owners can rename teams
        with self.role(ROLE_OWNER):
            self.assertTrue(can_rename_team(team, user))

        # But no one else can rename a team
        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN]:
            with self.role(r):
                self.assertFalse(can_rename_team(team, user))

    def test_can_add_video(self):
        user = self.user
        team = self.team

        # Ensure that the "members can add" policies work.
        for policy in [Team.MEMBER_ADD, Team.MEMBER_REMOVE]:
            team.video_policy = policy
            team.save()

            for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
                with self.role(r):
                    self.assertTrue(can_add_video(team, user))

            self.assertFalse(can_add_video(team, self.outsider))

        # Ensure the "managers can add" policy works.
        team.video_policy = Team.MANAGER_REMOVE
        team.save()

        for r in [ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_add_video(team, user))

        with self.role(ROLE_CONTRIBUTOR):
            self.assertFalse(can_add_video(team, user))

        self.assertFalse(can_add_video(team, self.outsider))

        # Make sure narrowings are taken into account.
        with self.role(ROLE_MANAGER, self.test_project):
            self.assertFalse(can_add_video(team, user))
            self.assertTrue(can_add_video(team, user, project=self.test_project))

    def test_can_view_settings_tab(self):
        # Only admins and owners can view/change the settings tab, so this one
        # is pretty simple.
        user = self.user
        team = self.team

        for r in [ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_view_settings_tab(team, user))

        with self.role(ROLE_ADMIN, self.test_project):
            self.assertFalse(can_view_settings_tab(team, user))

        for r in [ROLE_MANAGER, ROLE_CONTRIBUTOR]:
            with self.role(r):
                self.assertFalse(can_view_settings_tab(team, user))

    def test_can_change_team_settings(self):
        # Only admins and owners can view/change the settings tab, so this one
        # is pretty simple.
        user = self.user
        team = self.team

        for r in [ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_change_team_settings(team, user))

        with self.role(ROLE_ADMIN, self.test_project):
            self.assertFalse(can_change_team_settings(team, user))

        for r in [ROLE_MANAGER, ROLE_CONTRIBUTOR]:
            with self.role(r):
                self.assertFalse(can_change_team_settings(team, user))

    def test_can_view_tasks_tab(self):
        # Any team member can view tasks.
        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_view_tasks_tab(self.team, self.user))

        # But outsiders can't (for now).
        self.assertFalse(can_view_tasks_tab(self.team, self.outsider))

    def test_can_invite(self):
        team, user, outsider = self.team, self.user, self.outsider

        # If the policy is by-application, only admins+ can send invites.
        team.membership_policy = Team.APPLICATION
        team.save()

        for r in [ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_invite(team, user))

        for r in [ROLE_ADMIN]:
            with self.role(r, self.test_project):
                self.assertFalse(can_invite(team, user))

        for r in [ROLE_MANAGER, ROLE_CONTRIBUTOR]:
            with self.role(r):
                self.assertFalse(can_invite(team, user))

        self.assertFalse(can_invite(team, outsider))

        # Manager invites.
        team.membership_policy = Team.INVITATION_BY_MANAGER
        team.save()

        for r in [ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_invite(team, user))

        for r in [ROLE_MANAGER, ROLE_ADMIN]:
            with self.role(r, self.test_project):
                self.assertFalse(can_invite(team, user))

        for r in [ROLE_CONTRIBUTOR]:
            with self.role(r):
                self.assertFalse(can_invite(team, user))

        self.assertFalse(can_invite(team, outsider))

        # Admin invites.
        team.membership_policy = Team.INVITATION_BY_ADMIN
        team.save()

        for r in [ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_invite(team, user))

        for r in [ROLE_ADMIN]:
            with self.role(r, self.test_project):
                self.assertFalse(can_invite(team, user))

        for r in [ROLE_MANAGER, ROLE_CONTRIBUTOR]:
            with self.role(r):
                self.assertFalse(can_invite(team, user))

        self.assertFalse(can_invite(team, outsider))

        # Open and All are the same for the purpose of sending invites.
        for policy in [Team.OPEN, Team.INVITATION_BY_ALL]:
            team.membership_policy = policy
            team.save()

            for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
                with self.role(r):
                    self.assertTrue(can_invite(team, user))

            for r in [ROLE_MANAGER, ROLE_ADMIN]:
                with self.role(r, self.test_project):
                    self.assertTrue(can_invite(team, user))

            self.assertFalse(can_invite(team, outsider))

    def test_can_change_video_settings(self):
        user, outsider = self.user, self.outsider

        for r in [ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_change_video_settings(user, self.project_video))
                self.assertTrue(can_change_video_settings(user, self.nonproject_video))

        for r in [ROLE_CONTRIBUTOR]:
            with self.role(r):
                self.assertFalse(can_change_video_settings(user, self.project_video))
                self.assertFalse(can_change_video_settings(user, self.nonproject_video))

        for r in [ROLE_MANAGER, ROLE_ADMIN]:
            with self.role(r, self.test_project):
                self.assertTrue(can_change_video_settings(user, self.project_video))
                self.assertFalse(can_change_video_settings(user, self.nonproject_video))

        self.assertFalse(can_change_video_settings(outsider, self.project_video))
        self.assertFalse(can_change_video_settings(outsider, self.nonproject_video))

    def test_can_review(self):
        user, outsider = self.user, self.outsider
        workflow = Workflow.get_for_team_video(self.nonproject_video)

        # TODO: Test with Project/video-specific workflows.

        # Review disabled.
        workflow.review_allowed = Workflow.REVIEW_IDS["Don't require review"]
        workflow.save()

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertFalse(can_review(self.nonproject_video, user))

        self.assertFalse(can_review(self.nonproject_video, outsider))

        # Peer reviewing.
        workflow.review_allowed = Workflow.REVIEW_IDS["Peer must review"]
        workflow.save()

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_review(self.nonproject_video, user))

        self.assertFalse(can_review(self.nonproject_video, outsider))

        # Manager review.
        workflow.review_allowed = Workflow.REVIEW_IDS["Manager must review"]
        workflow.save()

        for r in [ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_review(self.nonproject_video, user))

        for r in [ROLE_CONTRIBUTOR]:
            with self.role(r):
                self.assertFalse(can_review(self.nonproject_video, user))

        for r in [ROLE_MANAGER, ROLE_ADMIN]:
            with self.role(r, self.test_project):
                self.assertFalse(can_review(self.nonproject_video, user))
                self.assertTrue(can_review(self.project_video, user))

        self.assertFalse(can_review(self.nonproject_video, outsider))

        # Admin review.
        workflow.review_allowed = Workflow.REVIEW_IDS["Admin must review"]
        workflow.save()

        for r in [ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_review(self.nonproject_video, user))

        for r in [ROLE_MANAGER, ROLE_CONTRIBUTOR]:
            with self.role(r):
                self.assertFalse(can_review(self.nonproject_video, user))

        for r in [ROLE_ADMIN]:
            with self.role(r, self.test_project):
                self.assertFalse(can_review(self.nonproject_video, user))
                self.assertTrue(can_review(self.project_video, user))

        self.assertFalse(can_review(self.nonproject_video, outsider))

    def test_can_message_all_members(self):
        team, user, outsider = self.team, self.user, self.outsider

        for r in [ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_message_all_members(team, user))

        for r in [ROLE_ADMIN]:
            with self.role(r, self.test_project):
                self.assertFalse(can_message_all_members(team, user))

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER]:
            with self.role(r):
                self.assertFalse(can_message_all_members(team, user))

        self.assertFalse(can_message_all_members(team, outsider))

    def test_can_edit_project(self):
        team, user, outsider = self.team, self.user, self.outsider
        default_project, test_project = self.default_project, self.test_project

        # The default project cannot be edited at all.
        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertFalse(can_edit_project(team, user, default_project))

        self.assertFalse(can_edit_project(team, outsider, default_project))

        # Projects can only be edited by admins+.
        for r in [ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_edit_project(team, user, test_project))

        for r in [ROLE_ADMIN]:
            with self.role(r, test_project):
                self.assertTrue(can_edit_project(team, user, test_project))

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER]:
            with self.role(r):
                self.assertFalse(can_edit_project(team, user, test_project))

        self.assertFalse(can_edit_project(team, outsider, test_project))

        # TODO: Test with a second project.

    def test_can_create_and_edit_subtitles(self):
        team, user, outsider = self.team, self.user, self.outsider

        # Anyone
        team.subtitle_policy = Team.SUBTITLE_IDS['Anyone']
        team.save()

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_create_and_edit_subtitles(user, self.nonproject_video))

        self.assertTrue(can_create_and_edit_subtitles(outsider, self.nonproject_video))

        # Contributors only.
        team.subtitle_policy = Team.SUBTITLE_IDS['Any team member']
        team.save()

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_create_and_edit_subtitles(user, self.nonproject_video))

        self.assertFalse(can_create_and_edit_subtitles(outsider, self.nonproject_video))

        # Managers only.
        team.subtitle_policy = Team.SUBTITLE_IDS['Only managers and admins']
        team.save()

        for r in [ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_create_and_edit_subtitles(user, self.nonproject_video))

        for r in [ROLE_MANAGER, ROLE_ADMIN]:
            with self.role(r, self.test_project):
                self.assertFalse(can_create_and_edit_subtitles(user, self.nonproject_video))
                self.assertTrue(can_create_and_edit_subtitles(user, self.project_video))

        for r in [ROLE_CONTRIBUTOR]:
            with self.role(r):
                self.assertFalse(can_create_and_edit_subtitles(user, self.nonproject_video))

        self.assertFalse(can_create_and_edit_subtitles(outsider, self.nonproject_video))

        # Admins only.
        team.subtitle_policy = Team.SUBTITLE_IDS['Only admins']
        team.save()

        for r in [ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_create_and_edit_subtitles(user, self.nonproject_video))

        for r in [ROLE_ADMIN]:
            with self.role(r, self.test_project):
                self.assertFalse(can_create_and_edit_subtitles(user, self.nonproject_video))
                self.assertTrue(can_create_and_edit_subtitles(user, self.project_video))

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER]:
            with self.role(r):
                self.assertFalse(can_create_and_edit_subtitles(user, self.nonproject_video))

        self.assertFalse(can_create_and_edit_subtitles(outsider, self.nonproject_video))


    # TODO: Ensure later steps block earlier steps.
    def test_can_create_task_subtitle(self):
        team, user, outsider = self.team, self.user, self.outsider

        # When no subtitles exist yet, it depends on the team's task creation
        # policy.
        self.assertTrue(can_create_task_subtitle(self.nonproject_video))

        # Any team member.
        team.task_assign_policy = Team.TASK_ASSIGN_IDS['Any team member']
        team.save()

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_create_task_subtitle(self.nonproject_video, user))

        self.assertFalse(can_create_task_subtitle(self.nonproject_video, outsider))

        # Manager+
        team.task_assign_policy = Team.TASK_ASSIGN_IDS['Managers and admins']
        team.save()

        for r in [ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_create_task_subtitle(self.nonproject_video, user))

        for r in [ROLE_CONTRIBUTOR]:
            with self.role(r):
                self.assertFalse(can_create_task_subtitle(self.nonproject_video, user))

        for r in [ROLE_MANAGER, ROLE_ADMIN]:
            with self.role(r, self.test_project):
                self.assertFalse(can_create_task_subtitle(self.nonproject_video, user))

        self.assertFalse(can_create_task_subtitle(self.nonproject_video, outsider))

        # Admin+
        team.task_assign_policy = Team.TASK_ASSIGN_IDS['Admins only']
        team.save()

        for r in [ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_create_task_subtitle(self.nonproject_video, user))

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER]:
            with self.role(r):
                self.assertFalse(can_create_task_subtitle(self.nonproject_video, user))

        for r in [ROLE_ADMIN]:
            with self.role(r, self.test_project):
                self.assertFalse(can_create_task_subtitle(self.nonproject_video, user))

        self.assertFalse(can_create_task_subtitle(self.nonproject_video, outsider))

        # Once a subtitle task exists, no one can create another.
        team.task_assign_policy = Team.TASK_ASSIGN_IDS['Any team member']
        team.save()

        t = Task(type=Task.TYPE_IDS['Subtitle'], team=team, team_video=self.nonproject_video)
        t.save()

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertFalse(can_create_task_subtitle(self.nonproject_video, user))

        # Even if it's completed.
        t.completed = datetime.datetime.now()
        t.save()

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertFalse(can_create_task_subtitle(self.nonproject_video, user))

        # Unless it's deleted, of course.
        t.deleted = True
        t.save()

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertTrue(can_create_task_subtitle(self.nonproject_video, user))

        # Once subtitles exist, no one can create a new task.
        _set_subtitles(self.nonproject_video, 'en', True, True)

        self.assertFalse(can_create_task_subtitle(self.nonproject_video))

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                self.assertFalse(can_create_task_subtitle(self.nonproject_video, user))

        self.assertFalse(can_create_task_subtitle(self.nonproject_video, outsider))

    def test_can_create_task_translate(self):
        team, user, outsider = self.team, self.user, self.outsider

        # When no subtitles exist yet, no translations can be created.
        self.assertEqual(can_create_task_translate(self.nonproject_video), [])

        # Add some sample subtitles.  Now we can create translation tasks
        # (but not to that language, since it's already done).
        _set_subtitles(self.nonproject_video, 'en', True, True)

        langs = can_create_task_translate(self.nonproject_video)

        self.assertEqual(len(langs), TOTAL_LANGS - 1)
        self.assertTrue('en' not in langs)

        # Languages with translations finished can't have new translation tasks.
        _set_subtitles(self.nonproject_video, 'en', True, True, ['fr', 'de'])

        langs = can_create_task_translate(self.nonproject_video)

        self.assertEqual(len(langs), TOTAL_LANGS - 3)
        self.assertTrue('en' not in langs)
        self.assertTrue('fr' not in langs)

        # Test role restrictions.
        _set_subtitles(self.nonproject_video, 'en', True, True, ['fr'])

        # Any team member.
        team.task_assign_policy = Team.TASK_ASSIGN_IDS['Any team member']
        team.save()

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                langs = can_create_task_translate(self.nonproject_video, user)

                self.assertEqual(len(langs), TOTAL_LANGS - 2)
                self.assertTrue('en' not in langs)
                self.assertTrue('fr' not in langs)

        langs = can_create_task_translate(self.nonproject_video, outsider)
        self.assertEqual(langs, [])

        # Managers+
        team.task_assign_policy = Team.TASK_ASSIGN_IDS['Managers and admins']
        team.save()

        for r in [ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                langs = can_create_task_translate(self.nonproject_video, user)

                self.assertEqual(len(langs), TOTAL_LANGS - 2)
                self.assertTrue('en' not in langs)
                self.assertTrue('fr' not in langs)

        for r in [ROLE_CONTRIBUTOR]:
            with self.role(r):
                langs = can_create_task_translate(self.nonproject_video, user)
                self.assertEqual(langs, [])

        for r in [ROLE_MANAGER, ROLE_ADMIN]:
            with self.role(r, self.test_project):
                langs = can_create_task_translate(self.nonproject_video, user)
                self.assertEqual(langs, [])

        langs = can_create_task_translate(self.nonproject_video, outsider)
        self.assertEqual(langs, [])

        # Admins+
        team.task_assign_policy = Team.TASK_ASSIGN_IDS['Admins only']
        team.save()

        for r in [ROLE_ADMIN, ROLE_OWNER]:
            with self.role(r):
                langs = can_create_task_translate(self.nonproject_video, user)

                self.assertEqual(len(langs), TOTAL_LANGS - 2)
                self.assertTrue('en' not in langs)
                self.assertTrue('fr' not in langs)

        for r in [ROLE_CONTRIBUTOR, ROLE_MANAGER]:
            with self.role(r):
                langs = can_create_task_translate(self.nonproject_video, user)
                self.assertEqual(langs, [])

        for r in [ROLE_ADMIN]:
            with self.role(r, self.test_project):
                langs = can_create_task_translate(self.nonproject_video, user)
                self.assertEqual(langs, [])

        langs = can_create_task_translate(self.nonproject_video, outsider)
        self.assertEqual(langs, [])

    # TODO: Review/approve task tests.
