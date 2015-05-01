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

from datetime import datetime
import time

from django.test import TestCase
from nose.tools import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory

from comments.models import Comment
from subtitles import pipeline
from utils.factories import *
from videos.models import Action

class ActivityTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('api:activity-list')
        # create a bunch of action objects of various types
        self.team = TeamFactory()
        self.team_member = TeamMemberFactory(user=self.user, team=self.team)
        self.video = VideoFactory()
        TeamVideoFactory(video=self.video, team=self.team)
        self.user2 = UserFactory()
        Action.create_video_handler(self.video, self.user)
        self.video.title = 'new-title'
        self.video.save()
        Action.change_title_handler(self.video, self.user)
        # creating comment will automatically create the action object
        Comment(content_object=self.video, user=self.user,
                content="Test Comment").save()
        v = pipeline.add_subtitles(self.video, 'en', None, author=self.user)
        Action.create_caption_handler(v, datetime.now())
        Action.create_approved_video_handler(v, self.user2)
        Action.create_rejected_video_handler(v, self.user2)
        Action.create_new_member_handler(self.team_member)
        Action.create_member_left_handler(self.team, self.user)
        self.action_qs = Action.objects.for_user(self.user)

    def detail_url(self, action):
        return reverse('api:activity-detail', (action.id,))

    def filtered_list_url(self, filters):
        query = '&'.join('{}={}'.format(k, v) for k, v in filters.items())
        return '{}?{}'.format(self.list_url, query)

    def check_activity_data(self, activity_data, activity):
        assert_equal(activity_data['type'], activity.action_type)
        assert_equal(activity_data['created'], activity.created.isoformat())
        assert_equal(activity_data['new_video_title'],
                     activity.new_video_title)
        assert_equal(activity_data['id'], activity.id)
        if activity.comment:
            assert_equal(activity_data['comment'], activity.comment.content)
        else:
            assert_equal(activity_data['comment'], None)
        assert_equal(activity_data['resource_uri'], reverse(
            'api:activity-detail', kwargs={'id': activity.id},
            request=APIRequestFactory().get('/')))
        if activity.video:
            assert_equal(activity_data['video'], activity.video.video_id)
            assert_equal(activity_data['video_uri'], reverse(
                'api:video-detail', kwargs={
                         'video_id': activity.video.video_id,
                }, request=APIRequestFactory().get('/'))
            )
        else:
            assert_equal(activity_data['video'], None)
            assert_equal(activity_data['video_uri'], None)
        if activity.new_language:
            assert_equal(activity_data['language'],
                         activity.new_language.language_code)
            assert_equal(activity_data['language_url'], reverse(
                'api:subtitle-language-detail', kwargs={
                    'video_id': activity.new_language.video.video_id,
                    'language_code': activity.new_language.language_code,
                }, request=APIRequestFactory().get('/'))
            )
        else:
            assert_equal(activity_data['language'], None)
            assert_equal(activity_data['language_url'], None)
        if activity.user:
            assert_equal(activity_data['user'], activity.user.username)
        else:
            assert_equal(activity_data['user'], None)

    def test_list(self):
        activity_map = {a.id: a for a in self.action_qs}
        response = self.client.get(self.list_url)
        assert_equal(response.status_code, status.HTTP_200_OK)
        assert_items_equal([a['id'] for a in response.data['objects']],
                           activity_map.keys())
        for activity_data in response.data['objects']:
            self.check_activity_data(activity_data,
                                     activity_map[activity_data['id']])

    def test_detail(self):
        for action in self.action_qs:
            response = self.client.get(self.detail_url(action))
            assert_equal(response.status_code, status.HTTP_200_OK)
            self.check_activity_data(response.data, action)

    def check_filter(self, filters, correct_actions):
        response = self.client.get(self.filtered_list_url(filters))
        assert_equal(response.status_code, status.HTTP_200_OK)
        assert_items_equal([a['id'] for a in response.data['objects']],
                           [a.id for a in correct_actions])

    def test_team_filter(self):
        self.check_filter({
            'team': self.team.slug,
        }, self.team.fetch_video_actions())

    def test_team_activity_flag(self):
        self.check_filter({
            'team': self.team.slug,
            'team-activity': 1,
        }, Action.objects.filter(team=self.team))

    def test_video_filter(self):
        self.check_filter({
            'video': self.video.video_id,
        }, Action.objects.for_video(self.video))

    def test_type_filter(self):
        for (type_id, label) in Action.TYPES:
            self.check_filter({
                'type': type_id,
            }, self.action_qs.filter(action_type=type_id))

    def test_language_filter(self):
        self.check_filter({
            'language': 'en'
        }, self.action_qs.filter(new_language__language_code='en'))

    def _make_timestamp(self, datetime):
        return int(time.mktime(datetime.timetuple()))

    def test_before_and_after_filters(self):
        all_actions = list(self.action_qs)
        old_actions = all_actions[:4]
        new_actions = all_actions[4:]
        (Action.objects
         .filter(id__in=[a.id for a in old_actions])
         .update(created=datetime(2014, 12, 31)))
        self.check_filter({
            'before': self._make_timestamp(datetime(2015, 1, 1))
        }, old_actions)
        self.check_filter({
            'after': self._make_timestamp(datetime(2015, 1, 1))
        }, new_actions)

    def test_team_filter_permission_check(self):
        # users should get a 403 response when trying to get activity for a
        # team that they are not a member of
        self.team_member.delete()
        url = self.filtered_list_url({'team': self.team.slug})
        response = self.client.get(url)
        assert_equal(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_video_filter_permission_check(self):
        # users should get a 403 response when trying to get activity for a
        # team video when they are not a member of the team
        self.team_member.delete()
        url = self.filtered_list_url({'video': self.video.video_id})
        response = self.client.get(url)
        assert_equal(response.status_code, status.HTTP_403_FORBIDDEN)
