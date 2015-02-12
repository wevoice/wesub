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

import json

from django.http import Http404
from django.test import TestCase
from nose.tools import *
from rest_framework.exceptions import PermissionDenied
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory
import babelsubs
import mock

from api.views.subtitles import (SubtitleLanguageSerializer,
                                 SubtitleLanguageViewSet,
                                 SubtitlesSerializer,
                                 SubtitlesView)
from subtitles import compat
from subtitles import pipeline
from utils import test_utils
from utils.factories import *

class SubtitleLanguageSerializerTest(TestCase):
    def setUp(self):
        self.video = VideoFactory(primary_audio_language_code='en')
        self.user = UserFactory(is_staff=True)
        self.language = SubtitleLanguageFactory(video=self.video,
                                                language_code='en')
        self.show_private_versions = mock.Mock(return_value=True)
        self.serializer_context = {
            'video': self.video,
            'show_private_versions': self.show_private_versions,
            'request': APIRequestFactory().get("/mock-url/"),
        }
        self.serializer = SubtitleLanguageSerializer(
            context=self.serializer_context)

    def get_serializer_data(self):
        return self.serializer.to_representation(self.language)

    def test_fields(self):
        serializer_data = self.get_serializer_data()
        assert_equal(serializer_data['id'], self.language.id)
        assert_equal(serializer_data['created'],
                     self.language.created.isoformat())
        assert_equal(serializer_data['is_original'], True)
        assert_equal(serializer_data['is_primary_audio_language'], True)
        assert_equal(serializer_data['is_rtl'], self.language.is_rtl())
        assert_equal(serializer_data['language_code'],
                     self.language.language_code)
        assert_equal(serializer_data['name'],
                     self.language.get_language_code_display())
        assert_equal(serializer_data['title'], self.language.get_title())
        assert_equal(serializer_data['description'],
                     self.language.get_description())
        assert_equal(serializer_data['metadata'],
                     self.language.get_metadata())
        assert_equal(serializer_data['subtitle_count'],
                     self.language.get_subtitle_count())
        assert_equal(serializer_data['subtitles_complete'],
                     self.language.subtitles_complete)
        assert_equal(serializer_data['is_translation'],
                     compat.subtitlelanguage_is_translation(self.language))
        assert_equal(
            serializer_data['original_language_code'],
            compat.subtitlelanguage_original_language_code(self.language))
        assert_equal(serializer_data['resource_uri'],
                     reverse('api:subtitle-language-detail', kwargs={
                             'video_id': self.video.video_id,
                             'language_code': self.language.language_code,
                     }, request=APIRequestFactory().get("/")))

    def make_version(self, language_code, **kwargs):
        return pipeline.add_subtitles(self.video, language_code,
                                      SubtitleSetFactory(), **kwargs)

    def test_versions_field(self):
        self.make_version('en', visibility='public',
                          author=UserFactory(username='user1'))
        self.make_version('en', visibility='private',
                          author=UserFactory(username='user2'))

        serializer_data = self.get_serializer_data()
        assert_equal(serializer_data['num_versions'], 2)
        assert_equal(serializer_data['versions'], [
            {
                'author': 'user2',
                'published': False,
                'version_no': 2,
            },
            {
                'author': 'user1',
                'published': True,
                'version_no': 1,
            },
        ])

    def test_hiding_private_versions(self):
        # Test show_private_versions being False
        self.show_private_versions.return_value = False
        self.make_version('en', visibility='private', author=self.user)
        self.make_version('en', visibility='public', author=self.user)

        serializer_data = self.get_serializer_data()
        assert_equal(serializer_data['num_versions'], 1)
        assert_equal(serializer_data['versions'], [
            {
                'author': self.user.username,
                'published': True,
                'version_no': 2,
            },
        ])
        # check the arguments passed to show_private_versions
        assert_equal(self.show_private_versions.call_args,
                     mock.call('en'))

    def test_reviewed_and_approved_by(self):
        # For reviewed_by and approved_by, the values are set on subtitle
        # versions, but we return it for the language as a whole.
        #
        # We should return the value from the earliest version in the
        # language.  This seems wrong, but that's how we originally
        # implemented it.
        u1 = UserFactory(username='user1')
        u2 = UserFactory(username='user2')
        u3 = UserFactory(username='user3')
        v1 = self.make_version('en')
        v2 = self.make_version('en')
        v3 = self.make_version('en')
        v1.set_reviewed_by(u1)
        v2.set_reviewed_by(u2)
        v2.set_approved_by(u2)
        v3.set_approved_by(u3)

        serializer_data = self.get_serializer_data()
        assert_equal(serializer_data['reviewer'], 'user1')
        assert_equal(serializer_data['approver'], 'user2')

    def test_create(self):
        language = self.serializer.create({
            'language_code': 'es',
            'is_primary_audio_language': True,
            'subtitles_complete': True,
        })
        assert_equal(language.video, self.video)
        assert_equal(language.language_code, 'es')
        assert_equal(self.video.primary_audio_language_code, 'es')
        assert_equal(language.subtitles_complete, True)
        test_utils.assert_saved(language)
        test_utils.assert_saved(self.video)

    def test_update(self):
        language = SubtitleLanguageFactory(video=self.video,
                                           language_code='es')
        self.serializer.update(language, {
            'is_primary_audio_language': True,
            'subtitles_complete': True,
        })
        assert_equal(language.subtitles_complete, True)
        assert_equal(self.video.primary_audio_language_code, 'es')
        test_utils.assert_saved(language)
        test_utils.assert_saved(self.video)

    def test_cant_change_language_code(self):
        language = SubtitleLanguageFactory(video=self.video,
                                           language_code='es')
        self.serializer.update(language, {
            'language_code': 'fr',
        })
        assert_equal(language.language_code, 'es')

    def test_deprecated_aliases(self):
        language = SubtitleLanguageFactory(video=self.video,
                                           language_code='es')
        self.serializer.update(language, {
            'is_original': True,
            'is_complete': True,
        })
        assert_equal(self.video.primary_audio_language_code, 'es')
        assert_equal(language.subtitles_complete, True)

    def test_runs_tasks(self):
        language = self.serializer.create({'language_code': 'es'})
        assert_equal(test_utils.video_changed_tasks.delay.call_count, 1)
        self.serializer.update(language, {})
        assert_equal(test_utils.video_changed_tasks.delay.call_count, 2)

    def test_language_code_read_only(self):
        serializer = SubtitleLanguageSerializer(
            context=self.serializer_context, instance=self.language)
        assert_true(serializer.fields['language_code'].read_only)

