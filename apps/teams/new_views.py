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
import pickle

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from . import views as old_views
from . import forms
from . import permissions
from . import tasks
from .models import Setting, Team, Project, TeamLanguagePreference
from .statistics import compute_statistics
from django.contrib.auth.views import redirect_to_login
from utils.breadcrumbs import BreadCrumb
from utils.translation import get_language_choices
from videos.models import Action

logger = logging.getLogger('teams.views')

ACTIONS_ON_PAGE = 20

def team_view(view_func):
    def wrapper(request, slug, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect_to_login(request.path)
        try:
            team = Team.objects.get(slug=slug, members__user=request.user)
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

def fetch_actions_for_activity_page(team, tab, page, params):
    if tab == 'team':
        action_qs = Action.objects.filter(team=team)
    else:
        video_language = params.get('video_language')
        subtitles_language = params.get('subtitles_language', 'any')
        if video_language == 'any':
            video_language = None
        action_qs = team.fetch_video_actions(video_language)
        if subtitles_language != 'any':
            action_qs = action_qs.filter(
                new_language__language_code=subtitles_language)

    end = page * ACTIONS_ON_PAGE
    start = end - ACTIONS_ON_PAGE

    if params.get('action_type', 'any') != 'any':
        action_qs = action_qs.filter(action_type=params.get('action_type'))

    action_qs = action_qs.select_related('new_language', 'video')

    sort = params.get('sort', '-created')
    action_qs = action_qs.order_by(sort)

    action_qs = action_qs[start:end].select_related(
        'user', 'new_language__video'
    )
    return list(action_qs)

@team_view
def activity(request, team, tab):
    try:
        page = int(request.GET['page'])
    except (ValueError, KeyError):
        page = 1
    activity_list = fetch_actions_for_activity_page(team, tab, page,
                                                    request.GET)
    language_choices = None
    if tab == 'videos':
        readable_langs = TeamLanguagePreference.objects.get_readable(team)
        language_choices = [(code, name) for code, name in get_language_choices()
                            if code in readable_langs]
    action_types = Action.TYPES_CATEGORIES[tab]

    has_more = len(activity_list) >= ACTIONS_ON_PAGE

    filtered = bool(set(request.GET.keys()).intersection([
        'action_type', 'language', 'sort']))

    next_page_query = request.GET.copy()
    next_page_query['page'] = page + 1

    context = {
        'activity_list': activity_list,
        'filtered': filtered,
        'action_types': action_types,
        'language_choices': language_choices,
        'team': team,
        'user': request.user,
        'next_page': page + 1,
        'next_page_query': next_page_query.urlencode(),
        'tab': tab,
        'has_more': has_more,
        'breadcrumbs': [
            BreadCrumb(team, 'teams:dashboard', team.slug),
            BreadCrumb(_('Activity')),
        ],
    }
    if team.is_old_style():
        template_dir = 'teams/'
    else:
        template_dir = 'new-teams/'

    if not request.is_ajax():
        return render(request, template_dir + 'activity.html', context)
    else:
        # for ajax requests we only want to return the activity list, since
        # that's all that the JS code needs.
        return render(request, template_dir + '_activity-list.html', context)

@team_view
def statistics(request, team, tab):
    """For the team activity, statistics tabs
    """
    if (tab == 'teamstats' and
        not permissions.can_view_stats_tab(team, request.user)):
        return HttpResponseForbidden("Not allowed")
    cache_key = 'stats-' + team.slug + '-' + tab
    cached_context = cache.get(cache_key)
    if cached_context:
        context = pickle.loads(cached_context)
    else:
        context = compute_statistics(team, stats_type=tab)
        cache.set(cache_key, pickle.dumps(context), 60*60*24)
    context['tab'] = tab
    context['team'] = team
    context['breadcrumbs'] = [
        BreadCrumb(team, 'teams:dashboard', team.slug),
        BreadCrumb(_('Activity')),
    ]
    if team.is_old_style():
        return render(request, 'teams/statistics.html', context)
    else:
        return render(request, 'new-teams/statistics.html', context)


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
        'team_messages': team.get_messages([
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
        'team': team,
        'form': form,
        'breadcrumbs': [
            BreadCrumb(team, 'teams:dashboard', team.slug),
            BreadCrumb(_('Settings')),
        ],
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
        'team': team,
        'form': form,
        'breadcrumbs': [
            BreadCrumb(team, 'teams:dashboard', team.slug),
            BreadCrumb(_('Settings'), 'teams:settings_basic', team.slug),
            BreadCrumb(_('Messages')),
        ],
    })

@team_settings_view
def settings_projects(request, team):
    if team.is_old_style():
        return old_views.settings_projects(request, team)

    projects = team.project_set.exclude(name=Project.DEFAULT_NAME)

    return render(request, "new-teams/settings-projects.html", {
        'team': team,
        'projects': projects,
        'breadcrumbs': [
            BreadCrumb(team, 'teams:dashboard', team.slug),
            BreadCrumb(_('Settings'), 'teams:settings_basic', team.slug),
            BreadCrumb(_('Projects')),
        ],
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
        'team': team,
        'form': form,
        'breadcrumbs': [
            BreadCrumb(team, 'teams:dashboard', team.slug),
            BreadCrumb(_('Settings'), 'teams:settings_basic', team.slug),
            BreadCrumb(_('Projects'), 'teams:settings_projects', team.slug),
            BreadCrumb(_('Add Project')),
        ],
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
        'team': team,
        'form': form,
        'breadcrumbs': [
            BreadCrumb(team, 'teams:dashboard', team.slug),
            BreadCrumb(_('Settings'), 'teams:settings_basic', team.slug),
            BreadCrumb(_('Projects'), 'teams:settings_projects', team.slug),
            BreadCrumb(project.name),
        ],
    })

@team_settings_view
def settings_workflows(request, team):
    return team.new_workflow.workflow_settings_view(request, team)
