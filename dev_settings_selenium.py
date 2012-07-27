# Amara, universalsubtitles.org
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

from settings import *
from dev_settings import *


SITE_ID = 15
STATIC_URL = "http://unisubs.example.com:80/site_media/"
MEDIA_URL = "http://unisubs.example.com:80/user-data/"
DEFAULT_PROTOCOL  = 'http'
INSTALLED_APPS + ('django_nose', 'webdriver_testing',)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': "/tmp/django_sel_db.sqlite",
        'USER': "",
        'PASSWORD': "",
        'HOST': "",
        'PORT': ''
        }
    }
STATIC_URL_BASE = STATIC_URL
if COMPRESS_MEDIA:
    STATIC_URL += "%s/%s/" % (COMPRESS_OUTPUT_DIRNAME, LAST_COMMIT_GUID.split("/")[1])


CACHE_PREFIX = "testcache"
CACHE_TIMEOUT = 60
DEFAULT_PROTOCOL = 'http'
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--nocapture', ]
CELERY_ALWAYS_EAGER = True
