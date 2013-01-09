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

"""
Fix all the Youtube descriptions!
=================================

This command will attempt to fix all team Youtube videos.  These videos had
their Youtube descriptions changed by accident by an earlier sync.

The new descriptions were produced by adding

    `credit`: `amara video url`

    `original description`

Where `credit` is "Help us caption and translate this video on Amara.org".

So, this script looks up all video urls that could possibly be affected by this
and then attempts to fix them one by one.  It reconstructs the supposed
description addition and checks (via the Youtube API) if the Youtube video
description starts with it.  If it does, it replaces it with nothing and
updates the description on Youtube.

You can also fix an individual video by using the --video flag.  It takes a
video_id.
"""

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from django.conf import settings
import gdata

from apps.videos.models import VideoUrl, Video, VIDEO_TYPE_YOUTUBE
from apps.videos.types import video_type_registrar
from apps.videos.types.youtube import YouTubeApiBridge


UPLOAD_URI_BASE = 'http://gdata.youtube.com/feeds/api/users/default/uploads/%s'
YOUTUBE_API_SECRET  = getattr(settings, "YOUTUBE_API_SECRET", None)


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--video', '-d', dest='video_id', type="str",
            default=None),
    )

    _current_site = None

    def _get_site(self):
        if not self._current_site:
            self._current_site = Site.objects.get_current()
        return self._current_site

    def _fix_video(self, vurl):
        from apps.accountlinker.models import ThirdPartyAccount
        video = vurl.video
        language_code = video.language

        if not language_code:
            language_code = 'en'

        vt = video_type_registrar.video_type_for_url(vurl.url)
        username = vurl.owner_username
        account = ThirdPartyAccount.objects.get(type=vurl.type,
                username=username)
        bridge = YouTubeApiBridge(account.oauth_access_token,
                                account.oauth_refresh_token,
                                vt.videoid)

        video_url = video.get_absolute_url()
        video_url = u"http://%s%s" % (unicode(self._get_site().domain),
                video_url)

        supposed_credit = self._get_supposed_credit(video_url, language_code)

        uri = UPLOAD_URI_BASE % bridge.youtube_video_id
        entry = bridge.GetVideoEntry(uri=uri)
        entry = entry.to_string()
        entry = gdata.youtube.YouTubeVideoEntryFromString(entry)

        current_description = entry.media.description.text

        if not current_description.startswith(supposed_credit):
            print '%s seems ok' % vurl.url
            return

        new_description = current_description.replace(supposed_credit, '')

        entry.media.description.text = new_description
        entry = entry.ToString()

        status_code = bridge._make_update_request(uri, entry)

        if status_code == 401:
            bridge.refresh()
            status_code = bridge._make_update_request(uri, entry)

        if status_code == 200:
            print '%s success' % vurl.url

    def _get_supposed_credit(self, vurl, language='en'):
        # Sometimes I hate Python :(
        from apps.accountlinker.models import (
            translate_string, AMARA_DESCRIPTION_CREDIT
        )
        credit = translate_string(AMARA_DESCRIPTION_CREDIT, language)
        return "%s: %s\n\n" % (credit, vurl)

    def handle(self, video_id, *args, **kwargs):
        if video_id:
            try:
                video = Video.objects.get(video_id=video_id)
            except Video.DoesNotExist:
                raise CommandError("Video doesn't exist")

            yt_urls = video.videourl_set.filter(type=VIDEO_TYPE_YOUTUBE)

            if not yt_urls.exists():
                raise CommandError("Not a Youtube video.")

            for vurl in yt_urls:
                self._fix_video(vurl)

            return

        videos = Video.objects.filter(teamvideo__isnull=False)

        urls = VideoUrl.objects.filter(type=VIDEO_TYPE_YOUTUBE,
                video__in=videos)

        print '%s videos to process' % len(urls)

        for vurl in urls:
            self._fix_video(vurl)
