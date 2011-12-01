# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2011 Participatory Culture Foundation
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

from utils import render_to, render_to_json
from utils.translation import get_languages_list
from teams.forms import (
    CreateTeamForm, EditTeamForm, EditTeamFormAdmin, AddTeamVideoForm,
    EditTeamVideoForm, EditLogoForm, AddTeamVideosFromFeedForm, TaskAssignForm,
    SettingsForm, CreateTaskForm, PermissionsForm, WorkflowForm, InviteForm
)
from teams.models import Team, TeamMember, Invite, Application, TeamVideo, Task, Project
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext
from django.conf import settings
from django.views.generic.list_detail import object_list
from django.template import RequestContext
from django.db.models import Q, Count
from django.contrib.auth.decorators import permission_required
import random
from widget.views import base_widget_params
import widget
from videos.models import Action
from django.utils import simplejson as json
from utils.amazon import S3StorageError
from utils.translation import get_user_languages_from_request
from teams.search_indexes import TeamVideoLanguagesIndex
from widget.rpc import add_general_settings
from django.contrib.admin.views.decorators import staff_member_required

from teams.permissions import (
    can_add_video, can_assign_role, can_view_settings_tab, can_assign_tasks,
    can_create_task_subtitle, can_create_task_translate, can_create_task_review,
    can_create_task_approve, can_view_tasks_tab, can_invite, roles_user_can_assign,
    can_join_team, can_edit_video, can_create_tasks, can_delete_tasks
)

TEAMS_ON_PAGE = getattr(settings, 'TEAMS_ON_PAGE', 10)
HIGHTLIGHTED_TEAMS_ON_PAGE = getattr(settings, 'HIGHTLIGHTED_TEAMS_ON_PAGE', 10)
CUTTOFF_DUPLICATES_NUM_VIDEOS_ON_TEAMS = getattr(settings, 'CUTTOFF_DUPLICATES_NUM_VIDEOS_ON_TEAMS', 20)

VIDEOS_ON_PAGE = getattr(settings, 'VIDEOS_ON_PAGE', 15) 
MEMBERS_ON_PAGE = getattr(settings, 'MEMBERS_ON_PAGE', 15)
APLICATIONS_ON_PAGE = getattr(settings, 'APLICATIONS_ON_PAGE', 15)
ACTIONS_ON_PAGE = getattr(settings, 'ACTIONS_ON_PAGE', 20)
DEV = getattr(settings, 'DEV', False)
DEV_OR_STAGING = DEV or getattr(settings, 'STAGING', False)

def index(request, my_teams=False):
    q = request.REQUEST.get('q')
    
    ordering = request.GET.get('o', 'name')

    if my_teams and request.user.is_authenticated():
        qs = Team.objects.filter(members__user=request.user)
    else:
        qs = Team.objects.for_user(request.user).annotate(_member_count=Count('users__pk'))
    
    if q:
        qs = qs.filter(Q(name__icontains=q)|Q(description__icontains=q))
    
    order_fields = {
        'name': 'name',
        'date': 'created',
        'members': '_member_count'
    }
    order_fields_name = {
        'name': _(u'Name'),
        'date': _(u'Newest'),
        'members': _(u'Most Members')
    }
    order_fields_type = {
        'name': 'asc',
        'date': 'desc',
        'members': 'desc'
    }    
    order_type = request.GET.get('ot', order_fields_type.get(ordering, 'desc'))

    if ordering in order_fields and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+order_fields[ordering])
    
    highlighted_ids = list(Team.objects.for_user(request.user).filter(highlight=True).values_list('id', flat=True))
    random.shuffle(highlighted_ids)
    highlighted_qs = Team.objects.filter(pk__in=highlighted_ids[:HIGHTLIGHTED_TEAMS_ON_PAGE]) \
        .annotate(_member_count=Count('users__pk'))
    
    extra_context = {
        'my_teams': my_teams,
        'query': q,
        'ordering': ordering,
        'order_type': order_type,
        'order_name': order_fields_name.get(ordering, 'name'),
        'highlighted_qs': highlighted_qs
    }
    return object_list(request, queryset=qs,
                       paginate_by=TEAMS_ON_PAGE,
                       template_name='teams/index.html',
                       template_object_name='teams',
                       extra_context=extra_context)

