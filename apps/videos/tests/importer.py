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

import datetime

from django.test import TestCase
import mock

from utils import test_utils, test_factories
from videos import signals
from videos.models import Video, VideoUrl, VideoFeed, ImportedVideo
from videos.feed_parser import importer
from videos.types import HtmlFiveVideoType

class VideoImporterTestCase(TestCase):
    @test_utils.patch_for_test('videos.feed_parser.importer.FeedParser')
    def setUp(self, mock_feedparser_class):
        TestCase.setUp(self)
        self.user = test_factories.create_user()
        self.base_url = 'http://example.com/'
        self.mock_feedparser_class = mock_feedparser_class

    def feed_url(self):
        return self.url('feed.rss')

    def url(self, name):
        return self.base_url + name

    def entry(self, name):
        return {
            'link': self.url(name),
        }

    def video_type(self, name):
        return HtmlFiveVideoType(self.url(name))

    def setup_feed_items(self, item_info):
        """Setup the return vaule for FeedParser.

        :param item_info: list of (name, extra_info dict) tuples to
        return.
        """
        self.feed_parser = mock.Mock()
        self.feed_parser.feed.entries = [self.entry(name)
                                    for (name, extra) in item_info]
        self.feed_parser.feed.feed = {}
        self.feed_parser.items.return_value = [
            (self.video_type(name), info, self.entry(name))
            for (name, info) in item_info
        ]

        self.mock_feedparser_class.return_value = self.feed_parser

    def run_import_videos(self, import_since=None):
        import_obj = importer.VideoImporter(self.feed_url(), self.user,
                                            import_since=import_since)
        self.import_videos_rv = import_obj.import_videos()

    def check_videos(self, *feed_item_names):
        all_videos = list(Video.objects.all())
        self.assertEquals(len(all_videos), len(feed_item_names))
        self.assertEquals(set(v.get_video_url() for v in all_videos),
                          set(self.url(name) for name in feed_item_names))
        self.assertEquals(len(self.import_videos_rv), len(feed_item_names))
        self.assertEquals(set(v.id for v in self.import_videos_rv),
                          set(v.id for v in all_videos))

    def test_import(self):
        # test a simple import
        self.setup_feed_items([
            ('item-1', {}),
            ('item-2', {}),
            ('item-3', {}),
        ])
        self.run_import_videos()
        self.feed_parser.items.assert_called_with(
            since=None,
            ignore_error=True,
        )
        self.check_videos('item-1', 'item-2', 'item-3')

    def test_import_extra_values(self):
        # test feedparser returning extra values to set on our items.
        self.setup_feed_items([
            ('item-1', {'title': 'foo'}),
            ('item-2', {'title': 'bar'}),
            ('item-3', {}),
        ])
        self.run_import_videos()
        self.check_videos('item-1', 'item-2', 'item-3')
        video1 = VideoUrl.objects.get(url=self.url('item-1')).video
        video2 = VideoUrl.objects.get(url=self.url('item-2')).video
        self.assertEquals(video1.title, 'foo')
        self.assertEquals(video2.title, 'bar')

    def test_import_since(self):
        # test the import_since paramater.  There's not much to do here, just
        # make sure it gets passed on to the items function.
        self.setup_feed_items([])
        self.run_import_videos(import_since=self.url('item-1'))
        self.feed_parser.items.assert_called_with(
            since=self.url('item-1'),
            ignore_error=True,
        )

    def test_import_extra_links_from_youtube(self):
        # test importing extra items from youtube.
        #
        # For youtube, we import extra videos based on the links for the feed.
        # The way it works is that each time we parse a feed, we look for a
        # link with rel=next.  If the link is present, then we parse that link
        # and check again for a link with rel=next.
        self.base_url = 'http://youtube.com/'
        # to keep things simple, each feed has 0 items.  We just care about
        # which feed urls get parsed.
        self.setup_feed_items([])
        links_iter = iter([
            [
                { 'href': self.url('feed.rss?p=1'), 'rel': 'next', },
                { 'href': self.url('other-thing.html')},
            ],
            [
                { 'href': self.url('feed.rss?p=2'), 'rel': 'next', },
                { 'href': self.url('license.html'), 'rel': 'license'},
            ],
            [
                { 'href': self.url('license.html'), 'rel': 'license'},
            ],
        ])
        urls_parsed = []
        def make_feed_parser(url):
            urls_parsed.append(url)
            self.feed_parser.feed.feed = {
                'links': links_iter.next()
            }
            return self.feed_parser
        self.mock_feedparser_class.side_effect = make_feed_parser

        self.run_import_videos()
        self.assertEquals(urls_parsed, [
            self.feed_url(),
            self.url('feed.rss?p=1'),
            self.url('feed.rss?p=2'),
        ])

