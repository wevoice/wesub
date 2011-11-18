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

from django.contrib.contenttypes.models import ContentType
from django.utils.functional import  wraps
from utils.translation import SUPPORTED_LANGUAGES_DICT

from teams.permissions_const import (
    EDIT_TEAM_SETTINGS_PERM, EDIT_PROJECT_SETTINGS_PERM, ASSIGN_ROLE_PERM,
    CREATE_TASKS_PERM, ASSIGN_TASKS_PERM, ADD_VIDEOS_PERM,
    EDIT_VIDEO_SETTINGS_PERM, MESSAGE_ALL_MEMBERS_PERM, ACCEPT_ASSIGNMENT_PERM,
    PERFORM_MANAGER_REVIEW_PERM, PERFORM_PEER_REVIEW_PERM, EDIT_SUBS_PERM,
    RULES, ROLES_ORDER, ROLE_OWNER, ROLE_CONTRIBUTOR, ROLE_ADMIN, ROLE_MANAGER,
    ROLE_OUTSIDER
)

from teams.models import MembershipNarrowing, Team, Workflow

def can_rename_team(team, user):
    return team.is_owner(user)

    
def _passes_test(team, user, project, lang, perm_name):
    if isinstance(perm_name, tuple):
        perm_name = perm_name[0]
    member = team.members.get(user=user)
    if member.role == ROLE_OWNER:
        # short circuit logic for onwers, as they can do anything
        return True
    # first we check if this role has (withouth narrowning)
    # the permission asked. E.g. contributor cannot rename
    # a team

    for model in [x for x in (team, project, lang) if x]:
        if model_has_permission(member, perm_name, model) is False:
            continue 

        if MembershipNarrowing.objects.for_type(model).filter(member=member).exists():
            return True
    
def _check_perms( perm_name,):
    def wrapper(func):
        def wrapped(team, user, project=None, lang=None, video=None):
            return _passes_test(team, user, project, lang, perm_name)
        return wraps(func)(wrapped)
    return wrapper
            
def _is_owner(func):
    def wrapper(team, user, *args, **kwargs):
        if team.members.filter(
            user=user,
            role = ROLE_OWNER).exists():
            return True
        return func(team, user, *args, **kwargs)
    return wraps(func)(wrapper)
        
def _owner(team, user):
    from teams.models import TeamMember
    return  team.members.filter(
        user=user,
        role = TeamMember.ROLE_OWNER).exists()

@_check_perms(EDIT_TEAM_SETTINGS_PERM)
def can_change_team_settings(team, user, project=None, lang=None, role=None) :
    return False    

def _perms_equal_or_lower(role):
    return ROLES_ORDER[ROLES_ORDER.index(role):]

def _perms_equal_or_greater(role, include_outsiders=False):
    roles = ROLES_ORDER

    if include_outsiders:
        roles = roles + [ROLE_OUTSIDER]

    return roles[:roles.index(role) + 1]

def roles_assignable_to(team, user, project=None, lang=None):
    roles_for_user = set([x.role for x in team.members.filter(user=user)])
    higer_role = ROLES_ORDER[max([ROLES_ORDER.index(x) for x in roles_for_user ])]
        
    return _perms_equal_or_lower(higer_role)
    
def can_assign_roles(team, user, project=None, lang=None,  role=None):
    """
    Checks if the user can generally assing roles for that model
    (team or project or lang), but also that he can only assign 'lesser'
    roles than his own.
    """
    if not user.is_authenticated():
        return False

    member = team.members.get(user=user)
    # only owner can assing owner role!
    if member.role == ROLE_OWNER:
        return True
    can_do =  _passes_test(team, user, project, lang, ASSIGN_ROLE_PERM)    
    if can_do:
        # makes sure we allow only <= new roles assignment, e.g
        # a project owner can assign any other role, but a manager
        # cannot assign admins nor owners
        return role in roles_assignable_to(team, user,project, lang)
    return False


@_check_perms(CREATE_TASKS_PERM)
def can_create_tasks(team, user, project=None):
    pass

@_check_perms(ASSIGN_TASKS_PERM)
def can_assign_tasks(team, user, project=None, lang=None):
    pass

def can_add_video(team, user, project=None, lang=None):
    if not team.video_policy :
        return True
    return _passes_test(team, user, project, lang, ADD_VIDEOS_PERM)

