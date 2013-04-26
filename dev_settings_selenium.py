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

import os
from settings import *
from dev_settings import *

# We need unisubs-integration for the tests to pass
if not USE_INTEGRATION:
    raise AssertionError("unisubs-integration not present at %s" %
                         INTEGRATION_PATH)
#There are differences in the configs for selenium testing when running 
#in vagrant vm.

SITE_ID = 4
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': "django_test_db.sqlite",
        'USER': "",
        'PASSWORD': "",
        'HOST': "",
        'PORT': ''
        }
    }

INSTALLED_APPS + ('django_nose',
                  'webdriver_testing',)

JS_USE_COMPILED = False
COMPRESS_MEDIA = False

if os.getenv("HOME") == '/home/vagrant':
    SITE_ID = 19
    STATIC_URL = "http://unisubs.example.com:80/site_media/"
    MEDIA_URL = "http://unisubs.example.com:80/user-data/"
    HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr/vagrant'
else:
    STATIC_URL = '/site_media/'
    MEDIA_URL =  '/user-data/'
    HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr/testing'
    INSTALLED_APPS  + ('django.contrib.staticfiles',
                       )
    TEMPLATE_CONTEXT_PROCESSORS + ('django.core.context_processors.static',)

    STATICFILES_FINDERS = (
       'django.contrib.staticfiles.finders.FileSystemFinder',
       'django.contrib.staticfiles.finders.AppDirectoriesFinder',
       )

    MEDIA_ROOT = rel('user-data/')
    STATIC_ROOT = rel('static/')
    STATICFILES_DIRS = (rel('media/'), rel('user-data/'))

STATIC_URL_BASE = STATIC_URL

CACHE_PREFIX = "testcache"
CACHE_TIMEOUT = 60
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--logging-filter=test_steps, -remote_connection, '
             '-selenium.webdriver.remote.remote_connection',
             '--with-xunit',
             '--xunit-file=nosetests.xml',
             #'--failed',
            ]

CELERY_ALWAYS_EAGER = True
import logging
logging.getLogger('pysolr').setLevel(logging.ERROR)