class VideoFeedTest(TestCase):
    @test_utils.patch_for_test('videos.models.VideoImporter')
    def setUp(self, MockVideoImporter):
        self.MockVideoImporter = MockVideoImporter
        self.mock_video_importer = mock.Mock()
        self.mock_video_importer.last_link = None
        MockVideoImporter.return_value = self.mock_video_importer

    def test_video_feed(self):
        mock_feed_imported_handler = mock.Mock()
        signals.feed_imported.connect(mock_feed_imported_handler, weak=False)
        self.addCleanup(signals.feed_imported.disconnect,
                        mock_feed_imported_handler)
        user = test_factories.create_user()

        url = 'http://example.com/feed.rss'
        last_link = 'http://example.com/video3'
        feed = VideoFeed.objects.create(url=url, user=user)

        feed_videos = list(test_factories.create_video() for i in xrange(3))

        self.mock_video_importer.last_link = last_link
        self.mock_video_importer.import_videos.return_value = feed_videos
        rv = feed.update()
        self.MockVideoImporter.assert_called_with(url, user, '')
        self.mock_video_importer.import_videos.assert_called()
        self.assertEquals(rv, feed_videos)
        self.assertEquals(feed.last_link, last_link)
        mock_feed_imported_handler.assert_called_with(
            signal=signals.feed_imported, sender=feed, new_videos=feed_videos)
        # check doing another update, we should pass the last link in to
        # VideoImporter
        self.mock_video_importer.import_videos.return_value = []
        rv = feed.update()
        self.MockVideoImporter.assert_called_with(url, user, last_link)
        self.mock_video_importer.import_videos.assert_called()
        self.assertEquals(rv, [])
        mock_feed_imported_handler.assert_called_with(
            signal=signals.feed_imported, sender=feed, new_videos=[])
        self.assertEquals(feed.last_link, self.mock_video_importer.last_link)

    @test_utils.patch_for_test('videos.models.VideoFeed.now')
    def test_update_logging(self, mock_now):
        feed = VideoFeed.objects.create(url='http://example.com/feed.rss')
        # run update().  Check that we update last_imported and that
        # ImportedVideo objects get created.  ImportedVideo objects should be
        # ordered last to first
        now = datetime.datetime(2000, 1, 1)
        mock_now.return_value = now
        videos = [test_factories.create_video() for i in xrange(5)]
        self.mock_video_importer.import_videos.return_value = videos
        feed.update()
        self.assertEquals(feed.last_update, now)
        self.assertEquals([iv.video for iv in feed.importedvideo_set.all()],
                          list(reversed(videos)))
        # run VideoFeed.update() again.  new videos should be added at the
        # start of the list
        videos2 = [test_factories.create_video() for i in xrange(5)]
        self.mock_video_importer.import_videos.return_value = videos2
        now += datetime.timedelta(days=1)
        mock_now.return_value = now
        feed.update()
        self.assertEquals(feed.last_update, now)
        self.assertEquals([iv.video for iv in feed.importedvideo_set.all()],
                          list(reversed(videos2)) + list(reversed(videos)))
        # run VideoFeed.update() one more time, with no new videos.
        # last_update should still be upated
        # start of the list
        self.mock_video_importer.import_videos.return_value = []
        now += datetime.timedelta(days=1)
        mock_now.return_value = now
        feed.update()
        self.assertEquals(feed.last_update, now)
        self.assertEquals([iv.video for iv in feed.importedvideo_set.all()],
                          list(reversed(videos2)) + list(reversed(videos)))
