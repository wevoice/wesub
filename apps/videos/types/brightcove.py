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
import urlparse

import requests

from vidscraper.errors import Error as VidscraperError
from base import VideoType, VideoTypeError
from django.conf import settings
from django.utils.html import strip_tags

BRIGHTCOVE_API_KEY = getattr(settings, 'BRIGHTCOVE_API_KEY', None)
BRIGHTCOVE_API_SECRET = getattr(settings, 'BRIGHTCOVE_API_SECRET' , None)

BRIGHTCOVE_REGEXES = [
    r'http://[\w_-]+.brightcove.com/',
    r'http://bcove.me/[\w_-]+',
]
BRIGHTCOVE_REGEXES = [re.compile(x) for x in BRIGHTCOVE_REGEXES]

class BrightcoveVideoType(VideoType):

    abbreviation = 'C'
    name = 'Brightcove'
    site = 'brightcove.com'
    js_url = "//admin.brightcove.com/js/BrightcoveExperiences_all.js"

    def __init__(self, url):
        self.url = self._resolve_url_redirects(url)
        self._extract_brightcove_ids()

    def _extract_brightcove_ids(self):
        parsed = urlparse.urlparse(self.url)
        query = urlparse.parse_qs(parsed.query)
        path_parts = parsed.path.split("/")
        self.brightcove_id = self._find_brightcode_id('bctid', query,
                                                      path_parts)

    def _find_brightcode_id(self, name, query, path_parts):
        if name in query:
            return query[name][0]
        for part in path_parts:
            if part.startswith(name):
                return part[len(name):]
        raise ValueError("cant find %s in %s" % (name, self.url))

    def _resolve_url_redirects(self, url):
        return requests.head(url, allow_redirects=True).url

    @property
    def video_id(self):
        return self.brightcove_id

    @classmethod
    def matches_video_url(cls, url):
        if bool(url):
            for r in BRIGHTCOVE_REGEXES:
                if bool(r.match(url)):
                    return True
            from videos.models import VideoTypeUrlPattern
            for pattern in VideoTypeUrlPattern.objects.patterns_for_type(cls.abbreviation):
                if url.find(pattern.url_pattern) == 0 and url.find('bctid') > 0:
                    return True
        return False
