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

import subprocess

from django.conf import settings

def static_url():
    """Get the base URL for static media

    This is a function rather than just a value in the settings because it's a
    bit complicated to calculate.

    The simple case is when STATIC_MEDIA_USES_S3 is False.  Then we simple
    return the "/media/".  If STATIC_MEDIA_USES_S3 is True, then we return an
    URL pointing to where we upload media to on S3, which includes the git
    checksum as a way to keep the URLs unique between different deployments.
    """
    if not settings.STATIC_MEDIA_USES_S3:
        return "/media/"

    raise NotImplemented()

def run_command(commandline, stdin=None):
    """Run a command and return the results.

    An exception will be raised if the command doesn't return 0 or prints to
    stderr.
    """
    p = subprocess.Popen(commandline, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(stdin)
    if stderr:
        raise ValueError("Got error from %s: %s" % (commandline, stderr))
    elif p.returncode != 0:
        raise ValueError("Got error code from %s: %s" % (commandline,
                                                         p.returncode))
    else:
        return stdout
