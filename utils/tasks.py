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

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from celery.decorators import periodic_task
from celery.schedules import crontab
from celery.task import task

from utils import send_templated_email

from utils import errorreport

@task
def send_templated_email_async(to, subject, body_template, body_dict,
                               from_email=None, ct="html", fail_silently=False,
                               check_user_preference=True):
    return send_templated_email(
        to,subject, body_template, body_dict, from_email=None, ct="html",
        fail_silently=False, check_user_preference=check_user_preference)


@periodic_task(run_every=crontab(minute=0, hour=1))
def send_error_report(date=None):
    date = date or datetime.datetime.now() - datetime.timedelta(days=1)
    recipients = getattr(settings,'SEND_ERROR_REPORT_TO', None)
    if not recipients:
        return 
    data = errorreport._error_report_data(date)
    message = render_to_string("internal/error-report.txt", data)
    subject = date.strftime("Errors for Amara for %Y/%M/%d")
    send_mail(subject, message, "unisubs error bot", recipients)
