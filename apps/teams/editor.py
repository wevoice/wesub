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

from django.utils.translation import ugettext as _

from subtitles import editorworkmodes
from utils.behaviors import DONT_OVERRIDE

@editorworkmodes.editor_work_mode.override
def team_editor_work_mode(user, video, language_code):
    team_video = video.get_team_video()
    if team_video is None or not team_video.team.is_tasks_team():
        return DONT_OVERRIDE

    task = team_video.get_task_for_editor(language_code)
    if task is not None:
        if task.is_approve_task():
            heading = _("Approve Work")
        elif task.is_review_task():
            heading = _("Review Work")
        else:
            # get_task_for_editor should only return approve/review tasks
            raise ValueError("Wrong task type: %s" % task)
        return editorworkmodes.ReviewWorkMode(heading)
    else:
        return editorworkmodes.NormalWorkMode()
