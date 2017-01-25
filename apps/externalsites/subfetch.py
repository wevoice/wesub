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

import unilangs

from externalsites import google
from externalsites.models import YouTubeAccount
from subtitles.models import ORIGIN_IMPORTED
from subtitles import pipeline
from videos.models import VIDEO_TYPE_YOUTUBE

logger = logging.getLogger('externalsites.subfetch')

def convert_language_code(lc):
    """
    Convert from a YouTube language code to an Amara one
    """
    try:
        return unilangs.LanguageCode(lc, 'youtube_with_mapping').encode('unisubs')
    except KeyError:
        # Error looking up the youtube language code.  Return none and we'll
        # skip importing the subtitles.
        return None

def should_fetch_subs(video_url):
    if video_url.type == VIDEO_TYPE_YOUTUBE:
        return (YouTubeAccount.objects
                .filter(channel_id=video_url.owner_username)
                .exists())
    else:
        return False

def fetch_subs(video_url):
    if video_url.type == VIDEO_TYPE_YOUTUBE:
        fetch_subs_youtube(video_url)
    else:
        logger.warn("fetch_subs() bad video type: %s" % video_url.type)

def fetch_subs_youtube(video_url):
    video_id = video_url.videoid
    channel_id = video_url.owner_username
    if not channel_id:
        logger.warn("fetch_subs() no username: %s", video_url.pk)
        return
    try:
        account = YouTubeAccount.objects.get(channel_id=channel_id)
    except YouTubeAccount.DoesNotExist:
        logger.warn("fetch_subs() no youtube account for %s", channel_id)
        return

    existing_langs = set(
        l.language_code for l in
        video_url.video.newsubtitlelanguage_set.having_versions()
    )

    access_token = google.get_new_access_token(account.oauth_refresh_token)
    captions_list = google.captions_list(access_token, video_id)
    for caption_id, language_code, caption_name in captions_list:
        language_code = convert_language_code(language_code)
        if language_code and language_code not in existing_langs:
            dfxp = google.captions_download(access_token, caption_id)
            try:
                pipeline.add_subtitles(video_url.video, language_code, dfxp,
                                       note="From youtube", complete=True,
                                       origin=ORIGIN_IMPORTED)
            except Exception, e:
                logger.error("Exception while importing subtitles " + str(e))
