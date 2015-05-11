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

"""new_views -- New team views

This module holds view functions for new-style teams.  Eventually it should
replace the old views.py module.
"""

from __future__ import absolute_import
import functools
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from . import views as old_views
from . import forms
from . import permissions
from . import tasks
from .models import Setting, Team, Project

logger = logging.getLogger('teams.views')

def team_view(view_func):
    def wrapper(request, slug, *args, **kwargs):
        try:
            team = Team.objects.for_user(request.user, exclude_private=True).get(slug=slug)
        except Team.DoesNotExist:
            raise Http404
        return view_func(request, team, *args, **kwargs)
    return wrapper

def team_settings_view(view_func):
    """Decorator for the team settings pages."""
    @functools.wraps(view_func)
    def wrapper(request, slug, *args, **kwargs):
        team = get_object_or_404(Team, slug=slug)
        if not permissions.can_view_settings_tab(team, request.user):
            messages.error(request,
                           _(u'You do not have permission to edit this team.'))
            return HttpResponseRedirect(team.get_absolute_url())
        return view_func(request, team, *args, **kwargs)
    return login_required(wrapper)

def dashboard(request, slug):
    team = get_object_or_404(
        Team.objects.for_user(request.user, exclude_private=False),
        slug=slug)
    if not team.is_old_style() and not team.user_is_member(request.user):
        return welcome(request, team)
    else:
        return team.new_workflow.dashboard_view(request, team)

def welcome(request, team):
    if team.is_visible:
        videos = team.videos.order_by('-id')[:2]
    else:
        videos = None
    return render(request, 'new-teams/welcome.html', {
        'team': team,
        'messages': team.get_messages([
            'pagetext_welcome_heading',
        ]),
        'videos': videos,
    })

@team_settings_view
def settings_basic(request, team):
    if team.is_old_style():
        return old_views.settings_basic(request, team)

    if permissions.can_rename_team(team, request.user):
        FormClass = forms.RenameableSettingsForm
    else:
        FormClass = forms.SettingsForm

    if request.POST:
        form = FormClass(request.POST, request.FILES, instance=team)

        is_visible = team.is_visible

        if form.is_valid():
            try:
                form.save()
            except:
                logger.exception("Error on changing team settings")
                raise

            if is_visible != form.instance.is_visible:
                tasks.update_video_public_field.delay(team.id)
                tasks.invalidate_video_visibility_caches.delay(team)

            messages.success(request, _(u'Settings saved.'))
            return HttpResponseRedirect(request.path)
    else:
        form = FormClass(instance=team)

    return render(request, "new-teams/settings.html", {
            'team': team, 'form': form,
    })

@team_settings_view
def settings_messages(request, team):
    if team.is_old_style():
        return old_views.settings_messages(request, team)

    initial = team.settings.all_messages()
    if request.POST:
        form = forms.GuidelinesMessagesForm(request.POST, initial=initial)

        if form.is_valid():
            for key, val in form.cleaned_data.items():
                setting, c = Setting.objects.get_or_create(team=team, key=Setting.KEY_IDS[key])
                setting.data = val
                setting.save()

            messages.success(request, _(u'Guidelines and messages updated.'))
            return HttpResponseRedirect(request.path)
    else:
        form = forms.GuidelinesMessagesForm(initial=initial)

    return render(request, "new-teams/settings-messages.html", {
            'team': team, 'form': form,
    })

@team_settings_view
def settings_projects(request, team):
    if team.is_old_style():
        return old_views.settings_projects(request, team)

    projects = team.project_set.exclude(name=Project.DEFAULT_NAME)

    return render(request, "new-teams/settings-projects.html", {
            'team': team, 'projects': projects,
    })

@team_settings_view
def add_project(request, team):
    if team.is_old_style():
        return old_views.add_project(request, team)

    if request.POST:
        form = forms.ProjectForm(team, data=request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('teams:settings_projects', args=(team.slug,))
            )
    else:
        form = forms.ProjectForm(team)

    return render(request, "new-teams/settings-projects-add.html", {
            'team': team, 'form': form,
    })

@team_settings_view
def edit_project(request, team, project_slug):
    if team.is_old_style():
        return old_views.edit_project(request, team, project_slug)

    project = get_object_or_404(Project, slug=project_slug)
    if 'delete' in request.POST:
        project.delete()
        return HttpResponseRedirect(
            reverse('teams:settings_projects', args=(team.slug,))
        )
    elif request.POST:
        form = forms.ProjectForm(team, instance=project, data=request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('teams:settings_projects', args=(team.slug,))
            )
    else:
        form = forms.ProjectForm(team, instance=project)

    return render(request, "new-teams/settings-projects-edit.html", {
            'team': team, 'form': form,
    })

@team_settings_view
def settings_workflows(request, team):
    return team.new_workflow.workflow_settings_view(request, team)
