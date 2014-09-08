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
from django.utils.translation import ugettext_lazy

from subtitles import workflows
from teams.models import Task
from utils.behaviors import DONT_OVERRIDE
from videos.tasks import video_changed_tasks

class Complete(workflows.Action):
    """Used when the initial transcriber/translator completes their work """
    name = 'complete'
    label = ugettext_lazy('Complete')
    in_progress_text = ugettext_lazy('Saving')
    visual_class = 'endorse'
    complete = True

    def do_perform(self, user, video, subtitle_language, saved_version):
        if saved_version is not None:
            # I think the cleanest way to handle things would be to create the
            # review/approve task now but there is already code in
            # subtitles.pipeline to do that.  It would be nice to move that
            # code out of that app and into here, but maybe we should just
            # leave it and wait to phase the tasks system out
            return
        task = (video.get_team_video().task_set
                .incomplete_subtitle_or_translate()
                .filter(language=subtitle_language.language_code).get())
        task.complete()

def _complete_task(user, video, subtitle_language, saved_version, approved):
    team_video = video.get_team_video()
    task = (team_video.task_set
            .incomplete_review_or_approve()
            .get(language=subtitle_language.language_code))
    if task.assignee is None:
        task.assignee = user
    elif task.assignee != user:
        raise ValueError("Task not assigned to user")
    task.new_subtitle_version = subtitle_language.get_tip()
    task.approved = approved
    task.complete()
    if saved_version is None:
        if saved_version is None:
            version_id = None
        else:
            version_id = saved_version.id
            video_changed_tasks.delay(team_video.video_id, version_id)

class Approve(workflows.Action):
    name = 'approve'
    label = ugettext_lazy('Approve')
    in_progress_text = ugettext_lazy('Approving')
    visual_class = 'endorse'
    complete = True

    def do_perform(self, user, video, subtitle_language, saved_version):
        _complete_task(user, video, subtitle_language, saved_version,
                       Task.APPROVED_IDS['Approved'])

class SendBack(workflows.Action):
    name = 'send-back'
    label = ugettext_lazy('Send Back')
    in_progress_text = ugettext_lazy('Sending back')
    visual_class = 'send-back'
    complete = False

    def do_perform(self, user, video, subtitle_language, saved_version):
        _complete_task(user, video, subtitle_language, saved_version,
                       Task.APPROVED_IDS['Rejected'])

class TaskTeamWorkflow(workflows.Workflow):
    def __init__(self, team_video, language_code):
        workflows.Workflow.__init__(self, team_video.video, language_code)
        self.team_video = team_video

    def get_work_mode(self, user):
        task = self.team_video.get_task_for_editor(self.language_code)
        if task is not None:
            if task.is_approve_task():
                heading = _("Approve Work")
            elif task.is_review_task():
                heading = _("Review Work")
            else:
                # get_task_for_editor should only return approve/review tasks
                raise ValueError("Wrong task type: %s" % task)
            return workflows.ReviewWorkMode(heading)
        else:
            return workflows.NormalWorkMode()

    def get_actions(self, user):
        task = self.team_video.get_task_for_editor(self.language_code)
        if task is not None:
            # review/approve task
            return [SendBack(), Approve()]
        else:
            # subtitle/translate task
            return [Complete()]

    def user_can_view_private_subtitles(self, user):
        raise NotImplementedError()

    def user_can_edit_subtitles(self, user):
        raise NotImplementedError()

@workflows.get_workflow.override
def get_task_team_workflow(video, language_code):
    team_video = video.get_team_video()
    if team_video is None or not team_video.team.is_tasks_team():
        return DONT_OVERRIDE
    return TaskTeamWorkflow(team_video, language_code)
