from django.test import TestCase
from apps.teams.models import Team, TeamVideo, TeamMember, Workflow
from auth.models import CustomUser as User
from contextlib import contextmanager

from apps.teams.permissions_const import *
from apps.teams.permissions import (
    remove_role, add_role, can_message_all_members, can_add_video,
    can_assign_tasks, can_assign_role, _perms_for, roles_user_can_assign,
    add_narrowing_to_member, can_rename_team, can_view_settings_tab,
    can_change_team_settings, can_view_tasks_tab, can_invite,
    can_change_video_settings, can_review, can_message_all_members,
    can_edit_project, can_create_and_edit_subtitles
)


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

