#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
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

"""Long-running data migration script for the Data Model Refactor."""

#      __     __------
#   __/o `\ ,~   _~~  . .. pb. ..
#  ~ -.   ,'   _~-----
#      `\     ~~~--_'__
#        `~-==-~~~~~---'
#
# The [Arctic Tern] is strongly migratory, seeing two summers each year as it
# migrates from its northern breeding grounds along a winding route to the
# oceans around Antarctica and back, a round trip of about 70,900 km (c. 44,300
# miles) each year.  This is by far the longest regular migration by any known
# animal.
#
# https://en.wikipedia.org/wiki/Arctic_Tern

import datetime
import csv as csv_module
import os, sys
import warnings
from optparse import OptionGroup, OptionParser


csv = csv_module.writer(sys.stdout)
single = False


# Output
def log(model, event_type, original_pk, new_pk):
    csv.writerow([
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        model,
        event_type,
        str(original_pk),
        str(new_pk),
    ])

def die(msg):
    sys.stderr.write('ERROR: %s\n' % msg)
    sys.exit(1)


# Utilities
def get_unsynced_subtitle_language():
    """Return a SubtitleLanguage that needs to be synced.

    SubtitleLanguages will be returned in a random order.  Forcing the syncing
    code to deal with this will make it robust against different data in
    dev/staging/prod.

    """
    from apps.videos.models import SubtitleLanguage

    try:
        return SubtitleLanguage.objects.filter(needs_sync=True).order_by('?')[0]
    except SubtitleLanguage.DoesNotExist:
        return None


# Commands
def header():
    print 'Time,Model,Action,Original PK,New PK'

def count():
    from apps.videos.models import SubtitleLanguage, SubtitleVersion

    slo = SubtitleLanguage.objects
    total = slo.count()
    unsynced = slo.filter(new_subtitle_language=None, needs_sync=True).count()
    broken   = slo.filter(new_subtitle_language=None, needs_sync=False).count()
    outdated = slo.filter(new_subtitle_language__isnull=False, needs_sync=True).count()
    done     = slo.filter(new_subtitle_language__isnull=False, needs_sync=False).count()
    print "SubtitleLanguage"
    print "-" * 40
    print "%10d total" % total
    print "%10d never synced" % unsynced
    print "%10d synced but out of date" % outdated
    print "%10d synced and up to date" % done
    print "%10d broken" % broken
    print

    svo = SubtitleVersion.objects
    total = svo.count()
    unsynced = svo.filter(new_subtitle_version=None, needs_sync=True).count()
    broken   = svo.filter(new_subtitle_version=None, needs_sync=False).count()
    outdated = svo.filter(new_subtitle_version__isnull=False, needs_sync=True).count()
    done     = svo.filter(new_subtitle_version__isnull=False, needs_sync=False).count()
    print "SubtitleVersion"
    print "-" * 40
    print "%10d total" % total
    print "%10d never synced" % unsynced
    print "%10d synced but out of date" % outdated
    print "%10d synced and up to date" % done
    print "%10d broken" % broken
    print

def _sync_language():
    """Try to sync one SubtitleLanguage.
    
    Returns True if a language was synced, False if there were no more left.

    """
    sl = get_unsynced_subtitle_language()

    if not sl:
        return False

    log('SubtitleLanguage', 'create', sl.pk, '0')

    return True

def sync_languages():
    result = _sync_language()
    if not single:
        while result:
            result = _sync_language()


# Setup
def setup_path():
    """Set up the Python path with the appropriate magic directories."""

    sys.path.insert(0, './apps')
    sys.path.insert(0, './libs')
    sys.path.insert(0, '..') # Don't ask.
    sys.path.insert(0, '.')

def setup_settings(options):
    """Set up the Django settings module boilerplate."""

    if not options.settings:
        die('you must specify a Django settings module!')

    os.environ['DJANGO_SETTINGS_MODULE'] = options.settings

    from django.conf import settings
    assert settings


# Main
def build_option_parser():
    p = OptionParser('usage: %prog [options]')

    p.add_option('-s', '--settings', default=None,
                 help='django settings module to use',
                 metavar='MODULE_NAME')

    p.add_option('-o', '--one', default=False,
                 dest='single', action='store_true',
                 help='only sync one object instead of all of them')

    g = OptionGroup(p, "Commands")

    g.add_option('-C', '--count', dest='command', default=None,
                 action='store_const', const='count',
                 help='output the number of unsynced items remaining')

    g.add_option('-L', '--languages', dest='command',
                 action='store_const', const='languages',
                 help='sync SubtitleLanguage objects')

    g.add_option('-H', '--header', dest='command',
                 action='store_const', const='header',
                 help='output the header for the CSV output')

    p.add_option_group(g)

    return p

def main():
    global single

    parser = build_option_parser()
    (options, args) = parser.parse_args()

    if not options.command:
        die('no command given!')

    single = options.single

    setup_path()
    setup_settings(options)

    if options.command == 'count':
        count()
    elif options.command == 'languages':
        sync_languages()
    elif options.command == 'header':
        header()

if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=UserWarning, message=".*was already imported from.*")
        warnings.filterwarnings("ignore", message=".*integer argument expected, got float.*")

        main()
