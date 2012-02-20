# Universal Subtitles, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
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

from videos.models import VIDEO_TYPE
from .videos.types import (
    video_type_registrar, UPDATE_VERSION_ACTION, DELETE_LANGUAGE_ACTION
)

# for now, they kind of match
ACCOUNT_TYPES = VIDEO_TYPE

class ThirdPartyAccountManager(models.Manager):

    def mirror_on_third_party(self, video, language, action, version=None):
        """
        Does the specified action (video.types.UPDATE_VERSION_ACTION or
                                   video.types.DELETE_LANGUAGE_ACTION) 
        on the original account (e.g. Youtube video).
        For example, to update a given version to Youtube:
             ThirdPartyAccountManager.objects.mirror_on_third_party(
                       video, language, "update_subtitles", version)
        For deleting, we only delete languages, so it should be 
              ThirdPartyAccountManager.objects.mirror_on_third_party(
                        video, language, "delete_subtitles")
        This method is 'safe' to call, meaning that we only do syncing if there 
        are matching third party credentials for this video.
        The update will only be done if the version is synced
        """
        if action not in [UPDATE_VERSION_ACTION, DELETE_LANGUAGE_ACTION]:
            raise NotImplementedError(
                "Mirror to third party does not support the %s action" % action)

        if version:
            if not version.is_public() or not version.is_synced():
                # We can't mirror unsynced or non-public versions.
                return

        for vurl in video.videourl_set.all():
            username = vurl.owner_username
            if not username:
                continue
            try:
                account = ThirdPartyAccount.objects.get(type=vurl.type, username=username)
            except ThirdPartyAccount.DoesNotExist:
                continue

            vt = video_type_registrar.video_type_for_url(vurl.url)
            if hasattr(vt, action):
                if action == UPDATE_VERSION_ACTION:
                    vt.update_subtitles(version, account)
                elif action == DELETE_LANGUAGE_ACTION:
                    vt.delete_subtitles(language, account)

class ThirdPartyAccount(models.Model):
    """
    Links a third party account (e.g. YouTube's') to a certain video URL
    This allows us to push changes in Unisubs back to that video provider.
    The user links a video on unisubs to his youtube account. Once edits to
    any languages are done, we push those back to Youtube.
    For know, this only supports Youtube, but nothing is stopping it from
    working with others.
    """
    type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    # this is the third party account user name, eg the youtube user
    username  = models.CharField(max_length=255, db_index=True, 
                                 null=False, blank=False)
    oauth_access_token = models.CharField(max_length=255, db_index=True, 
                                          null=False, blank=False)
    oauth_refresh_token = models.CharField(max_length=255, db_index=True,
                                           null=False, blank=False)
    
    objects = ThirdPartyAccountManager()
    
    class Meta:
        unique_together = ("type", "username")
    
