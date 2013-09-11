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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from celery.task import task
from externalsites.models import (get_account, SyncedSubtitleVersion,
                                  SyncHistory)
from subtitles.models import SubtitleLanguage, SubtitleVersion
from videos.models import VideoUrl

@task
def update_subtitles(account_type, account_id, video_url_id, lang_id,
                     version_id):
    """Update a subtitles for a language"""
    account = get_account(account_type, account_id)
    language = SubtitleLanguage.objects.get(id=lang_id)
    video_url = VideoUrl.objects.get(id=video_url_id)
    version = SubtitleVersion.objects.get(id=version_id)
    _update_subtitles(account, video_url, language, version)

def _update_subtitles(account, video_url, language, version):
    sync_history_values = {
        'account': account,
        'video_url': video_url,
        'language': language,
        'action': SyncHistory.ACTION_UPDATE_SUBTITLES,
        'version': version,
    }

    try:
        account.update_subtitles(video_url, language, version)
    except StandardError, e:
        SyncHistory.objects.create_for_error(e, **sync_history_values)
    else:
        SyncHistory.objects.create_for_success(**sync_history_values)
        SyncedSubtitleVersion.objects.set_synced_version(
            account, video_url, language, version)

@task
def delete_subtitles(account_type, account_id, video_url_id, lang_id):
    """Delete a subtitles for a language"""

    account = get_account(account_type, account_id)
    video_url = VideoUrl.objects.get(id=video_url_id)
    language = SubtitleLanguage.objects.get(id=lang_id)

    sync_history_values = {
        'account': account,
        'language': language,
        'video_url': video_url,
        'action': SyncHistory.ACTION_DELETE_SUBTITLES,
    }

    try:
        account.delete_subtitles(video_url, language)
    except StandardError, e:
        SyncHistory.objects.create_for_error(e, **sync_history_values)
    else:
        SyncHistory.objects.create_for_success(**sync_history_values)
        SyncedSubtitleVersion.objects.unset_synced_version(
            account, video_url, language)

@task
def update_all_subtitles(account_type, account_id):
    """Update all subtitles for a given account."""
    account = get_account(account_type, account_id)
    team = account.team
    for video in team.videos.all():
        for video_url in video.get_video_urls():
            if account.is_for_video_url(video_url):
                _sync_all_languages(account, video_url, video)

def _sync_all_languages(account, video_url, video):
    for language in video.newsubtitlelanguage_set.having_public_versions():
        _update_subtitles(account, video_url, language,
                          language.get_public_tip())
