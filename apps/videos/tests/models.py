# -*- coding: utf-8 -*-
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

from django.test import TestCase

from apps.auth.models import CustomUser as User
from apps.videos.models import Video
from apps.videos.tasks import video_changed_tasks
from apps.videos.tests.data import (
    get_video, make_subtitle_language, make_subtitle_version, make_rollback_to
)
from apps.widget import video_cache


def refresh(m):
    return m.__class__._default_manager.get(pk=m.pk)

class TestVideo(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.youtube_video = 'http://www.youtube.com/watch?v=pQ9qX8lcaBQ'
        self.html5_video = 'http://mirrorblender.top-ix.org/peach/bigbuckbunny_movies/big_buck_bunny_1080p_stereo.ogg'

    def test_get_or_create_for_url(self):
        def _assert_create_and_get(video_url):
            video, created = Video.get_or_create_for_url(video_url)
            self.assertIsNotNone(video)
            self.assertTrue(created)

            video2, created = Video.get_or_create_for_url(video_url)
            self.assertEqual(video.pk, video2.pk)
            self.assertFalse(created)

        _assert_create_and_get(self.youtube_video)
        _assert_create_and_get(self.html5_video)

    def test_url_cache(self):
        video = get_video(1)
        video_url = video.get_video_url()

        # After adding the video, we should be able to look up its ID in the
        # cache, given just the URL.
        cache_id_1 = video_cache.get_video_id(video_url)
        self.assertIsNotNone(cache_id_1)
        self.assertTrue(Video.objects.filter(video_id=cache_id_1).exists())

        # Remove the video (and make sure it's gone).
        video.delete()
        self.assertFalse(Video.objects.exists())

        # Trying to get the video ID out of the cache now actually *creates* the
        # video!
        cache_id_2 = video_cache.get_video_id(video_url)
        self.assertTrue(Video.objects.exists())

        # The video_id will be different than before (since this is a new Video
        # record) and the cache should have been updated properly.
        self.assertNotEqual(cache_id_1, cache_id_2)
        self.assertTrue(Video.objects.filter(video_id=cache_id_2).exists())

        # Now try to create a new video with the same URL.  This should return
        # the existing video.
        video2, created = Video.get_or_create_for_url(video_url)
        self.assertFalse(created)

        video2_url = video2.get_video_url()

        # The cache should still have the correct ID, of course.
        cache_id_3 = video_cache.get_video_id(video2_url)
        self.assertEqual(cache_id_2, cache_id_3)
        self.assertEqual(Video.objects.count(), 1)

    def test_video_title(self):
        video = get_video(url='http://www.youtube.com/watch?v=pQ9qX8lcaBQ')

        def _assert_title(correct_title):
            self.assertEquals(refresh(video).title, correct_title)

        # Test title before any subtitles are added.
        _assert_title("The Sea Organ of Zadar")

        # Make a subtitle language in the primary language.
        video.primary_audio_language_code = 'en'
        video.save()
        sl_en = make_subtitle_language(video, 'en')

        # Just adding languages shouldn't affect the title.
        _assert_title("The Sea Organ of Zadar")

        # Add subtitles with a custom title.  The title should be updated to
        # reflect this.
        make_subtitle_version(sl_en, [], title="New Title")
        _assert_title("New Title")

        # New versions should continue update the title properly.
        make_subtitle_version(sl_en, [], title="New Title 2")
        _assert_title("New Title 2")

        # Versions in a non-primary-audio-language should not affect the video
        # title.
        sl_ru = make_subtitle_language(video, 'ru')
        make_subtitle_version(sl_ru, [], title="New Title 3")
        _assert_title("New Title 2")

        # Rollbacks (of the primary audio language) should affect the title just
        # like a new version.
        make_rollback_to(sl_en, 1)
        _assert_title("New Title")

class TestModelsSaving(TestCase):
    # TODO: These tests may be more at home in the celery_tasks test file...
    def test_video_languages_count(self):
        # TODO: Merge this into the metadata tests file?
        video = get_video()

        # Start with no languages.
        self.assertEqual(video.languages_count, 0)
        self.assertEqual(video.newsubtitlelanguage_set.having_nonempty_tip()
                                                      .count(),
                         0)

        # Create one.
        sl_en = make_subtitle_language(video, 'en')
        make_subtitle_version(sl_en, [(100, 200, "foo")])

        # The query should immediately show it.
        self.assertEqual(video.newsubtitlelanguage_set.having_nonempty_tip()
                                                      .count(),
                         1)

        # But the model object will not.
        self.assertEqual(video.languages_count, 0)

        # Even if we refresh it, the model still doesn't show it.
        video = Video.objects.get(pk=video.pk)
        self.assertEqual(video.languages_count, 0)

        # Until we run the proper tasks.
        video_changed_tasks.delay(video.pk)

        # But we still need to refresh it to see the change.
        self.assertEqual(video.languages_count, 0)
        video = Video.objects.get(pk=video.pk)
        self.assertEqual(video.languages_count, 1)

    def test_subtitle_language_save(self):
        def _refresh(video):
            video_changed_tasks.delay(video.pk)
            return Video.objects.get(pk=video.pk)

        # Start out with a video with one language.
        # By default languages are not complete, so the video should not be
        # complete either.
        video = get_video()
        sl_en = make_subtitle_language(video, 'en')
        self.assertIsNone(video.complete_date)
        self.assertEqual(video.newsubtitlelanguage_set.count(), 1)

        # Marking the language as complete doesn't complete the video on its own
        # -- we need at least one version!
        sl_en.subtitles_complete = True
        sl_en.save()
        video = _refresh(video)
        self.assertIsNone(video.complete_date)

        # But an unsynced version can't be complete either!
        # TODO: uncomment once babelsubs supports unsynced subs...
        # make_subtitle_version(sl_en, [(100, None, "foo")])
        # video = _refresh(video)
        # self.assertIsNone(video.complete_date)

        # A synced version (plus the previously set flag on the language) should
        # result in a completed video.
        make_subtitle_version(sl_en, [(100, 200, "foo")])
        video = _refresh(video)
        self.assertIsNotNone(video.complete_date)

        # Unmarking the language as complete should uncomplete the video.
        sl_en.subtitles_complete = False
        sl_en.save()
        video = _refresh(video)
        self.assertIsNone(video.complete_date)

        # Any completed language is enough to complete the video.
        sl_ru = make_subtitle_language(video, 'ru')
        make_subtitle_version(sl_ru, [(100, 200, "bar")])
        sl_ru.subtitles_complete = True
        sl_ru.save()

        video = _refresh(video)
        self.assertIsNotNone(video.complete_date)
