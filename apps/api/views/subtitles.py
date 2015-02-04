# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
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
Video Language Resource
^^^^^^^^^^^^^^^^^^^^^^^

Container for subtitles in a language for a video on Amara.

Listing video languages
+++++++++++++++++++++++

.. http:get:: /api2/partners/videos/[video-id]/languages/

    :>json language_code: BCP 47 code for this language
    :>json name: Human-readable name for this language
    :>json is_primary_audio_language: Is this language the primary language
        spoken in the video?
    :>json is_rtl: Is this language RTL?
    :>json resource_uri: API URL for the language
    :>json created: date/time the language was created
    :>json title: Video title, translated into this language
    :>json description: Video description, translated into this language
    :>json metadata: Video metadata, translated into this language
    :>json subtitles_complete: Are the subtitles complete for this language?
    :>json subtitle_count: Number of subtitles for this language
    :>json reviewer: Username of the reviewer fro task-based teams
    :>json approver: Username of the approver for task-based teams
    :>json is_translation: Is this language translated from other languages
        **(deprecated)**
    :>json original_language_code: Source translation language **(deprecated)**
    :>json num_versions: Number of subtitle versions, the length of the
        versions array should be used instead of this **(deprecated)**
    :>json id: Internal ID for the language **(deprecated)**
    :>json is_original: alias for is_primary_audio_language **(deprecated)**
    :>json versions: List of subtitle version data
    :>json versions.author: Subtitle author's username
    :>json versions.version_no: number of the version 
    :>json versions.published: is this version publicly viewable?

.. note:
    The `original_language_code` and `is_translation` fields are remnants
    from the old subtitle system.  With the new editor, users can use multiple
    languages as a translation source.  These fields are should not be relied
    on.

Creating Video Languages
++++++++++++++++++++++++

.. http:post:: /api2/partners/videos/[video-id]/languages/

    :form language_code: bcp-47 code for the language
    :form is_primary_audio_language: Boolean indicating if this is the primary
        spoken language of the video *(optional)*.
    :form subtitles_complete: Boolean indicating if the subtitles for this
        languagge is complete *(optional)*.
    :form is_original: Alias for is_primary_audio_language **(deprecated)**
    :form is_complete: Alias for subtitles_complete  **(deprecated)**

Getting details on a specific language
++++++++++++++++++++++++++++++++++++++

.. http:get:: /api2/partners/videos/[video-id]/languages/[lang-identifier]/

    :param lang-identifier: language code to fetch.  **deprecated:** this can
        also be value from the id field

.. seealso::  To list available languages, see ``Language Resource``.

Subtitles Action Resource
^^^^^^^^^^^^^^^^^^^^^^^^^

Actions are operations on subtitles.  Actions correspond to the buttons in the
upper-right hand corner of the subtitle editor (save, save a draft, approve,
reject, etc).  This resource is used to list and perform actions on the
subtitle set.

.. note:: You can also perform an action together a new set of subtitles using
    the action param of the :ref:`old-subtitles-resource`.

Get the list of possible actions:

.. http:get:: /api/videos/[video-id]/languages/[lang-identifier]/subtitles/actions/

    :param video-id: ID of the video
    :param lang-identifier: subtitle language code
    :>json action: Action name
    :>json label: Human-friendly string for the action
    :>json complete: Does this action complete the subtitles?  If true, then
        when the action is performed, we will mark the subtitles complete.  If
        false, we will mark them incomplete.  If null, then we will not change
        the subtitles_complete flag.

Perform an action on a subtitle set

.. http:post:: /api/videos/[video-id]/languages/[lang-identifier]/subtitles/actions/

    :query video-id: ID of the video
    :query lang-identifier: subtitle language code
    :<json action: name of the action to perform

Subtitles Notes Resource
^^^^^^^^^^^^^^^^^^^^^^^^

Get/Create notes saved in the editor.

.. note:: Subtitle notes are currently only supported for team videos

Get the list of notes:

.. http:get:: /api/videos/[video-id]/languages/[lang-identifier]/subtitles/notes

    :query video-id: ID of the video
    :query lang-identifier: subtitle language code
    :>json user: Username of the note author
    :>json created: date/time that the note was created
    :>json body: text of the note.


Create a new note

.. http:post:: /api/videos/[video-id]/languages/[lang-identifier]/subtitles/actions/

    :query video-id: ID of the video
    :query lang-identifier: subtitle language code
    :<json body: note body