def detail(request, slug, is_debugging=False, project_slug=None, languages=None):
    team = Team.get(slug, request.user)

    if languages is None:
        languages = get_user_languages_from_request(request)
    if bool(is_debugging):
        languages = request.GET.get('langs', '').split(',')

    if project_slug is not None:
        project = get_object_or_404(Project, team=team, slug=project_slug)
    else:
        project = None
    qs_list, mqs = team.get_videos_for_languages_haystack(languages, user=request.user, project=project)

    extra_context = widget.add_onsite_js_files({})
    extra_context.update({
        'team': team,
        'project':project,
        'can_add_video': can_add_video(team, request.user, project),
        'can_edit_videos': can_add_video(team, request.user, project),
        'can_create_tasks': can_create_tasks(team, request.user, project),
    })

    general_settings = {}
    add_general_settings(request, general_settings)
    extra_context['general_settings'] = json.dumps(general_settings)

    if team.video:
        extra_context['widget_params'] = base_widget_params(request, {
            'video_url': team.video.get_video_url(), 
            'base_state': {}
        })

    if bool(is_debugging) and request.user.is_staff:
        extra_context.update({
                'mqs': mqs,
                'qs_list': qs_list,
                'languages': languages
            })
        return render_to_response("teams/detail-debug.html", extra_context, RequestContext(request))

    all_langs = set()
    for search_record in mqs:
        if search_record.video_completed_langs:
            all_langs.update(search_record.video_completed_langs)

    language_choices = [(code, name) for code, name in get_languages_list()
                        if code in all_langs]

    extra_context['language_choices'] = language_choices

    return object_list(request, queryset=mqs, 
                       paginate_by=VIDEOS_ON_PAGE, 
                       template_name='teams/detail.html', 
                       extra_context=extra_context, 
                       template_object_name='team_video_md')


def completed_videos(request, slug):
    team = Team.get(slug, request.user)
    if team.is_member(request.user):
        qs  = TeamVideoLanguagesIndex.results_for_members(team)
    else:
        qs = TeamVideoLanguagesIndex.results()
    qs = qs.filter(team_id=team.id).filter(is_complete=True).order_by('-video_complete_date')

    extra_context = widget.add_onsite_js_files({})    
    extra_context.update({
        'team': team
    })
    
    if team.video:
        extra_context['widget_params'] = base_widget_params(request, {
            'video_url': team.video.get_video_url(), 
            'base_state': {}
        })

    return object_list(request, queryset=qs, 
                       paginate_by=VIDEOS_ON_PAGE, 
                       template_name='teams/completed_videos.html', 
                       extra_context=extra_context, 
                       template_object_name='team_video')    

def detail_members(request, slug, role=None):
    #just other tab of detail view
    q = request.REQUEST.get('q')
    
    team = Team.get(slug, request.user)
    
    qs = team.members.all()
    if q:
        qs = qs.filter(Q(user__first_name__icontains=q)|Q(user__last_name__icontains=q)
                       |Q(user__username__icontains=q)|Q(user__biography__icontains=q))

    if role:
        if role == 'admin':
            qs = qs.filter(role__in=[TeamMember.ROLE_OWNER, TeamMember.ROLE_ADMIN])
        else:
            qs = qs.filter(role=role)

    extra_context = widget.add_onsite_js_files({})

    # if we are a member that can also edit roles, we create a dict of
    # roles that we can assign, this will vary from user to user, since
    # let's say an admin can change roles, but not for anyone above him
    # the owner, for example
    assignable_roles = []
    if roles_user_can_assign(team, request.user):
        for member in qs:
            if can_assign_role(team, request.user, member.role, member.user):
                assignable_roles.append(member)

    extra_context.update({
        'team': team,
        'query': q,
        'role': role,
        'assignable_roles': assignable_roles,
    })
    
    if team.video:
        extra_context['widget_params'] = base_widget_params(request, {
            'video_url': team.video.get_video_url(), 
            'base_state': {}
        })    
    return object_list(request, queryset=qs, 
                       paginate_by=MEMBERS_ON_PAGE, 
                       template_name='teams/detail_members.html', 
                       extra_context=extra_context, 
                       template_object_name='team_member')

def videos_actions(request, slug):
    team = Team.get(slug, request.user)  
    videos_ids = team.teamvideo_set.values_list('video__id', flat=True)
    qs = Action.objects.filter(video__pk__in=videos_ids)
    extra_context = {
        'team': team
    }   
    return object_list(request, queryset=qs, 
                       paginate_by=ACTIONS_ON_PAGE, 
                       template_name='teams/videos_actions.html', 
                       extra_context=extra_context, 
                       template_object_name='videos_action')

