# Amara, universalsubtitles.org
#
# Copyright (C) 2014 Participatory Culture Foundation
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
from django.db.models.signals import post_save, post_delete, m2m_changed

from subtitles.models import SubtitleLanguage, SubtitleVersion
from videos.models import Video, VideoUrl

@receiver(post_save, sender=VideoUrl)
@receiver(post_save, sender=SubtitleLanguage)
@receiver(post_save, sender=SubtitleVersion)
@receiver(post_delete, sender=VideoUrl)
def on_video_related_change(sender, instance, **kwargs):
    if instance.video_id is not None:
        Video.invalidate_cache_for_video(instance.video_id)

@receiver(post_save, sender=Video)
def on_video_change(sender, instance, **kwargs):
    instance.invalidate_cache()

@receiver(m2m_changed, sender=Video.followers.through)
def on_video_followers_changed(instance, reverse, **kwargs):
    if not reverse:
        instance.invalidate_cache()
    else:
        for video in instance.followed_videos.all():
            video.invalidate_cache()
