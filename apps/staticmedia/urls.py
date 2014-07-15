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

from django.conf import settings
from django.conf.urls.defaults import patterns, url

if settings.STATIC_MEDIA_USES_S3:
    # don't serve up the media from the local server if we're using S3
    urlpatterns = patterns('staticmedia.views')
else:
    urlpatterns = patterns(
        'staticmedia.views',
        url(r'^(?P<bundle_name>[\w\.-]+)$', 'bundle', name='bundle'),
    )
