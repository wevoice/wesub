# -*- coding: utf-8 -*-
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

"""Basic sanity tests to make sure the subtitle models aren't completely broken."""

from django.test import TestCase
from django.db import IntegrityError

from apps.subtitles.models import SubtitleLanguage
from apps.videos.models import Video


VIDEO_URL = 'http://youtu.be/heKK95DAKms'

def make_video():
    video, _ = Video.get_or_create_for_url(VIDEO_URL)
    return video

def refresh(m):
    return m.__class__.objects.get(id=m.id)

def ids(ms):
    return set(m.id for m in ms)

def parent_ids(version):
    return ids(version.parents.all())


class TestSubtitleLanguage(TestCase):
    def setUp(self):
        self.video = make_video()

    def test_create_subtitle_language(self):
        l = SubtitleLanguage(video=self.video, language_code='en')
        l.save()

        l = refresh(l)
        self.assertEqual(l.language_code, 'en')

    def test_subtitle_language_unique_constraints(self):
        l1 = SubtitleLanguage(video=self.video, language_code='en')
        l1.save()

        l2 = SubtitleLanguage(video=self.video, language_code='en')
        self.assertRaises(IntegrityError, lambda: l2.save())

class TestSubtitleVersion(TestCase):
    def setUp(self):
        self.video = make_video()

        self.sl_en = SubtitleLanguage(video=self.video, language_code='en')
        self.sl_en.save()

        self.sl_fr = SubtitleLanguage(video=self.video, language_code='fr')
        self.sl_fr.save()

    def test_create_subtitle_version(self):
        sv = self.sl_en.add_version(title='title a', description='desc a',
                                    subtitles=[{}])

        sv = refresh(sv)

        self.assertEqual(sv.language_code, 'en')
        self.assertEqual(sv.video.id, self.video.id)
        self.assertEqual(sv.subtitle_language.id, self.sl_en.id)
        self.assertEqual(sv.title, 'title a')
        self.assertEqual(sv.description, 'desc a')
        self.assertEqual(sv.subtitles, [{}])
        self.assertEqual(sv.visibility, 'public')

    def test_linear_parents(self):
        sv1 = self.sl_en.add_version()
        sv2 = self.sl_en.add_version()
        sv3 = self.sl_en.add_version()

        sv1 = refresh(sv1)
        sv2 = refresh(sv2)
        sv3 = refresh(sv3)

        self.assertEqual(parent_ids(sv1), ids([]))
        self.assertEqual(parent_ids(sv2), ids([sv1]))
        self.assertEqual(parent_ids(sv3), ids([sv2]))

        self.assertEqual(ids(sv1.get_ancestors()), ids([]))
        self.assertEqual(ids(sv2.get_ancestors()), ids([sv1]))
        self.assertEqual(ids(sv3.get_ancestors()), ids([sv1, sv2]))

    def test_multiple_parents(self):
        # en fr
        #    4
        #    |
        #    3
        #   /|
        #  3 |
        #  | 2
        #  2 |
        #  | 1
        #  |/
        #  1
        e1 = self.sl_en.add_version()
        f1 = self.sl_fr.add_version(parents=[e1])
        e2 = self.sl_en.add_version()
        f2 = self.sl_fr.add_version()
        e3 = self.sl_en.add_version()
        f3 = self.sl_fr.add_version(parents=[e3])
        f4 = self.sl_fr.add_version()

        e1 = refresh(e1)
        e2 = refresh(e2)
        e3 = refresh(e3)
        f1 = refresh(f1)
        f2 = refresh(f2)
        f3 = refresh(f3)
        f4 = refresh(f4)

        # Parents
        self.assertEqual(parent_ids(e1), ids([]))
        self.assertEqual(parent_ids(f1), ids([e1]))

        self.assertEqual(parent_ids(e2), ids([e1]))
        self.assertEqual(parent_ids(f2), ids([f1]))

        self.assertEqual(parent_ids(e3), ids([e2]))
        self.assertEqual(parent_ids(f3), ids([f2, e3]))

        self.assertEqual(parent_ids(f4), ids([f3]))

        # Ancestors
        self.assertEqual(ids(e1.get_ancestors()), ids([]))
        self.assertEqual(ids(e2.get_ancestors()), ids([e1]))
        self.assertEqual(ids(e3.get_ancestors()), ids([e1, e2]))

        self.assertEqual(ids(f1.get_ancestors()), ids([e1]))
        self.assertEqual(ids(f2.get_ancestors()), ids([e1, f1]))
        self.assertEqual(ids(f3.get_ancestors()), ids([e1, f1, e2, f2, e3]))
        self.assertEqual(ids(f4.get_ancestors()), ids([e1, f1, e2, f2, e3, f3]))


