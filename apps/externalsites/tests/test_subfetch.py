# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from __future__ import absolute_import

from babelsubs import storage
from django.test import TestCase
from nose.tools import *
import mock

from externalsites.subfetch import should_fetch_subs, fetch_subs
from subtitles import pipeline
from subtitles.models import ORIGIN_IMPORTED
from utils import test_utils
from utils.factories import *

class ShouldFetchSubsTest(TestCase):
    def test_should_fetch_subs_with_youtube_account(self):
        YouTubeAccountFactory(channel_id="username", user=UserFactory())
        video = YouTubeVideoFactory(channel_id="username")
        assert_true(should_fetch_subs(video.get_primary_videourl_obj()))

    def test_should_fetch_subs_no_youtube_account(self):
        video = YouTubeVideoFactory(channel_id="username")
        assert_false(should_fetch_subs(video.get_primary_videourl_obj()))

    def test_should_fetch_subs_no_channel_id(self):
        video = YouTubeVideoFactory(channel_id=None)
        assert_false(should_fetch_subs(video.get_primary_videourl_obj()))

    def test_should_fetch_subs_non_youtube_video(self):
        video = VideoFactory()
        assert_false(should_fetch_subs(video.get_primary_videourl_obj()))


class SubFetchTestCase(TestCase):
    @test_utils.patch_for_test("externalsites.google.get_new_access_token")
    @test_utils.patch_for_test("externalsites.google.captions_list")
    @test_utils.patch_for_test("externalsites.google.captions_download")
    def setUp(self, mock_captions_download, mock_captions_list,
              mock_get_new_access_token):
        self.mock_captions_download = mock_captions_download
        self.mock_captions_list = mock_captions_list
        self.mock_get_new_access_token = mock_get_new_access_token
        self.mock_get_new_access_token.return_value = 'test-access-token'
        self.account = YouTubeAccountFactory(channel_id="username",
                                             user=UserFactory())
        self.video = YouTubeVideoFactory(channel_id="username")
        self.video_url = self.video.get_primary_videourl_obj()
        self.video_id = self.video_url.videoid

    def test_fetch_subs(self):
        self.mock_captions_list.return_value = [
            ('caption-1', 'en', 'English'),
            ('caption-2', 'fr', 'French'),
        ]

        en_subs = storage.SubtitleSet('en')
        en_subs.append_subtitle(100, 200, 'text')
        fr_subs = storage.SubtitleSet('fr')
        fr_subs.append_subtitle(100, 200, 'french text')
        def captions_download(access_token, video_id, language_code):
            if language_code == 'en':
                return en_subs.to_xml()
            elif language_code == 'fr':
                return fr_subs.to_xml()
            else:
                raise ValueError(language_code)
        self.mock_captions_download.side_effect = captions_download

        fetch_subs(self.video_url)
        # check that we called the correct API methods
        assert_equal(self.mock_get_new_access_token.call_args,
                     mock.call(self.account.oauth_refresh_token))

        assert_equal(self.mock_captions_list.call_args,
                     mock.call('test-access-token', self.video_id))
        assert_equal(self.mock_captions_download.call_args_list, [
            mock.call('test-access-token', self.video_id, 'en'),
            mock.call('test-access-token', self.video_id, 'fr'),
        ])
        # check that we created the correct languages
        assert_equal(set(l.language_code for l in
                         self.video.all_subtitle_languages()),
                     set(['en', 'fr']))
        lang_en = self.video.subtitle_language('en')
        lang_fr = self.video.subtitle_language('fr')
        # check subtitle data
        assert_equal(lang_en.get_tip().get_subtitles().to_xml(),
                     en_subs.to_xml())
        assert_equal(lang_fr.get_tip().get_subtitles().to_xml(),
                     fr_subs.to_xml())
        # check additional data
        assert_equal(lang_en.subtitles_complete, True)
        assert_equal(lang_fr.subtitles_complete, True)
        assert_equal(lang_en.get_tip().origin, ORIGIN_IMPORTED)
        assert_equal(lang_fr.get_tip().origin, ORIGIN_IMPORTED)
        assert_equal(lang_en.get_tip().note, "From youtube")
        assert_equal(lang_fr.get_tip().note, "From youtube")

    def test_fetch_subs_skips_existing_languages(self):
        # test that we don't try to get subtitles for languages that already
        # have data in the DB
        self.mock_captions_list.return_value = [
            ('caption-1', 'en', 'English'),
        ]

        existing_version = pipeline.add_subtitles(self.video, 'en', None)
        fetch_subs(self.video_url)
        assert_equal(self.mock_captions_download.call_count, 0)
        assert_equal(self.video.subtitle_language('en').get_tip(),
                         existing_version)

    def test_fetch_subs_handles_bcp47_codes(self):
        # youtube uses BCP-47 language codes.  Ensure that we use this code
        # when talking to youtube, but our own internal codes when storing
        # subtitles.
        self.mock_captions_list.return_value = [
            ('caption-1', 'pt-BR', 'Brazilian Portuguese'),
        ]

        subs = storage.SubtitleSet('pt-br')
        subs.append_subtitle(100, 200, 'text')
        self.mock_captions_download.return_value = subs.to_xml()

        fetch_subs(self.video_url)
        assert_equal(
            self.mock_captions_download.call_args,
            mock.call('test-access-token', self.video_url.videoid, 'pt-BR'))

        assert_equal(
            [l.language_code for l in self.video.all_subtitle_languages()],
            ['pt-br'])
