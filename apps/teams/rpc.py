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

from auth.models import CustomUser as User
from teams.models import (
    Team, TeamMember, Application, Workflow, Project, TeamVideo, Task, Setting,
    ALL_LANGUAGES
)

from videos.models import SubtitleLanguage

from django.shortcuts import get_object_or_404

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.utils.translation import ugettext as _
from django.forms.models import model_to_dict
from utils.rpc import Error, Msg, RpcRouter
from utils.forms import flatten_errorlists
from utils.translation import SUPPORTED_LANGUAGES_DICT

from teams.tasks import update_one_team_video
from teams.project_forms import ProjectForm
from teams.forms import (
    TaskAssignForm, TaskDeleteForm, GuidelinesMessagesForm, SettingsForm,
    WorkflowForm, PermissionsForm
)
from teams.permissions import (
    roles_user_can_assign, can_assign_role, can_edit_project, set_narrowings,
    can_rename_team, can_set_project_narrowings, can_set_language_narrowings
)



class TeamsApiClass(object):

    def create_application(self, team_id, msg, user):
        if not user.is_authenticated():
            return Error(_('You should be authenticated.'))

        try:
            if not team_id:
                raise Team.DoesNotExist
            team = Team.objects.get(pk=team_id)
        except Team.DoesNotExist:
            return Error(_('Team does not exist'))

        try:
            TeamMember.objects.get(team=team, user=user)
            return Error(_(u'You are already a member of this team.'))
        except TeamMember.DoesNotExist:
            pass

        if team.is_open():
            TeamMember(team=team, user=user).save()
            return Msg(_(u'You are now a member of this team because it is open.'))
        elif team.is_by_application():
            application, created = Application.objects.get_or_create(team=team, user=user)
            application.note = msg
            application.save()
            return Msg(_(u'Application sent success. Wait for answer from team.'))
        else:
            return Error(_(u'You can\'t join this team by application.'))

    def promote_user(self, team_id, member_id, role, user):
        try:
            team = Team.objects.for_user(user).get(pk=team_id)
        except Team.DoesNotExist:
            return Error(_(u'Team does not exist.'))

        if not team.is_manager(user):
            return Error(_(u'You are not manager of this team.'))

        if not role in dict(TeamMember.ROLES):
            return Error(_(u'Incorrect team member role.'))

        try:
            tm = TeamMember.objects.get(pk=member_id, team=team)
        except TeamMember.DoesNotExist:
            return Error(_(u'Team member does not exist.'))

        if tm.user == user:
            return Error(_(u'You can\'t promote yourself.'))

        tm.role = role
        tm.save()
        return Msg(_(u'Team member role changed.'))

TeamsApi = TeamsApiClass()


def _project_to_dict(p):
    d  = model_to_dict(p, fields=["name", "slug", "order", "description", "pk", "workflow_enabled"])
    d.update({
        "pk":p.pk,
        "url": reverse("teams:project_video_list", kwargs={
            "slug":p.team.slug,
            "project_slug": p.slug,
        })
    })
    return d




