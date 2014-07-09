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

from django.core.management.base import BaseCommand
from django.db import connection

# hack to avoid exceptions to do circular imports
from haystack import site

from accountlinker.models import ThirdPartyAccount
from accountlinker import newyoutube

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.find_account_ids_to_update()
        while self.account_ids_to_update:
            print '* %s accounts to update' % len(self.account_ids_to_update)
            self.update_one_account()
            # commit our transaction to try to avoid any deadlocks
            connection.cursor().execute("COMMIT")

    def find_account_ids_to_update(self):
        self.account_ids_to_update = list(
            ThirdPartyAccount.objects
            .filter(channel_id='')
            .values_list('id', flat=True))

    def update_one_account(self):
        account_id = self.account_ids_to_update.pop()
        account = ThirdPartyAccount.objects.get(id=account_id)
        try:
            channel_id = self.lookup_channel_id(account)
        except StandardError, e:
            print 'error with account %s (%s)' % (account, e)
            return
        account.channel_id = channel_id
        account.save()

    def lookup_channel_id(self, account):
        access_token = newyoutube.get_new_access_token(
            account.oauth_refresh_token)
        return newyoutube.get_user_info(access_token)[0]
