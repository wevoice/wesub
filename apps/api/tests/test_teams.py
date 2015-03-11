# Amara, universalsubtitles.org
#
# Copyright (C) 2015 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.html.

from django.test import TestCase
from nose.tools import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
import mock

from auth.models import CustomUser as User
from teams.models import Team, TeamMember
from utils import test_utils
from utils.factories import *

class TeamAPITest(TestCase):
    @test_utils.patch_for_test('teams.permissions.can_delete_team')
    @test_utils.patch_for_test('teams.permissions.can_change_team_settings')
    @test_utils.patch_for_test('teams.permissions.can_create_team')
    def setUp(self, mock_can_create_team, mock_can_change_team_settings,
             mock_can_delete_team):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.list_url = reverse('api:teams-list')

        self.mock_can_create_team = mock_can_create_team
        self.mock_can_delete_team = mock_can_delete_team
        self.mock_can_change_team_settings = mock_can_change_team_settings
        mock_can_create_team.return_value = True
        mock_can_delete_team.return_value = True
        mock_can_change_team_settings.return_value = True

    def detail_url(self, team):
        return reverse('api:teams-detail', kwargs={
            'slug': team.slug,
        })

    def check_team_data(self, data, team):
        assert_equal(data['name'], team.name)
        assert_equal(data['slug'], team.slug)
        assert_equal(data['description'], team.description)
        assert_equal(data['is_visible'], team.is_visible)
        assert_equal(data['membership_policy'],
                     team.get_membership_policy_display())
        assert_equal(data['video_policy'], team.get_video_policy_display())

    def test_get_list(self):
        # we should display these teams
        teams = [
            TeamFactory(is_visible=True),
            TeamFactory(is_visible=False, membership_policy=Team.OPEN),
            TeamFactory(is_visible=False, membership_policy=Team.APPLICATION),
            TeamFactory(is_visible=False,
                        membership_policy=Team.INVITATION_BY_MANAGER,
                        member=self.user),
        ]
        # we should not display these teams
        TeamFactory(is_visible=False,
                    membership_policy=Team.INVITATION_BY_ALL)
        TeamFactory(is_visible=False,
                    membership_policy=Team.INVITATION_BY_MANAGER)
        TeamFactory(is_visible=False,
                    membership_policy=Team.INVITATION_BY_ADMIN)

        team_map = dict((t.slug, t) for t in teams)
        response = self.client.get(self.list_url)
        assert_equal(response.status_code, status.HTTP_200_OK)
        teams_data = response.data['objects']
        assert_items_equal([t['slug'] for t in teams_data], team_map.keys())
        for team_data in teams_data:
            self.check_team_data(team_data, team_map[team_data['slug']])

    def test_get_details(self):
        team = TeamFactory()
        response = self.client.get(self.detail_url(team))
        assert_equal(response.status_code, status.HTTP_200_OK)
        self.check_team_data(response.data, team)

    def test_create_team(self):
        response = self.client.post(self.list_url, data={
            'name': 'Test Team',
            'slug': 'test-team',
        })
        assert_equal(response.status_code, status.HTTP_201_CREATED,
                     response.content)
        team = Team.objects.get(slug='test-team')
        self.check_team_data(response.data, team)

    def test_create_team_with_data(self):
        response = self.client.post(self.list_url, data={
            'name': 'Test Team',
            'slug': 'test-team',
            'description': 'Test Description',
            'is_visible': False,
            'membership_policy': u'Invitation by any team member',
            'video_policy': u'Managers and admins',
        })
        assert_equal(response.status_code, status.HTTP_201_CREATED,
                     response.content)
        team = Team.objects.get(slug='test-team')
        self.check_team_data(response.data, team)

    def test_create_team_slug_collision(self):
        TeamFactory(slug='slug')
        response = self.client.post(self.list_url, data={
            'slug': 'slug',
            'name': 'Name',
        })
        assert_equal(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_policy_choice(self):
        response = self.client.post(self.list_url, data={
            'slug': 'slug',
            'name': 'Name',
            'membership_policy': 'invalid-choice',
            'video_policy': 'invalid-choice',
        })
        assert_equal(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_team(self):
        team = TeamFactory()
        response = self.client.put(self.detail_url(team), data={
            'name': 'New Name',
        })
        assert_equal(response.status_code, status.HTTP_200_OK,
                     response.content)
        team = test_utils.reload_obj(team)
        assert_equal(team.name, 'New Name')

    def test_delete_team(self):
        team = TeamFactory()
        team_id = team.id
        response = self.client.delete(self.detail_url(team))
        assert_false(Team.objects.filter(id=team_id).exists())

    def test_create_team_permissions(self):
        self.mock_can_create_team.return_value = False
        response = self.client.post(self.list_url, data={
            'slug': 'new-slug',
            'name': 'New Name',
        })
        assert_equal(response.status_code, status.HTTP_403_FORBIDDEN)
        assert_equal(self.mock_can_create_team.call_args, mock.call(self.user))

    def test_update_team_permissions(self):
        team = TeamFactory()
        self.mock_can_change_team_settings.return_value = False
        response = self.client.put(self.detail_url(team), data={
            'name': 'New Name',
        })
        assert_equal(response.status_code, status.HTTP_403_FORBIDDEN)
        assert_equal(self.mock_can_change_team_settings.call_args,
                     mock.call(team, self.user))

    def test_delete_team_permissions(self):
        team = TeamFactory()
        self.mock_can_delete_team.return_value = False
        response = self.client.delete(self.detail_url(team))
        assert_equal(response.status_code, status.HTTP_403_FORBIDDEN)
        assert_equal(self.mock_can_delete_team.call_args,
                     mock.call(team, self.user))

class TeamMemberAPITest(TestCase):
    @test_utils.patch_for_test('teams.permissions.can_add_member')
    @test_utils.patch_for_test('teams.permissions.can_assign_role')
    @test_utils.patch_for_test('teams.permissions.can_remove_member')
    def setUp(self, mock_can_remove_member, mock_can_assign_role,
              mock_can_add_member):
        self.user = UserFactory()
        self.team = TeamFactory(owner=self.user)
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.list_url = reverse('api:team-members-list', kwargs={
            'team_slug': self.team.slug,
        })

        self.mock_can_add_member = mock_can_add_member
        self.mock_can_assign_role = mock_can_assign_role
        self.mock_can_remove_member = mock_can_remove_member
        mock_can_add_member.return_value = True
        mock_can_assign_role.return_value = True
        mock_can_remove_member.return_value = True

    def detail_url(self, user):
        return reverse('api:team-members-detail', kwargs={
            'team_slug': self.team.slug,
            'username': user.username,
        })

    def test_add_team_member(self):
        user = UserFactory()
        response = self.client.post(self.list_url, data={
            'username': user.username,
            'role': 'contributor',
        })
        assert_equal(response.status_code, status.HTTP_201_CREATED,
                     response.content)
        member = self.team.members.get(user=user)
        assert_equal(member.role, TeamMember.ROLE_CONTRIBUTOR)

    def test_add_existing_team_member(self):
        user = TeamMemberFactory(team=self.team).user
        response = self.client.post(self.list_url, data={
            'username': user.username,
            'role': 'contributor',
        })
        assert_equal(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_role(self):
        member = TeamMemberFactory(team=self.team,
                                   role=TeamMember.ROLE_CONTRIBUTOR)
        response = self.client.put(self.detail_url(member.user), data={
            'role': 'admin',
        })
        assert_equal(response.status_code, status.HTTP_200_OK,
                     response.content)
        assert_equal(test_utils.reload_obj(member).role,
                     TeamMember.ROLE_ADMIN)

    def test_username_in_put(self):
        # test the username field being in a PUT request.  It doesn't really
        # make sense in this case so we should just ignore it
        member = TeamMemberFactory(team=self.team,
                                   role=TeamMember.ROLE_CONTRIBUTOR)
        response = self.client.put(self.detail_url(member.user), data={
            'username': 'foo',
            'role': 'admin',
        })
        assert_equal(response.status_code, status.HTTP_200_OK,
                     response.content)
        assert_equal(test_utils.reload_obj(member).role,
                     TeamMember.ROLE_ADMIN)

    def test_remove_member(self):
        member = TeamMemberFactory(team=self.team,
                                   role=TeamMember.ROLE_CONTRIBUTOR)
        user = member.user
        response = self.client.delete(self.detail_url(member.user))
        assert_equal(response.status_code, status.HTTP_204_NO_CONTENT,
                     response.content)
        assert_false(self.team.members.filter(user=user).exists())
    
    def test_cant_remove_owner(self):
        member = TeamMemberFactory(team=self.team, role=TeamMember.ROLE_OWNER)
        response = self.client.delete(self.detail_url(member.user))
        assert_equal(response.status_code, status.HTTP_400_BAD_REQUEST,
                     response.content)
        assert_true(self.team.members.filter(
            user=member.user, role=TeamMember.ROLE_OWNER).exists())

    def test_cant_remove_self(self):
        response = self.client.delete(self.detail_url(self.user))
        assert_equal(response.status_code, status.HTTP_400_BAD_REQUEST,
                     response.content)
        assert_true(self.team.members.filter(
            user=self.user, role=TeamMember.ROLE_OWNER).exists())

    def test_view_list_permissions(self):
        # only members can view the membership list
        non_member = UserFactory()
        self.client.force_authenticate(user=non_member)
        response = self.client.get(self.list_url)
        assert_equal(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_details_permissions(self):
        # only members can view details on a member
        non_member = UserFactory()
        self.client.force_authenticate(user=non_member)
        response = self.client.get(self.detail_url(self.user))
        assert_equal(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_checks_permissions(self):
        self.mock_can_add_member.return_value = False
        response = self.client.post(self.list_url, data={
            'username': UserFactory().username,
            'role': 'contributor',
        })
        assert_equal(response.status_code, status.HTTP_403_FORBIDDEN)
        assert_equal(self.mock_can_add_member.call_args,
                     mock.call(self.team, self.user))

    def test_change_checks_permissions(self):
#def can_assign_role(team, user, role, to_user):
        self.mock_can_assign_role.return_value = False
        member = TeamMemberFactory(team=self.team,
                                   role=TeamMember.ROLE_CONTRIBUTOR)
        response = self.client.put(self.detail_url(member.user), data={
            'username': member.user,
            'role': TeamMember.ROLE_ADMIN,
        })
        assert_equal(response.status_code, status.HTTP_403_FORBIDDEN)
        assert_equal(test_utils.reload_obj(member).role,
                     TeamMember.ROLE_CONTRIBUTOR)
        assert_equal(self.mock_can_assign_role.call_args,
                     mock.call(self.team, self.user, TeamMember.ROLE_ADMIN,
                               member.user))

    def test_remove_checks_permissions(self):
        self.mock_can_remove_member.return_value = False
        member = TeamMemberFactory(team=self.team,
                                   role=TeamMember.ROLE_CONTRIBUTOR)
        response = self.client.delete(self.detail_url(member.user))
        assert_equal(response.status_code, status.HTTP_403_FORBIDDEN)
        assert_true(self.team.members.filter(user=member.user).exists())
        assert_equal(self.mock_can_remove_member.call_args,
                     mock.call(self.team, self.user))

class SafeTeamMemberAPITest(TeamMemberAPITest):
    # The safe team member API should work the same as the regular team member
    # API for the most part.  So we subclass the unittest, but use different
    # URLs to test against

    @test_utils.patch_for_test('messages.tasks.team_invitation_sent')
    def setUp(self, mock_team_invitation_sent):
        super(SafeTeamMemberAPITest, self).setUp()
        self.mock_team_invitation_sent = mock_team_invitation_sent
        self.list_url = reverse('api:safe-team-members-list', kwargs={
            'team_slug': self.team.slug,
        })

    def detail_url(self, user):
        return reverse('api:safe-team-members-detail', kwargs={
            'team_slug': self.team.slug,
            'username': user.username,
        })

    def check_invitation(self, user):
        assert_false(self.team.members.filter(user=user).exists())
        invitation = self.team.invitations.get(user=user)
        assert_equal(self.mock_team_invitation_sent.delay.call_args,
                     mock.call(invitation.pk))

    def test_add_team_member(self):
        # When adding a team member, we should send an invite instead of
        # directly adding them
        user = UserFactory()
        response = self.client.post(self.list_url, data={
            'username': user.username,
            'role': 'contributor',
        })
        # we should return HTTP 202, since we created haven't created the team
        # member object yet
        assert_equal(response.status_code, status.HTTP_202_ACCEPTED,
                     response.content)
        self.check_invitation(user)

    def test_add_nonexistant_user(self):
        # We should create a user if the username doesn't exist
        response = self.client.post(self.list_url, data={
            'username': 'new-username',
            'email': 'new-user@example.com',
            'role': 'contributor',
        })
        assert_equal(response.status_code, status.HTTP_202_ACCEPTED,
                     response.content)
        user = User.objects.get(username='new-username')
        assert_equal(user.email, 'new-user@example.com')
        self.check_invitation(user)

    def test_need_email_if_user_doesnt_exist(self):
        # When creating a user, require the email.  Otherwise there is no way
        # to for the person to login since there's no password recovery.
        response = self.client.post(self.list_url, data={
            'username': 'new-username',
            'role': 'contributor',
        })
        assert_equal(response.status_code, status.HTTP_400_BAD_REQUEST)
