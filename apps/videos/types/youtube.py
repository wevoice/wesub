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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.
import re
from urlparse import urlparse

from base import VideoType
from externalsites import google

class YoutubeVideoType(VideoType):

    _url_patterns = [re.compile(x) for x in [
        r'youtube.com/.*?v[/=](?P<video_id>[\w-]+)',
        r'youtu.be/(?P<video_id>[\w-]+)',
    ]]

    HOSTNAMES = ( "youtube.com", "youtu.be", "www.youtube.com",)

    abbreviation = 'Y'
    name = 'Youtube'
    site = 'youtube.com'

    # changing this will cause havock, let's talks about this first
    URL_TEMPLATE = 'http://www.youtube.com/watch?v=%s'

    CAN_IMPORT_SUBTITLES = True

    def __init__(self, url):
        self.url = url
        self.videoid = self._get_video_id(self.url)

    @property
    def video_id(self):
        return self.videoid

    def convert_to_video_url(self):
        return 'http://www.youtube.com/watch?v=%s' % self.video_id

    @classmethod
    def video_url(cls, obj):
        """
        This method can be called with wither a VideoType object or
        an actual VideoURL object, therefore the if statement
        """
        if obj.videoid:
            return YoutubeVideoType.url_from_id(obj.videoid)
        else:
            return obj.url

    @classmethod
    def matches_video_url(cls, url):
        hostname = urlparse(url).netloc
        return (hostname in YoutubeVideoType.HOSTNAMES and
                any(pattern.search(url) for pattern in cls._url_patterns))

    def get_direct_url(self, prefer_audio=False):
        if prefer_audio:
            return google.get_direct_url_to_audio(self.video_id)
        else:
            return google.get_direct_url_to_video(self.video_id)

    def get_video_info(self):
        if not hasattr(self, '_video_info'):
            self._video_info = google.get_video_info(self.video_id)
        return self._video_info

    def set_values(self, video):
        try:
            video_info = self.get_video_info()
        except google.APIError:
            return
        video.title = video_info.title
        video.description = video_info.description
        video.duration = video_info.duration
        video.thumbnail = video_info.thumbnail_url

    def owner_username(self):
        try:
            return self.get_video_info().channel_id
        except google.APIError:
            return None

    @classmethod
    def url_from_id(cls, video_id):
        return YoutubeVideoType.URL_TEMPLATE % video_id

    @classmethod
    def _get_video_id(cls, video_url):
        for pattern in cls._url_patterns:
            match = pattern.search(video_url)
            video_id = match and match.group('video_id')
            if bool(video_id):
                return video_id
        raise ValueError("Unknown video id")
