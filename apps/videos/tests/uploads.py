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
from apps.videos.tests.data import (
    get_video
)
from apps.videos.tests.utils import WebUseTest, refresh_obj, _create_trans
from apps.widget.rpc import Rpc
from apps.widget.tests import (
    create_two_sub_dependent_session, create_two_sub_session, RequestMockup,
    NotAuthenticatedUser
)

up = os.path.dirname

def refresh(m):
    return m.__class__._default_manager.get(pk=m.pk)

class UploadRequiresLoginTest(WebUseTest):
    def test_upload_requires_login(self):
        # When not logged in trying to upload should redirect to the login page.
        self._simple_test('videos:upload_subtitles', status=302)

class UploadSubtitlesTest(WebUseTest):
    fixtures = ['test.json']

    def _srt(self, filename):
        return os.path.join(up(up(__file__)), 'fixtures/%s' % filename)

    def _data(self, video, language_code, primary_audio_language_code,
              from_language_code, complete, draft):
        return {
            'video': video.pk,
            'language_code': language_code,
            'primary_audio_language_code': primary_audio_language_code,
            'from_language_code': from_language_code or '',
            'complete': '1' if complete else '0',
            'draft': draft,
        }

    def _upload(self, video, language_code, primary_audio_language_code,
                from_language_code, complete, filename):
        with open(self._srt(filename)) as draft:
            return self.client.post(
                reverse('videos:upload_subtitles'),
                self._data(video, language_code, primary_audio_language_code,
                           from_language_code, complete, draft))


    def setUp(self):
        self._login()

    def test_upload_subtitles_primary_language(self):
        # Start with a fresh video.
        video = get_video()
        self.assertEqual(video.primary_audio_language_code, '')
        self.assertFalse(video.has_original_language())
        self.assertIsNone(video.complete_date)

        # Upload subtitles in the primary audio language.
        response = self._upload(video, 'en', 'en', None, True, 'test.srt')
        self.assertEqual(response.status_code, 200)

        video = refresh(video)

        # The writelock should be gone once the subtitles have been uploaded.
        self.assertFalse(video.is_writelocked)

        # The video should now have a primary audio language, since it was set
        # as part of the upload process.
        self.assertEqual(video.primary_audio_language_code, 'en')
        self.assertTrue(video.has_original_language())

        # Ensure that the subtitles actually got uploaded too.
        sl_en = video.subtitle_language()
        self.assertIsNotNone(sl_en)
        self.assertEqual(sl_en.subtitleversion_set.count(), 1)

        en1 = sl_en.get_tip()
        subtitles = en1.get_subtitles()
        self.assertEqual(en1.subtitle_count, 32)
        self.assertEqual(len(subtitles), 32)

        # Now that we've uploaded a complete set of subtitles, the video and
        # language should be marked as completed.
        self.assertIsNotNone(video.complete_date)
        self.assertTrue(sl_en.subtitles_complete)

        # Let's make sure they didn't get mistakenly marked as a translation.
        self.assertIsNone(sl_en.get_translation_source_language())

        # Upload another version just to be sure.
        response = self._upload(video, 'en', 'en', None, True, 'test.srt')
        self.assertEqual(response.status_code, 200)

        video = refresh(video)
        sl_en = refresh(sl_en)

        self.assertEqual(sl_en.subtitleversion_set.count(), 2)

    def test_upload_subtitles_non_primary_language(self):
        # Start with a fresh video.
        video = get_video()
        self.assertEqual(video.primary_audio_language_code, '')
        self.assertFalse(video.has_original_language())
        self.assertIsNone(video.complete_date)

        # Upload subtitles in a language other than the primary.
        response = self._upload(video, 'fr', 'en', None, True, 'test.srt')
        self.assertEqual(response.status_code, 200)

        video = refresh(video)

        # The writelock should be gone once the subtitles have been uploaded.
        self.assertFalse(video.is_writelocked)

        # The video should now have a primary audio language, since it was set
        # as part of the upload process.
        self.assertEqual(video.primary_audio_language_code, 'en')

        # But it doesn't have a SubtitleLanguage for it.
        self.assertFalse(video.has_original_language())
        self.assertIsNone(video.subtitle_language())
        self.assertIsNone(video.get_primary_audio_subtitle_language())

        # Ensure that the subtitles actually got uploaded too.
        sl_fr = video.subtitle_language('fr')
        self.assertIsNotNone(sl_fr)
        self.assertEqual(sl_fr.subtitleversion_set.count(), 1)

        fr1 = sl_fr.get_tip()
        subtitles = fr1.get_subtitles()
        self.assertEqual(fr1.subtitle_count, 32)
        self.assertEqual(len(subtitles), 32)

        # Now that we've uploaded a complete set of subtitles, the video and
        # language should be marked as completed.
        self.assertIsNotNone(video.complete_date)
        self.assertTrue(sl_fr.subtitles_complete)

        # Let's make sure they didn't get mistakenly marked as a translation.
        # They're not in the primary language but are still a transcription.
        self.assertIsNone(sl_fr.get_translation_source_language())

        # Upload another version just to be sure.
        response = self._upload(video, 'fr', 'en', None, True, 'test.srt')
        self.assertEqual(response.status_code, 200)

        video = refresh(video)
        sl_fr = refresh(sl_fr)

        self.assertFalse(video.has_original_language())
        self.assertIsNone(video.subtitle_language())
        self.assertIsNone(video.get_primary_audio_subtitle_language())
        self.assertIsNotNone(video.complete_date)
        self.assertTrue(sl_fr.subtitles_complete)
        self.assertEqual(sl_fr.subtitleversion_set.count(), 2)

    def test_upload_subtitles(self):
        video = get_video()

        with open(self._srt('test.srt')) as draft:
            response = self.client.post(
                reverse('videos:upload_subtitles'),
                self._data(video, 'ru', 'en', None, True, draft))

        self.assertEqual(response.status_code, 200)

        video = refresh(video)

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

