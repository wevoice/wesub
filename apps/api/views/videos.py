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
Videos Resource
^^^^^^^^^^^^^^^

Get info for a specific video
+++++++++++++++++++++++++++++

.. http:get:: /api/videos/[video-id]/

    :>json id: Amara video id
    :>json primary_audio_language_code: language code for the audio language
    :>json title: Video title
    :>json description: Video description
    :>json duration: Video duration in seconds (or null if not known)
    :>json thumbnail: URL to the video thumbnail
    :>json created: Video creation date/time
    :>json team: Slug of the Video's team (or null)
    :>json metadata: Dict mapping metadata names to values
    :>json languages: List of languages that have subtitles started (see below)
    :>json video_type: Video type identifier
    :>json all_urls: List of URLs for the video (the first one is the primary
     video URL)
    :>json resource_uri: API uri for the video
    :>json original_language: contains a copy of the primary_audio_language_code
      data **(deprecated)**

    **Language data:**

    :>json code: Language code
    :>json name: Human readable label for the language
    :>json visibile: Are the subtitles publicly viewable?
    :>json dir: Language direction ("ltr" or "rtl")
    :>json subtitles_uri: API URI for the subtitles
    :>json resource_uri: API URI for the video language

Listing videos
++++++++++++++

.. http:get:: /api/videos/

    ``paginated``

    :query video_url:  list only videos with the given URL, useful for finding out information about a video already on Amara.
    :query team:       Only show videos that belong to a team identified by ``slug``.
    :query project:    Only show videos that belong to a project with the given slug.
        Passing in ``null`` will return only videos that don't belong to a project.
    :query order_by:   Applies sorting to the video list. Possible values:

        * `title`: ascending
        * `-title`: descending
        * `created`: older videos first
        * `-created` : newer videos

Creating Videos
+++++++++++++++

