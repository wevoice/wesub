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

import logging

from celery.task import task
from django.core.exceptions import ObjectDoesNotExist

from externalsites.models import get_account
from subtitles.models import SubtitleLanguage, SubtitleVersion
from videos.models import VideoUrl

celery_logger = logging.getLogger('celery.task')

@task
def update_subtitles(account_type, account_id, video_url_id, lang_id):
    """Update a subtitles for a language"""
    celery_logger.info("externalsites.tasks.update_subtitles"
                       "(%s, %s, %s, %s, %s)", account_type, account_id,
                       video_url_id, lang_id)
    try:
        account = get_account(account_type, account_id)
        language = SubtitleLanguage.objects.get(id=lang_id)
        video_url = VideoUrl.objects.get(id=video_url_id)
    except ObjectDoesNotExist, e:
        celery_logger.error(
            'Lookup error in update_subtitles(): %s' % e,
            exc_info=True,
            extra={
                'data': {
                    'account_type': account_type,
                    'account_id': account_id,
                    'video_url_id': video_url_id,
                    'lang_id': lang_id,
                }
            }
        )
        return
    else:
        account.update_subtitles(video_url, language)

@task
def delete_subtitles(account_type, account_id, video_url_id, lang_id):
    """Delete a subtitles for a language"""
    celery_logger.info("externalsites.tasks.delete_subtitles"
                       "(%s, %s, %s, %s)", account_type, account_id,
                       video_url_id, lang_id)

    try:
        account = get_account(account_type, account_id)
        video_url = VideoUrl.objects.get(id=video_url_id)
        language = SubtitleLanguage.objects.get(id=lang_id)
    except ObjectDoesNotExist, e:
        celery_logger.error(
            'Lookup error in delete_subtitles(): %s' % e,
            exc_info=True,
            extra={
                'data': {
                    'account_type': account_type,
                    'account_id': account_id,
                    'video_url_id': video_url_id,
                    'lang_id': lang_id,
                    'version_id': version_id,
                }
            }
        )
        return

    account.delete_subtitles(video_url, language)

@task
def update_all_subtitles(account_type, account_id):
    """Update all subtitles for a given account."""
    celery_logger.info("externalsites.tasks.update_all_subtitles(%s, %s)",
                       account_type, account_id)
    try:
        account = get_account(account_type, account_id)
    except ObjectDoesNotExist, e:
        celery_logger.error(
            'Lookup error in update_all_subtitles(): %s' % e,
            exc_info=True,
            extra={
                'data': {
                    'account_type': account_type,
                    'account_id': account_id,
                    'video_url_id': video_url_id,
                    'lang_id': lang_id,
                    'version_id': version_id,
                }
            }
        )
        return
    team = account.team
    for video in team.videos.all():
        for video_url in video.get_video_urls():
            if account.is_for_video_url(video_url):
                _sync_all_languages(account, video_url, video)

def _sync_all_languages(account, video_url, video):
    for language in video.newsubtitlelanguage_set.having_public_versions():
        account.update_subtitles(video_url, language)
