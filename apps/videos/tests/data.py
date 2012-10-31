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
"""Data creation and retrieval functions for the video tests."""

from apps.auth.models import CustomUser as User
from apps.videos.models import Video
from apps.subtitles import pipeline
from apps.subtitles.models import SubtitleLanguage


# Normal Users ----------------------------------------------------------------
def get_user(n=1):
    username = 'test_user_%s' % n
    email = "test_user_%s@example.com" % n
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create(
            username=username, email=email,
            is_active=True, is_superuser=False, is_staff=False,
            password="sha1$6b3dc$72c6a16f127d2c217f72009632c745effef7eb3f",
        )
    return user


# Site Admins -----------------------------------------------------------------
def get_site_admin(n=1):
    username = 'test_admin_%s' % n
    email = "test_admin_%s@example.com" % n
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create(
            username=username, email=email,
            is_active=True, is_superuser=True, is_staff=True,
            password="sha1$6b3dc$72c6a16f127d2c217f72009632c745effef7eb3f",
        )
    return user


# Videos ----------------------------------------------------------------------
VIDEO_URLS = ('http://youtu.be/heKK95DAKms',
              'http://youtu.be/e4MSN6IImpI',
              'http://youtu.be/i_0DXxNeaQ0',)

def get_video(n=1, user=None):
    video, _ = Video.get_or_create_for_url(VIDEO_URLS[n], user=user)
    return video


# Subtitle Languages ----------------------------------------------------------
def make_subtitle_language(video, language_code):
    sl = SubtitleLanguage(video=video, language_code=language_code)
    sl.save()
    return sl


# Subtitle Versions -----------------------------------------------------------
def make_subtitle_version(subtitle_language, subtitles=[], author=None):
    return pipeline.add_subtitles(subtitle_language.video,
                                  subtitle_language.language_code,
                                  subtitles,
                                  author=author)
