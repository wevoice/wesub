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

from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from externalsites.models import get_account_for_videourl
from videos.models import VideoUrl
from teams.views import settings_page
from externalsites import forms

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
        return redirect('teams:settings_externalsites', slug=team.slug)

    return render(request, 'externalsites/team-settings-tab.html', {
        'team': team,
        'forms': formset,
    })

@staff_member_required
def resync(request, video_url_id, language_code):
    video_url = get_object_or_404(VideoUrl, id=video_url_id)
    video = video_url.video
    language = video.subtitle_language(language_code)

    if request.method == 'POST':
        logger.info("resyncing subtitles: %s (%s)", video, video_url)
        team_video = video.get_team_video()
        if team_video is not None:
            _resync_video(team_video.team, video_url, language)
        else:
            logger.warning("resyncing subtitles: not a team video")

    redirect_url = reverse('videos:translation_history', kwargs={
        'video_id': video.video_id,
        'lang': language_code,
        'lang_id': language.id
    })
    return HttpResponseRedirect(redirect_url + '?tab=sync-history')

def _resync_video(team, video_url, language):
    account = get_account_for_videourl(team, video_url)
    if account is None:
        return
    tip = language.get_public_tip()
    if tip is not None:
        account.update_subtitles(video_url, language)
    else:
        account.delete_subtitles(video_url, language)