@render_to('teams/create.html')
@staff_member_required
def create(request):
    user = request.user
    
    if not DEV and not (user.is_superuser and user.is_active):
        raise Http404 
    
    if request.method == 'POST':
        form = CreateTeamForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            team = form.save(user)
            messages.success(request, _('Your team has been created. Review or edit its information below.'))
            return redirect(reverse("teams:settings", kwargs={"slug":team.slug}))
    else:
        form = CreateTeamForm(request.user)
    return {
        'form': form
    }


# Settings
@render_to('teams/settings.html')
@login_required
def team_settings(request, slug):
    team = Team.get(slug, request.user)

    if not can_view_settings_tab(team, request.user):
        return HttpResponseForbidden("You cannot view this team")

    member = team.members.get(user=request.user)
    if request.method == 'POST':
        if request.user.is_staff:
            form = EditTeamFormAdmin(request.POST, request.FILES, instance=team)
        else:
            form = EditTeamForm(request.POST, request.FILES, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, _(u'Your changes have been saved'))
            return redirect(reverse("teams:settings", kwargs={"slug":team.slug}))
    else:
        if request.user.is_staff:
            form = EditTeamFormAdmin(instance=team)
        else:
            form = EditTeamForm(instance=team)

    return {
        'basic_settings_form': form,
        'team': team,
        'user_can_delete_tasks': can_delete_tasks(team, request.user),
        'user_can_assign_tasks': can_assign_tasks(team, request.user),
        'assign_form': TaskAssignForm(team, member),
        'settings_form': SettingsForm(),
        'permissions_form': PermissionsForm(),
        'workflow_form': WorkflowForm(),
    }

@login_required
def edit_logo(request, slug):
    team = Team.get(slug, request.user)

    if not team.is_member(request.user):
        raise Http404
    
    output = {}
    form = EditLogoForm(request.POST, instance=team, files=request.FILES)
    if form.is_valid():
        try:
            form.save()
            output['url'] =  str(team.logo_thumbnail())
        except S3StorageError:
            output['error'] = {'logo': ugettext(u'File server unavailable. Try later. You can edit some other information without any problem.')}
    else:
        output['error'] = form.get_errors()
    return HttpResponse('<textarea>%s</textarea>'  % json.dumps(output))

@login_required
def upload_logo(request, slug):
    team = Team.get(slug, request.user)

    if not team.is_member(request.user):
        raise Http404

    output = {}
    form = EditLogoForm(request.POST, instance=team, files=request.FILES)
    if form.is_valid():
        try:
            form.save()
            output['url'] =  str(team.logo_thumbnail())
            output['url_full'] =  str(team.logo.url)
        except S3StorageError:
            output['error'] = {'logo': ugettext(u'File server unavailable. Try later. You can edit some other information without any problem.')}
    else:
        output['error'] = form.get_errors()

    return HttpResponse(json.dumps(output))


# Adding videos
@render_to('teams/add_video.html')
@login_required
def add_video(request, slug):
    team = Team.get(slug, request.user)

    if not can_add_video(team, request.user):
        messages.error(request, _(u'You can\'t add video.'))
        return HttpResponseRedirect(team.get_absolute_url())

    initial = {
        'video_url': request.GET.get('url', ''),
        'title': request.GET.get('title', '')
    }
    
    form = AddTeamVideoForm(team, request.user, request.POST or None, request.FILES or None, initial=initial)
    
    if form.is_valid():
        obj =  form.save(False)
        obj.added_by = request.user
        obj.save()
        return redirect(obj)
        
    return {
        'form': form,
        'team': team
    }

@render_to('teams/add_videos.html')
@login_required
def add_videos(request, slug):
    team = Team.get(slug, request.user)

    if not can_add_video(team, request.user):
        messages.error(request, _(u'You can\'t add video.'))
        return HttpResponseRedirect(team.get_absolute_url())

    form = AddTeamVideosFromFeedForm(team, request.user, request.POST or None)

    if form.is_valid():
        team_videos = form.save()
        messages.success(request, form.success_message() % {'count': len(team_videos)})
        return redirect(team)

    return { 'form': form, 'team': team, }


