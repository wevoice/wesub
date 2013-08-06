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

import string

from django.utils.translation import gettext as _

from utils.behaviors import DONT_OVERRIDE
from videos.behaviors import make_video_title

@make_video_title.override
def amara_make_video_title(video, title, metadata):
    if not metadata.get('speaker-name'):
        return DONT_OVERRIDE
    tv = video.get_team_video()
    if tv is None or tv.team.slug != 'ted':
        return DONT_OVERRIDE
    return string.Template(_('$speaker_name: $title')).substitute({
        'speaker_name': metadata['speaker-name'],
        'title': title,
    })
