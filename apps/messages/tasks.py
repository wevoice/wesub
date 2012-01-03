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
from utils import get_object_or_none

        
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
    send_templated_email(user, subject, "messages/email/message_received.html", context)

@task()
def team_invitation_sent(invite_pk):
    if getattr(settings, "MESSAGES_DISABLED", False):
        return
    from messages.models import Message
    from teams.models import Invite, Setting
    invite = Invite.objects.get(pk=invite_pk)
    custom_message = get_object_or_none(Setting, team=invite.team,
                                     key=Setting.KEY_IDS['messages_invite'])
    template_name = 'messages/email/invitation-sent.html'
    
    context = {'invite': invite, 'custom_message': custom_message}
    title = ugettext(u"You've been invited to team %s on Universal Subtitles" % invite.team.name)
    if invite.user.notify_by_message:
        msg = Message()
        msg.subject = title
        msg.user = invite.user
        msg.object = invite
        msg.author = invite.author
        msg.save()
    context = {
        "user":invite.user,
        "inviter":invite.author,
        "team": invite.team,
        "invite_pk": invite_pk,
        "note": invite.note,
    }
    send_templated_email(invite.user, title, template_name, context)
    return True

@task()
def application_sent(application_pk):
    if getattr(settings, "MESSAGES_DISABLED", False):
        return
    from messages.models import Message
    from teams.models import Application, TeamMember
    application = Application.objects.get(pk=application_pk)
    notifiable = TeamMember.objects.filter( team=application.team,
       role__in=[TeamMember.ROLE_ADMIN, TeamMember.ROLE_OWNER])
    for m in notifiable:

        template_name = "messages/email/application_sent.html"
        context = {
            "applicant": application.user,
            "team":application.team,
            "note":application.note,
            "user":m.user,
        }
        body = render_to_string(template_name,context) 
        subject  = ugettext(u'%s is applying for team %s') % (application.user, application.team.name)
        if m.user.notify_by_message:
            msg = Message()
            msg.subject = subject
            msg.content = body
            msg.user = m.user
            msg.object = application.team
            msg.author = application.user
            msg.save()
        send_templated_email(m.user, subject, template_name, context)
        

@task()
def team_application_denied(application_pk):
    
    if getattr(settings, "MESSAGES_DISABLED", False):
        return
    from messages.models import Message
    from teams.models import Application
    application = Application.objects.get(pk=application_pk)
    template_name = "messages/email/team-application-denied.html"
    context = {
        "team": application.team,
        "user": application.user,
    }
    msg = Message()
    msg.subject = ugettext(u'Your application to join the %s team has been declined' % application.team.name)
    msg.content = render_to_string(template_name, context)
    msg.user = application.user
    msg.object = application.team
    msg.author = User.get_anonymous()
    msg.save()
    send_templated_email(msg.user, msg.subject, template_name, context)
    application.delete()

@task()
def team_member_new(member_pk):
    if getattr(settings, "MESSAGES_DISABLED", False):
        return
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
       role__in=[TeamMember.ROLE_ADMIN, TeamMember.ROLE_OWNER]).exclude(pk=member.pk)
    for m in notifiable:
        template_name = "messages/email/team-new-member.html"
        context = {
            "new_member": member.user,
            "team":member.team,
            "user":m.user,
            "role":member.role
        }
        body = render_to_string(template_name,context) 
 
        msg = Message()
        msg.subject = ugettext("%s team has a new member" % (member.team))
        msg.content = body
        msg.user = m.user
        msg.object = m.team
        msg.save()
        send_templated_email(msg.user, msg.subject, template_name, context)

        
    # now send welcome mail to the new member
    template_name = "messages/email/team-welcome.html"
    context = {
        "team":member.team,
        "user":member.user,
    }
    body = render_to_string(template_name,context) 

    msg = Message()
    msg.subject = ugettext("You've joined the %s team!" % (member.team))
    msg.content = body
    msg.user = member.user
    msg.object = member.team
    msg.save()
    send_templated_email(msg.user, msg.subject, template_name, context)

@task()
def team_member_leave(team_pk, user_pk):
    if getattr(settings, "MESSAGES_DISABLED", False):
        return
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
        template_name = "messages/email/team-member-left.html"
        context = {
            "parting_user": user,
            "team":team,
            "user":m.user,
        }
        body = render_to_string(template_name,context) 
 
        msg = Message()
        msg.subject = ugettext(u"%s has left the %s team" % (user, team))
        msg.content = body
        msg.user = user
        msg.object = team
        msg.save()
        send_templated_email(msg.user, msg.subject, template_name, context)

        
    # now send welcome mail to the new member
    template_name = "messages/email/team-member-you-have-left.html"
    context = {
        "team":team,
        "user":user,
    }
    body = render_to_string(template_name,context) 

    msg = Message()
    msg.subject = ugettext("You've left the %s team!" % (team))
    msg.content = body
    msg.user = user
    msg.object = team
    msg.save()
    send_templated_email(msg.user, msg.subject, template_name, context)
@task()
def email_confirmed(user_pk):
    from messages.models import Message
    user = User.objects.get(pk=user_pk)
    subject = "Welcome aboard!"
    template_name = "messages/email/email_confirmed.html"
    context = {"user":user}
    body = render_to_string(template_name, context)
    message  = Message(
        user=user,
        subject=subject,
        content=body
    )
    message.save()
    send_templated_email(user, subject, template_name, context )
    return True