class SubtitleLanguageViewset(TestCase):
    @test_utils.patch_for_test('subtitles.workflows.get_workflow')
    def setUp(self, mock_get_workflow):
        self.video = VideoFactory()
        self.language = SubtitleLanguageFactory(video=self.video,
                                                language_code='en')
        self.workflow = mock.Mock()
        mock_get_workflow.return_value = self.workflow
        self.workflow.user_can_view_private_subtitles.return_value = True
        self.user = UserFactory()
        self.viewset = SubtitleLanguageViewSet(kwargs={
            'video_id': self.video.video_id,
            'language_code': 'en',
        }, request=mock.Mock(user=self.user))

    def test_check_user_can_view_video(self):
        # test successful permissions check
        self.workflow.user_can_view_video.return_value = True
        self.viewset.get_queryset()
        self.viewset.get_object()
        # test failed permissions check
        self.workflow.user_can_view_video.return_value = False
        with assert_raises(PermissionDenied):
            self.viewset.get_queryset()
        with assert_raises(PermissionDenied):
            self.viewset.get_object()
        # check the arguments for the permissions check
        assert_equal(self.workflow.user_can_view_video.call_args_list, [
            mock.call(self.user),
            mock.call(self.user),
            mock.call(self.user),
            mock.call(self.user),
        ])

    def test_show_private_versions(self):
        # test successful permissions check
        self.workflow.user_can_view_private_subtitles.return_value = True
        assert_equal(self.viewset.show_private_versions('en'), True)
        # test failed permissions check
        self.workflow.user_can_view_private_subtitles.return_value = False
        assert_equal(self.viewset.show_private_versions('en'), False)
        # check the arguments for the permissions check
        assert_equal(
            self.workflow.user_can_view_private_subtitles.call_args_list, [
                mock.call(self.user, 'en'),
                mock.call(self.user, 'en'),
            ])

    def test_serializer_context(self):
        serializer_context = self.viewset.get_serializer_context()
        assert_equal(serializer_context['show_private_versions'],
                     self.viewset.show_private_versions)
        assert_equal(serializer_context['video'], self.video)