@login_required
def edit_videos(request, slug):
    team = Team.get(slug, request.user)
    
    if not team.is_member(request.user):
        raise Http404
    
    qs = team.teamvideo_set.all()
    
    extra_context = {
        'team': team,
    }
    return object_list(request, queryset=qs,
                       paginate_by=VIDEOS_ON_PAGE,
                       template_name='teams/edit_videos.html',
                       template_object_name='videos',
                       extra_context=extra_context)


@login_required
@render_to('teams/team_video.html')
def team_video(request, team_video_pk):
    team_video = get_object_or_404(TeamVideo, pk=team_video_pk)

    if not can_edit_video(team_video, request.user):
        messages.error(request, _(u'You can\'t edit this video.'))
        return HttpResponseRedirect(team_video.team.get_absolute_url())

    meta = team_video.video.metadata()
    form = EditTeamVideoForm(request.POST or None, request.FILES or None,
                             instance=team_video, user=request.user, initial=meta)

    if form.is_valid():
        form.save()
        messages.success(request, _('Video has been updated.'))
        return redirect(team_video)

    context = widget.add_onsite_js_files({})

    context.update({
        'team': team_video.team,
        'team_video': team_video,
        'form': form,
        'widget_params': base_widget_params(request, {'video_url': team_video.video.get_video_url(), 'base_state': {}})
    })
    return context

@render_to_json
@login_required
def remove_video(request, team_video_pk):
    team_video = get_object_or_404(TeamVideo, pk=team_video_pk)

    if request.method != 'POST':
        error = _(u'Request must be a POST request.')

        if request.is_ajax():
            return { 'success': False, 'error': error }
        else:
            messages.error(request, error)
            return HttpResponseRedirect(reverse('teams:user_teams'))

    next = request.POST.get('next', reverse('teams:user_teams'))

    # TODO: check if this should be on a project level
    if not can_add_video(team_video.team, request.user):
        error = _(u'You can\'t remove that video.')

        if request.is_ajax():
            return { 'success': False, 'error': error }
        else:
            messages.error(request, error)
            return HttpResponseRedirect(next)

    for task in team_video.task_set.all():
        task.delete()

    team_video.delete()

    if request.is_ajax():
        return { 'success': True }
    else:
        return HttpResponseRedirect(next)


# Members
@render_to_json
@login_required
def remove_member(request, slug, user_pk):
    team = Team.get(slug, request.user)

    member = get_object_or_404(TeamMember, team=team, user__pk=user_pk)
    if can_assign_role(team, request.user, member.role, member.user):
        user = member.user
        if not user == request.user:
            TeamMember.objects.filter(team=team, user=user).delete()
            return {
                'success': True
            }
        else:
            return {
                'success': False,
                'error': ugettext('You can\'t remove youself')
            }
    else:
        return {
            'success': False,
            'error': ugettext('You can\'t remove user')
        }

@login_required
def applications(request, slug):
    team = Team.get(slug, request.user)
    
    if not team.is_member(request.user):
        return  HttpResponseForbidden("Not allowed")
    
    qs = team.applications.all()
        
    extra_context = {
        'team': team
    }
    return object_list(request, queryset=qs,
                       paginate_by=APLICATIONS_ON_PAGE,
                       template_name='teams/applications.html',
                       template_object_name='applications',
                       extra_context=extra_context) 

@login_required
def approve_application(request, slug, user_pk):
    team = Team.get(slug, request.user)

    if not team.is_member(request.user):
        raise Http404

    if can_invite(team, request.user):
        try:
            Application.objects.get(team=team, user=user_pk).approve()
            messages.success(request, _(u'Application approved.'))
        except Application.DoesNotExist:
            messages.error(request, _(u'Application does not exist.'))
    else:
        messages.error(request, _(u'You can\'t approve applications.'))

    return redirect('teams:applications', team.pk)

@login_required
def deny_application(request, slug, user_pk):
    team = Team.get(slug, request.user)

    if not team.is_member(request.user):
        raise Http404

    if can_invite(team, request.user):
        try:
            Application.objects.get(team=team, user=user_pk).deny()
            messages.success(request, _(u'Application denied.'))
        except Application.DoesNotExist:
            messages.error(request, _(u'Application does not exist.'))
    else:
        messages.error(request, _(u'You can\'t deny applications.'))

    return redirect('teams:applications', team.pk)


@render_to('teams/invite_members.html')
@login_required
def invite_members(request, slug):
    team = Team.get(slug, request.user)

    if not can_invite(team, request.user):
        return HttpResponseForbidden(_(u'You cannot invite people to this team.'))

    if request.POST:
        form = InviteForm(team, request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('teams:detail_members',
                                                args=[], kwargs={'slug': team.slug}))
    else:
        form = InviteForm(team, request.user)

    return {
        'team': team,
        'form': form,
    }

