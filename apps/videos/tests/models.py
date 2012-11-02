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

from django.test import TestCase

from apps.auth.models import CustomUser as User
from apps.videos.models import Video
from apps.videos.tasks import video_changed_tasks
from apps.videos.tests.data import (
    get_video, make_subtitle_language, make_subtitle_version
)
from apps.widget import video_cache


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
        # make a video
        youtube_url = 'http://www.youtube.com/watch?v=pQ9qX8lcaBQ'
        video, created = Video.get_or_create_for_url(youtube_url)
        # test title before any subtitles are added
        self.assertEquals(video.title, "The Sea Organ of Zadar")
        # Make a subtitle language
        lang = SubtitleLanguage(video=video, language='en', is_original=True)
        lang.save()
        # delete the cached _original_subtitle attribute to let the new
        # language be found.
        if hasattr(video, '_original_subtitle'):
            del video._original_subtitle
        # add a subtitle
        fake_parser = []
        v = SubtitleVersion.objects.new_version(fake_parser, lang, self.user,
                                            title="New Title")
        def check_title(correct_title):
            # reload the video to ensure we have the latest version
            self.assertEquals(Video.objects.get(pk=video.pk).title,
                              correct_title)
        check_title("New Title")
        # update subtitle
        SubtitleVersion.objects.new_version(fake_parser, lang, self.user,
                                            title="Title 2")
        check_title("Title 2")
        # add a subtitle for a different language
        other_lang = SubtitleLanguage(video=video, language='ru',
                                      is_original=False)
        other_lang.save()
        SubtitleVersion.objects.new_version(fake_parser, other_lang,
                                            self.user, title="Title 3")
        check_title("Title 2")
        # revert
        video.version(0).rollback(self.user)
        check_title("New Title")

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
