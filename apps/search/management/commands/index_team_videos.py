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

