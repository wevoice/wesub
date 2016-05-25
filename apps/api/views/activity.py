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
"""
Activity
--------

Activity Resource
*****************

List activity
^^^^^^^^^^^^^

.. http:get:: /api/activity/

    :queryparam slug team: Show only items related to a given team
    :queryparam boolean team-activity: If team is given, we normally return
        activity on the team's videos.  If you want to see activity for the
        team itself (members joining/leaving and team video deletions, then
        add team-activity=1)
    :queryparam video-id video: Show only items related to a given video
    :queryparam integer type: Show only items with a given activity type.
        Possible values:

        1.  Add video
        2.  Change title
        3.  Comment
        4.  Add version
        5.  Add video URL
        6.  Add translation
        7.  Subtitle request
        8.  Approve version
        9.  Member joined
        10. Reject version
        11. Member left
        12. Review version
        13. Accept version
        14. Decline version
        15. Delete video

    :queryparam bcp-47 language: Show only items with a given language code
    :queryparam timestamp before: Only include items before this time
    :queryparam timestamp after: Only include items after this time

.. note::
    If both team and video are given as GET params, then team will be used and
    video will be ignored.

Get details on one activity item
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. http:get:: /api/activity/[activity-id]/

    :>json integer type: activity type.  The values are listed above
    :>json datetime created: date/time of the activity
    :>json video-id video: ID of the video
    :>json uri video_uri: Video Resource
    :>json bcp-47 language: language for the activity
    :>json uri language_url: Subtile Language Resource
    :>json uri resource_uri: Activity Resource
    :>json username user: username of the user user associated with the
        activity, or null
    :>json string comment: comment body for comment activity, null for other
        types
    :>json string new_video_title: new title for the title-change activity, null
        for other types
    :>json integer id: object id **(deprecated use resource_uri if you need to
        get details on a particular activity)**
"""

from __future__ import absolute_import

from datetime import datetime

from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.reverse import reverse

from activity.models import ActivityRecord
from api.fields import TimezoneAwareDateTimeField
from subtitles.models import SubtitleLanguage
from teams.models import Team
from videos.models import Video

class ActivitySerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(source='type_code')
    type_name = serializers.SlugField(source='type')
    user = serializers.CharField(source='user.username')
    comment = serializers.SerializerMethodField()
    new_video_title = serializers.SerializerMethodField()
    created = TimezoneAwareDateTimeField(read_only=True)
    video = serializers.CharField(source='video.video_id')
    video_uri = serializers.HyperlinkedRelatedField(
        source='video',
        view_name='api:video-detail',
        lookup_field='video_id',
        read_only=True)
    language = serializers.SerializerMethodField()
    language_url = serializers.SerializerMethodField()
    resource_uri = serializers.HyperlinkedIdentityField(
        view_name='api:activity-detail',
        lookup_field='id',
    )

    def get_language(self, record):
        return record.language_code or None

    def get_comment(self, record):
        if record.type == 'comment-added':
            return record.get_related_obj().content
        else:
            return None

    def get_new_video_title(self, record):
        if record.type == 'video-title-changed':
            return record.get_related_obj().new_title
        else:
            return None

    def get_language_url(self, record):
        if not (record.language_code and record.video):
            return None
        return reverse('api:subtitle-language-detail', kwargs={
            'video_id': record.video.video_id,
            'language_code': record.language_code,
        }, request=self.context['request'])

    class Meta:
        model = ActivityRecord
        fields = (
            'id', 'type', 'type_name', 'created', 'video', 'video_uri',
            'language', 'language_url', 'user', 'comment', 'new_video_title',
            'resource_uri'
        )

class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'id'
    serializer_class = ActivitySerializer
    paginate_by = 20

    def get_queryset(self):
        params = self.request.query_params
        if 'team' in params:
            try:
                team = Team.objects.get(slug=params['team'])
            except Team.DoesNotExist:
                return ActivityRecord.objects.none()
            if not team.user_is_member(self.request.user):
                raise PermissionDenied()
            qs = ActivityRecord.objects.for_team(team)
            if 'team-activity' in params:
                qs = qs.team_activity()
            else:
                qs = qs.team_video_activity()
        elif 'video' in params:
            try:
                video = Video.objects.get(video_id=params['video'])
            except Video.DoesNotExist:
                return ActivityRecord.objects.none()
            team_video = video.get_team_video()
            if (team_video and not
                team_video.team.user_is_member(self.request.user)):
                raise PermissionDenied()
            qs = video.activity.original()
        else:
            qs = ActivityRecord.objects.for_api_user(self.request.user)
        return qs.select_related(
                'video', 'user', 'language', 'language__video')

    def filter_queryset(self, queryset):
        params = self.request.query_params
        if 'type' in params:
            try:
                type_filter = int(params['type'])
            except ValueError:
                queryset = ActivityRecord.objects.none()
            else:
                queryset = queryset.filter(type=type_filter)
        if 'language' in params:
            queryset = queryset.filter(language_code=params['language'])
        if 'before' in params:
            queryset = queryset.filter(
                created__lt=datetime.fromtimestamp(int(params['before'])))
        if 'after' in params:
            queryset = queryset.filter(
                created__gte=datetime.fromtimestamp(int(params['after'])))
        return queryset
