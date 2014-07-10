# Amara, universalsubtitles.org
#
# Copyright (C) 2014 Participatory Culture Foundation
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

"""externalsites.subfetch -- Fetch subtitles from external services
"""

import logging

from subtitles.models import ORIGIN_IMPORTED
from subtitles import pipeline
from utils import youtube
from videos.models import VIDEO_TYPE_YOUTUBE

logger = logging.getLogger('externalsites.subfetch')

def should_fetch_subs(video_url):
    return video_url.type == VIDEO_TYPE_YOUTUBE

def fetch_subs(video_url):
    if video_url.type == VIDEO_TYPE_YOUTUBE:
        fetch_subs_youtube(video_url)
    else:
        logger.warn("fetch_subs() bad video type: %s" % video_url.type)

def fetch_subs_youtube(video_url):
    video_id = video_url.videoid
    existing_langs = set(
        l.language_code for l in
        video_url.video.newsubtitlelanguage_set.having_versions()
    )

    for language_code in youtube.get_subtitled_languages(video_id):
        if language_code not in existing_langs:
            subs = youtube.get_subtitles(video_id, language_code)
            pipeline.add_subtitles(video_url.video, language_code, subs,
                                   note="From youtube", complete=True,
                                   origin=ORIGIN_IMPORTED)
