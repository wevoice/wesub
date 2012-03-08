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
import requests

from django.conf import settings


AUTH = getattr(settings, 'BASIC_AUTH_DOMAINS', None)

def url_exists(url):
    """Check that a url (when following redirection) exists.

    This is needed because Django's validators rely on Python's urllib2
    which in verions < 2.6 won't follow redirects.

    """
    try:
        # This AUTH stuff is a hack to get around the HTTP Basic Auth on dev
        # and staging to prevent partner stuff from going public.
        if AUTH:
            for domain, auth in AUTH.items():
                if domain in url:
                    return 200 <= requests.head(url, auth=auth).status_code < 400

        return 200 <= requests.head(url).status_code < 400
    except requests.ConnectionError:
        return False
