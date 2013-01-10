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
from django.conf import settings
import gdata

from apps.videos.models import VideoUrl, Video, VIDEO_TYPE_YOUTUBE
from apps.videos.types import video_type_registrar, UPDATE_VERSION_ACTION
from apps.videos.types.youtube import YouTubeApiBridge


UPLOAD_URI_BASE = 'http://gdata.youtube.com/feeds/api/users/default/uploads/%s'
YOUTUBE_API_SECRET  = getattr(settings, "YOUTUBE_API_SECRET", None)


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--video', '-d', dest='video_id', type="str",
            default=None),
    )

    def _resync_subs_for_video(self, video):
        from apps.accountlinker.models import ThirdPartyAccount
        languages = video.subtitlelanguage_set.all()
        print video

        for language in languages:
            latest_version = language.latest_version(public_only=True)

            if latest_version:
                print ' ', language
            else:
                print '  no version for:', language
                continue

            ThirdPartyAccount.objects.mirror_on_third_party(video,
                    language, UPDATE_VERSION_ACTION,
                    version=latest_version)

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

        uri = UPLOAD_URI_BASE % bridge.youtube_video_id
        entry = bridge.GetVideoEntry(uri=uri)
        entry = entry.to_string()
        entry = gdata.youtube.YouTubeVideoEntryFromString(entry)

        current_description = entry.media.description.text

        # For some reason the above video.get_absolute_url() call didn't
        # include the /en/ prefix.
        unisubs_video_url = "http://www.universalsubtitles.org/en%s" % video_url
        amara_video_url = "http://www.amara.org/en%s" % video_url

        unisubs_supposed_credit = self._get_supposed_credit(unisubs_video_url,
                language_code)
        amara_supposed_credit = self._get_supposed_credit(amara_video_url,
                language_code)

        credits = (amara_supposed_credit, unisubs_supposed_credit,)

        if not current_description.startswith(credits):
            print "%s doesn't have desc credit" % vurl.url
            return

        if current_description.startswith(amara_supposed_credit):
            new_description = current_description.replace(
                    amara_supposed_credit, '')

        if current_description.startswith(unisubs_supposed_credit):
            new_description = current_description.replace(
                    unisubs_supposed_credit, '')

        entry.media.description.text = new_description
        entry = entry.ToString()

        status_code = bridge._make_update_request(uri, entry)

        if status_code == 401:
            bridge.refresh()
            status_code = bridge._make_update_request(uri, entry)

        if status_code == 200:
            print '%s success' % vurl.url
            return

        print 'FAIL %s' % vurl.url

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

            self._resync_subs_for_video(video)

            return

        videos = Video.objects.filter(teamvideo__isnull=False)

        urls = VideoUrl.objects.filter(type=VIDEO_TYPE_YOUTUBE,
                video__in=videos)

        print '%s video descriptions to process' % len(urls)

        for vurl in urls:
            self._fix_video(vurl)

        # Now, sync all completed languages to Youtube to remove the last sub
        # credit.

        print '%s videos to resync' % len(videos)

        for video in videos:
            self._resync_subs_for_video(video)
