# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
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

from django.test.client import Client

class APIClient(Client):
    def __init__(self):
        self.auth_headers = {}
        Client.__init__(self)

    def set_auth_headers(self, user):
        if user is None:
            self.auth_headers = {}
        else:
            self.auth_headers = {
                'HTTP_X_API_USERNAME': user.username,
                'HTTP_X_APIKEY': user.get_api_key(),
            }

    def request(self, **request):
        request.update(self.auth_headers)
        return Client.request(self, **request)
