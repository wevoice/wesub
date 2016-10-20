# Amara, universalsubtitles.org
#
# Copyright (C) 2016 Participatory Culture Foundation
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

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from auth.models import CustomUser as User
from notifications.handlers import (call_event_handler,
                                    call_event_handler_for_video)
from teams.models import TeamVideo, TeamMember
import auth.signals
import subtitles.signals
import teams.signals

@receiver(post_save, sender=TeamVideo)
def on_team_video_save(sender, instance, created, **kwargs):
    if created:
        call_event_handler(instance.team, 'on_video_added', instance.video,
                           None)

@receiver(pre_delete, sender=TeamVideo)
def on_team_video_delete(sender, instance, **kwargs):
    call_event_handler(instance.team, 'on_video_removed', instance.video, None)

@receiver(teams.signals.video_moved_from_team_to_team)
def on_team_video_move(sender, destination_team, old_team, **kwargs):
    video = sender.video
    call_event_handler(destination_team, 'on_video_added', video, old_team)
    call_event_handler(old_team, 'on_video_removed', video, destination_team)

@receiver(subtitles.signals.subtitles_added)
def on_subtitles_added(sender, version, **kwargs):
    subtitle_language = sender
    video = subtitle_language.video
    call_event_handler_for_video(video, 'on_subtitles_added', video,
                                 version)

@receiver(subtitles.signals.subtitles_published)
def on_subtitles_published(sender, **kwargs):
    subtitle_language = sender
    video = subtitle_language.video
    call_event_handler_for_video(video, 'on_subtitles_published', video,
                                 subtitle_language)

@receiver(subtitles.signals.language_deleted)
def on_language_deleted(sender, **kwargs):
    subtitle_language = sender
    video = subtitle_language.video
    call_event_handler_for_video(video, 'on_subtitles_deleted', video,
                                 subtitle_language)

@receiver(post_save, sender=TeamMember)
def on_team_member_save(sender, instance, created, **kwargs):
    member = instance
    if created:
        call_event_handler(member.team, 'on_user_added', member.user)

@receiver(pre_delete, sender=TeamMember)
def on_team_member_delete(sender, instance, **kwargs):
    member = instance
    call_event_handler(member.team, 'on_user_removed', member.user)

@receiver(auth.signals.user_profile_changed)
def on_user_save(sender, **kwargs):
    user = sender
    for team in user.teams.all():
        call_event_handler(team, 'on_user_info_updated', user)