@_check_perms(EDIT_VIDEO_SETTINGS_PERM)
def can_change_video_settings(team, user, project, lang):
    pass

@_check_perms(MESSAGE_ALL_MEMBERS_PERM)
def can_message_all_members(team, user, project=None, lang=None):
    pass

@_check_perms(ACCEPT_ASSIGNMENT_PERM)
def can_accept_assignments(team, user, project=None, lang=None):
    pass

@_check_perms(PERFORM_MANAGER_REVIEW_PERM)
def can_manager_review(team, user, project=None, lang=None):
    pass

@_check_perms(PERFORM_PEER_REVIEW_PERM)
def can_peer_review(team, user, project=None, lang=None):
    pass

@_check_perms(EDIT_SUBS_PERM)    
def can_edit_subs_for(team, user, project=None, lang=None):
    pass
    
@_check_perms(EDIT_PROJECT_SETTINGS_PERM)
def can_edit_project(team, user, project, lang=None):
    pass
    
def can_view_settings_tab(team, user):
    return team.members.filter(user=user,role__in =[ROLE_ADMIN, ROLE_OWNER]).exists()

def can_view_tasks_tab(team, user):
    return team.members.filter(user=user).exists()
    
def model_has_permission(member, perm_name, model):
    return perm_name in _perms_for(member.role, model)
                               
def _perms_for(role, model):
    return [x[0] for x in RULES[role].\
            intersection(model._meta.permissions)]
    
def add_role(team, cuser, added_by,  role, project=None, lang=None):
    from teams.models import TeamMember
    member, created = TeamMember.objects.get_or_create(
        user=cuser,team=team, defaults={'role':role})
    member.role = role
    member.save()
    narrowing = lang or project or team
    add_narrowing_to_member(member, narrowing, added_by)
    return member 

def remove_role(team, user, role, project=None, lang=None):
    role = role or ROLE_CONTRIBUTOR
    team.members.filter(user=user, role=role).delete()


def add_narrowing_to_member(member, narrowing, added_by):
    """
    If adding any a narrowing one must remove any Team objects
    that will allow an user to execute actions on anything
    withing that team
    """
    if not isinstance(narrowing, Team):
       MembershipNarrowing.objects.for_type(Team).filter(member=member).delete()
    return MembershipNarrowing.objects.create(member, narrowing, added_by)
    
def add_narrowing(team, user, narrowing, added_by):
    return add_narrowing_to_member(team.members.get(user=user), narrowing. added_by)


def remove_narrowings(team, user, narrowings):
    try:
        iter(narrowings)
    except TypeError:
        narrowings = [narrowings]
    member = team.members.get(user=user)
    [MembershipNarrowing.objects.get(
        object_pk=x.pk,
        content_type=ContentType.objects.get_for_model(x),
        member=member) for x in narrowings]
    
         
def list_narrowings(team, user, models, lists=False):
   data = {}
   for model in models:
       items =  MembershipNarrowing.objects.for_type(model).filter(
               member=team.members.get(user=user))
       data[model._meta.object_name] = items if not lists else list(items)
   return data    
    


# Task creation checks
def _user_can_create_task_subtitle(user, team_video):
    role = team_video.team.members.get(user=user).role

    role_req = {
        10: ROLE_CONTRIBUTOR,
        20: ROLE_MANAGER,
        30: ROLE_ADMIN,
    }[team_video.team.task_assign_policy]

    return role in _perms_equal_or_greater(role_req)

def _user_can_create_task_translate(user, team_video):
    role = team_video.team.members.get(user=user).role

    role_req = {
        10: ROLE_CONTRIBUTOR,
        20: ROLE_MANAGER,
        30: ROLE_ADMIN,
    }[team_video.team.task_assign_policy]

    return role in _perms_equal_or_greater(role_req)

def _user_can_create_task_review(user, team_video):
    workflow = Workflow.get_for_team_video(team_video)

    if not workflow.review_enabled:
        # TODO: Allow users to create on-the-fly review tasks even if reviewing
        #       is not enabled in the workflow?
        return False

    role = team_video.team.members.get(user=user).role

    role_req = {
        10: ROLE_CONTRIBUTOR,
        20: ROLE_MANAGER,
        30: ROLE_ADMIN,
    }[workflow.review_allowed]

    return role in _perms_equal_or_greater(role_req)

