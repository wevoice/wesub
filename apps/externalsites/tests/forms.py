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
import mock
from urllib import quote_plus

from externalsites.forms import BrightcoveAccountForm, AccountFormset
from externalsites.models import BrightcoveAccount
from videos.models import VideoFeed
from utils import test_utils
from utils import test_factories

class TestAccountFormset(TestCase):
    def setUp(self):
        self.team = test_factories.create_team()
        self.setup_forms()

    def setup_forms(self):
        self.foo_form_class = self.make_mock_form_class()
        self.bar_form_class = self.make_mock_form_class()
        self.foo_form = self.foo_form_class.return_value
        self.bar_form = self.bar_form_class.return_value

    def make_mock_form_class(self):
        form = mock.Mock()
        form.is_valid.return_value = True
        form_class = mock.Mock()
        form_class.return_value = form
        form_class.get_account.return_value = None
        return form_class

    def make_formset(self, post_data=None):
        class TestAccountFormset(AccountFormset):
            form_classes = {
                'foo': self.foo_form_class,
                'bar': self.bar_form_class,
            }
        return TestAccountFormset(self.team, post_data)

    def test_forms(self):
        # We should create a form object for each account form.  Also we
        # should create a form to enable/disable each account.
        formset = self.make_formset()
        self.assertEquals(set(formset.keys()),
                          set(['foo', 'bar', 'enabled_accounts']))
        self.foo_form_class.assert_called_with(self.team, None, instance=None,
                                               prefix='foo')
        self.bar_form_class.assert_called_with(self.team, None, instance=None,
                                               prefix='bar')

    def test_forms_and_fields_with_post_data(self):
        data = {
            'enabled_accounts-foo': '1',
            'foo': 'bar',
        }
        formset = self.make_formset(data)
        self.assertEquals(set(formset.keys()),
                          set(['foo', 'bar', 'enabled_accounts']))
        # foo is enabled, so it should get data
        self.foo_form_class.assert_called_with(self.team, data, instance=None,
                                               prefix='foo')
        # bar is not enabled, so it should be unbound
        self.bar_form_class.assert_called_with(self.team, None, instance=None,
                                               prefix='bar')

    def test_forms_and_fields_with_existing_accounts(self):
        # AccountFormset should call get_account() for each form class.  If it
        # returns a value, then we should pass it as the instance argument to
        # the form constructor
        foo_account = mock.Mock()
        self.foo_form_class.get_account.return_value = foo_account
        formset = self.make_formset()
        self.foo_form_class.get_account.assert_called_with(self.team)
        self.foo_form_class.assert_called_with(self.team, None,
                                               instance=foo_account,
                                               prefix='foo')

    def test_accounts_enabled_form(self):
        foo_account = mock.Mock()
        self.foo_form_class.get_account.return_value = mock.Mock()
        formset = self.make_formset()

        self.assertEquals(set(formset['enabled_accounts'].fields.keys()),
                          set(['foo', 'bar']))
        foo_enabled_field = formset['enabled_accounts'].fields['foo']
        bar_enabled_field = formset['enabled_accounts'].fields['bar']

        # we should allow users to check or not check the checkboxes
        self.assertEquals(foo_enabled_field.required, False)
        self.assertEquals(bar_enabled_field.required, False)
        # the label should always be "Enabled"
        self.assertEquals(foo_enabled_field.label, "Enabled")
        self.assertEquals(bar_enabled_field.label, "Enabled")
        # we should set the initial value to True if the account is created
        self.assertEquals(foo_enabled_field.initial, True)
        self.assertEquals(bar_enabled_field.initial, False)

    def test_is_valid(self):
        # is valid should return true if all forms either valid or not enabled
        data = {
            'enabled_accounts-foo': '1',
            'enabled_accounts-bar': '1',
            'foo': 'bar',
        }
        formset = self.make_formset(data)
        self.assertEquals(formset.is_valid(), True)
        self.foo_form.is_valid.assert_called_with()
        self.bar_form.is_valid.assert_called_with()

        self.foo_form.is_valid.return_value = False
        self.assertEquals(self.make_formset(data).is_valid(), False)

        # if the foo account is not enabled, we shouldn't call is_valid() for
        # it
        del data['enabled_accounts-foo']
        self.foo_form.is_valid.reset_mock()
        self.foo_form.is_valid.return_value = False
        self.bar_form.is_valid.reset_mock()
        self.assertEquals(self.make_formset(data).is_valid(), True)
        self.assertEquals(self.foo_form.is_valid.call_count, 0)
        self.assertEquals(self.bar_form.is_valid.call_count, 1)

    def test_is_valid_no_post_data(self):
        # check a corner case, calling is_valid() without post data
        formset = self.make_formset()
        self.assertEquals(formset.is_valid(), False)

    def test_save(self):
        # save should call save on all account forms that are enabled
        data = {
            'enabled_accounts-foo': '1',
            'enabled_accounts-bar': '1',
        }
        self.make_formset(data).save()
        self.foo_form.save.assert_called_with()
        self.bar_form.save.assert_called_with()

    def test_delete_accounts(self):
        # If enabled is not set, then we should delete accounts
        data = {
            'enabled_accounts-foo': '1',
        }
        self.make_formset(data).save()
        self.foo_form.save.assert_called_with()
        self.assertEquals(self.foo_form.delete_account.call_count, 0)
        self.assertEquals(self.bar_form.save.call_count, 0)
        self.bar_form.delete_account.assert_called_with()

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
        })
        self.assert_(form.is_valid(), form.errors.as_text())
        account = form.save()
        self.assertEquals(account.publisher_id, self.publisher_id)
        self.assertEquals(account.write_token, self.write_token)
        self.assertEquals(account.team, self.team)
        self.assertEquals(account.import_feed, None)

    def feed_url(self, *tags):
        if tags:
            return ('http://link.brightcove.com'
                    '/services/mrss/player%s/%s/tags/%s') % (
                        self.player_id, self.publisher_id,
                        '/'.join(quote_plus(t) for t in tags))
        else:
            return ('http://link.brightcove.com'
                    '/services/mrss/player%s/%s/new') % (
                        self.player_id, self.publisher_id,
                    )

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
        self.assertEquals(account.import_feed.url, self.feed_url())
        test_utils.import_videos_from_feed.delay.assert_called_with(
            account.import_feed.id)

    def test_feed_with_tags(self):
        # feed tags should be a comma separated list of tags.  If there are
        # spaces inside the tag we should preserve them
        form = BrightcoveAccountForm(self.team, {
            'publisher_id': self.publisher_id,
            'write_token': self.write_token,
            'feed_enabled': '1',
            'player_id': self.player_id,
            'feed_type': BrightcoveAccountForm.FEED_WITH_TAGS,
            'feed_tags': 'cats, cute pets,dogs  ',
        })
        self.assert_(form.is_valid(), form.errors.as_text())
        account = form.save()
        self.assertNotEquals(account.import_feed, None)
        self.assertEquals(account.import_feed.url,
                          self.feed_url('cats', 'cute pets', 'dogs'))
        test_utils.import_videos_from_feed.delay.assert_called_with(
            account.import_feed.id)

    def test_feed_exists(self):
        # test that we set initial values for the feed inputs for accounts
        # with feeds created.

        # create an account with an import feed
        account = BrightcoveAccount.objects.create(
            team=self.team, publisher_id=self.publisher_id,
            write_token=self.write_token)
        account.make_feed(self.player_id)
        form = BrightcoveAccountForm(self.team, instance=account)
        self.assertEquals(form.fields['player_id'].initial, self.player_id)
        self.assertEquals(form.fields['feed_type'].initial,
                          BrightcoveAccountForm.FEED_ALL_NEW)
        self.assertEquals(form.fields['feed_tags'].initial, '')

        # try again when using tags
        account.make_feed(self.player_id, ['cats', 'dogs'])
        form = BrightcoveAccountForm(self.team, instance=account)
        self.assertEquals(form.fields['player_id'].initial, self.player_id)
        self.assertEquals(form.fields['feed_type'].initial,
                          BrightcoveAccountForm.FEED_WITH_TAGS)
        self.assertEquals(form.fields['feed_tags'].initial, 'cats, dogs')

    def test_change_feed(self):
        # test saving a form when we already have an import feed

        # create an account with an import feed
        account = BrightcoveAccount.objects.create(
            team=self.team, publisher_id=self.publisher_id,
            write_token=self.write_token)
        account.make_feed(self.player_id, ['cats'])
        first_feed = account.import_feed
        # test saving a form with different feed tags.  We should update the
        # feed URL, but not make a new feed object
        data = {
            'publisher_id': self.publisher_id,
            'write_token': self.write_token,
            'feed_enabled': '1',
            'player_id': self.player_id,
            'feed_type': BrightcoveAccountForm.FEED_WITH_TAGS,
            'feed_tags': 'cats, dogs',
        }
        form = BrightcoveAccountForm(self.team, data, instance=account)
        account = form.save()
        self.assertEquals(account.import_feed.id, first_feed.id)
        test_utils.import_videos_from_feed.delay.assert_called_with(
            account.import_feed.id)
        # test saving the form with the same tags.  We should import videos
        # for this save
        form = BrightcoveAccountForm(self.team, data, instance=account)
        account = form.save()
        self.assertEquals(account.import_feed.id, first_feed.id)
        self.assertEquals(test_utils.import_videos_from_feed.delay.call_count,
                          1)

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
        }, instance=account)
        account = form.save()
        self.assertEquals(account.import_feed, None)
        self.assert_(not VideoFeed.objects.filter(id=old_import_feed.id))

