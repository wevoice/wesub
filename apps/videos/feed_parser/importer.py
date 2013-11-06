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

"""videos.feed_parser.import -- Import videos from a feed."""

from .parser import FeedParser

class VideoImporter(object):
    """Import videos from a feed URL."""
    def __init__(self, url, user, import_since=None, team=None):
        """Create a VideoImporter

        :param url: feed url
        :param user: User that creates videos for
        :param import_since: URL of the last imported link.  If set, we will
        only import videos after this link
        :param team: Team to create videos for
        """
        self.url = url
        self.user = user
        self.import_since = import_since
        self.checked_entries = 0
        self.last_link = ''
        self.team = team

    def import_videos(self):
        self._created_videos = []
        feed_parser = FeedParser(self.url)
        # the link at the top of the feed should be the latest link
        try:
            self.last_link = feed_parser.feed.entries[0]['link']
        except (IndexError, KeyError):
            pass
        self._create_videos(feed_parser)
        if self.import_since is None and 'youtube' in self.url:
            self._import_extra_links_from_youtube(feed_parser)
        rv = self._created_videos
        del self._created_videos
        return rv

    def _next_urls(self, feed_parser):
        return [
            link for link in feed_parser.feed.feed.get('links', [])
            if link.get('rel') == 'next'
        ]

    def _import_extra_links_from_youtube(self, main_feed_parser):
        next_urls = self._next_urls(main_feed_parser)

        while next_urls:
            url = next_urls[0]['href']
            feed_parser = FeedParser(url)
            self._create_videos(feed_parser)
            next_urls = self._next_urls(feed_parser)

    def _create_videos(self, feed_parser):
        _iter = feed_parser.items(since=self.import_since,
                                  ignore_error=True)

        for vt, info, entry in _iter:
            if vt:
                self._create_video(vt, info, entry)
            self.checked_entries += 1

    def _create_video(self, video_type, info, entry):
        from videos.models import Video
        from teams.models import TeamVideo
        from teams.signals import api_teamvideo_new
        video, created = Video.get_or_create_for_url(
            vt=video_type, user=self.user)
        if info:
            for name, value in info.items():
                setattr(video, name, value)
            video.save()
        if created:
            self._created_videos.append(video)
        if created and self.team is not None:
            tv = TeamVideo.objects.create(
                video=video, team=self.team, added_by=self.user,
                description=video.description)
            api_teamvideo_new.send(tv)
