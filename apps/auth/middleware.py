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

import functools

from django.contrib import auth

from auth.models import CustomUser as User

SESSION_KEY = '_cached_user_id'

class AmaraAuthenticationMiddleware(object):
    def use_cached_user(self, request):
        try:
            user_id = request.session[SESSION_KEY]
        except KeyError:
            request.user = auth.get_user(request)
            request.session[SESSION_KEY] = request.user.id
        else:
            request.user = User.cache.get_instance(user_id)

    def process_request(self, request):
        # FIXME: this should probably be the default behavior, but that would
        # prevent the user from being modified during the request.  We should
        # take a survey of our view functions and see which ones need to do
        # that.
        request.use_cached_user = functools.partial(self.use_cached_user,
                                                    request)
