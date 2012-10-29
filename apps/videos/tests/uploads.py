# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
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

import os
import json

from django.core.urlresolvers import reverse

from apps.auth.models import CustomUser as User
from apps.videos import metadata_manager
from apps.videos.models import Video, SubtitleLanguage, Subtitle
from apps.videos.tasks import video_changed_tasks
from apps.videos.tests.videos import WebUseTest, refresh_obj, _create_trans
from apps.widget.rpc import Rpc
from apps.widget.tests import (
    create_two_sub_dependent_session, create_two_sub_session, RequestMockup,
    NotAuthenticatedUser
)


class UploadSubtitlesTest(WebUseTest):
    fixtures = ['test.json']

    def _make_data(self, lang='ru', video_pk=None):
        if video_pk is None:
            video_pk = self.video.id
        return {
            'language': lang,
            'video_language': 'en',
            'video': video_pk,
            'draft': open(os.path.join(os.path.dirname(__file__), 'fixtures/test.srt')),
            'is_complete': True
            }


    def _make_altered_data(self, video=None, language_code='ru', subs_filename='test_altered.srt'):
        video = video or self.video
        return {
            'language': language_code,
            'video': video.pk,
            'video_language': 'en',
            'draft': open(os.path.join(os.path.dirname(__file__), 'fixtures/%s' % subs_filename))
            }

    def setUp(self):
        self._make_objects()

    def test_upload_subtitles(self):
        self._simple_test('videos:upload_subtitles', status=302)

        self._login()

        data = self._make_data()

        language = self.video.subtitle_language(data['language'])
        self.assertEquals(language, None)

        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

        video = Video.objects.get(pk=self.video.pk)
        self.assertFalse(video.is_writelocked)
        original_language = video.subtitle_language()
        self.assertEqual(original_language.language, data['video_language'])

        language = video.subtitle_language(data['language'])
        version = language.latest_version(public_only=True)
        self.assertEqual(len(version.subtitles()), 32)
        self.assertTrue(language.is_forked)
        self.assertTrue(version.is_forked)
        self.assertTrue(language.has_version)
        self.assertTrue(language.had_version)
        self.assertEqual(language.is_complete, data['is_complete'])
        # FIXME: why should these be false?
        # self.assertFalse(video.is_subtitled)
        # self.assertFalse(video.was_subtitled)
        metadata_manager.update_metadata(video.pk)
        language = refresh_obj(language)
        # two of the test srts end up being empty, so the subtitle_count
        # should be real
        self.assertEquals(30, language.subtitle_count)
        self.assertEquals(0, language.percent_done)

        data = self._make_data()
        data['is_complete'] = not data['is_complete']
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        video = Video.objects.get(pk=self.video.pk)
        language = video.subtitle_language(data['language'])
        self.assertEqual(language.is_complete, data['is_complete'])
        self.assertFalse(video.is_writelocked)

    def test_upload_original_subtitles(self):
        self._login()
        data = self._make_data(lang='en')
        video = Video.objects.get(pk=self.video.pk)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

        video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(1, video.subtitlelanguage_set.count())
        language = video.subtitle_language()
        self.assertEqual('en', language.language)
        self.assertTrue(language.is_original)
        self.assertTrue(language.has_version)
        self.assertTrue(video.is_subtitled)

    def test_upload_translation(self):
        self._login()
        data = self._make_data(lang='en')
        video = Video.objects.get(pk=self.video.pk)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

        video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(1, video.subtitlelanguage_set.count())
        language = video.subtitle_language()
        self.assertEqual('en', language.language)
        self.assertTrue(language.is_original)
        self.assertTrue(language.has_version)
        self.assertTrue(video.is_subtitled)
        self.assertFalse(language.is_dependent())

        data = self._make_data(lang='fr')
        data['translated_from'] = 'en'

        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

        video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(2, video.subtitlelanguage_set.count())
        language = video.subtitle_language("fr")
        self.assertEqual('fr', language.language)
        self.assertFalse(language.is_original)
        self.assertTrue(language.has_version)
        self.assertTrue(video.is_subtitled)
        self.assertTrue(language.is_dependent())
        self.assertEquals(language.standard_language.language, "en")

    def test_upload_twice(self):
        self._login()
        data = self._make_data()
        self.client.post(reverse('videos:upload_subtitles'), data)
        language = self.video.subtitle_language(data['language'])
        version_no = language.latest_version(public_only=True).version_no
        self.assertEquals(1, language.subtitleversion_set.count())
        num_languages_1 = self.video.subtitlelanguage_set.all().count()
        # now post the same file.
        data = self._make_data()
        self.client.post(reverse('videos:upload_subtitles'), data)
        self._make_objects()
        language = self.video.subtitle_language(data['language'])
        self.assertEquals(1, language.subtitleversion_set.count())
        self.assertEquals(version_no, language.latest_version(public_only=True).version_no)
        num_languages_2 = self.video.subtitlelanguage_set.all().count()
        self.assertEquals(num_languages_1, num_languages_2)

    def test_upload_over_translated(self):
        # for https://www.pivotaltracker.com/story/show/11804745
        request = RequestMockup(User.objects.all()[0])
        session = create_two_sub_dependent_session(request)
        video_pk = session.language.video.pk
        video = Video.objects.get(pk=video_pk)

        self._login()
        data = self._make_data(lang='en', video_pk=video_pk)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

        video = Video.objects.get(pk=video_pk)
        self.assertEqual(2, video.subtitlelanguage_set.count())

    def test_upload_over_empty_translated(self):
        request = RequestMockup(User.objects.all()[0])
        session = create_two_sub_session(request)
        video_pk = session.language.video.pk
        video = Video.objects.get(pk=video_pk)
        original_en = video.subtitlelanguage_set.filter(language='en').all()[0]

        # save empty espanish
        es = SubtitleLanguage(
            video=video,
            language='ht',
            is_original=False,
            is_forked=False,
            standard_language=original_en)
        es.save()

        # now upload over the original english.
        self._login()
        data = self._make_data(lang='en', video_pk=video_pk)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

    def test_upload_respects_lock(self):
        request = RequestMockup(User.objects.all()[0])
        session = create_two_sub_dependent_session(request)
        video = session.video

        self._login()
        translated = video.subtitlelanguage_set.all().filter(language='es')[0]
        translated.writelock(request)
        translated.save()
        data = self._make_data(lang='en', video_pk=video.pk)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content[10:-11])
        self.assertFalse(data['success'])


    def test_upload_then_rollback_preservs_dependends(self):
        self._login()
        # for https://www.pivotaltracker.com/story/show/14311835
        # 1. Submit a new video.
        video, created = Video.get_or_create_for_url("http://example.com/blah.mp4")
        # 2. Upload some original subs to this video.
        data = self._make_data(lang='en', video_pk=video.pk)
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        original = video.subtitle_language()
        original_version = version = original.version()
        # 3. Upload another, different file to overwrite the original subs.
        data = self._make_altered_data(language_code='en', video=video, subs_filename="welcome-subs.srt")
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        video = Video.objects.get(pk=video.pk)
        version = video.version()
        self.assertEqual(response.status_code, 200)
        self.assertTrue (len(version.subtitles()) != len(original_version.subtitles()))

        # 4. Make a few translations.
        pt = _create_trans(video, latest_version=version, lang_code="pt", forked=False )
        pt_count = len(pt.latest_subtitles())
        # 5. Roll the original subs back to #0. The translations will be wiped clean (to 0 lines).
        original_version.rollback(self.user)
        original_version.save()
        video_changed_tasks.run(original_version.video.id, original_version.id)
        # we should end up with 1 forked pts
        pts = video.subtitlelanguage_set.filter(language='pt')
        self.assertEqual(pts.count(), 1)
        # one which is forkded and must retain the original count
        pt_forked = video.subtitlelanguage_set.get(language='pt', is_forked=True)
        self.assertEqual(len(pt_forked.latest_subtitles()), pt_count)
        # now we roll back  to the second version, we should not be duplicating again
        # because this rollback is already a rollback
        version.rollback(self.user)
        pts = video.subtitlelanguage_set.filter(language='pt')
        self.assertEqual(pts.count(), 1)
        self.assertEqual(len(pt_forked.latest_subtitles()), pt_count)

    def test_upload_file_with_unsynced(self):
        self._login()
        data = self._make_data()
        data = self._make_altered_data(subs_filename="subs-with-unsynced.srt")
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)
        language = self.video.subtitlelanguage_set.get(language='ru')
        subs = Subtitle.objects.filter(version=language.version())
        num_subs = len(subs)

        num_unsynced = len(Subtitle.objects.unsynced().filter(version=language.version()))


        self.assertEquals(82, num_subs)
        self.assertEquals(26 ,num_unsynced)

    def test_upload_from_failed_session(self):
        self._login()

        data = self._make_data( video_pk=self.video.pk, lang='ru')

        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

        data = self._make_altered_data(video=self.video, language_code='ru', subs_filename='subs-from-fail-session.srt')

        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

        language = self.video.subtitlelanguage_set.get(language='ru')
        subs = Subtitle.objects.filter(version=language.version())

        for sub in subs[8:]:
            self.assertEquals(None, sub.start_time)
            self.assertEquals(None, sub.end_time)

        num_subs = len(subs)
        num_unsynced = len(Subtitle.objects.unsynced().filter(version=language.version()))
        self.assertEquals(10, num_subs)
        self.assertEquals(2 , num_unsynced)

    def test_upload_from_widget_last_end_unsynced(self):
        self._login()

        data = self._make_altered_data(video=self.video, language_code='en', subs_filename='subs-last-unsynced.srt')

        response = self.client.post(reverse('videos:upload_subtitles'), data)
        self.assertEqual(response.status_code, 200)

        language = self.video.subtitle_language('en')
        subs = language.latest_version().subtitles()
        self.assertEquals(7.071, subs[2].start_time)

        request = RequestMockup(NotAuthenticatedUser())
        rpc = Rpc()
        subs = rpc.fetch_subtitles(request, self.video.video_id, language.pk)
        last_sub = subs['subtitles'][2]
        self.assertEquals(7.071, last_sub['start_time'])
        self.assertEquals(-1, last_sub['end_time'])

