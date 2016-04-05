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

from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.reverse import reverse

from api.fields import TimezoneAwareDateTimeField
from subtitles.models import SubtitleLanguage
from teams.models import Team
from videos.models import Action, Video

class ActivitySerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(source='action_type')
    user = serializers.CharField(source='user.username')
    comment = serializers.CharField(source='comment.content')
    created = TimezoneAwareDateTimeField(read_only=True)
    video = serializers.CharField(source='video.video_id')
    video_uri = serializers.HyperlinkedRelatedField(
        source='video',
        view_name='api:video-detail',
        lookup_field='video_id',
        read_only=True)
    language = serializers.CharField(source='new_language.language_code')
    language_url = serializers.SerializerMethodField()
    resource_uri = serializers.HyperlinkedIdentityField(
        view_name='api:activity-detail',
        lookup_field='id',
    )

    def get_language_url(self, action):
        if not action.new_language:
            return None
        return reverse('api:subtitle-language-detail', kwargs={
            'video_id': action.new_language.video.video_id,
            'language_code': action.new_language.language_code,
        }, request=self.context['request'])

    class Meta:
        model = Action
        fields = (
            'id', 'type', 'created', 'video', 'video_uri', 'language',
            'language_url', 'user', 'comment', 'new_video_title',
            'resource_uri'
        )

class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for activity.

    # Listing/Details #

    ## `GET /api/activity/`
    List activity items (paginated)

    ### Filter query params:

    - **slug team:** Show only items related to a given team
    - **team-activity:** If team is given, we normally return activity on the
       team's videos.  If you want to see activity for the team itself (members
       joining/leaving and team video deletions, then add team-activity=1)
    - **video:** Show only items related to a given video
    - **type:** Show only items with a given activity type (see
        below for values)
    - **language:** Show only items with a given language code
    - **before:** A unix timestamp in seconds
    - **after:** A unix timestamp in seconds

    **Note:** If both team and video are given as GET params, then team will
    be used and video will be ignored.

    ## `GET /api/activity/[activity-id]/`
    Get details on a single activity item

    ### Fields:

    - **type:** activity type as an integer.  Possible values:

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

    - **created:** date/time of the activity
    - **video:** ID of the video
    - **video_uri:** API URI for the video
    - **language:** language for the activity
    - **language_url:** API URI for the video language
    - **resource_uri:** API URI for the activity
    - **user:** username of the user user associated with the activity,
        or null
    - **comment:** comment body for comment activity, null for other types
    - **new_video_title:** new title for the title-change activity, null
        for other types
    - **id:** object id **(deprecated use resource_uri if you need to get
        details on a particular activity)**

    """

    lookup_field = 'id'
    serializer_class = ActivitySerializer
    paginate_by = 20

    def get_queryset(self):
        self.applied_language_filter = False
        params = self.request.query_params
        if 'team' in params:
            try:
                team = Team.objects.get(slug=params['team'])
            except Team.DoesNotExist:
                return Action.objects.none()
            if not team.user_is_member(self.request.user):
                raise PermissionDenied()
            if 'team-activity' in params:
                qs = Action.objects.filter(team=team)
            elif 'language' in params:
                language_qs = (
                    SubtitleLanguage.objects
                    .filter(language_code=params['language'],
                            video__teamvideo__team_id=team.id)
                    .values_list('id')
                )
                qs = Action.objects.filter(new_language_id__in=language_qs)
                self.applied_language_filter = True
            else:
                qs = team.fetch_video_actions()
        elif 'video' in params:
            try:
                video = Video.objects.get(video_id=params['video'])
            except Video.DoesNotExist:
                return Action.objects.none()
            team_video = video.get_team_video()
            if (team_video and not
                team_video.team.user_is_member(self.request.user)):
                raise PermissionDenied()
            qs = Action.objects.for_video(video)
        else:
            qs = Action.objects.for_user(self.request.user)
        return qs.select_related(
                'video', 'user', 'language', 'language__video')

    def filter_queryset(self, queryset):
        params = self.request.query_params
        if 'type' in params:
            queryset = queryset.filter(action_type=params['type'])
        if 'language' in params and not self.applied_language_filter:
            queryset = queryset.filter(
                new_language__language_code=params['language'])
            self.applied_language_filter = True
        if 'before' in params:
            queryset = queryset.filter(
                created__lt=datetime.fromtimestamp(int(params['before'])))
        if 'after' in params:
            queryset = queryset.filter(
                created__gte=datetime.fromtimestamp(int(params['after'])))
        return queryset
