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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from __future__ import absolute_import

from django.test import TestCase

from externalsites.forms import BrightcoveAccountForm
from externalsites.models import BrightcoveAccount
from videos.models import VideoFeed
from utils import test_factories

class BrightcoveFormTest(TestCase):
    def setUp(self):
        self.team = test_factories.create_team()
        self.publisher_id = '123'
        self.player_id = '456'
        self.write_token = '789'

    def test_no_feed(self):
        form = BrightcoveAccountForm(self.team, {
            'publisher_id': self.publisher_id,
            'write_token': self.write_token,
            'player_id': '',
            'feed_type': BrightcoveAccountForm.FEED_ALL_NEW,
            'feed_tags': '',
        })
        self.assert_(form.is_valid(), form.errors.as_text())
        account = form.save()
        self.assertEquals(account.publisher_id, self.publisher_id)
        self.assertEquals(account.write_token, self.write_token)
        self.assertEquals(account.team, self.team)
        self.assertEquals(account.import_feed, None)

    def feed_url(self, *tags):
         return ('http://link.brightcove.com'
                 '/services/mrss/player%s/%s/%s') % (
                     self.player_id, self.publisher_id,
                     '/'.join(tags))

    def test_feed_all_new(self):
        form = BrightcoveAccountForm(self.team, {
            'publisher_id': self.publisher_id,
            'write_token': self.write_token,
            'feed_enabled': '1',
            'player_id': self.player_id,
            'feed_type': BrightcoveAccountForm.FEED_ALL_NEW,
            'feed_tags': '',
        })
        self.assert_(form.is_valid(), form.errors.as_text())
        account = form.save()
        self.assertNotEquals(account.import_feed, None)
        self.assertEquals(account.import_feed.url, self.feed_url('new'))

    def test_feed_with_tags(self):
        form = BrightcoveAccountForm(self.team, {
            'publisher_id': self.publisher_id,
            'write_token': self.write_token,
            'feed_enabled': '1',
            'player_id': self.player_id,
            'feed_type': BrightcoveAccountForm.FEED_WITH_TAGS,
            'feed_tags': 'cats dogs  ',
        })
        self.assert_(form.is_valid(), form.errors.as_text())
        account = form.save()
        self.assertNotEquals(account.import_feed, None)
        self.assertEquals(account.import_feed.url,
                          self.feed_url('cats', 'dogs'))

    def test_player_id_required_with_feed(self):
        form = BrightcoveAccountForm(self.team, {
            'publisher_id': self.publisher_id,
            'write_token': self.write_token,
            'feed_enabled': '1',
            'player_id': '',
            'feed_type': BrightcoveAccountForm.FEED_ALL_NEW,
            'feed_tags': '',
        })
        self.assertEquals(form.is_valid(), False)
        self.assertEquals(form.errors.keys(), ['player_id'])

    def test_tags_required_with_feed_with_tags(self):
        form = BrightcoveAccountForm(self.team, {
            'publisher_id': self.publisher_id,
            'write_token': self.write_token,
            'feed_enabled': '1',
            'player_id': self.player_id,
            'feed_type': BrightcoveAccountForm.FEED_WITH_TAGS,
            'feed_tags': '',
        })
        self.assertEquals(form.is_valid(), False)
        self.assertEquals(form.errors.keys(), ['feed_tags'])

    def test_remove_feed(self):
        account = BrightcoveAccount.objects.create(
            team=self.team, publisher_id=self.publisher_id,
            write_token=self.write_token)
        account.make_feed(self.player_id)
        old_import_feed = account.import_feed

        form = BrightcoveAccountForm(self.team, {
            'publisher_id': self.publisher_id,
            'write_token': self.write_token,
            'player_id': self.player_id,
            'feed_type': BrightcoveAccountForm.FEED_ALL_NEW,
            'feed_tags': '',
        })
        account = form.save()
        self.assertEquals(account.import_feed, None)
        self.assert_(not VideoFeed.objects.filter(id=old_import_feed.id))

