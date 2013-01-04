from django.core.management import call_command

from apps.auth.models import CustomUser as User
from apps.teams.models import Team, TeamMember, Workflow

from widget.rpc import Rpc    

def create_member(team, role):
    username  =  "test_user_%s" % (User.objects.count() + 1)
    user = User.objects.get_or_create(username=username)[0]
    member = TeamMember.objects.get_or_create(team=team, role=role, user=user)[0]
    return member

def create_team(slug=None, review_setting=0, approve_setting=0,
                autocreate_subtitle=False, autocreate_translate=False):
    team = Team.objects.create(
        slug=slug or 'test team',
        name='test team',
        workflow_enabled = bool(review_setting or approve_setting))
    if review_setting or approve_setting:
        Workflow.objects.get_or_create(team=team, review_allowed=review_setting,
            approve_allowed = approve_setting,  autocreate_translate=autocreate_translate,
            autocreate_subtitle=autocreate_subtitle)
    return team

def refresh_obj(m):
    return m.__class__._default_manager.get(pk=m.pk)

def reset_solr():
    # cause the default site to load
    from haystack import backend
    sb = backend.SearchBackend()
    sb.clear()
    call_command('update_index')


rpc = Rpc()    
