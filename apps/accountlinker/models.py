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

from django.db import models

from videos.models import  VIDEO_TYPE

ACCOUNT_TYPES = VIDEO_TYPE

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
    username  = models.CharField(max_length=512, db_index=True, 
                                 null=False, blank=False)
    oauth_access_token = models.CharField(max_length=256, db_index=True, 
                                          null=False, blank=False)
    oauth_refresh_token = models.CharField(max_length=256, db_index=True,
                                           null=False, blank=False)
    
    class Meta:
        unique_together = ("type", "oauth_access_token")
    
