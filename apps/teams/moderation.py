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

from apps.teams.moderation_const import *

import datetime

from django.core.exceptions import SuspiciousOperation

from haystack import site

from apps.videos.models import Video, SubtitleVersion, SubtitleLanguage, Action
from apps.teams.models import TeamVideo

from apps.comments.notifications import notify_comment_by_email

from widget import video_cache


def _update_search_index(video):
    """
    Updates the search team video index for that video if that video is under moderation
    """
    if video.moderated_by:
        tv = TeamVideo.objects.get(video=video, team=video.moderated_by)
        site.get_index(TeamVideo).update_object(tv)

class AlreadyModeratedException(Exception):
    pass

def user_can_moderate(video, user):
    if not user.is_authenticated():
        return False
    return video.moderated_by and video.moderated_by.is_contributor(user)

def is_moderated(version_lang_or_video):
    if isinstance(version_lang_or_video , SubtitleVersion):
        return version_lang_or_video.moderation_status != UNMODERATED
    elif isinstance(version_lang_or_video, SubtitleLanguage):
        video = version_lang_or_video.video
    elif isinstance(version_lang_or_video, Video):
        video = version_lang_or_video
    return bool(video.moderated_by)


#@require_lock
def add_moderation( video, team, user):
    """
    Adds moderation and approves all
    """
    if video.moderated_by :
        raise AlreadyModeratedException("Video is already moderated")
    if not team.can_add_moderation(user) :
        raise SuspiciousOperation("User cannot set this video as moderated")
    video.moderated_by = team
    video.save()
    SubtitleVersion.objects.filter(language__video__id = video.pk, moderation_status=UNMODERATED).update(moderation_status=APPROVED)
    video_cache.invalidate_cache(video.video_id)
    _update_search_index(video)
    return True


#@require_lock
def remove_moderation( video,  team, user):
    """
    Removes the moderation lock for that video, sets all the sub versions to
    approved , invalidates the cache and updates the search index.
    """
    if not video.moderated_by:
        return None
    if not team.can_remove_moderation( user) :
        raise SuspiciousOperation("User cannot unset this video as moderated")
    for lang in video.subtitlelanguage_set.all():
        latest = lang.latest_version(public_only=False)
        if latest and latest.moderation_status == REJECTED:
            # rollback to the last moderated status
            latest_approved = lang.latest_version(public_only=Tue)
            v = latest_approved.rollback(user)
            v.save()

    num = SubtitleVersion.objects.filter(language__video=video).update(moderation_status=UNMODERATED)
    video.moderated_by = None;
    video.save()
    video_cache.invalidate_cache(video.video_id)
    _update_search_index(video)
    return num

def _set_version_moderation_status(version, team, user, status, updates_meta=True):
    if not user_can_moderate(version.language.video, user):
        raise SuspiciousOperation("User cannot approve this version")
    version.moderation_status = status
    version.save()
    if updates_meta:
        video_cache.invalidate_cache(version.video.video_id)
        _update_search_index(version.video)
    return version

def approve_version( version, team, user, updates_meta=True):
    _set_version_moderation_status(version, team, user, APPROVED, updates_meta)
    Action.create_approved_video_handler(version, user)

def reject_version(version, team, user, rejection_message=None, sender=None, updates_meta=True, ):
    v = _set_version_moderation_status(version, team, user, REJECTED, updates_meta)
    latest = version.language.latest_version(public_only=False)
    if latest and latest.moderation_status == REJECTED:
        # rollback to the last moderated status
        latest_approved = version.language.latest_version(public_only=True)
        if latest_approved:
            latest_approved.rollback(user)
    if bool(rejection_message) and bool(sender):
        comment = create_comment_for_rejection(version, rejection_message, sender)
        notify_comment_by_email(comment, version.language, moderator = sender, is_rejection=True )
    Action.create_rejected_video_handler(version, user)
    return v

def remove_version_moderation(version, team, user, updates_meta=True):
    _set_version_moderation_status(version, team, user, WAITING_MODERATION, updates_meta)

def create_comment_for_rejection(version, msg, sender):
    from apps.comments.models import Comment
    comment = Comment(content_object=version.language,
                      user = sender,
                      content = msg,
                      submit_date = datetime.datetime.now()
    )
    comment.save()
    return comment


def get_pending_count(lang):
    return SubtitleVersion.objects.filter(language=lang).filter(moderation_status=WAITING_MODERATION).count()

def is_approved(version):
    return version.moderation_status == APPROVED

def is_rejected(version):
    return version.moderation_status == REJECTED

def is_waiting(version):
    return version.moderation_status == WAITING_MODERATION