"""

from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework import mixins
from rest_framework import serializers
from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from api.pagination import AmaraPaginationMixin
from api.views.videos import VideoMetadataSerializer
from videos.models import Video
from subtitles import compat
from subtitles import workflows
from subtitles.models import SubtitleLanguage
from subtitles.exceptions import ActionError
import videos.tasks

class MiniSubtitleVersionSerializer(serializers.Serializer):
    """Serialize a subtitle version for SubtitleLanguageSerializer """
    author = serializers.CharField(source='author.username')
    published = serializers.BooleanField(source='is_public')
    version_no = serializers.IntegerField(source='version_number')

class MiniSubtitleVersionsField(serializers.ListField):
    """Serialize the list of versions for SubtitleLanguageSerializer """
    child = MiniSubtitleVersionSerializer()

    def get_attribute(self, language):
        return self.parent.get_version_list(language)

class SubtitleLanguageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    language_code = serializers.CharField()
    is_primary_audio_language = serializers.BooleanField()
    is_rtl = serializers.BooleanField(read_only=True)
    is_translation = serializers.SerializerMethodField()
    original_language_code = serializers.SerializerMethodField()
    name = serializers.CharField(source='get_language_code_display',
                                 read_only=True)
    title = serializers.CharField(source='get_title', read_only=True)
    description = serializers.CharField(source='get_description',
                                        read_only=True)
    metadata = VideoMetadataSerializer(required=False, read_only=True)
    subtitle_count = serializers.IntegerField(read_only=True,
                                              source='get_subtitle_count')
    subtitles_complete = serializers.BooleanField()
    versions = MiniSubtitleVersionsField(read_only=True)
    resource_uri = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(SubtitleLanguageSerializer, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['language_code'].read_only = True

    def get_version_list(self, language):
        show_private_versions = self.context['show_private_versions']
        if show_private_versions(language.language_code):
            qs = language.subtitleversion_set.extant()
        else:
            qs = language.subtitleversion_set.public()
        return qs.order_by('-version_number')

    def get_is_translation(self, language):
        return compat.subtitlelanguage_is_translation(language)

    def get_original_language_code(self, language):
        return compat.subtitlelanguage_original_language_code(language)

    def get_resource_uri(self, language):
        return reverse('api:video-language-detail', kwargs={
            'video_id': language.video.video_id,
            'language_code': language.language_code,
        })

    def to_representation(self, language):
        data = super(SubtitleLanguageSerializer, self).to_representation(
            language)
        data['num_versions'] = len(data['versions'])
        data['is_original'] = data['is_primary_audio_language']
        self.add_reviewer_and_approver(data, language)
        return data

    def add_reviewer_and_approver(self, data, language):
        """Add the reviewer/approver fields."""
        for version in self.get_version_list(language):
            reviewer = version.get_reviewed_by()
            approver = version.get_approved_by()
            if reviewer:
                data['reviewer'] = reviewer.username
            if approver:
                data['approver'] = approver.username

    def create(self, validated_data):
        language = SubtitleLanguage(
            video=self.context['video'],
            language_code=validated_data['language_code'])
        return self.update(language, validated_data)

    def update(self, language, validated_data):
        subtitles_complete = validated_data.get(
            'subtitles_complete',
            validated_data.get('is_complete', None))
        primary_audio_language = validated_data.get(
            'is_primary_audio_language',
            validated_data.get('is_original', None))

        video = self.context['video']
        if subtitles_complete is not None:
            language.subtitles_complete = subtitles_complete
            language.save()
        if primary_audio_language is not None:
            video.primary_audio_language_code = language.language_code
            video.save()
        videos.tasks.video_changed_tasks.delay(video.pk)
        return language

class SubtitleLanguageViewSet(AmaraPaginationMixin, viewsets.ModelViewSet):
    serializer_class = SubtitleLanguageSerializer
    paginate_by = 20

    lookup_field = 'language_code'
    lookup_value_regex = r'\w+'

    @property
    def video(self):
        if not hasattr(self, '_video'):
            self._video = get_object_or_404(Video,
                                            video_id=self.kwargs['video_id'])
        return self._video

    def get_queryset(self):
        workflow = self.video.get_workflow()
        if not workflow.user_can_view_video(self.request.user):
            raise PermissionDenied()
        return self.video.newsubtitlelanguage_set.all()

    def show_private_versions(self, language_code):
        workflow = self.video.get_workflow()
        return workflow.user_can_view_private_subtitles(self.request.user,
                                                        language_code)

    def get_serializer_context(self):
        return {
            'video': self.video,
            'show_private_versions': self.show_private_versions,
        }

class ActionsSerializer(serializers.Serializer):
    action = serializers.CharField(source='name')
    label = serializers.CharField(read_only=True)
    complete = serializers.BooleanField(read_only=True)

class Actions(views.APIView):
    def get_serializer(self, **kwargs):
        return ActionsSerializer(**kwargs)

    def get(self, request, video_id, language_code, format=None):
        video = get_object_or_404(Video, video_id=video_id)
        workflow = workflows.get_workflow(video)
        action_list = workflow.get_actions(request.user, language_code)
        serializer = ActionsSerializer(action_list, many=True)
        return Response(serializer.data)

    def post(self, request, video_id, language_code, format=None):
        try:
            action = request.DATA['action']
        except KeyError:
            return Response('no action', status=status.HTTP_400_BAD_REQUEST)
        video = get_object_or_404(Video, video_id=video_id)
        workflow = workflows.get_workflow(video)
        try:
            workflow.perform_action(request.user, language_code, action)
        except (ActionError, LookupError), e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        return Response('')

class NotesSerializer(serializers.Serializer):
    user = serializers.CharField(source='user.username', read_only=True)
    created = serializers.DateTimeField(read_only=True)
    body = serializers.CharField()

    def create(self, validated_data):
        return self.context['editor_notes'].post(
            self.context['user'], validated_data['body'])

class NotesList(generics.ListCreateAPIView):
    serializer_class = NotesSerializer

    @csrf_exempt
    def dispatch(self, request, **kwargs):
        self.editor_notes = self.get_editor_notes(**kwargs)
        return generics.ListCreateAPIView.dispatch(self, request, **kwargs)

    def get_editor_notes(self, **kwargs):
        video = get_object_or_404(Video, video_id=kwargs['video_id'])
        workflow = workflows.get_workflow(video)
        return workflow.get_editor_notes(kwargs['language_code'])

    def get_queryset(self):
        return self.editor_notes.notes

    def get_serializer_context(self):
        return {
            'editor_notes': self.editor_notes,
            'user': self.request.user,
        }
