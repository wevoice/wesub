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

from django.core.urlresolvers import reverse
from django.test import TestCase
from nose.tools import *
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory
import mock

from api.views.subtitles import (SubtitleLanguageSerializer,
                                 SubtitleLanguageViewSet)
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
            'show_private_versions': self.show_private_versions
        }

    def get_serializer_data(self):
        serializer = SubtitleLanguageSerializer(context=self.serializer_context)
        return serializer.to_representation(self.language)

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
                     reverse('api:video-language-detail', kwargs={
                         'video_id': self.video.video_id,
                         'language_code': self.language.language_code,
                     })
        )


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
        pass

    def test_update(self):
        pass

    def test_set_primary_audio_language(self):
        pass

    def test_set_original_language(self):
        pass

class SubtitleLanguageViewsetPermissionsTest(TestCase):
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

    def test_serializer_context_includes_show_private_versions(self):
        serializer_context = self.viewset.get_serializer_context()
        assert_equal(serializer_context['show_private_versions'],
                     self.viewset.show_private_versions)
