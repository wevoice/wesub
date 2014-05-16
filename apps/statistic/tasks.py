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
from datetime import timedelta

from celery.schedules import crontab
from celery.task import task

from django.db.models import Count

from statistic import hitcounts
from statistic.models import (
    EmailShareStatistic, TweeterShareStatistic, FBShareStatistic,
)
from utils.metrics import Gauge

@task
def gauge_statistic():
    Gauge('statistic.shares.twitter').report(TweeterShareStatistic.objects.count())
    Gauge('statistic.shares.facebook').report(FBShareStatistic.objects.count())
    Gauge('statistic.shares.email').report(EmailShareStatistic.objects.count())
    total_key = st_sub_fetch_handler.total_key.get()
    if total_key:
        total_key = int(total_key)
    else:
        total_key = 0
    Gauge('statistic.views.subtitles').report(total_key)

def graphite_slugify(s):
    for c in ' -.,:':
        s = s.replace(c, '_')
    return s

@task
def gauge_statistic_languages():
    from apps.videos.models import SubtitleLanguage, ALL_LANGUAGES

    lang_names = dict(ALL_LANGUAGES)
    lang_names[u''] = 'Unknown'

    ls = SubtitleLanguage.objects.values('language').annotate(count=Count('language'))

    for l in ls:
        language_code = l['language']
        language_name = lang_names.get(language_code, 'Unknown')
        count = l['count']
        name = graphite_slugify(language_name)

        Gauge('statistic.languages.%s.count' % name).report(count)


@task
def migrate_hit_counts():
    hitcounts.migrate_all()
