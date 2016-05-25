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

from __future__ import absolute_import
from datetime import datetime
import time

from django.test import TestCase
from nose.tools import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory

from api.tests.utils import format_datetime_field
from comments.models import Comment
from subtitles import pipeline
from utils.factories import *
from activity.models import ActivityRecord

class ActivityTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('api:activity-list')
        # create a bunch of activity records of various types
        self.team = TeamFactory()
        self.team_member = TeamMemberFactory(user=self.user, team=self.team)
        self.video = VideoFactory(user=self.user)
        TeamVideoFactory(video=self.video, team=self.team)
        self.user2 = UserFactory()
        ActivityRecord.objects.create_for_video_added(self.video)
        self.video.title = 'new-title'
        self.video.save()
        v = pipeline.add_subtitles(self.video, 'en', None, author=self.user)
        ActivityRecord.objects.create_for_subtitle_version(v)
        ActivityRecord.objects.create_for_version_approved(v, self.user2)
        ActivityRecord.objects.create_for_version_rejected(v, self.user2)
        ActivityRecord.objects.create_for_new_member(self.team_member)
        ActivityRecord.objects.create_for_member_deleted(self.team_member)
        self.record_qs = ActivityRecord.objects.all()

    def detail_url(self, record):
        return reverse('api:activity-detail', (record.id,))

    def filtered_list_url(self, filters):
        query = '&'.join('{}={}'.format(k, v) for k, v in filters.items())
        return '{}?{}'.format(self.list_url, query)

    def check_activity_data(self, activity_data, record):
        assert_equal(activity_data['id'], record.id)
        assert_equal(activity_data['type'], record.type_code)
        assert_equal(activity_data['type_name'], record.type)
        assert_equal(activity_data['created'],
                     format_datetime_field(record.created))
        if record.type == 'video-url-edited':
            assert_equal(activity_data['new_video_title'],
                         record.get_related_obj().new_title)
        else:
            assert_equal(activity_data['new_video_title'], None)
        if record.type == 'comment-added':
            assert_equal(activity_data['comment'],
                         record.get_related_obj().content)
        else:
            assert_equal(activity_data['comment'], None)
        assert_equal(activity_data['resource_uri'], reverse(
            'api:activity-detail', kwargs={'id': record.id},
            request=APIRequestFactory().get('/')))
        if record.video:
            assert_equal(activity_data['video'], record.video.video_id)
            assert_equal(activity_data['video_uri'], reverse(
                'api:video-detail', kwargs={
                         'video_id': record.video.video_id,
                }, request=APIRequestFactory().get('/'))
            )
        else:
            assert_equal(activity_data['video'], None)
            assert_equal(activity_data['video_uri'], None)
        if record.language_code:
            assert_equal(activity_data['language'], record.language_code)
            assert_equal(activity_data['language_url'], reverse(
                'api:subtitle-language-detail', kwargs={
                    'video_id': record.video.video_id,
                    'language_code': record.language_code,
                }, request=APIRequestFactory().get('/'))
            )
        else:
            assert_equal(activity_data['language'], None)
            assert_equal(activity_data['language_url'], None)
        if record.user:
            assert_equal(activity_data['user'], record.user.username)
        else:
            assert_equal(activity_data['user'], None)

    def test_list(self):
        activity_map = {a.id: a for a in self.record_qs}
        response = self.client.get(self.list_url)
        assert_equal(response.status_code, status.HTTP_200_OK)
        assert_items_equal([a['id'] for a in response.data['objects']],
                           activity_map.keys())
        for activity_data in response.data['objects']:
            self.check_activity_data(activity_data,
                                     activity_map[activity_data['id']])

    def test_detail(self):
        for record in self.record_qs:
            response = self.client.get(self.detail_url(record))
            assert_equal(response.status_code, status.HTTP_200_OK)
            self.check_activity_data(response.data, record)

    def check_filter(self, filters, correct_records):
        response = self.client.get(self.filtered_list_url(filters))
        assert_equal(response.status_code, status.HTTP_200_OK)
        assert_items_equal([a['id'] for a in response.data['objects']],
                           [a.id for a in correct_records])

    def test_team_filter(self):
        self.check_filter({
            'team': self.team.slug,
        }, ActivityRecord.objects.filter(team=self.team, video__isnull=False))

    def test_team_activity_flag(self):
        self.check_filter({
            'team': self.team.slug,
            'team-activity': 1,
        }, ActivityRecord.objects.filter(team=self.team, video__isnull=True))

    def test_video_filter(self):
        self.check_filter({
            'video': self.video.video_id,
        }, ActivityRecord.objects.filter(video=self.video))

    def test_type_filter(self):
        type_field = ActivityRecord._meta.get_field('type')
        for (slug, label) in type_field.choices:
            self.check_filter({
                'type': type_field.get_prep_value(slug),
            }, self.record_qs.filter(type=slug))

    def test_language_filter(self):
        self.check_filter({
            'language': 'en'
        }, self.record_qs.filter(language_code='en'))

    def _make_timestamp(self, datetime):
        return int(time.mktime(datetime.timetuple()))

    def test_before_and_after_filters(self):
        all_records = list(self.record_qs)
        old_records = all_records[:4]
        new_records = all_records[4:]
        (ActivityRecord.objects
         .filter(id__in=[a.id for a in old_records])
         .update(created=datetime(2014, 12, 31)))
        self.check_filter({
            'before': self._make_timestamp(datetime(2015, 1, 1))
        }, old_records)
        self.check_filter({
            'after': self._make_timestamp(datetime(2015, 1, 1))
        }, new_records)

    def test_comment(self):
        # Test the comment activity, which fills in the comment field
        Comment(content_object=self.video, user=self.user,
                content="Test Comment").save()
        record = ActivityRecord.objects.get(type='comment-added',
                                            video=self.video)
        response = self.client.get(self.detail_url(record))
        assert_equal(response.status_code, status.HTTP_200_OK)
        assert_equal(response.data['comment'], 'Test Comment')
        self.check_activity_data(response.data, record)

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
