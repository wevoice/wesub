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

from __future__ import absolute_import

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from teams import views as old_views
from teams import forms
from teams.workflows import TeamWorkflow
from utils.breadcrumbs import BreadCrumb
from .subtitleworkflows import TeamVideoWorkflow

class SimpleTeamWorkflow(TeamWorkflow):
    """Workflow for basic public/private teams

    This class implements a basic workflow for teams:  Members can edit any
    subtitles, non-members can't edit anything.
    """

    type_code = 'S'
    label = _('Simple')
    api_slug = 'simple'
    dashboard_view = staticmethod(old_views.old_dashboard)

    def get_subtitle_workflow(self, team_video):
        """Get the SubtitleWorkflow for a video with this workflow.  """
        return TeamVideoWorkflow(team_video)

    def workflow_settings_view(self, request, team):
        if request.method == 'POST':
            form = forms.SimplePermissionsForm(instance=team,
                                               data=request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _(u'Workflow updated'))
                return redirect('teams:settings_workflows', team.slug)
            else:
                messages.error(request, form.errors.as_text())
        else:
            form = forms.SimplePermissionsForm(instance=team)

        return render(request, "new-teams/settings-simple-workflow.html", {
            'team': team,
            'form': form,
            'breadcrumbs': [
                BreadCrumb(team, 'teams:dashboard', team.slug),
                BreadCrumb(_('Settings'), 'teams:settings_basic', team.slug),
                BreadCrumb(_('Workflow')),
            ],
        })

