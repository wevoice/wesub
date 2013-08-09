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

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from haystack import site
from teams.models import Team
from videos.models import Video
import time

class Command(BaseCommand):
    args = '<team slug>'
    help = 'Re-index all videos from a team'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Usage index_team_videos <team-slug>')
        try:
            team = Team.objects.get(slug=args[0])
        except Team.DoesNotExist:
            raise CommandError('Team with slug %r not found' % (args[0],))

        video_index = site.get_index(Video)
        self.stdout.write("Fetching videos\n")
        video_list = list(team.videos.all())
        start_time = time.time()
        self.stdout.write("Indexing")
        self.stdout.flush()
        with transaction.commit_manually():
            for video in video_list:
                video_index.update_object(video)
                self.stdout.write(".")
                self.stdout.flush()
                # commit after each pass to make sure that we aren't keeping
                # open any database locks
                transaction.commit()
        end_time = time.time()
        self.stdout.write("\ndone indexed %s videos in %0.1f seconds\n" %
                          (len(video_list), end_time-start_time))