.. http:post:: /api/videos/

    :<json video_url: The url for the video. Any url that Amara accepts will 
        work here. You can send the URL for a file (e.g.
        http:///www.example.com/my-video.ogv), or a link to one of our
        accepted providers (youtube, vimeo, dailymotion)
    :<json title: title of the video
    :<json description: About this video
    :<json duration: Duration in seconds, in case it can not be retrieved automatically by Amara
    :<json primary_audio_language_code: language code for the main
        language spoken in the video.
    :<json thumbnail: URL to the video thumbnail
    :<json metadata: Dictionary of metadata key/value pairs.  These handle
        extra information about the video.  Right now the type keys supported
        are "speaker-name" and "location".  Values can be any string.
    :<json team: team slug for the video or null to remove it from its team.
    :<json project: project slug for the video or null to put it in the
        default project.

.. note::
    **Deprecated:** For all fields, if you pass an empty string, we will treat
    it as if the field was not present in the input.

    **Deprecated:** For slug and project, You can use the string "null" as a
    synonym for the null object.

When submitting URLs of external providers (i.e. youtube, vimeo), the metadata
(title, description, duration) can be fetched from them. If you're submitting
a link to a file (mp4, flv) then you can make sure those attributes are set
with these parameters. Note that these parameters (except the video duration)
override any information from the original provider or the file header.

Updating a video object
+++++++++++++++++++++++

.. http:put:: /api/videos/[video-id]/

With the same parameters for creation, excluding video_url. Note that through
out our system, a video cannot have its URLs changed. So you can change other
video attributes (title, description) but the URL sent must be the same
original one. As with creating video, an update can not override the duration
received from the provider or specified in the file header.

Moving videos between teams and projects
++++++++++++++++++++++++++++++++++++++++

To move a video from one team to another, you can make a put request with a
``team`` value.  Similarly, you can move a video to a different project using
the ``project`` field.  The user making the change must have permission to
remove a video from the originating team and permission to add a video to the
target team.

.. note::
    To move a video to a different project, the team must be specified in the
    payload even if it doesn't change.

Video URL Resource
^^^^^^^^^^^^^^^^^^

Listing video urls
++++++++++++++++++

.. http:get:: /api/videos/[video-id]/urls/

  ``paginated``

  :param video-id: Amara video ID
  :>json created: creation date/time
  :>json url: URL string
  :>json primary: is this the primary URL for the video?
  :>json original: was this the URL that was created with the video?
  :>json resource_uri: API URL for the video URL
  :>json id: Internal ID for the object **(deprecated, use resource_uri
       instead to create URLs for the object)**

Adding a video url
+++++++++++++++++++

.. http:post:: /api/videos/[video-id]/urls/

    :param video-id: Amara Video ID

    :<json url: Video URL.  This can be any URL that works in the add video
        form for the site (mp4 files, youtube, vimeo, etc).  Note: The URL
        cannot be in use by another video.
    :<json primary: If True, this URL will be made the primary URL
    :<json original: Is this is the first url for the video?

Get details on a single URL
+++++++++++++++++++++++++++

.. http:get:: [url-resource-uri]

    :param url-resource-url: resource_uri returned from the video URLs listing

    The response fields are the same as for the list endpoint

Make a URL the primary URL for a video
++++++++++++++++++++++++++++++++++++++

.. http:put:: [url-resource-uri]

    :param url-resource-url: resource_uri returned from the video URLs listing
    :<json primary: True to make the URL the primary URL.  This will unset the
                    primary flag for all other URLs.
    :<json original: Is this is the first url for the video?

Deleting URLs
+++++++++++++

.. http:delete:: [url-resource-uri]

    :param url-resource-url: resource_uri returned from the video URLs listing

.. note:

    A video must have a primary URL.  If this the primary URL for a video, the
    request will fail with a 400 code.
"""

from __future__ import absolute_import

from django import http
from django.db.models import Q
from django.db.models.query import QuerySet
from rest_framework import filters
from rest_framework import generics
from rest_framework import mixins
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticatedOrReadOnly
import json

from .apiswitcher import APISwitcherMixin
from api.fields import LanguageCodeField, TimezoneAwareDateTimeField
from api.pagination import AmaraPaginationMixin
from teams import permissions as team_perms
from teams.models import Team, TeamVideo, Project
from subtitles.models import SubtitleLanguage
from videos import metadata
from videos.models import Video
from videos.types import video_type_registrar
import videos.tasks

class VideoLanguageShortSerializer(serializers.Serializer):
    code = serializers.CharField(source='language_code')
    name = serializers.CharField(source='get_language_code_display')
    visible = serializers.BooleanField(source='has_public_version')
    dir = serializers.CharField()
    subtitles_uri = serializers.SerializerMethodField()
    resource_uri = serializers.SerializerMethodField()

    def get_resource_uri(self, language):
        kwargs = {
            'video_id': language.video.video_id,
            'language_code': language.language_code,
        }
        return reverse('api:subtitle-language-detail', kwargs=kwargs,
                       request=self.context['request'])

    def get_subtitles_uri(self, language):
        kwargs = {
            'video_id': language.video.video_id,
            'language_code': language.language_code,
        }
        return reverse('api:subtitles', kwargs=kwargs,
                       request=self.context['request'])

class VideoMetadataSerializer(serializers.Serializer):
    default_error_messages = {
        'unknown-key': "Unknown metadata key: {name}",
    }
    def __init__(self, *args, **kwargs):
        super(VideoMetadataSerializer, self).__init__(*args, **kwargs)
        for name in metadata.all_names():
            self.fields[name] = serializers.CharField(required=False)

    def get_attribute(self, video):
        return video.get_metadata()

    def to_internal_value(self, data):
        for key in data:
            if key not in self.fields:
                self.fail('unknown-key', name=key)
        return data

class TeamSerializer(serializers.CharField):
    default_error_messages = {
        'unknown-team': 'Unknown team: {team}',
    }

    def get_attribute(self, video):
        team_video = video.get_team_video()
        return team_video.team.slug if team_video else None

    def to_internal_value(self, slug):
        try:
            return Team.objects.get(slug=slug)
        except Team.DoesNotExist:
            self.fail('unknown-team', team=slug)

class ProjectSerializer(serializers.CharField):
    def get_attribute(self, video):
        team_video = video.get_team_video()
        if not team_video:
            return None
        elif team_video.project.is_default_project:
            return None
        else:
            return team_video.project.slug

class VideoListSerializer(serializers.ListSerializer):
    def to_representation(self, qs):
        # Do some optimizations to reduce the number of queries before passing
        # the result to the default to_representation() method

        if isinstance(qs, QuerySet):
            # Note: we have to use prefetch_related the teamvideo attributes,
            # otherwise it will filter out non-team videos.  I think this is a
            # django 1.4 bug.
            qs = (qs.select_related('teamvideo')
                  .prefetch_related('teamvideo__team', 'teamvideo__project',
                                    'newsubtitlelanguage_set', 'videourl_set'))
        # run bulk_has_public_version(), otherwise we have a query for each
        # language of each video
        videos = list(qs)
        all_languages = []
        for v in videos:
            all_languages.extend(v.all_subtitle_languages())
        SubtitleLanguage.bulk_has_public_version(all_languages)
        return super(VideoListSerializer, self).to_representation(videos)

class VideoSerializer(serializers.Serializer):
    # Note we could try to use ModelSerializer, but we are so far from the
    # default implementation that it makes more sense to not inherit.
    id = serializers.CharField(source='video_id', read_only=True)
    video_url = serializers.URLField(write_only=True, required=True)
    video_type = serializers.SerializerMethodField()
    primary_audio_language_code = LanguageCodeField(required=False,
                                                    allow_blank=True)
    original_language = serializers.CharField(source='language',
                                              read_only=True)
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    duration = serializers.IntegerField(required=False)
    thumbnail = serializers.URLField(required=False, allow_blank=True)
    created = TimezoneAwareDateTimeField(read_only=True)
    team = TeamSerializer(required=False, allow_null=True)
    project = ProjectSerializer(required=False, allow_null=True)
    all_urls = serializers.SerializerMethodField()
    metadata = VideoMetadataSerializer(required=False)
    languages = VideoLanguageShortSerializer(source='all_subtitle_languages',
                                             many=True, read_only=True)
    resource_uri = serializers.HyperlinkedIdentityField(
        view_name='api:video-detail',
        lookup_field='video_id')

    default_error_messages = {
        'project-without-team': "Can't specify project without team",
        'unknown-project': 'Unknown project: {project}',
        'video-exists': 'Video already exists for {url}',
        'invalid-url': 'Invalid URL: {url}',
    }

    class Meta:
        list_serializer_class = VideoListSerializer

    def __init__(self, *args, **kwargs):
        super(VideoSerializer, self).__init__(*args, **kwargs)
        if self.instance:
            # video_url should only be sent for creation
            self.fields['video_url'].read_only = True

    @property
    def team_video(self):
        if self.instance:
            return self.instance.get_team_video()
        else:
            return None

    def get_all_urls(self, video):
        video_urls = list(video.get_video_urls())
        video_urls.sort(key=lambda vurl: vurl.primary, reverse=True)
        return [vurl.url for vurl in video_urls]

    def get_video_type(self, video):
        types = set()
        for url in video.get_video_urls():
            video_type = video_type_registrar.video_type_for_url(url.url)
            if video_type is not None:
                types.add(video_type)
        if len(types) == 1:
            return types.pop().abbreviation
        return ""

    def will_add_video_to_team(self):
        if not self.team_video:
            return 'team' in self.validated_data
        if 'team' in self.validated_data:
            if self.validated_data['team'] != self.team_video.team:
                return True
            if 'project' in self.validated_data:
                if self.validated_data['project'] != self.team_video.project:
                    return True
        return False

    def will_remove_video_from_team(self):
        if 'team' not in self.validated_data or not self.team_video:
            return False
        return self.team_video.team != self.validated_data['team']

    def to_internal_value(self, data):
        data = self.fixup_data(data)
        data = super(VideoSerializer, self).to_internal_value(data)
        # we have to wait until now because we can't fetch the project until
        # we know the team
        if data.get('project'):
            if not data.get('team'):
                self.fail('project-without-team')
            try:
                data['project'] = Project.objects.get(team=data['team'],
                                                      slug=data['project'])
            except Project.DoesNotExist:
                self.fail('unknown-project', project=data['project'])
        return data

    def fixup_data(self, data):
        """Alter incoming data to support deprecated behavior."""
        # iterate over data to build a new dictionary.  This is required
        # because data is a MergeDict, which has issues with deletion.
        new_data = {}
        for name, value in data.items():
            # Remove any field has the empty string as its value
            # This is deprecated behavior form the old API.
            if value == '':
                continue
            # Replace "null" with None for team/project
            if name in ('team', 'project') and value == 'null':
                value = None
            new_data[name] = value
        return new_data

    def to_representation(self, video):
        data = super(VideoSerializer, self).to_representation(video)
        # convert blank language codes to None
        if video.primary_audio_language_code == '':
            data['primary_audio_language_code'] = None
            data['original_language'] = None
        return data

    def create(self, validated_data):
        set_values = {}
        for key in ('title', 'description', 'duration', 'thumbnail',
                    'primary_audio_language_code', 'metadata'):
            if key in validated_data:
                set_values[key] = validated_data[key]
        video, created = Video.get_or_create_for_url(
            validated_data['video_url'], user=self.context['user'],
            set_values=set_values,
        )
        if video is None:
            self.fail('invalid-url', url=validated_data['video_url'])
        if not created:
            self.fail('video-exists', url=validated_data['video_url'])
        self._update_team(video, validated_data)
        return video

    def update(self, video, validated_data):
        simple_fields = (
            'title', 'description', 'duration', 'thumbnail',
            'primary_audio_language_code',
        )
        for field_name in simple_fields:
            if field_name in validated_data:
                if field_name == "duration":
                    if not getattr(video, field_name):
                        setattr(video, field_name, validated_data[field_name])
                else:
                    setattr(video, field_name, validated_data[field_name])
        if validated_data.get('metadata'):
            video.update_metadata(validated_data['metadata'], commit=True)
        else:
            video.save()
        self._update_team(video, validated_data)
        return video

    def _update_team(self, video, validated_data):
        if 'team' not in validated_data:
            return
        team = validated_data['team']
        project = validated_data.get('project')
        team_video = video.get_team_video()
        if team is None:
            if team_video:
                team_video.delete()
        else:
            if project is None:
                project = team.default_project
            if team_video:
                team_video.move_to(team, project)
            else:
                TeamVideo.objects.create(video=video, team=team,
                                         project=project)
        video.clear_team_video_cache()

class VideoViewSet(AmaraPaginationMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = VideoSerializer
    queryset = Video.objects.all()
    paginate_by = 20

    lookup_field = 'video_id'
    lookup_value_regex = r'(\w|-)+'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('title', 'created')

    def get_serializer_context(self):
        return {
            'request': self.request,
            'user': self.request.user,
        }

    def get_queryset(self):
        query_params = self.request.query_params
        if 'team' not in query_params:
            qs = self.get_videos_for_user()
        else:
            qs = self.get_videos_for_team(query_params)
        if 'video_url' in query_params:
            vt = video_type_registrar.video_type_for_url(query_params['video_url'])
            if vt:
                qs = qs.filter(videourl__url=vt.convert_to_video_url())
            else:
                qs = qs.filter(videourl__url=query_params['video_url'])
        return qs

    def get_videos_for_user(self):
        visibility = Q(is_visible=True)
        if self.request.user.is_authenticated():
            members = self.request.user.team_members.all()
            visibility = visibility | Q(id__in=members.values_list('team_id'))
        user_visible_teams = Team.objects.filter(visibility)
        return Video.objects.filter(
            Q(teamvideo__isnull=True) |
            Q(teamvideo__team__in=user_visible_teams))

    def get_videos_for_team(self, query_params):
        try:
            team = Team.objects.get(slug=query_params['team'])
        except Team.DoesNotExist:
            return Video.objects.none()
        if not team.user_can_view_videos(self.request.user):
            return Video.objects.none()

        if 'project' in query_params:
            if query_params['project'] != 'null':
                project_slug = query_params['project']
            else:
                project_slug = "_root"
            try:
                project = team.project_set.get(slug=project_slug)
            except Project.DoesNotExist:
                return Video.objects.none()
            return Video.objects.filter(teamvideo__project=project)
        else:
            return Video.objects.filter(teamvideo__team=team)

    def get_object(self):
        try:
            video = (Video.objects
                     .select_related('teamvideo')
                     .get(video_id=self.kwargs['video_id']))
        except Video.DoesNotExist:
            if self.request.user.is_staff:
                raise http.Http404
            else:
                raise PermissionDenied()
        workflow = video.get_workflow()
        if not workflow.user_can_view_video(self.request.user):
            raise PermissionDenied()
        SubtitleLanguage.bulk_has_public_version(
            video.all_subtitle_languages())
        return video

    def check_save_permissions(self, serializer):
        team = serializer.validated_data.get('team')
        project = serializer.validated_data.get('project')
        if serializer.will_add_video_to_team():
            if not team_perms.can_add_video(team, self.request.user, project):
                raise PermissionDenied()
        if serializer.will_remove_video_from_team():
            team_video = serializer.instance.get_team_video()
            if not team_perms.can_remove_video(team_video, self.request.user):
                raise PermissionDenied()

    def perform_create(self, serializer):
        self.check_save_permissions(serializer)
        return serializer.save()

    def perform_update(self, serializer):
        self.check_save_permissions(serializer)
        video = serializer.save()
        videos.tasks.video_changed_tasks.delay(video.pk)
        return video

class VideoURLSerializer(serializers.Serializer):
    created = TimezoneAwareDateTimeField(read_only=True)
    url = serializers.CharField()
    primary = serializers.BooleanField(required=False)
    original = serializers.BooleanField(required=False)
    id = serializers.IntegerField(read_only=True)
    resource_uri = serializers.SerializerMethodField()

    def get_resource_uri(self, video_url):
        return reverse('api:video-url-detail', kwargs={
            'video_id': self.context['video'].video_id,
            'pk': video_url.id,
        }, request=self.context['request'])

    def create(self, validated_data):
        vt = video_type_registrar.video_type_for_url(validated_data['url'])

        new_url = self.context['video'].videourl_set.create(
            url=validated_data['url'],
            original=validated_data.get('original', False),
            type=vt.abbreviation,
            added_by=self.context['user'],
        )
        if validated_data.get('primary'):
            new_url.make_primary()
        return new_url

    def update(self, video_url, validated_data):
        if ('original' in validated_data and
            validated_data['original'] != video_url.original):
            video_url.original = validated_data['original']
            video_url.save()

        if validated_data.get('primary'):
            video_url.make_primary()

        return video_url

class VideoURLUpdateSerializer(VideoURLSerializer):
    url = serializers.CharField(read_only=True)

class VideoURLViewSet(AmaraPaginationMixin, viewsets.ModelViewSet):
    serializer_class = VideoURLSerializer
    update_serializer_class = VideoURLUpdateSerializer

    def get_serializer_class(self):
        if 'pk' in self.kwargs:
            return self.update_serializer_class
        else:
            return self.serializer_class

    @property
    def video(self):
        if not hasattr(self, '_video'):
            self._video = Video.objects.get(video_id=self.kwargs['video_id'])
        return self._video

    def get_queryset(self):
        return self.video.videourl_set.all().select_related('video')

    def perform_destroy(self, instance):
        if instance.primary:
            raise serializers.ValidationError("Can't delete the primary URL")
        instance.delete()

    def get_serializer_context(self):
        return {
            'video': self.video,
            'user': self.request.user,
            'request': self.request,
        }

class VideoViewSetSwitcher(APISwitcherMixin, VideoViewSet):
    switchover_date = 20150716

    class Deprecated(VideoViewSet):
        class serializer_class(VideoSerializer):
            created = serializers.DateTimeField(read_only=True)

class VideoURLViewSetSwitcher(APISwitcherMixin, VideoURLViewSet):
    switchover_date = 20150716

    class Deprecated(VideoURLViewSet):
        class serializer_class(VideoURLSerializer):
            created = serializers.DateTimeField(read_only=True)

        class update_serializer_class(VideoURLUpdateSerializer):
            created = serializers.DateTimeField()