class SubtitlesSerializerTest(TestCase):
    def setUp(self):
        self.video = VideoFactory(title='test-video-title',
                                  description='test-video-description')
        self.version = pipeline.add_subtitles(
            self.video, 'en', SubtitleSetFactory(),
            title='test-title', description='test-description',
            metadata={'location': 'test-location'})
        self.context = {
            'request': None,
            'version_number': None,
            'sub_format': 'srt',
        }
        self.serializer = SubtitlesSerializer(context=self.context)

    def test_simple_fields(self):
        data = self.serializer.to_representation(self.version)
        assert_equal(data['version_number'], self.version.version_number)
        assert_equal(data['title'], self.version.title)
        assert_equal(data['description'], self.version.description)
        assert_equal(data['metadata'], self.version.get_metadata())
        assert_equal(data['video_title'], self.video.title)
        assert_equal(data['video_description'], self.video.description)
        assert_equal(data['resource_uri'],
                     reverse('api:subtitles', kwargs={
                             'video_id': self.video.video_id,
                             'language_code': self.version.language_code,
                     }))
        assert_equal(data['site_uri'],
                     reverse('videos:subtitleversion_detail', kwargs={
                         'video_id': self.video.video_id,
                         'lang': self.version.language_code,
                         'lang_id': self.version.subtitle_language_id,
                         'version_id': self.version.id,
                     }))
        assert_equal(data['language'], {
            'code': 'en',
            'name': 'English',
            'dir': 'ltr',
        })

    def test_subtitles(self):
        # test the subtitles and sub_format fields
        self.context['sub_format'] = 'vtt'
        data = self.serializer.to_representation(self.version)
        assert_equal(data['subtitles'],
                     babelsubs.to(self.version.get_subtitles(), 'vtt'))
        assert_equal(data['sub_format'], 'vtt')

    def test_json_sub_format(self):
        # for the json sub_format, we should return actual JSON data, not a
        # that data encoded as a string
        self.context['sub_format'] = 'json'
        data = self.serializer.to_representation(self.version)
        json_encoding = babelsubs.to(self.version.get_subtitles(), 'json')
        assert_equal(data['subtitles'], json.loads(json_encoding))

class SubtitlesViewTest(TestCase):
    def setUp(self):
        self.video = VideoFactory()
        self.version = pipeline.add_subtitles(self.video, 'en',
                                              SubtitleSetFactory(num_subs=1))
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = reverse('api:subtitles', kwargs={
            'video_id': self.video.video_id,
            'language_code': 'en',
        })

    def test_raw_format(self):
        # if we request a format like text/srt that's a subtile format, then
        # we should just return the subtitle data, nothing else
        response = self.client.get(self.url, HTTP_ACCEPT='text/srt')
        assert_equal(response.content,
                     babelsubs.to(self.version.get_subtitles(), 'srt'))

    def test_raw_format_with_format_param(self):
        response = self.client.get(self.url + "?format=dfxp")
        assert_equal(response.content,
                     babelsubs.to(self.version.get_subtitles(), 'dfxp'))

    def test_normal_format(self):
        # if we're not using a raw subtitle format, we should just return json
        response = self.client.get(self.url)
        # assume we're good if this next statement doesn't crash
        json.loads(response.content)

    def run_get_object(self, version_number=None):
        view = SubtitlesView()
        view.kwargs = {
            'video_id': self.video.video_id,
            'language_code': 'en',
        }
        view.request = APIRequestFactory().get(self.url)
        if version_number is None:
            view.request.query_params = {}
        else:
            view.request.query_params = {
                'version_number': version_number
            }
        view.request.user = self.user
        return view.get_object()

    def test_version_number_param(self):
        v2 = pipeline.add_subtitles(self.video, 'en',
                                      SubtitleSetFactory(num_subs=1))
        assert_equal(self.run_get_object(self.version.version_number),
                     self.version)
        assert_equal(self.run_get_object(v2.version_number), v2)

    def test_deleted_version_raises_404(self):
        v = pipeline.add_subtitles(self.video, 'en',
                                   SubtitleSetFactory(num_subs=1),
                                   visibility='public',
                                   visibility_override='deleted')
        with assert_raises(Http404):
            self.run_get_object(v.version_number)

    def test_no_public_tip_raises_404(self):
        self.version.delete()
        with assert_raises(Http404):
            self.run_get_object(None)

    def test_no_version_number_gets_public_tip(self):
        # this version shouldn't be returned by default since it's private
        pipeline.add_subtitles(self.video, 'en',
                               SubtitleSetFactory(num_subs=1),
                               visibility='private')
        assert_equal(self.run_get_object(None), self.version)

    def test_check_user_can_view_video_permission(self):
        with test_utils.patch_get_workflow() as workflow:
            workflow.user_can_view_video.return_value = False
            with assert_raises(PermissionDenied):
                self.run_get_object(None)
            # check the call args
            assert_equal(workflow.user_can_view_video.call_args,
                         mock.call(self.user))

    def test_check_user_can_view_private_versions_permission(self):
        v = pipeline.add_subtitles(self.video, 'en',
                                   SubtitleSetFactory(num_subs=1),
                                   visibility='private')
        with test_utils.patch_get_workflow() as workflow:
            workflow.user_can_view_private_subtitles.return_value = False
            with assert_raises(PermissionDenied):
                self.run_get_object(v.version_number)
            # check the call args
            assert_equal(workflow.user_can_view_private_subtitles.call_args,
                         mock.call(self.user))
