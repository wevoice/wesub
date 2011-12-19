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
"""
Centralizes notification sending throught the website.
Currently we support:
    - email messages
    - site inbox (messages.models.Message)
    - activity feed (videos.models.Action)

Messages models will trigger an email to be sent if
the user has allowed email notifications
"""
import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _, ugettext
from django.template.loader import render_to_string

from sentry.client.models import client
from celery.task import task

from auth.models import CustomUser as User

from utils import send_templated_email

@task()
def send_new_message_notification(message_id):
    from messages.models import Message
    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        msg = '**send_new_message_notification**. Message does not exist. ID: %s' % message_id
        client.create_from_text(msg, logger='celery')
        return
    
    user = message.user

    if not user.email or not user.is_active or not user.notify_by_email:
        return

    to = "%s <%s>" % (user, user.email)
    if message.author:
        subject = _(u"New message from %(author)s on Universal Subtitles: %(subject)s")
    else: 
        subject = _("New message on Universal Subtitles: %(subject)s")
    subject = subject % {
        'author': message.author, 
        'subject': message.subject
    }
        
    context = {
        "message": message,
        "domain":  Site.objects.get_current().domain,
        "STATIC_URL": settings.STATIC_URL,
    }

    send_templated_email(to, subject, "messages/email/message_received.html", context)
    
@task()    
def team_invitation_sent(invite_pk):
    from messages.models import Message
    from teams.models import Invite
    invite = Invite.objects.get(pk=invite_pk)
    msg = Message()
    msg.subject = ugettext("You've been invited to team %s on Universal Subtitles" % invite.team.name)
    msg.user = invite.user
    msg.object = invite
    msg.author = invite.author
    msg.save()
    return True
        
@task()
def application_sent(application_pk):
    from messages.models import Message
    from teams.models import Application, TeamMember
    
    application = Application.objects.get(pk=application_pk)
    notifiable = TeamMember.objects.filter( team=application.team,
       role__in=[TeamMember.ROLE_ADMIN, TeamMember.ROLE_OWNER])
    for m in notifiable:
        msg = Message()
        msg.subject = ugettext(u'%s is applying for team %s') % (application.user, application.team.name)
        msg.content = ugettext(u'%s is applying for team %s') % (application.user, application.team.name)
        msg.user = m.user
        msg.object = application.team
        msg.author = application.user
        msg.save()

def team_application_approved(application_pk):
    from messages.models import Message
    from teams.models import Application
    application = Application.objects.get(pk=application_pk)
    msg = Message()
    msg.subject = ugettext(u'Your application to %s was approved!') % application.team.name
    msg.content = ugettext(u"Congratulations, you're now a member of %s!") % application.team.name
    msg.user = application.user
    msg.object = application.team
    msg.author = User.get_anonymous()
    msg.save()


@task() 
def team_application_denied(application_pk):
    from messages.models import Message
    from teams.models import Application
    application = Application.objects.get(pk=application_pk)
    msg = Message()
    msg.subject = ugettext(u'Your application to %s was denied.') % application.team.name
    msg.content = ugettext(u"Sorry, your application to %s was rejected.") % application.team.name
    msg.user = application.user
    msg.object = application.team
    msg.author = User.get_anonymous()
    msg.save()

@task() 
def team_member_new(member_pk):
    from messages.models import Message
    from teams.models import TeamMember
    member = TeamMember.objects.get(pk=member_pk)
    from videos.models import Action   
    from teams.models import TeamMember
    # the feed item should appear on the timeline for all team members
    # as a team might have thousands of members, this one item has
    # to show up on all of them
    Action.create_new_member_handler(member)
    # notify  admins and owners through messages
    notifiable = TeamMember.objects.filter( team=member.team,
       role__in=[TeamMember.ROLE_ADMIN, TeamMember.ROLE_OWNER])
    for m in notifiable:
        msg = Message()
        if m.user == member.user:
             base_str = ugettext("You've joined the %s team as a(n) %s'" %
                                 (m.team, m.role))
        base_str = ugettext("%s joined the %s team as a(n) %s" % (
            m.user, m.team, m.role))
        msg.subject = ugettext(base_str)
        msg.content = ugettext(base_str + " on %s" % (datetime.datetime.now()))
        msg.user = m.user
        msg.object = m.team
        msg.save()

@task() 
def team_member_leave(team_pk, user_pk):
    from messages.models import Message
    from teams.models import TeamMember, Team
    user = User.objects.get(pk=user_pk)
    team = Team.objects.get(pk=team_pk)
    from videos.models import Action   
    # the feed item should appear on the timeline for all team members
    # as a team might have thousands of members, this one item has
    # to show up on all of them
    Action.create_member_left_handler(team, user)
    # notify  admins and owners through messages
    notifiable = TeamMember.objects.filter( team=team,
       role__in=[TeamMember.ROLE_ADMIN, TeamMember.ROLE_OWNER])
    for m in notifiable:
        msg = Message()
        if m.user == user:
             base_str = ugettext("You've left the %s team.'" %
                                 (team))
        base_str = ugettext("%s left the %s team " % (
            m.user, m.team))
        msg.subject = ugettext(base_str)
        msg.content = ugettext(base_str + " on %s" % (datetime.datetime.now()))
        msg.user = m.user
        msg.object = m.team
        msg.save()
        
@task()
def email_confirmed(user_pk):
    from messages.models import Message
    user = User.objects.get(pk=user_pk)
    subject = "Welcome aboard!"
    body = render_to_string("messages/email/email_confirmed.html", {"user":user})
    message  = Message(
        user=user,
        subject=subject,
        content=body
    )
    message.save()
    return True
    
    
