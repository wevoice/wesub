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

from django.utils.translation import ugettext_lazy as _, ugettext

from auth.models import CustomUser as User
from messages.models import Message
   
def team_invitation_sent(invite):
    msg = Message()
    msg.subject = ugettext("You've been invited to team %s on Universal Subtitles" % invite.team.name)
    msg.user = invite.user
    msg.object = invite
    msg.author = invite.author
    msg.save()
        
def team_application_approved(application):
    msg = Message()
    msg.subject = ugettext(u'Your application to %s was approved!') % application.team.name
    msg.content = ugettext(u"Congratulations, you're now a member of %s!") % application.team.name
    msg.user = application.user
    msg.object = application.team
    msg.author = User.get_anonymous()
    msg.save()


def team_application_denied(application):
    msg = Message()
    msg.subject = ugettext(u'Your application to %s was denied.') % application.team.name
    msg.content = ugettext(u"Sorry, your application to %s was rejected.") % application.team.name
    msg.user = application.user
    msg.object = application.team
    msg.author = User.get_anonymous()
    msg.save()


