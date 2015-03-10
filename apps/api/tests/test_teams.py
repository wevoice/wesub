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

from teams.models import Team
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
        teams = [TeamFactory() for i in range(3)]
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
