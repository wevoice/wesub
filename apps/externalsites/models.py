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

from django.db import models
from subtitles.models import SubtitleLanguage, SubtitleVersion
from teams.models import Team
from django.utils.translation import ugettext_lazy as _
import videos.models

class KalturaAccount(models.Model):
    account_type = 'K'
    team = models.OneToOneField(Team, unique=True)
    partner_id = models.CharField(max_length=100,
                                  verbose_name=_('Partner ID'))
    secret = models.CharField(
        max_length=100, verbose_name=_('Secret'),
        help_text=_('Administrator secret found in Settings -> '
                    'Integration on your Kaltura control panel'))

account_models = [
    KalturaAccount,
]
_account_type_to_model = dict((model.account_type, model)
                              for model in account_models)

def get_account(account_type, account_id):
    AccountModel = _account_type_to_model[account_id]
    return AccountModel.objects.get(id=account_id)

_video_type_to_account_model = {
    videos.models.VIDEO_TYPE_KALTURA: KalturaAccount
}
def accounts_for_video(video):
    """Lookup an external accounts for a given video.

    This function examines the team associated with the video and the set of
    VideoURLs to determine external accounts that we should sync with.
    """
    team_video = video.get_team_video()
    if team_video is None:
        return []
    team = team_video.team
    rv = []
    for video_url in video.get_video_urls():
        AccountModel = _video_type_to_account_model.get(video_url.type)
        if AccountModel is None:
            continue
        rv.extend(AccountModel.objects.filter(team=team))
    return rv

def lookup_accounts(team):
    """Lookup all accounts for a given team."""
    account_models = [
        KalturaAccount,
    ]
    rv = []
    for model in account_models:
        rv.extend(model.objects.filter(team=team))
    return rv

# import the signalhandlers module from models.py to ensure that it's loaded
import externalsites.signalhandlers
