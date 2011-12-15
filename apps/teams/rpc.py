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


    # Guidelines and messages
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