class TeamsApiV2Class(object):
    def test_api(self, message, user):
        return Msg(u'Received message: "%s" from user "%s"' % (message, unicode(user)))


    # Basic Settings
    def team_get(self, team_slug, user):
        return Team.objects.get(slug=team_slug).to_dict()

    def team_set(self, team_slug, data, user):
        team = Team.objects.get(slug=team_slug)
        name = team.name

        form = SettingsForm(data, instance=team)
        if form.is_valid():
            if form.cleaned_data['name'] != name and not can_rename_team(team, user):
                return Error(_(u'You cannot rename this team.'))

            form.save()
            return team.to_dict()
        else:
            return Error(_(u'\n'.join(flatten_errorlists(form.errors))))


    # Permissions
    def permissions_set(self, team_slug, data, user):
        team = Team.objects.get(slug=team_slug)

        form = PermissionsForm(data, instance=team)
        if form.is_valid():
            form.save()
            return team.to_dict()
        else:
            return Error(_(u'\n'.join(flatten_errorlists(form.errors))))


    def task_assign(self, task_id, assignee_id, user):
        '''Assign a task to the given user, or unassign it if null/None.'''
        task = Task.objects.get(pk=task_id)

        form = TaskAssignForm(task.team, user,
                              data={'task': task_id, 'assignee': assignee_id})
        if form.is_valid():
            assignee = User.objects.get(pk=assignee_id) if assignee_id else None

            task.assignee = assignee
            task.save()

            return task.to_dict(user)
        else:
            return Error(_(u'\n'.join(flatten_errorlists(form.errors))))


    def task_translate_assign(self, team_video_id, language, assignee_id, user):
        '''Assign a translation task to the given user, or unassign it if given null/None.

        This is special-cased from the normal assignment function because we
        don't create translation tasks in advance -- it would be too wasteful.
        The translation task will be created if it does not already exist.

        '''
        # TODO: Check permissions here. This will be tricky because of ghost tasks.

        tv = TeamVideo.objects.get(pk=team_video_id)
        task, created = Task.objects.get_or_create(team=tv.team, team_video=tv,
                language=language, type=Task.TYPE_IDS['Translate'])
        assignee = User.objects.get(pk=assignee_id) if assignee_id else None

        task.assignee = assignee
        task.save()

        return task.to_dict(user)

    def task_translate_delete(self, team_video_id, language, user):
        '''Mark a translation task as deleted.

        This is special-cased from the normal delete function because we don't
        create translation tasks in advance -- it would be too wasteful.  The
        translation task will be created if it does not already exist.

        The task will not be physically deleted from the database, but will be
        flagged and won't appear in further task listings.

        '''
        tv = TeamVideo.objects.get(pk=team_video_id)
        task, created = Task.objects.get_or_create(team=tv.team, team_video=tv,
                language=language, type=Task.TYPE_IDS['Translate'])

        task.deleted = True
        task.save()

        return task.to_dict()


    # Workflows
    def workflow_get(self, team_slug, project_id, team_video_id, user):
        if team_video_id:
            target_id, target_type = team_video_id, 'team_video'
        elif project_id:
            target_id, target_type = project_id, 'project'
        else:
            team = Team.objects.get(slug=team_slug)
            target_id, target_type = team.id, 'team'

        return Workflow.get_for_target(target_id, target_type).to_dict()

    def workflow_set(self, team_slug, project_id, team_video_id, data, user):
        workflow = _get_or_create_workflow(team_slug, project_id, team_video_id)

        form = WorkflowForm(data, instance=workflow)
        if form.is_valid():
            form.save()

            # If we're setting a workflow, the workflow's target obviously must
            # have workflows enabled.
            team = get_object_or_404(Team, slug=team_slug)
            if team and (not project_id) and (not team_video_id):
                team.workflow_enabled = True
                team.save()

            return workflow.to_dict()
        else:
            return Error(_(u'\n'.join(flatten_errorlists(form.errors))))


    # Projects
    def project_list(self, team_slug,   user):
        team = get_object_or_404(Team, slug=team_slug)
        project_objs = []
        for p in Project.objects.for_team(team):
            project_objs.append(_project_to_dict(p))
        return project_objs

    def project_edit(self, team_slug, project_pk, name,
                     slug, description, order, workflow_enabled, user):
        team = get_object_or_404(Team, slug=team_slug)
        if project_pk:
            project = get_object_or_404(Project, team=team, pk=project_pk)
        else:
            project = None
        
        if can_edit_project(team, user, project) is False:
            return {"success":False, "message": "This team member cannot edit project"}
        # insert a new project as the last one
        if bool(order):
            num_projects = team.project_set.exclude(pk=project_pk).count()
            order = num_projects    
        form = ProjectForm(instance=project, data=dict(
            name=name, 
            description=description,
            slug=slug, 
            pk=project and project.pk,
            order=order,
            workflow_enabled=workflow_enabled,
                ))
        if form.is_valid():
            p = form.save(commit=False)
            p.team = team
            p.save()
            return dict(
                success = True,
                msg = _("The project %s has been saved" % (p.name)),
                obj = _project_to_dict(p)
            )
        else:
             return dict(
                 success=False,
                 msg = "Please correct the errors below",
                 errors = form.errors
                 )   

    def project_delete(self, team_slug, project_pk, user):
        team = get_object_or_404(Team, slug=team_slug)
        project = get_object_or_404(Project, team=team, pk=project_pk)

        if not can_edit_project(team, user, project):
            return {"success": False, "message": "This team member cannot edit project"}

        team_videos = [tv.id for tv in project.teamvideo_set.all()]

        videos_affected = project.teamvideo_set.all().update(project=team.default_project)
        for id in team_videos:
            update_one_team_video(id)

        project.delete()

        return dict(
            videos_affected=videos_affected,
            success=True,
            msg="Project %s has been deleted" % project.name,
            isRemoval=True
        )


    # Guidelines and messages
    def guidelines_get(self, team_slug, user):
        team = Team.objects.get(slug=team_slug)
        return [{'key': s.key_name, 'data': s.data}
                for s in team.settings.messages_guidelines()]

    def guidelines_set(self, team_slug, data, user):
        team = Team.objects.get(slug=team_slug)

        form = GuidelinesMessagesForm(data)
        if form.is_valid():
            for key, val in form.cleaned_data.items():
                setting, created = Setting.objects.get_or_create(
                        team=team, key=Setting.KEY_IDS[key])
                setting.data = val
                setting.save()

            return {}
        else:
            return Error(_(u'\n'.join(flatten_errorlists(form.errors))))

    def member_role_info(self, team_slug, member_pk, user):
        team = Team.objects.get(slug=team_slug)
        member = team.members.get(pk=member_pk)
        roles =  roles_user_can_assign(team, user, member.user)
        # massage the data format to make it easier to work with
        # over the client side templating
        verbose_roles = [{"val":x[0], "name":x[1]} for x in TeamMember.ROLES if x[0] in roles]
        narrowings = member.narrowings.all()

        current_languages = [n.language for n in narrowings if n.language]
        current_projects = [n.project for n in narrowings if n.project]

        projects = []
        if can_set_project_narrowings(team, user, member.user):
            for p in Project.objects.for_team(team):
                data = dict(pk=p.pk, name=p.name)
                if p in current_projects:
                    data['selected'] = "selected"
                projects.append(data)

        langs = []
        if can_set_language_narrowings(team, user, member.user):
            for code, name in ALL_LANGUAGES:
                lang = {
                    'selected': True if code in current_languages else False,
                    'code': code,
                    'name': name,
                }
                langs.append(lang)

            langs.sort(key=lambda l: unicode(l['name']))

        return {
            'current_role': member.role,
            'roles': verbose_roles,
            'languages': langs,
            'projects': projects,
        }

    def save_role(self, team_slug, member_pk, role, projects, languages, user=None):
        team = Team.objects.get(slug=team_slug)
        member = team.members.get(pk=member_pk)

        projects = map(int, projects or [])
        languages = languages or []

        if can_assign_role(team, user, role, member.user):
            member.role = role
            member.save()

            set_narrowings(member, projects, languages, user)

            return { 'success': True }
        else:
            return { 'success': False,
                     'errors': [_('You cannot assign that role to that member.')] }


TeamsApiV2 = TeamsApiV2Class()

rpc_router = RpcRouter('teams:rpc_router', {
    'TeamsApi': TeamsApi,
    'TeamsApiV2': TeamsApiV2,
})
