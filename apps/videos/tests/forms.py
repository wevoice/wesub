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

from apps.videos.forms import VideoForm
from apps.videos.models import Video
from apps.videos.types import video_type_registrar


class TestVideoForm(TestCase):
    def setUp(self):
        self.vimeo_urls = ("http://vimeo.com/17853047",)
        self.youtube_urls = ("http://youtu.be/HaAVZ2yXDBo",
                             "http://www.youtube.com/watch?v=HaAVZ2yXDBo")
        self.html5_urls = ("http://blip.tv/file/get/Miropcf-AboutUniversalSubtitles715.mp4",)
        self.daily_motion_urls = ("http://www.dailymotion.com/video/xb0hsu_qu-est-ce-que-l-apache-software-fou_tech",)

    def _test_urls(self, urls):
        for url in urls:
            form = VideoForm(data={"video_url":url})
            self.assertTrue(form.is_valid())
            video = form.save()
            video_type = video_type_registrar.video_type_for_url(url)
            # double check we never confuse video_id with video.id with videoid, sigh
            model_url = video.get_video_url()
            if hasattr(video_type, "videoid"):
                self.assertTrue(video_type.videoid  in model_url)
            # check the pk is never on any of the urls parts
            for part in model_url.split("/"):
                self.assertTrue(str(video.pk)  != part)
            self.assertTrue(video.video_id  not in model_url)

            self.assertTrue(Video.objects.filter(videourl__url=model_url).exists())

    def test_youtube_urls(self):
        self._test_urls(self.youtube_urls)

    def test_vimeo_urls(self):
        self._test_urls(self.vimeo_urls)

    def test_html5_urls(self):
        self._test_urls(self.html5_urls)

    def test_dailymotion_urls(self):
        self._test_urls(self.daily_motion_urls)


