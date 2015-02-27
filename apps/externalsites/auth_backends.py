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

from __future__ import absolute_import
from collections import namedtuple

from django.db import IntegrityError

from auth.backends import CustomUserBackend
from auth.models import CustomUser as User
from .models import OpenIDConnectLink

OpenIDConnectInfo = namedtuple('OpenIDConnectInfo',
                               'sub email openid_key profile_data')

class OpenIDConnectBackend(CustomUserBackend):
    def authenticate(self, **credentials):
        connect_info = credentials.get('openid_connect_info')
        if connect_info is None:
            return None

        # Log in a user based on OpenID Connect credentials
        # There are 3 cases we need to handle
        #
        # - First login:
        #     Create a user object and use profile_data to fill in user data
        #
        # - Logged in with OpenID Connect before:
        #     Lookup the user object and don't change the user data
        #
        # - Logged in with the deprecated OpenID 2.0:
        #     we will lookup the user from the OpenidProfile model, create an
        #     OpenIDConnectLink instance, and update their user data
        #
        try:
            return User.objects.get(openid_connect_link__sub=connect_info.sub)
        except User.DoesNotExist:
            pass
        if connect_info.openid_key:
            try:
                return self._get_openid20_user(connect_info)
            except User.DoesNotExist:
                pass
        return self._create_new_user(connect_info)

    def _get_openid20_user(self, connect_info):
        user = User.objects.get(
            openidprofile__openid_key=connect_info.openid_key)
        for name, value in connect_info.profile_data.items():
            if not getattr(user, name):
                setattr(user, name, value)
        user.save()
        OpenIDConnectLink.objects.create(user=user, sub=connect_info.sub)
        return user

    def _create_new_user(self, connect_info):
        usernames = self._generate_usernames(connect_info.email)
        while True:
            try:
                user = User.objects.create(username=usernames.next(),
                                           email=connect_info.email,
                                           **connect_info.profile_data)
                break
            except IntegrityError:
                continue

        OpenIDConnectLink.objects.create(user=user, sub=connect_info.sub)
        return user

    def _generate_usernames(self, email):
        yield email
        parts = email.split('@', 1)
        username = parts[0]
        for i in xrange(1, 20):
            parts[0] = username + str(i)
            yield '@'.join(parts)
        raise ValueError("Can't find unique username for {}".format(email))
