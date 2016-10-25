#!/usr/bin/python
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

"""startup.py -- code that we run at startup

This module handles running code when we start up.  Currently there are a
couple ways of starting up:
    - mangage.py -- shell and dev servers
    - deploy/unisubs.wsgi -- production server

For any of these cases we should call the startup() function early on in the
startup process.  Right after the django settings are set up is a good time.
"""

import os
import sys

import optionalapps

def setup_ca():
    # This lets the requests library use the system CA certs, which are more
    # up-to-date.  In particular, they work with the google HTTPS
    os.environ['REQUESTS_CA_BUNDLE'] = "/etc/ssl/certs/ca-certificates.crt"

def setup_monkeypatches():
    from localeurl import patch_reverse
    patch_reverse()

def setup_celery_loader():
    os.environ.setdefault("CELERY_LOADER",
                          "amaracelery.loaders.AmaraCeleryLoader")

def run_startup_modules():
    """For all django apps, try to run the startup module.  """

    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        module = __import__(app)
        package_dir = os.path.dirname(module.__file__)
        for module in ('startup', 'signalhandlers'):
            filename = module + '.py'
            if os.path.exists(os.path.join(package_dir, filename)):
                __import__('{}.{}'.format(app, module))

def startup():
    """Set up the amara environment.  This should be called before running any
    other code.
    """
    optionalapps.setup_path()
    setup_ca()
    setup_monkeypatches()
    setup_celery_loader()
    run_startup_modules()
