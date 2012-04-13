# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
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
import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'This command "view" 1000 videos widget and then migrate data to DB and uddate search index'
    def handle(self, *args, **kwargs):
        from videos.models import Video, Subtitle, SubtitleVersion
        from auth.models import CustomUser
        from teams.models import TeamVideo


        AVAILABLE_METRICS= {
            "users":{
                "model": CustomUser,
            },
            "videos":{
                "model": Video
            },
            "videos-with-subs":{

                "model": Video,
                "filters": {
                    "was_subtitled": True
                },
            },
            "subtitles":{
                "model": Subtitle
            },
            "subtitle-versions":{
                "model": SubtitleVersion
            },
            "team-videos":{
                "model": TeamVideo
            }
        }
        conf = AVAILABLE_METRICS.get(args[0], None)
        if not conf:
            print "Error, available metrics are %s" % (",".join(AVAILABLE_METRICS.keys()))
            
            sys.exit(3)
        query = conf['model'].objects.all()
        filters = conf.get('filters', None)
        if filters:
            query = query.filter(**filters)
        print query.count()
        sys.exit(0)
         

