# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
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
from django import template

from messages.models import Message


register = template.Library()

@register.inclusion_tag('messages/_messages.html', takes_context=True)
def messages(context):
    user = context['user']
    if user.is_authenticated():
        hidden_message_id = context['request'].COOKIES.get(Message.hide_cookie_name)
        qs = user.unread_messages(hidden_message_id)
        try:
            last_unread = qs[:1].get().pk
        except Message.DoesNotExist:
            last_unread = ''
        count = user.unread_messages_count(hidden_message_id)
    else:
        qs = Message.objects.none()
        last_unread = ''
        count = 0

    return {
        'msg_count': count,
        'last_unread': last_unread,
        'cookie_name': Message.hide_cookie_name
    }

