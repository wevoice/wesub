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

from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import connection
# hack to avoid exceptions to do circular imports
from haystack import site

from accountlinker.models import ThirdPartyAccount
from accountlinker import newyoutube

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--after-id', dest='after_id', default=None,
                    metavar='ID', help='Only lookup accounts later than ID'),
    )

    def handle(self, *args, **options):
        self.options = options
        self.find_account_ids_to_update()
        while self.account_ids_to_update:
            self.stdout.write('* %s accounts to update\n' %
                              len(self.account_ids_to_update))
            self.update_one_account()
            # commit our transaction to try to avoid any deadlocks
            connection.cursor().execute("COMMIT")
        self.stdout.write('lookup complete\n')
        self.stdout.write('to lookup new accounts use:\n')
        self.stdout.write('lookup_youtube_channelids --after-id %s\n' %
                          self.max_account_id)

    def find_account_ids_to_update(self):
        qs = ThirdPartyAccount.objects.filter(channel_id='')
        if self.options['after_id']:
            qs = qs.filter(id__gt=self.options['after_id'])
        self.account_ids_to_update = list(qs.values_list('id', flat=True))
        if len(self.account_ids_to_update) > 0:
            self.max_account_id = max(self.account_ids_to_update)
        else:
            self.max_account_id = 0

    def update_one_account(self):
        account_id = self.account_ids_to_update.pop()
        account = ThirdPartyAccount.objects.get(id=account_id)
        try:
            channel_id = self.lookup_channel_id(account)
        except StandardError, e:
            self.stdout.write('error with account %s (%s)\n' % (account, e))
            return
        account.channel_id = channel_id
        account.save()

    def lookup_channel_id(self, account):
        access_token = newyoutube.get_new_access_token(
            account.oauth_refresh_token)
        return newyoutube.get_user_info(access_token)[0]
