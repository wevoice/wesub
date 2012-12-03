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

"""utils.test_factories.py -- Factory methods to create objects for testing
"""

import itertools

from apps.auth.models import CustomUser as User
from apps.teams.models import Project, Team, TeamMember, TeamVideo
from apps.videos.types import video_type_registrar
from apps.videos.models import Video, VideoUrl

create_user_counter = itertools.count()
def create_user(password=None, **kwargs):
    current_count = create_user_counter.next()
    defaults = {
        'username': 'test_user_%s' % current_count,
        'email': 'test_user_%s@example.com' % current_count,
        'notify_by_email': True,
        'valid_email': True,
    }
    defaults.update(kwargs)
    user = User.objects.create(**defaults)
    if password is not None:
        user.set_password(password)
        user.save()
    return user

create_video_counter = itertools.count()
def create_video(url=None, **kwargs):
    current_count = create_video_counter.next()
    defaults = {
        'title': 'Test Video %s' % current_count,
        'duration': 100,
        'allow_community_edits': False,
        'primary_audio_language_code': 'en',
    }
    defaults.update(kwargs)
    video =  Video.objects.create(**defaults)
    # make a video url for this video
    if url is None:
        url = 'http://example.com/videos/video-%s' % current_count
    video_url = VideoUrl.objects.create(url=url, type="H", primary=True,
                                        video=video)
    return video

create_team_counter = itertools.count()
def create_team(**kwargs):
    current_count = create_team_counter.next()
    defaults = {
        'name': 'Team %s' % current_count,
        'slug': 'team-%s' % current_count,
        'membership_policy': Team.OPEN,
    }
    defaults.update(kwargs)
    return Team.objects.create(**defaults)

def create_team_video(team, added_by, video=None, **kwargs):
    if video is None:
        video = create_video()
    return TeamVideo.objects.create(team=team, video=video, added_by=added_by,
                                    **kwargs)

def create_team_member(team, user, **kwargs):
    return TeamMember.objects.create(team=team, user=user, **kwargs)

def create_project(team, **kwargs):
    defaults = {
        'name':'Test Project',
    }
    defaults.update(kwargs)
    return Project.objects.create(team=team, **defaults)
