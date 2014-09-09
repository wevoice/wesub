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

def setup_path():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, os.path.join(root_dir, 'apps'))
    sys.path.insert(0, os.path.join(root_dir, 'libs'))
    # hack to make the unisubs package available.  We alter the path so that
    # we can import it, then undo the changes.  We don't want to be able to
    # import any other python modules that happen to live in the directory
    # above root_dir.
    sys.path.append(os.path.dirname(root_dir))
    import unisubs
    sys.path.pop()

def setup_patch_reverse():
    from localeurl import patch_reverse
    patch_reverse()

def setup_celery_loader():
    os.environ.setdefault("CELERY_LOADER",
                          "amaracelery.loaders.AmaraCeleryLoader")

def run_startup_modules():
    """For all django apps, try to run the startup module.  """

    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        try:
            __import__('%s.startup' % app)
        except ImportError:
            pass

def startup():
    """Set up the amara environment.  This should be called before running any
    other code.
    """
    setup_path()
    setup_patch_reverse()
    setup_celery_loader()
    run_startup_modules()
