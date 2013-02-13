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

import feedparser
from StringIO import StringIO

from django.core.urlresolvers import reverse
from django.test import TestCase

from apps.videos.feed_parser import FeedParser
from apps.videos.models import Video, VideoFeed
from apps.videos.types.vimeo import VimeoVideoType


class TestFeedsSubmit(TestCase):
    def setUp(self):
        self.client.login(username='admin', password='admin')

    def test_video_feed_submit(self):
        old_count = Video.objects.count()
        data = {
            'feed_url': u'http://blip.tv/coxman/rss'
        }
        response = self.client.post(reverse('videos:create_from_feed'), data)
        self.assertRedirects(response, reverse('videos:create'))
        self.assertNotEqual(old_count, Video.objects.count())
        self.assertEqual(Video.objects.count(), 7)

    def test_video_youtube_username_submit(self):
        self.assertEqual(Video.objects.count(), 0)
        data = {
            'usernames': u'amaratestuser'
        }
        response = self.client.post(reverse('videos:create_from_feed'), data)
        self.assertRedirects(response, reverse('videos:create'))
        self.assertEqual(Video.objects.count(), 3)

    def test_empty_feed_submit(self):
        base_open_resource = feedparser._open_resource

        def _open_resource_mock(*args, **kwargs):
            return StringIO(str(u"".join([u"<?xml version='1.0' encoding='UTF-8'?>",
            u"<feed xmlns='http://www.w3.org/2005/Atom' xmlns:openSearch='http://a9.com/-/spec/opensearchrss/1.0/'>",
            u"<id>http://gdata.youtube.com/feeds/api/users/test/uploads</id>",
            u"<updated>2011-07-05T09:17:40.888Z</updated>",
            u"<category scheme='http://schemas.google.com/g/2005#kind' term='http://gdata.youtube.com/schemas/2007#video'/>",
            u"<title type='text'>Uploads by test</title>",
            u"<logo>http://www.youtube.com/img/pic_youtubelogo_123x63.gif</logo>",
            u"<link rel='related' type='application/atom+xml' href='https://gdata.youtube.com/feeds/api/users/test'/>",
            u"<link rel='alternate' type='text/html' href='https://www.youtube.com/profile_videos?user=test'/>",
            u"<link rel='http://schemas.google.com/g/2005#feed' type='application/atom+xml' href='https://gdata.youtube.com/feeds/api/users/test/uploads'/>",
            u"<link rel='http://schemas.google.com/g/2005#batch' type='application/atom+xml' href='https://gdata.youtube.com/feeds/api/users/test/uploads/batch'/>",
            u"<link rel='self' type='application/atom+xml' href='https://gdata.youtube.com/feeds/api/users/test/uploads?start-index=1&amp;max-results=25'/>",
            u"<author><name>test</name><uri>https://gdata.youtube.com/feeds/api/users/test</uri></author>",
            u"<generator version='2.0' uri='http://gdata.youtube.com/'>YouTube data API</generator>",
            u"<openSearch:totalResults>0</openSearch:totalResults><openSearch:startIndex>1</openSearch:startIndex>",
            u"<openSearch:itemsPerPage>25</openSearch:itemsPerPage></feed>"])))

        feedparser._open_resource = _open_resource_mock

        old_count = Video.objects.count()
        feed_url = u'http://gdata.youtube.com/feeds/api/users/testempty/uploads'
        data = {
            'feed_url': feed_url,
            'save_feed': True
        }
        response = self.client.post(reverse('videos:create_from_feed'), data)
        self.assertRedirects(response, reverse('videos:create'))
        self.assertEqual(old_count, Video.objects.count())

        vf = VideoFeed.objects.get(url=feed_url)
        self.assertEqual(vf.last_link, '')

        feedparser._open_resource = base_open_resource

class TestFeedParser(TestCase):
    # TODO: add test for MediaFeedEntryParser. I just can't find RSS link for it
    # RSS should look like this http://www.dailymotion.com/rss/ru/featured/channel/tech/1
    # but not from supported site
    youtube_feed_url_pattern =  'https://gdata.youtube.com/feeds/api/users/%s/uploads'
    youtube_username = 'universalsubtitles'

    vimeo_feed_url = 'http://vimeo.com/blakewhitman/videos/rss'

    def setUp(self):
        pass

    def test_vimeo_feed_parsing(self):
        # vimeo is blocking us from jenkins, we need to coordinate with
        # them on how best to proceed here
        return
        feed_parser = FeedParser(self.vimeo_feed_url)
        vt, info, entry = feed_parser.items().next()
        self.assertTrue(isinstance(vt, VimeoVideoType))

        video, created = Video.get_or_create_for_url(vt=vt)
        self.assertTrue(video)

    def test_youtube_feed_parsing(self):
        # I hate you, Python.
        from videos.types.youtube import YoutubeVideoType as YoutubeVideoTypeA
        from apps.videos.types.youtube import YoutubeVideoType as YoutubeVideoTypeB

        feed_url = self.youtube_feed_url_pattern % self.youtube_username

        feed_parser = FeedParser(feed_url)
        vt, info, entry = feed_parser.items().next()
        self.assertTrue(isinstance(vt, YoutubeVideoTypeA)
                        or isinstance(vt, YoutubeVideoTypeB))

        video, created = Video.get_or_create_for_url(vt=vt)
        self.assertTrue(video)

# FIXME: this test is failing, and it looks like it's because of the feed.
#    def test_enclosure_parsing(self):
#        feed_url = 'http://webcast.berkeley.edu/media/common/rss/Computer_Science_10__001_Spring_2011_Video__webcast.rss'
#
#        feed_parser = FeedParser(feed_url)
#        vt, info, entry = feed_parser.items().next()
#        self.assertTrue(isinstance(vt, HtmlFiveVideoType))
#
#        video, created = Video.get_or_create_for_url(vt=vt)
#        self.assertTrue(video)

    def test_dailymotion_feed_parsing(self):
        # Welp.
        from videos.types.dailymotion import DailymotionVideoType as DailymotionVideoTypeA
        from apps.videos.types.dailymotion import DailymotionVideoType as DailymotionVideoTypeB

        feed_url = 'http://www.dailymotion.com/rss/ru/featured/channel/tech/1'

        feed_parser = FeedParser(feed_url)
        vt, info, entry = feed_parser.items().next()
        self.assertTrue(isinstance(vt, DailymotionVideoTypeA)
                        or isinstance(vt, DailymotionVideoTypeB))

        video, created = Video.get_or_create_for_url(vt=vt)
        self.assertTrue(video)

