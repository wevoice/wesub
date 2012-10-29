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
from apps.videos.tests.videos import create_langs_and_versions
from apps.widget import video_cache


class TestVideo(TestCase):
    def _create_video(self, video_url):
        video, created = Video.get_or_create_for_url(video_url)
        self.failUnless(video)
        self.failUnless(created)
        more_video, created = Video.get_or_create_for_url(video_url)
        self.failIf(created)
        self.failUnlessEqual(video, more_video)

    def setUp(self):
        self.user = User.objects.all()[0]
        self.youtube_video = 'http://www.youtube.com/watch?v=pQ9qX8lcaBQ'
        self.html5_video = 'http://mirrorblender.top-ix.org/peach/bigbuckbunny_movies/big_buck_bunny_1080p_stereo.ogg'

    def test_video_create(self):
        self._create_video(self.youtube_video)
        self._create_video(self.html5_video)

    def test_video_cache_busted_on_delete(self):
        start_url = 'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv'
        video, created = Video.get_or_create_for_url(start_url)
        video_url = video.get_video_url()
        video_pk = video.pk

        cache_id_1 = video_cache.get_video_id(video_url)
        self.assertTrue(cache_id_1)
        video.delete()
        self.assertEqual(Video.objects.filter(pk=video_pk).count() , 0)
        # when cache is not cleared this will return arn
        cache_id_2 = video_cache.get_video_id(video_url)
        self.assertNotEqual(cache_id_1, cache_id_2)
        # create a new video with the same url, has to have same# key
        video2, created= Video.get_or_create_for_url(start_url)
        video_url = video2.get_video_url()
        cache_id_3 = video_cache.get_video_id(video_url)
        self.assertEqual(cache_id_3, cache_id_2)

class TestModelsSaving(TestCase):
    # TODO: These tests may be more at home in the celery_tasks test file...
    fixtures = ['test.json', 'subtitle_fixtures.json']

    def setUp(self):
        self.video = Video.objects.all()[:1].get()
        self.language = self.video.subtitle_language()

    def test_video_languages_count(self):
        #test if fixtures has correct data
        langs_count = self.video.newsubtitlelanguage_set.having_nonempty_tip().count()

        self.assertEqual(self.video.languages_count, langs_count)
        self.assertTrue(self.video.languages_count > 0)

        self.video.languages_count = 0
        self.video.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(id=self.video.id)
        self.assertEqual(self.video.languages_count, langs_count)

    def test_subtitle_language_save(self):
        self.assertEqual(self.video.complete_date, None)
        self.assertEqual(self.video.subtitlelanguage_set.count(), 1)

        self.language.subtitles_complete = True
        self.language.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)

        self.language.subtitles_complete = False
        self.language.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(self.video.complete_date, None)

        version = create_langs_and_versions(self.video, ['ru'])
        new_language = version[0].subtitle_language
        new_language.subtitles_complete = True
        new_language.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)

        self.language.subtitles_complete = True
        self.language.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)

        new_language.subtitles_complete = False
        new_language.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertNotEqual(self.video.complete_date, None)

        self.language.subtitles_complete = False
        self.language.save()
        video_changed_tasks.delay(self.video.pk)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertEqual(self.video.complete_date, None)

