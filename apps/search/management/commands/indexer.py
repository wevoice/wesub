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

import datetime
from optparse import make_option
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db import reset_queries
from haystack import site

from statistic.models import VideoViewCounter
from videos.models import Video

class Command(BaseCommand):
    help = 'Continuously index videos'

    option_list = BaseCommand.option_list + (
        make_option('--rate', dest='rate',
                    default=1,
                    help='Number of videos per second to index'),
    )

    def handle(self, *args, **options):
        self.queued_versions = []
        self.last_index_time = {}
        self.video_index = site.get_index(Video)
        self.last_fetch_all_videos_time = 0
        self.last_fetch_popular_videos_time = 0
        self.all_video_queue = []
        self.popular_video_queue = []
        time_per_version = 1.0 / options.get('rate', 1)

        while True:
            start_time = time.time()
            if not self.queued_versions:
                self.queue_up_versions()
                queue_time = time.time() - start_time
                self.stdout.write("queue_up_versions() took %0.3fs seconds\n" %
                                  queue_time)
                start_time = time.time()
            video_id = self.index_one_version()
            index_time = time.time() - start_time
            self.stdout.write("indexing %s took %0.3f seconds\n" % (
                video_id, index_time))
            if index_time < time_per_version:
                time.sleep(time_per_version - index_time)

    def queue_up_versions(self):
        current_time = time.time()
        # fetch all video ids every hour
        if (current_time - self.last_fetch_all_videos_time > 3600 or
            len(self.all_video_queue) == 0):
            self.stdout.write("fetching all video ids\n")
            self.fetch_all_video_ids()
            self.last_fetch_all_videos_time = current_time
        # fetch popular videos every 10 minutes
        if (current_time - self.last_fetch_all_videos_time > 600 or
            len(self.popular_video_queue) == 0):
            self.stdout.write("fetching popular video ids\n")
            self.fetch_popular_video_ids()

        # queue 100 videos from the popular list an 100 videos from the
        # non-popular list
        self.queued_versions = (self.popular_video_queue[:100] +
                                self.all_video_queue[:100])

    def fetch_all_video_ids(self):
        self.all_video_queue = list(Video.objects.all().
                                  values_list('id', flat=True))
        self.all_video_queue.sort(
            key=lambda video_pk: self.last_index_time.get(video_pk))

    def fetch_popular_video_ids(self):
        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)

        new_popular_video_queue = set(VideoViewCounter.objects
                                      .filter(date__gt=week_ago)
                                      .order_by()
                                      .distinct()
                                      .values_list('video_id', flat=True))
        # add the old popular video ids, if something just dropped off the
        # list, then we should re-index it
        new_popular_video_queue.update(self.popular_video_queue)
        self.popular_video_queue = list(new_popular_video_queue)
        self.popular_video_queue.sort(
            key=lambda video_pk: self.last_index_time.get(video_pk))

    @transaction.commit_manually
    def index_one_version(self):
        try:
            try:
                video_pk = self.queued_versions.pop()
                video = Video.objects.get(pk=video_pk)
            except Video.DoesNotExist:
                self.stdout.write("video deleted: %s\n" % video_pk)
                return None
            self.video_index.update_object(video)
            self.last_index_time[video_pk] = time.time()
            return video.video_id
        finally:
            # commit even though we didn't update the DB to ensure that our
            # transaction doesn't keep any locks open
            transaction.commit()
            reset_queries()
