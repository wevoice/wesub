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

import os
import sys

import startup

if __name__ == "__main__":
    # handle the --settings and --python-path options so that django.conf is
    # setup before we import localeurl.
    from django.core.management.base import (handle_default_options,
                                             BaseCommand)
    from django.core.management import LaxOptionParser, get_version
    parser = LaxOptionParser(usage="%prog subcommand [options] [args]",
                             version=get_version(),
                             option_list=BaseCommand.option_list)
    options, args = parser.parse_args(sys.argv)
    handle_default_options(options)

    startup.startup()

    # start the management command
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
