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

import json

import requests

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render_to_response

from accountlinker.models import ThirdPartyAccount
from teams.models import Team
import logging
import sentry_logger # Magical import to make sure Sentry's error recording happens.
logger = logging.getLogger("authbelt.views")


def youtube_oauth_callback(request):
    print request
    code = request.GET.get("code", None)
    if code is None:
        raise Exception("No code in youtube oauth callback")
    state = request.GET.get("state", None)
    if state is None:
        raise Exception("No state in youtube oauth callback")
    values = state.split("-")
    team_pk = values[0]
    if len(values) > 1:
        project_pk = values[1]
    team = Team.objects.get(pk=team_pk)
    
    base =  "https://accounts.google.com/o/oauth2/token"
    state = team.pk
    
    params = {
        "client_id": settings.YOUTUBE_CLIENT_ID,
        "client_secret": settings.YOUTUBE_API_SECRET,
        "redirect_uri": "http://%s%s" % (
            Site.objects.get_current().domain,
            reverse("accountlinker:youtube-oauth-callback")),
        "code": code,
        "grant_type": "authorization_code\n",
        
    }
    
    params = "&\n".join(["%s=%s" % (k,v) for k,v in params.items()])
    print params
    response = requests.post(base, data=params)
    if response.status_code != 200:
        logger.error("Error on requesting Youtube Oauth token", extra={
                    "data": {
                        "sent_params": params,
                        "original_request": request,
                    },
                })
        import pdb;pdb.set_trace()
        if settings.DEBUG:
            raise Exception("oh my!")
                    
    content = json.loads(response.content)
    new_account = ThirdPartyAccount(
        oauth_access_token = content['access_token'],
        oauth_refersh_token = content['refresh_token'],
        team = team
    )
    new_account.save()
    return redirect(reverse("teams:third-party-accounts", kwargs={"slug":team.slug}))
