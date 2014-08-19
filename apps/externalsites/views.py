# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
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

import logging

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render

from auth.models import CustomUser as User
from externalsites import forms
from externalsites.exceptions import YouTubeAccountExistsError
from externalsites.models import get_sync_account, YouTubeAccount
from localeurl.utils import universal_url
from teams.models import Team
from teams.views import settings_page
from utils import youtube
from videos.models import VideoUrl

logger = logging.getLogger('amara.externalsites.views')

class AccountFormHandler(object):
    """Handles a single form for the settings tab

    On the settings tab we show several forms for different accounts.
    AccountFormHandler handles the logic for a single form.
    """
    def __init__(self, form_name, form_class):
        self.form_name = form_name
        self.form_class = form_class
        self.should_redirect = False

    def handle_post(self, post_data, context):
        pass

    def handle_get(self, post_data, context):
        pass

@settings_page
def team_settings_tab(request, team):
    if request.method == 'POST':
        formset = forms.AccountFormset(team, request.POST)
    else:
        formset = forms.AccountFormset(team, None)

    if formset.is_valid():
        formset.save()
        if 'remove-youtube-account' in request.POST:
            account = YouTubeAccount.objects.for_owner(team).get(
                id=request.POST['remove-youtube-account'])
            account.delete()
        return redirect(settings_page_redirect_url(team, request.POST))

    return render(request, 'externalsites/team-settings-tab.html', {
        'team': team,
        'forms': formset,
        'youtube_accounts': YouTubeAccount.objects.for_owner(team),
    })

def settings_page_redirect_url(team, data):
    if 'add-youtube-account' in data:
        return '%s?team_slug=%s' % (
            reverse('externalsites:youtube-add-account'), team.slug)
    else:
        return reverse('teams:settings_externalsites', kwargs={
            'slug': team.slug,
        })

def youtube_callback_url():
    return universal_url(
        'externalsites:youtube-callback',
        protocol_override=settings.OAUTH_CALLBACK_PROTOCOL)

def youtube_add_account(request):
    if 'team_slug' in request.GET:
        state = {'team_slug': request.GET['team_slug']}
    elif 'username' in request.GET:
        state = {'username': request.GET['username']}
    else:
        logging.error("youtube_add_account: Unknown owner")
        raise Http404()
    return redirect(youtube.request_token_url(youtube_callback_url(), state))

def youtube_callback(request):
    try:
        auth_info = youtube.handle_callback(request, youtube_callback_url())
    except youtube.APIError, e:
        logging.error("youtube_callback_team: %s" % e)
        messages.error(request, e.message)
        # there's no good place to redirect the user to since we don't know
        # what team/user they were trying to add the account for.  I guess the
        # homepage is as good as any.
        return redirect('videos.views.index')

    account_data = {
        'username': auth_info.username,
        'channel_id': auth_info.channel_id,
        'oauth_refresh_token': auth_info.refresh_token,
    }
    if 'team_slug' in auth_info.state:
        team = get_object_or_404(Team, slug=auth_info.state['team_slug'])
        account_data['team'] = team
        redirect_url = reverse('teams:settings_externalsites', kwargs={
            'slug': team.slug,
        })
    elif 'username' in auth_info.state:
        user = get_object_or_404(User, username=auth_info.state['username'])
        account_data['user'] = user
        redirect_url = reverse('profiles:account')
    else:
        logger.error("youtube_callback: invalid state data: %s" %
                     auth_info.state)
        messages.error(request, _("Error in auth callback"))
        return redirect('videos.views.index')

    try:
        account = YouTubeAccount.objects.create_or_update(**account_data)
    except YouTubeAccountExistsError, e:
        messages.error(request, str(e))
    else:
        if 'username' in auth_info.state:
            account.create_feed()

    return redirect(redirect_url)

@staff_member_required
def resync(request, video_url_id, language_code):
    video_url = get_object_or_404(VideoUrl, id=video_url_id)
    video = video_url.video
    language = video.subtitle_language(language_code)

    if request.method == 'POST':
        logger.info("resyncing subtitles: %s (%s)", video, video_url)
        _resync_video(video, video_url, language)

    redirect_url = reverse('videos:translation_history', kwargs={
        'video_id': video.video_id,
        'lang': language_code,
        'lang_id': language.id
    })
    return HttpResponseRedirect(redirect_url + '?tab=sync-history')

def _resync_video(video, video_url, language):
    account = get_sync_account(video, video_url)
    if account is None:
        return
    tip = language.get_public_tip()
    if tip is not None:
        account.update_subtitles(video_url, language)
    else:
        account.delete_subtitles(video_url, language)
