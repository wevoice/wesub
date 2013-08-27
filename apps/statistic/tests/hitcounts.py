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

import calendar
from datetime import datetime, date, timedelta

from django.test import TestCase
import mock

from utils import test_factories
from utils import test_utils
from statistic import hitcounts
from statistic.models import LastHitCountMigration
from subtitles import pipeline
from videos.models import Video

class HitCountManagerTestBase(TestCase):
    """Base class for VideoHitCountManagerTest, SubtitleViewCountManagerTest.
    """
    # subclasses need to override the following:
    __test__ = False

    def make_hit_count_manager(self):
        raise NotImplementedError()

    def make_three_objects(self):
        """Make objects to test hit counts on.

        Why three objects?  There's no real reason, it just seemed like a good
        number to test with
        """
        raise NotImplementedError()

    last_hit_count_migration_type = None

    # start of the test code
    def check_hits(self, obj, hit_datetimes):
        hits = self.count_manager.hit_model.objects.filter(**{
            self.count_manager.obj_field_name: obj
        }).order_by('datetime')
        self.assertEquals([h.datetime for h in hits], hit_datetimes)

    def check_per_day_summaries(self, obj, dates_and_counts):
        per_day_qs = self.count_manager.per_day_model.objects.filter(**{
            self.count_manager.obj_field_name: obj
        }).order_by('date')
        self.assertEquals([(o.date, o.count) for o in per_day_qs],
                          dates_and_counts)

    def check_per_month_summaries(self, obj, dates_and_counts):
        per_day_qs = self.count_manager.per_month_model.objects.filter(**{
            self.count_manager.obj_field_name: obj
        }).order_by('date')
        self.assertEquals([(o.date, o.count) for o in per_day_qs],
                          dates_and_counts)

    def check_get_counts(self, obj, when, today, week, month, year):
        self.mock_now.return_value = when
        counts = self.count_manager.get_counts(obj)
        self.assertEquals(counts['today'], today)
        self.assertEquals(counts['week'], week)
        self.assertEquals(counts['month'], month)
        self.assertEquals(counts['year'], year)

    def get_last_hit_count_migration(self):
        return LastHitCountMigration.objects.get(
            type=self.last_hit_count_migration_type)

    @test_utils.patch_for_test('statistic.hitcounts.now')
    def setUp(self, mock_now):
        self.mock_now = mock_now
        self.count_manager = self.make_hit_count_manager()

    def add_hit(self, obj, when):
        """Add a hit """
        self.mock_now.return_value = when
        self.count_manager.add_hit(obj)

    def migrate(self, when):
        self.mock_now.return_value = when
        self.count_manager.migrate()

    def add_per_day_count(self, obj, date, count):
        data = {
            self.count_manager.obj_field_name: obj,
            'date': date,
            'count': count
        }
        self.count_manager.per_day_model.objects.create(**data)

    def add_per_month_count(self, obj, date, count):
        data = {
            self.count_manager.obj_field_name: obj,
            'date': date,
            'count': count
        }
        self.count_manager.per_month_model.objects.create(**data)

    def test_hit_removal_date(self):
        # test when we delete hits.  This is always 24 hours before the
        # current time
        migrater = self.count_manager.migrater
        self.assertEquals(
            migrater.hit_removal_date(datetime(2013, 1, 2, 5, 30)),
            datetime(2013, 1, 1, 5, 30))

    def test_per_day_removal_date(self):
        # test when we delete per day counts.  This always 30 days before the
        # start of today, which is enough to ensure that both:
        # - we can calculate the last 30 days of hits
        # - we can calculate the per-month counts at the first of next month.
        migrater = self.count_manager.migrater
        self.assertEquals(
            migrater.per_day_removal_date(datetime(2013, 3, 1, 5, 30)),
            date(2013, 1, 30))
        self.assertEquals(
            migrater.per_day_removal_date(datetime(2013, 3, 31, 5, 30)),
            date(2013, 3, 1))

    def test_add_hit(self):
        # Test inserting rows initially
        obj1, obj2, obj3 = self.make_three_objects()
        self.add_hit(obj1, datetime(2013, 1, 1))
        self.add_hit(obj1, datetime(2013, 1, 2))
        # test hits coming at the exact same time
        self.add_hit(obj2, datetime(2013, 1, 1))
        self.add_hit(obj2, datetime(2013, 1, 1))
        self.check_hits(obj1, [datetime(2013, 1, 1), datetime(2013, 1, 2)])
        self.check_hits(obj2, [datetime(2013, 1, 1), datetime(2013, 1, 1)])
        self.check_hits(obj3, [])

    def test_migrate_hits_to_days(self):
        obj1, obj2, obj3 = self.make_three_objects()
        self.add_hit(obj1, datetime(2013, 1, 1, 0))
        self.add_hit(obj1, datetime(2013, 1, 1, 1))
        self.add_hit(obj1, datetime(2013, 1, 1, 2))
        self.add_hit(obj1, datetime(2013, 1, 2, 0))
        self.add_hit(obj1, datetime(2013, 1, 2, 1))
        self.add_hit(obj2, datetime(2013, 1, 1, 0))
        self.add_hit(obj2, datetime(2013, 1, 1, 1))
        self.add_hit(obj2, datetime(2013, 1, 3, 12))
        self.add_hit(obj2, datetime(2013, 1, 4, 0))

        self.migrate(datetime(2013, 1, 4, 0, 5))
        self.check_per_day_summaries(obj1, [
            (date(2013, 1, 1), 3),
            (date(2013, 1, 2), 2),
        ])
        self.check_per_day_summaries(obj2, [
            (date(2013, 1, 1), 2),
            (date(2013, 1, 3), 1),
        ])
        self.check_per_day_summaries(obj3, [])
        # check that we delete hits older than 24 hours
        self.check_hits(obj1, [])
        self.check_hits(obj2, [
            datetime(2013, 1, 3, 12),
            datetime(2013, 1, 4, 0),
        ])
        self.check_hits(obj3, [])
        # check that we update LastHitCountMigration
        self.assertEquals(self.get_last_hit_count_migration().date,
                          date(2013, 1, 4))

    def test_migrate_day_to_month(self):
        # Test migrating day summary rows to the month summary
        obj1, obj2, obj3 = self.make_three_objects()
        self.add_per_day_count(obj1, date(2013, 1, 21), 10)
        self.add_per_day_count(obj1, date(2013, 2, 1), 10)
        self.add_per_day_count(obj1, date(2013, 2, 21), 10)
        self.add_per_day_count(obj1, date(2013, 3, 1), 10)

        self.add_per_day_count(obj2, date(2013, 1, 31), 10)
        self.add_per_day_count(obj2, date(2013, 2, 1), 10)
        self.add_per_day_count(obj2, date(2013, 2, 21), 10)
        self.add_per_day_count(obj2, date(2013, 2, 28), 10)

        self.migrate(datetime(2013, 3, 2, 0, 5))

        self.check_per_month_summaries(obj1, [
            (date(2013, 1, 1), 10),
            (date(2013, 2, 1), 20),
        ])
        self.check_per_month_summaries(obj2, [
            (date(2013, 1, 1), 10),
            (date(2013, 2, 1), 30),
        ])
        self.check_per_month_summaries(obj3, [])
        # check that we delete per day summaries older than 30 days
        self.check_per_day_summaries(obj1, [
            (date(2013, 2, 1), 10),
            (date(2013, 2, 21), 10),
            (date(2013, 3, 1), 10),
        ])
        self.check_per_day_summaries(obj2, [
            (date(2013, 1, 31), 10),
            (date(2013, 2, 1), 10),
            (date(2013, 2, 21), 10),
            (date(2013, 2, 28), 10),
        ])

        # check that we update LastHitCountMigration
        self.assertEquals(self.get_last_hit_count_migration().date,
                          date(2013, 3, 2))

    def test_long_term_migration(self):
        # test migrating hit counts every day for a year
        def days_in_month(date):
            return calendar.monthrange(date.year, date.month)[1]
        def even(number):
            return (number % 2) == 0

        obj1, obj2, obj3 = self.make_three_objects()
        start_date = datetime(2013, 1, 1)
        for i in range(365):
            today = start_date + timedelta(days=i)
            # obj 1 gets 10 hits a day
            for j in range(10):
                self.add_hit(obj1, today + timedelta(hours=j))
            # obj 2 gets 1 hit every other day
            if even(today.day):
                self.add_hit(obj2, today + timedelta(hours=12, minutes=30))
            # obj 3 gets 1 hit a day every other month
            if even(today.month):
                self.add_hit(obj3, today + timedelta(hours=6, minutes=45))
            # migrate the hits for today
            self.migrate(today + timedelta(days=1))

        last_30_days = [date(2013, 12, i) for i in range(2, 32)]
        last_12_months = [date(2013, i, 1) for i in range(1, 13)]

        self.check_hits(obj1, [datetime(2013, 12, 31, i) for i in range(10)])
        self.check_per_day_summaries(obj1, [(d, 10) for d in last_30_days])
        self.check_per_month_summaries(obj1, [
            (m, days_in_month(m) * 10) for m in last_12_months
        ])

        self.check_hits(obj2, [])
        self.check_per_day_summaries(obj2, [
            (d, 1) for d in last_30_days if even(d.day)
        ])
        self.check_per_month_summaries(obj2, [
            (m, days_in_month(m) // 2) for m in last_12_months
        ])

        self.check_hits(obj3, [
            datetime(2013, 12, 31, 6, 45),
        ])
        self.check_per_day_summaries(obj3, [
            (d, 1) for d in last_30_days
        ])
        self.check_per_month_summaries(obj3, [
            (m, days_in_month(m)) for m in last_12_months if even(m.month)
        ])

    def test_migrate_acquires_lock(self):
        # Test that we aquire a lock before doing the migration
        obj1, obj2, obj3 = self.make_three_objects()
        self.add_hit(obj1, datetime(2013, 1, 1, 0))
        migrater = self.count_manager.migrater
        lock_name = 'hitcount-migration-' + self.last_hit_count_migration_type
        def check_transaction(*args, **kwargs):
            self.assert_(lock_name in test_utils.current_locks)
        with mock.patch.object(migrater, '_migrate') as mock_migrate:
            mock_migrate.side_effect = check_transaction
            self.migrate(datetime(2013, 1, 2))

    def test_counts(self):
        # Test calculating the counts
        obj1, obj2, obj3 = self.make_three_objects()

        now = datetime(2013, 2, 2, 4, 30)

        self.add_hit(obj1, datetime(2013, 2, 2))
        self.add_hit(obj1, datetime(2013, 2, 2))
        self.add_hit(obj1, datetime(2013, 2, 2, 1, 30))
        self.add_per_day_count(obj1, date(2013, 1, 21), 10)
        self.add_per_day_count(obj1, date(2013, 1, 31), 10)
        self.add_per_month_count(obj1, date(2013, 1, 1), 20)
        self.add_per_month_count(obj1, date(2012, 8, 1), 100)

        self.add_hit(obj2, datetime(2013, 2, 2, 3, 30))
        self.add_hit(obj2, datetime(2013, 2, 1, 12, 30))
        self.add_per_day_count(obj2, date(2013, 2, 1), 10)
        self.add_per_month_count(obj2, date(2012, 2, 1), 30)

        # add counts that shouldn't be counted because they are too old
        self.add_hit(obj3, datetime(2013, 2, 1, 3, 30))
        self.add_per_day_count(obj3, date(2012, 12, 31), 100)
        self.add_per_month_count(obj3, date(2012, 1, 1), 100)

        LastHitCountMigration.objects.create(
            type=self.last_hit_count_migration_type,
            date=now.date())

        self.check_get_counts(obj1, now, 3, 10, 20, 120)
        self.check_get_counts(obj2, now, 2, 10, 10, 30)
        self.check_get_counts(obj3, now, 0, 0, 0, 0)

class VideoHitCountManagerTest(HitCountManagerTestBase):
    __test__ = True

    def make_hit_count_manager(self):
        return hitcounts.VideoHitCountManager()

    def make_three_objects(self):
        return [test_factories.create_video() for i in range(3)]

    last_hit_count_migration_type = 'V'

    # tests specific to videos
    def test_migrate_updates_view_count(self):
        video = test_factories.create_video()
        video2 = test_factories.create_video()
        self.add_hit(video, datetime(2013, 1, 1, 0))
        self.add_hit(video, datetime(2013, 1, 1, 1))
        self.add_hit(video, datetime(2013, 1, 1, 2))
        self.add_hit(video2, datetime(2013, 1, 1, 3))
        self.add_hit(video2, datetime(2013, 1, 1, 4))
        self.migrate(datetime(2013, 1, 2, 0, 5))
        self.assertEquals(Video.objects.get(id=video.id).view_count, 3)
        self.assertEquals(Video.objects.get(id=video2.id).view_count, 2)

        self.add_hit(video, datetime(2013, 1, 2, 0))
        self.add_hit(video, datetime(2013, 1, 2, 1))
        self.add_hit(video, datetime(2013, 1, 2, 2))
        self.add_hit(video, datetime(2013, 1, 2, 3))
        self.migrate(datetime(2013, 1, 3, 0, 5))
        self.assertEquals(Video.objects.get(id=video.id).view_count, 7)
        self.assertEquals(Video.objects.get(id=video2.id).view_count, 2)

class SubtitleViewCountManagerTest(HitCountManagerTestBase):
    __test__ = True

    def make_hit_count_manager(self):
        return hitcounts.SubtitleViewCountManager()

    def make_three_objects(self):
        v1 = test_factories.create_video()
        v2 = test_factories.create_video()
        return [
            pipeline.add_subtitles(v1, 'en', None).subtitle_language,
            pipeline.add_subtitles(v1, 'fr', None).subtitle_language,
            pipeline.add_subtitles(v2, 'en', None).subtitle_language,
        ]

    last_hit_count_migration_type = 'S'
