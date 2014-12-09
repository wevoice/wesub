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

from statistic.models import (
    EmailShareStatistic, TweeterShareStatistic, FBShareStatistic,
)
from utils.metrics import Gauge

@task
def gauge_statistic():
    Gauge('statistic.shares.twitter').report(TweeterShareStatistic.objects.count())
    Gauge('statistic.shares.facebook').report(FBShareStatistic.objects.count())
    Gauge('statistic.shares.email').report(EmailShareStatistic.objects.count())

def graphite_slugify(s):
    for c in ' -.,:':
        s = s.replace(c, '_')
    return s
