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
import time

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.http import cookie_date
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template

from auth.models import CustomUser as User
from messages.models import Message
from messages.rpc import MessagesApiClass
from messages.forms import SendMessageForm
from utils.rpc import RpcRouter
from utils import render_to_json

rpc_router = RpcRouter('messages:rpc_router', {
    'MessagesApi': MessagesApiClass()
})

MESSAGES_ON_PAGE = getattr(settings, 'MESSAGES_ON_PAGE', 30)


@login_required
def index(request, message_pk=None):
    user = request.user
    qs = Message.objects.for_user(user)

    extra_context = {
        'send_message_form': SendMessageForm(request.user, auto_id='message_form_id_%s'),
        'messages_display': True,
        'user_info': user
    }
    
    reply = request.GET.get('reply')

    if reply:
        try:
            reply_msg = Message.objects.get(pk=reply, user=user)
            reply_msg.read = True
            reply_msg.save()
            extra_context['reply_msg'] = reply_msg
        except (Message.DoesNotExist, ValueError):
            pass

    response = object_list(request, queryset=qs,
                       paginate_by=MESSAGES_ON_PAGE,
                       template_name='messages/index.html',
                       template_object_name='message',
                       extra_context=extra_context)
    try:
        last_message = qs[:1].get()
        max_age = 60*60*24*365
        expires = cookie_date(time.time()+max_age)
        response.set_cookie(Message.hide_cookie_name, last_message.pk, max_age, expires)
    except Message.DoesNotExist:
        pass
    
    return response
    
@login_required    
def sent(request):
    user = request.user
    qs = Message.objects.for_author(request.user)
    extra_context = {
        'send_message_form': SendMessageForm(request.user, auto_id='message_form_id_%s'),
        'messages_display': True,
        'user_info': user      
    }
    return object_list(request, queryset=qs,
                       paginate_by=MESSAGES_ON_PAGE,
                       template_name='messages/sent.html',
                       template_object_name='message',
                       extra_context=extra_context)

@login_required
def new(request):
    user = request.user
    context = {
        'user_info': user,
    }

    return direct_to_template(request, 'messages/new.html', context)

@render_to_json
def search_users(request):
    users = User.objects.all()
    q = request.GET.get('term')

    results = [[u.id, u.username]
               for u in users.filter(username__icontains=q,
                                            is_active=True)]

    return { 'results': results }
