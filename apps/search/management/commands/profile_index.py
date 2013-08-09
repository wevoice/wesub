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

import cProfile
import pstats

from django.core.management.base import BaseCommand, CommandError

from haystack import site
from videos.models import Video

class Command(BaseCommand):
    args = '<video pk>'
    help = 'Profile indexing'

    def handle(self, *args, **options):
        if len(args) < 1 or len(args) > 3:
            raise CommandError(
                'Usage profile_index <video-pk> [sort] [restrictions]')
        try:
            video = Video.objects.get(pk=args[0])
        except Video.DoesNotExist:
            raise CommandError('Video not found: %s' % (args[0],))
        try:
            sort = args[1]
        except IndexError:
            sort = 'cumulative'
        try:
            restrictions = args[2]
        except IndexError:
            restrictions = 10
        else:
            if '.' in restrictions:
                restrictions = float(restrictions)
            else:
                restrictions = int(restrictions)
        video_index = site.get_index(Video)
        pr = cProfile.Profile()
        pr.enable()
        video_index.update_object(video)
        pr.disable()
        stats = pstats.Stats(pr, stream=self.stdout)
        stats.strip_dirs().sort_stats(sort).print_stats(restrictions)
