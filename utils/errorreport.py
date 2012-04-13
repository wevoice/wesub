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

import datetime
from django.contrib.sites.models import Site
from sentry.models import GroupedMessage


def _errors_seen_on(date, last_seen=True):
    filters = {}
    if last_seen:
        filter_name = 'last_seen'
    else:
        filter_name = 'first_seen'
    for lookup in ("month", 'day', 'year'):
        filters["%s__%s" % (filter_name, lookup )] = getattr(date, lookup)
    return GroupedMessage.objects.filter(**filters)

def _error_report_data(date=None):
    data = {}
    date = date or datetime.datetime.now()
    errors = _errors_seen_on(date)
    new_errors = _errors_seen_on(date, last_seen=False)
    new_errors_data = []
    last_week = date - datetime.timedelta(days=7)
    for error in new_errors:
        new_errors_data.append ( {
            'message': error.message,
            'pk': error.pk,
            "total_count": error.message_set.count(),
            "today_count": error.message_set.filter(
                datetime__day=date.day,
                datetime__month=date.month,
                datetime__year=date.year,
            ).count(),
            "last_week_count":error.message_set.filter(
                datetime__gte=last_week,
                datetime__lte=date,

            ).count()
        })
    data['new_errors'] = new_errors_data
    data['errors_count'] = errors.count()
    data['new_errors_count'] = new_errors.count()
    data['base_url'] = Site.objects.get_current().domain
    return data
