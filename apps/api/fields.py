# Amara, universalsubtitles.org
#
# Copyright (C) 2015 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.html.

from __future__ import absolute_import

from django.utils import timezone
from rest_framework.fields import CharField
from rest_framework import serializers
import pytz

from auth.models import CustomUser as User
from teams.models import Team

class LanguageCodeField(CharField):
    def to_internal_value(self, language_code):
        return language_code.lower()

class UsernameField(CharField):
    default_error_messages = {
        'invalid-user': "Invalid User"
    }

    def to_representation(self, user):
        if user:
            return user.username
        else:
            return None

    def to_internal_value(self, username):
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                self.fail('invalid-user')
        else:
            return None

class TeamSlugField(CharField):
    default_error_messages = {
        'invalid-team': "Invalid Team"
    }

    def to_representation(self, team):
        if team:
            return team.slug
        else:
            return None

    def to_internal_value(self, slug):
        if slug:
            try:
                return Team.objects.get(slug=slug)
            except Team.DoesNotExist:
                self.fail('invalid-team')
        else:
            return None

class TimezoneAwareDateTimeField(serializers.DateTimeField):
    def __init__(self, *args, **kwargs):
        super(TimezoneAwareDateTimeField, self).__init__(*args, **kwargs)
        self.tz = timezone.get_default_timezone()

    def to_representation(self, value):
        return super(TimezoneAwareDateTimeField, self).to_representation(
            self.tz.localize(value).astimezone(pytz.utc))