def _user_can_create_task_approve(user, team_video):
    workflow = Workflow.get_for_team_video(team_video)

    if not workflow.approve_enabled:
        return False

    role = team_video.team.members.get(user=user).role

    role_req = {
        10: ROLE_MANAGER,
        20: ROLE_ADMIN,
    }[workflow.approve_allowed]

    return role in _perms_equal_or_greater(role_req)


def can_create_task_subtitle(team_video, user=None):
    """Return whether the given video can have a subtitle task created for it.

    If a user is given, return whether *that user* can create the task.

    A subtitle task can be created iff:

    * There are no subtitles for the video already.
    * There are no subtitle tasks for it already.
    * The user has permission to create subtitle tasks.

    """
    if user and not _user_can_create_task_subtitle(user, team_video):
        return False

    if team_video.subtitles_started():
        return False

    if list(team_video.task_set.all_subtitle()[:1]):
        return False

    return True

def can_create_task_translate(team_video, user=None):
    """Return a list of languages for which a translate task can be created for the given video.

    If a user is given, filter that list to contain only languages the user can
    create tasks for.

    A translation task can be created for a given language iff:

    * There is at least one set of complete subtitles for another language (to
      translate from).
    * There are no translation tasks for that language.
    * The user has permission to create the translation task.

    Note: you *can* create translation tasks if subtitles for that language
    already exist.  The task will simply "take over" that language from that
    point forward.

    """
    if user and not _user_can_create_task_translate(user, team_video):
        return []

    if not team_video.subtitles_finished():
        return []

    candidate_languages = set(SUPPORTED_LANGUAGES_DICT.keys())

    existing_translate_tasks = team_video.task_set.all_translate()
    existing_translate_languages = set(t.language for t in existing_translate_tasks)

    # TODO: Order this for individual users?
    return list(candidate_languages - existing_translate_languages)

def can_create_task_review(team_video, user=None):
    """Return a list of languages for which a review task can be created for the given video.

    If a user is given, filter that list to contain only languages the user can
    create tasks for.

    A review task can be created for a given language iff:

    * There is a set of complete subtitles for that language.
    * There are no open translation tasks for that language.
    * There are no review tasks for that language.
    * There are no approve tasks for that language.
    * The user has permission to create the review task.

    """
    if user and not _user_can_create_task_review(user, team_video):
        return []

    tasks = team_video.task_set

    # Find all languages that have a complete set of subtitles.
    # These are the ones we *might* be able to create a review task for.
    candidate_langs = set(sl.language for sl in team_video.video.completed_subtitle_languages())

    # Find all the languages that have a task which prevents a review task creation.
    # TODO: Make this an OR'ed Q query for performance.
    existing_task_langs = (
            set(t.language for t in tasks.incomplete_translate())
          | set(t.language for t in tasks.all_review())
          | set(t.language for t in tasks.all_approve())
    )

    # Return the candidate languages that don't have a review-preventing task.
    return list(candidate_langs - existing_task_langs)

def can_create_task_approve(team_video, user=None):
    """Return a list of languages for which an approve task can be created for the given video.

    If a user is given, filter that list to contain only languages the user can
    create tasks for.

    An approve task can be created for a given language iff:

    * If reviewing is enabled in the workflow:
        * There is a review task marked as accepted for that language.
    * If reviewing is NOT enabled in the workflow:
        * There is a set of complete subtitles for that language.
    * There are no open translation tasks for that language.
    * There are no approve tasks for that language.
    * The user has permission to create the approve task.

    """
    if user and not _user_can_create_task_review(user, team_video):
        return []

    tasks = team_video.task_set

    # Find all languages we *might* be able to create an approve task for.
    workflow = Workflow.get_for_team_video(team_video)
    if workflow.review_enabled:
        candidate_langs = set(t.language for t in tasks.complete_review('Approved'))
    else:
        candidate_langs = set(sl.language for sl in team_video.video.completed_subtitle_languages())

    # Find all the languages that have a task which prevents an approve task creation.
    # TODO: Make this an OR'ed Q query for performance.
    existing_task_langs = (
            set(t.language for t in tasks.incomplete_translate())
          | set(t.language for t in tasks.all_approve())
    )

    # Return the candidate languages that don't have a review-preventing task.
    return list(candidate_langs - existing_task_langs)

