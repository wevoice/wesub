# Amara, universalsubtitles.org
#
# Copyright (C) 2015 Participatory Culture Foundation
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

from optparse import make_option

from django.core.management.base import BaseCommand

from videos.models import Video, VideoIndex

class Command(BaseCommand):
    help = "Adds indexes that have to be defined with raw SQL commands"
    def handle(self, **options):
        last_id = -1
        count = 0
        while True:
            if last_id:
                qs = Video.objects.filter(id__gt=last_id)
            else:
                qs = Video.objects.all()
            qs = qs.order_by('id')[:100]
            videos = list(qs)
            if not videos:
                break
            for video in videos:
                VideoIndex.index_video(video)
                last_id = max(last_id, video.id)
                count += 1
            self.stdout.write('indexed {} videos\n'.format(count))
