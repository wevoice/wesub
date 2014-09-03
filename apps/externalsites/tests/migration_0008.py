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

"""Test the 0008 migration, which imports accountlinker data.

Note that this file does not follow the nose naming scheme, since we don't
want to pick it up automatically when running the unittests.  Since the
migration doesn't depend on other code, we only need to test it if we change
the migration itself.  In that case, we can run these tests specifying the
module name explicitly.
"""

from django.core.management.color import no_style
from django.db import connection
from django.db import models
from django.test import TestCase
from nose.tools import *
from south.migration import Migrations
from south import migration

from auth.models import CustomUser as User
from externalsites.models import YouTubeAccount, ExternalAccount
from teams.models import Team
from utils.factories import *
from videos.models import VideoFeed

# Define the ThirdPartyAccount model that was present in the accountlinker
# app.
#
# Note: these models don't exactly match the old definitions, for example some
# keys and constraints are missing.  But they should work enough to fill with
# data and test the migration.

class ThirdPartyAccount(models.Model):
    type = models.CharField(max_length=10)
    username  = models.CharField(max_length=255, db_index=True,
                                 null=False, blank=False)
    full_name = models.CharField(max_length=255, null=True, blank=True, default='')
    oauth_access_token = models.CharField(max_length=255, db_index=True,
                                          null=False, blank=False)
    oauth_refresh_token = models.CharField(max_length=255, db_index=True,
                                           null=False, blank=False)
    channel_id = models.CharField(max_length=255, default='', blank=True,
                                  db_index=True)

    class Meta:
        db_table = 'accountlinker_thirdpartyaccount'

# Define classes to handle the m2m fields that used to exist between
# ThirdPartyAccount and the CustomUser/Team models.
class UserThirdPartyAccountMap(models.Model):
    customuser = models.ForeignKey(User)
    thirdpartyaccount = models.ForeignKey(ThirdPartyAccount)

    class Meta:
        db_table = 'auth_customuser_third_party_accounts'

class TeamThirdPartyAccountMap(models.Model):
    team = models.ForeignKey(Team)
    thirdpartyaccount = models.ForeignKey(ThirdPartyAccount)

    class Meta:
        db_table = 'teams_team_third_party_accounts'

class AccountlinkerImportMigrationTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.create_old_tables()

    def tearDown(self):
        YouTubeAccount.objects.all().delete()
        TestCase.tearDown(self)

    def create_old_tables(self):
        self.create_table_for_model(ThirdPartyAccount)
        self.create_table_for_model(UserThirdPartyAccountMap)
        self.create_table_for_model(TeamThirdPartyAccountMap)

    def create_table_for_model(self, ModelClass):
        cursor = connection.cursor()
        output, references = connection.creation.sql_create_model(
            ModelClass, no_style(), [])
        for statement in output:
            cursor.execute(statement)
        self.addCleanup(self.drop_table, ModelClass._meta.db_table)

    def drop_table(self, table_name):
        cursor = connection.cursor()
        cursor.execute("DROP TABLE %s" % table_name)

    def run_migration(self):
        app = Migrations('externalsites')
        result = migration.migrate_app(app, '0007', fake=True)
        result = migration.migrate_app(app, '0008')

    def create_third_party_account(self, username, channel_id=None):
        if channel_id is None:
            channel_id = username + '-channel'
        return ThirdPartyAccount.objects.create(
            type='Y', # YOUTUBE
            username=username,
            full_name=username,
            channel_id=channel_id,
            oauth_access_token=channel_id + '-access-token',
            oauth_refresh_token=channel_id + '-refresh-token',
        )

    def link_account_to_user(self, account, user):
        UserThirdPartyAccountMap.objects.create(
            thirdpartyaccount=account, customuser=user)

    def link_account_to_team(self, account, team):
        TeamThirdPartyAccountMap.objects.create(
            thirdpartyaccount=account, team=team)

    def check_migration(self, old_account, owner):
        new_account = YouTubeAccount.objects.get(
            channel_id=old_account.channel_id)
        assert_equals(old_account.username, new_account.username)
        assert_equals(old_account.oauth_refresh_token,
                      new_account.oauth_refresh_token)
        assert_equals(old_account.channel_id, new_account.channel_id)
        if isinstance(owner, User):
            assert_equals(new_account.type, ExternalAccount.TYPE_USER)
        elif isinstance(owner, Team):
            assert_equals(new_account.type, ExternalAccount.TYPE_TEAM)
        else:
            raise AssertionError()
        assert_equals(new_account.owner_id, owner.id)

    def test_import_user_account(self):
        # test importing a user account
        user = UserFactory()
        old_account = self.create_third_party_account('My-Account')
        self.link_account_to_user(old_account, user)
        self.run_migration()

        assert_equals(YouTubeAccount.objects.count(), 1)
        self.check_migration(old_account, user)

    def test_import_team_account(self):
        # test importing a team account
        team = TeamFactory()
        old_account = self.create_third_party_account('My-Account')
        self.link_account_to_team(old_account, team)
        self.run_migration()

        assert_equals(YouTubeAccount.objects.count(), 1)
        self.check_migration(old_account, team)

    def test_import_feed(self):
        # test that we lookup the import feed and set that field
        user = UserFactory()
        old_account = self.create_third_party_account('My-Account')
        feed_url = ("https://gdata.youtube.com/"
                    "feeds/api/users/%s/uploads" % old_account.username)
        feed = VideoFeed.objects.create(url=feed_url, user=user)
        self.link_account_to_user(old_account, user)
        self.run_migration()
        new_account = YouTubeAccount.objects.get()

        assert_equals(new_account.import_feed, feed)

    def test_import_feed_owned_by_other_user(self):
        # If a VideoFeed exists with the correct URL, but it's not owned by
        # the user linked to the account.  In this case, we shouldn't
        # associate the feed with the YT account
        user = UserFactory()
        other_user = UserFactory()
        old_account = self.create_third_party_account('My-Account')
        feed_url = ("https://gdata.youtube.com/"
                    "feeds/api/users/%s/uploads" % old_account.username)
        feed = VideoFeed.objects.create(url=feed_url, user=other_user)
        self.link_account_to_user(old_account, user)
        self.run_migration()
        new_account = YouTubeAccount.objects.get()

        assert_equals(new_account.import_feed, None)

    def test_import_feed_with_team_account(self):
        # We shouldn't try to migrate the import feed for team accounts
        team = TeamFactory()
        old_account = self.create_third_party_account('My-Account')
        feed_url = ("https://gdata.youtube.com/"
                    "feeds/api/users/%s/uploads" % old_account.username)
        feed = VideoFeed.objects.create(url=feed_url, team=team)
        self.link_account_to_team(old_account, team)
        self.run_migration()
        new_account = YouTubeAccount.objects.get()

        assert_equals(new_account.import_feed, None)

    def test_duplicate_channel_id(self):
        # test multiple rows having the same channel_id, even though the
        # username column is unique.  We should keep the first row.
        user = UserFactory()
        user2 = UserFactory()
        old_account1 = self.create_third_party_account('YT-Account',
                                                       'channel')
        old_account2 = self.create_third_party_account('G+-Account',
                                                       'channel')

        self.link_account_to_user(old_account1, user)
        self.link_account_to_user(old_account2, user2)
        self.run_migration()

        new_account = YouTubeAccount.objects.get()
        assert_equals(new_account.username, old_account1.username)

    def test_multiple_users(self):
        # test multiple users being linked to a single account.  We should
        # only keep 1 account
        user = UserFactory()
        user2 = UserFactory()
        old_account = self.create_third_party_account('My-Account')
        self.link_account_to_user(old_account, user)
        self.link_account_to_user(old_account, user2)
        self.run_migration()

        new_account = YouTubeAccount.objects.get()
        assert_in(new_account.user.id, (user.id, user2.id))

    def test_multiple_teams(self):
        # test multiple users being linked to a single account.  One team
        # should own the account and the others should be linked to with the
        # sync_teams field

        teams = [TeamFactory() for i in xrange(5)]
        old_account = self.create_third_party_account('My-Account')
        for team in teams:
            self.link_account_to_team(old_account, team)
        self.run_migration()

        new_account = YouTubeAccount.objects.get()
        assert_in(new_account.team.id, [t.id for t in teams])
        assert_items_equal(new_account.sync_teams.all(),
                           [t for t in teams if t != new_account.team])

    def test_user_and_team_account(self):
        # test having both user and team accounts.  In this case we should
        # only keep the team accounts

        user = UserFactory()
        teams = [TeamFactory() for i in xrange(5)]
        old_account = self.create_third_party_account('My-Account')
        self.link_account_to_user(old_account, user)
        for team in teams:
            self.link_account_to_team(old_account, team)
        self.run_migration()

        new_account = YouTubeAccount.objects.get()
        assert_in(new_account.team.id, [t.id for t in teams])
        assert_items_equal(new_account.sync_teams.all(),
                           [t for t in teams if t != new_account.team])
