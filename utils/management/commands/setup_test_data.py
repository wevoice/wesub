# Amara, universalsubtitles.org
# 
# Copyright (C) 2015 Participatory Culture Foundation
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

from django.contrib.auth.models import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.dispatch import Signal

from auth.models import CustomUser as User
import optionalapps

signal = Signal()

def setup_admin():
    User.objects.create(username='admin', password=make_password('admin'),
                        is_staff=True, is_superuser=True,
                        email='admin@example.com', valid_email=True)

class Command(BaseCommand):
    help = u'Create data for testing preview/dev builds'

    def handle(self, *args, **kwargs):
        with transaction.commit_on_success():
            setup_admin()
            signal.send(sender=None)