@login_required
def accept_invite(request, invite_pk, accept=True):
    invite = get_object_or_404(Invite, pk=invite_pk, user=request.user)
    
    if accept:
        invite.accept()
    else:
        invite.deny()
        
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def join_team(request, slug):
    team = get_object_or_404(Team, slug=slug)
    user = request.user

    if not can_join_team(team, user):
        messages.error(request, _(u'You cannot join this team.'))
    else:
        TeamMember(team=team, user=user, role=TeamMember.ROLE_CONTRIBUTOR).save()
        messages.success(request, _(u'You are now a member of this team.'))

    return redirect(team)

@login_required
def leave_team(request, slug):
    team = get_object_or_404(Team, slug=slug)
    user = request.user
    try:
        tm = TeamMember.objects.get(team=team, user=user)
        
        if not team.members.exclude(pk=tm.pk).exists():
            messages.error(request, _(u'You are last member of this team.'))
        elif not team.members.filter(role=TeamMember.ROLE_OWNER).exclude(pk=tm.pk).exists():
            messages.error(request, _(u'You are last admin of this team.'))
        else:
            tm.delete()
            messages.success(request, _(u'You have left this team.'))
    except TeamMember.DoesNotExist:
        messages.error(request, _(u'You are not member of this team.'))
    
    return redirect(request.META.get('HTTP_REFERER') or team)


@permission_required('teams.change_team')
def highlight(request, slug, highlight=True):
    item = get_object_or_404(Team, slug=slug)
    item.highlight = highlight
    item.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


# Tasks
@render_to('teams/tasks.html')
@login_required
def team_tasks(request, slug):
    team = Team.get(slug, request.user)

    if not can_view_tasks_tab(team, request.user):
        return HttpResponseForbidden("You cannot view this team")

    member = team.members.get(user=request.user)

    return {
        'team': team,
        'user_can_delete_tasks': can_delete_tasks(team, request.user),
        'user_can_assign_tasks': can_assign_tasks(team, request.user),
        'assign_form': TaskAssignForm(team, member),
    }

@render_to('teams/create_task.html')
def create_task(request, slug, team_video_pk):
    team = get_object_or_404(Team, slug=slug)
    team_video = get_object_or_404(TeamVideo, pk=team_video_pk, team=team)
    can_assign = can_assign_tasks(team, request.user, team_video.project)

    if request.POST:
        form = CreateTaskForm(request.user, team, team_video, request.POST)

        if form.is_valid():
            task = form.save(commit=False)

            task.subtitle_language = form.subtitle_language
            task.team = team
            task.team_video = team_video

            if task.type in [Task.TYPE_IDS['Review'], Task.TYPE_IDS['Approve']]:
                task.approved = Task.APPROVED_IDS['In Progress']

            task.save()

            return HttpResponseRedirect(reverse('teams:team_tasks', args=[],
                                                kwargs={'slug': team.slug}))
    else:
        form = CreateTaskForm(request.user, team, team_video)

    subtitlable = json.dumps(can_create_task_subtitle(team_video, request.user))
    translatable_languages = json.dumps(can_create_task_translate(team_video, request.user))
    reviewable_languages = json.dumps(can_create_task_review(team_video, request.user))
    approvable_languages = json.dumps(can_create_task_approve(team_video, request.user))

    language_choices = json.dumps(get_languages_list(True))

    return { 'form': form, 'team': team, 'team_video': team_video,
             'translatable_languages': translatable_languages,
             'reviewable_languages': reviewable_languages,
             'approvable_languages': approvable_languages,
             'language_choices': language_choices,
             'subtitlable': subtitlable,
             'can_assign': can_assign, }

@login_required
def perform_task(request):
    task = Task.objects.get(pk=request.POST.get('task_id'))

    if not task.perform_allowed(request.user):
        return HttpResponseForbidden(_(u'You are not allowed to perform this task.'))

    task.assignee = request.user
    task.save()

    # ... perform task ...
    return HttpResponseRedirect(task.get_perform_url())


# Projects
def project_list(request, slug):
    team = get_object_or_404(Team, slug=slug)
    projects = Project.objects.for_team(team)
    return render_to_response("teams/project_list.html", {
        "team":team,
        "projects": projects
    }, RequestContext(request))
