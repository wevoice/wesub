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

from libs.dxfpy import SubtitleSet

from apps.auth.models import CustomUser as User
from apps.subtitles.models import SubtitleLanguage, Collaborator
from apps.videos.models import Video


VIDEO_URL = 'http://youtu.be/heKK95DAKms'
VIDEO_URL_2 = 'http://youtu.be/e4MSN6IImpI'


def make_video():
    video, _ = Video.get_or_create_for_url(VIDEO_URL)
    return video

def make_video_2():
    video, _ = Video.get_or_create_for_url(VIDEO_URL_2)
    return video


def refresh(m):
    return m.__class__.objects.get(id=m.id)

def versionid(version):
    return version.language_code[:1] + str(version.version_number)

def ids(vs):
    return set(versionid(v) for v in vs)

def parent_ids(version):
    return ids(version.parents.all())

def ancestor_ids(version):
    return ids(version.get_ancestors())


class TestSubtitleLanguage(TestCase):
    def setUp(self):
        self.video = make_video()
        self.video2 = make_video_2()


    def test_create_subtitle_language(self):
        """Basic sanity checks when creating a subtitlelanguage."""
        l = SubtitleLanguage(video=self.video, language_code='en')
        l.save()

        l = refresh(l)
        self.assertEqual(l.language_code, 'en')

    def test_subtitle_language_unique_constraints(self):
        """Test the unique constraints of subtitlelanguages."""

        # The first subtitle language has no restrictions.
        l1 = SubtitleLanguage(video=self.video, language_code='en')
        l1.save()

        # Cannot have more that one SL for the same video+language.
        l2 = SubtitleLanguage(video=self.video, language_code='en')
        self.assertRaises(IntegrityError, lambda: l2.save())

        # But other videos and other languages are fine.
        l3 = SubtitleLanguage(video=self.video2, language_code='en')
        l3.save()

        l4 = SubtitleLanguage(video=self.video, language_code='fr')
        l4.save()


class TestSubtitleVersion(TestCase):
    def setUp(self):
        self.video = make_video()
        self.video2 = make_video_2()

        self.sl_en = SubtitleLanguage(video=self.video, language_code='en')
        self.sl_en.save()


    def test_create_subtitle_version(self):
        """Basic sanity checks when creating a version."""

        sv = self.sl_en.add_version(title='title a', description='desc a',
                                    subtitles=[])

        sv = refresh(sv)

        self.assertEqual(sv.language_code, 'en')
        self.assertEqual(sv.video.id, self.video.id)
        self.assertEqual(sv.subtitle_language.id, self.sl_en.id)
        self.assertEqual(sv.title, 'title a')
        self.assertEqual(sv.description, 'desc a')
        self.assertEqual(list(sv.get_subtitles().subtitle_items()), [])
        self.assertEqual(sv.visibility, 'public')

    def test_subtitle_serialization(self):
        """Test basic subtitle serialization."""

        # Empty SubtitleSets
        # We explicitly test before and after refreshing to make sure the
        # serialization happens properly in both cases.
        sv = self.sl_en.add_version(subtitles=SubtitleSet())
        self.assertEqual(sv.get_subtitles(), SubtitleSet())
        sv = refresh(sv)
        self.assertEqual(sv.get_subtitles(), SubtitleSet())

        sv = self.sl_en.add_version(subtitles=None)
        self.assertEqual(sv.get_subtitles(), SubtitleSet())
        sv = refresh(sv)
        self.assertEqual(sv.get_subtitles(), SubtitleSet())

        sv = self.sl_en.add_version(subtitles=[])
        self.assertEqual(sv.get_subtitles(), SubtitleSet())
        sv = refresh(sv)
        self.assertEqual(sv.get_subtitles(), SubtitleSet())

        # Non-empty SubtitleSets
        # Again we test pre- and post-refresh.  Note that this is also checking
        # the equality handling for Subtitle and SubtitleSets.
        s0 = (100, 200, "a")
        s1 = (300, 400, "b")

        sv = self.sl_en.add_version(subtitles=SubtitleSet.from_list([s0, s1]))
        self.assertEqual(sv.get_subtitles(), SubtitleSet.from_list([s0, s1]))
        sv = refresh(sv)
        self.assertEqual(sv.get_subtitles(), SubtitleSet.from_list([s0, s1]))

        sv = self.sl_en.add_version(subtitles=[s0, s1])
        self.assertEqual(sv.get_subtitles(), SubtitleSet.from_list([s0, s1]))
        sv = refresh(sv)
        self.assertEqual(sv.get_subtitles(), SubtitleSet.from_list([s0, s1]))

    def test_denormalization_sanity_checks(self):
        """Test the sanity checks for data denormalized into the version model."""

        # Version videos must match their subtitlelanguage's videos.
        sv = self.sl_en.add_version()
        sv.video = self.video2
        self.assertRaises(AssertionError, lambda: sv.save())

        # Version language codes must match their subtitlelanguage's language
        # codes.
        sv = self.sl_en.add_version()
        sv.language_code = 'fr'
        self.assertRaises(AssertionError, lambda: sv.save())

    def test_visibility(self):
        """Test the (non-overrided) visibility filtering of versions."""

        sv1 = self.sl_en.add_version()
        sv2 = self.sl_en.add_version()
        sv3 = self.sl_en.add_version()

        def _count_public():
            return self.sl_en.subtitleversion_set.public().count()

        self.assertEqual(3, _count_public())

        sv1.visibility = 'private'
        sv1.save()
        self.assertEqual(2, _count_public())

        sv3.visibility = 'private'
        sv3.save()
        self.assertEqual(1, _count_public())

        sv2.visibility = 'private'
        sv2.save()
        self.assertEqual(0, _count_public())

    def test_visibility_override(self):
        """Test the overrided visibility filtering of versions."""

        sv = self.sl_en.add_version()

        def _count_public():
            return self.sl_en.subtitleversion_set.public().count()

        # vis     override
        # public  null
        self.assertEqual(1, _count_public())

        # vis     override
        # private null
        sv.visibility = 'private'
        sv.save()
        self.assertEqual(0, _count_public())

        # vis     override
        # private public
        sv.visibility_override = 'public'
        sv.save()
        self.assertEqual(1, _count_public())

        # vis     override
        # public  public
        sv.visibility = 'public'
        sv.save()
        self.assertEqual(1, _count_public())

        # vis     override
        # public  private
        sv.visibility_override = 'private'
        sv.save()
        self.assertEqual(0, _count_public())

        # vis     override
        # private private
        sv.visibility = 'private'
        sv.save()
        self.assertEqual(0, _count_public())


class TestHistory(TestCase):
    def setUp(self):
        self.video = make_video()

        self.sl_en = SubtitleLanguage(video=self.video, language_code='en')
        self.sl_en.save()

        self.sl_fr = SubtitleLanguage(video=self.video, language_code='fr')
        self.sl_fr.save()

        self.sl_de = SubtitleLanguage(video=self.video, language_code='de')
        self.sl_de.save()

        self.sl_cy = SubtitleLanguage(video=self.video, language_code='cy')
        self.sl_cy.save()


    def test_linear_parents(self):
        """Test the ancestry, parentage, and lineage for a simple linear history."""

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

        self.assertEqual(sv1.lineage, {})
        self.assertEqual(sv2.lineage, {'en': 1})
        self.assertEqual(sv3.lineage, {'en': 2})

    def test_multiple_parents(self):
        """Test the ancestry, parentage, and lineage for a merged history."""

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
        self.assertEqual(ancestor_ids(e1), ids([]))
        self.assertEqual(ancestor_ids(e2), ids([e1]))
        self.assertEqual(ancestor_ids(e3), ids([e1, e2]))

        self.assertEqual(ancestor_ids(f1), ids([e1]))
        self.assertEqual(ancestor_ids(f2), ids([e1, f1]))
        self.assertEqual(ancestor_ids(f3), ids([e1, f1, e2, f2, e3]))
        self.assertEqual(ancestor_ids(f4), ids([e1, f1, e2, f2, e3, f3]))

        # Lineage
        self.assertEqual(e1.lineage, {})
        self.assertEqual(e2.lineage, {'en': 1})
        self.assertEqual(e3.lineage, {'en': 2})

        self.assertEqual(f1.lineage, {'en': 1})
        self.assertEqual(f2.lineage, {'en': 1, 'fr': 1})
        self.assertEqual(f3.lineage, {'en': 3, 'fr': 2})
        self.assertEqual(f4.lineage, {'en': 3, 'fr': 3})

    def test_tangled_history(self):
        """Test the ancestry, parentage, and lineage for a terrifying history."""

        # en fr de cy
        #
        #    3
        #    |
        #    |     5
        #    |    /|
        #    |   / |
        #    |  7  |
        #    |  |\ |
        #    |  | \|
        # +--|--|--4
        # |  |  |  |
        # 3  |  |  |
        # |  |  |  |
        # |  |  6  |
        # |  |  |\ |
        # |  |  | \|
        # |  |  |  3
        # |  |  | /|
        # |  |  |/ |
        # |  |  5  |
        # |  |  |  2
        # |  |  4  |
        # |  | /|\ |
        # |  |/ | \|
        # |  |  |  1
        # |  |  | /
        # |  |  |/
        # |  |  3
        # |  |  |
        # |  2  |
        # |  |  |
        # +--|--2
        # |  | /|
        # 2  |/ |
        # |  1  |
        # |     |
        # +-----1
        # |
        # 1

        e1 = self.sl_en.add_version(parents=[])
        d1 = self.sl_de.add_version(parents=[e1])
        f1 = self.sl_fr.add_version(parents=[])
        e2 = self.sl_en.add_version(parents=[])
        d2 = self.sl_de.add_version(parents=[f1, e2])
        f2 = self.sl_fr.add_version(parents=[])
        d3 = self.sl_de.add_version(parents=[])
        c1 = self.sl_cy.add_version(parents=[d3])
        d4 = self.sl_de.add_version(parents=[f2, c1])
        c2 = self.sl_cy.add_version(parents=[])
        d5 = self.sl_de.add_version(parents=[])
        c3 = self.sl_cy.add_version(parents=[d5])
        d6 = self.sl_de.add_version(parents=[c3])
        e3 = self.sl_en.add_version(parents=[])
        c4 = self.sl_cy.add_version(parents=[e3])
        d7 = self.sl_de.add_version(parents=[c4])
        c5 = self.sl_cy.add_version(parents=[d7])
        f3 = self.sl_fr.add_version(parents=[])

        e1 = refresh(e1)
        d1 = refresh(d1)
        f1 = refresh(f1)
        e2 = refresh(e2)
        d2 = refresh(d2)
        f2 = refresh(f2)
        d3 = refresh(d3)
        c1 = refresh(c1)
        d4 = refresh(d4)
        c2 = refresh(c2)
        d5 = refresh(d5)
        c3 = refresh(c3)
        d6 = refresh(d6)
        e3 = refresh(e3)
        c4 = refresh(c4)
        d7 = refresh(d7)
        c5 = refresh(c5)
        f3 = refresh(f3)

        # Parents
        self.assertEqual(parent_ids(e1), ids([]))
        self.assertEqual(parent_ids(d1), ids([e1]))
        self.assertEqual(parent_ids(f1), ids([]))
        self.assertEqual(parent_ids(e2), ids([e1]))
        self.assertEqual(parent_ids(d2), ids([d1, e2, f1]))
        self.assertEqual(parent_ids(f2), ids([f1]))
        self.assertEqual(parent_ids(d3), ids([d2]))
        self.assertEqual(parent_ids(c1), ids([d3]))
        self.assertEqual(parent_ids(d4), ids([f2, d3, c1]))
        self.assertEqual(parent_ids(c2), ids([c1]))
        self.assertEqual(parent_ids(d5), ids([d4]))
        self.assertEqual(parent_ids(c3), ids([d5, c2]))
        self.assertEqual(parent_ids(d6), ids([d5, c3]))
        self.assertEqual(parent_ids(e3), ids([e2]))
        self.assertEqual(parent_ids(c4), ids([c3, e3]))
        self.assertEqual(parent_ids(d7), ids([d6, c4]))
        self.assertEqual(parent_ids(c5), ids([c4, d7]))
        self.assertEqual(parent_ids(f3), ids([f2]))

        # Ancestors
        self.assertEqual(ancestor_ids(e1), ids([]))
        self.assertEqual(ancestor_ids(d1), ids([e1]))
        self.assertEqual(ancestor_ids(f1), ids([]))
        self.assertEqual(ancestor_ids(e2), ids([e1]))
        self.assertEqual(ancestor_ids(d2), ids([e1, e2, f1, d1]))
        self.assertEqual(ancestor_ids(f2), ids([f1]))
        self.assertEqual(ancestor_ids(d3), ids([e1, e2, f1, d1, d2]))
        self.assertEqual(ancestor_ids(c1), ids([e1, e2, f1, d1, d2, d3]))
        self.assertEqual(ancestor_ids(d4), ids([e1, e2, f1, f2, d1, d2, d3, c1]))
        self.assertEqual(ancestor_ids(c2), ids([e1, e2, f1, d1, d2, d3, c1]))
        self.assertEqual(ancestor_ids(d5), ids([e1, e2, f1, f2, d1, d2, d3, d4, c1]))
        self.assertEqual(ancestor_ids(c3), ids([e1, e2, f1, f2, d1, d2, d3, d4, d5, c1, c2]))
        self.assertEqual(ancestor_ids(d6), ids([e1, e2, f1, f2, d1, d2, d3, d4, d5, c1, c2, c3]))
        self.assertEqual(ancestor_ids(e3), ids([e1, e2]))
        self.assertEqual(ancestor_ids(c4), ids([e1, e2, e3, f1, f2, d1, d2, d3, d4, d5, c1, c2, c3]))
        self.assertEqual(ancestor_ids(d7), ids([e1, e2, e3, f1, f2, d1, d2, d3, d4, d5, d6, c1, c2, c3, c4]))
        self.assertEqual(ancestor_ids(c5), ids([e1, e2, e3, f1, f2, d1, d2, d3, d4, d5, d6, d7, c1, c2, c3, c4]))
        self.assertEqual(ancestor_ids(f3), ids([f1, f2]))

        # Lineage
        self.assertEqual(e1.lineage, {})
        self.assertEqual(d1.lineage, {'en': 1})
        self.assertEqual(f1.lineage, {})
        self.assertEqual(e2.lineage, {'en': 1})
        self.assertEqual(d2.lineage, {'en': 2, 'fr': 1, 'de': 1})
        self.assertEqual(f2.lineage, {'fr': 1})
        self.assertEqual(d3.lineage, {'en': 2, 'fr': 1, 'de': 2})
        self.assertEqual(c1.lineage, {'en': 2, 'fr': 1, 'de': 3})
        self.assertEqual(d4.lineage, {'en': 2, 'fr': 2, 'de': 3, 'cy': 1})
        self.assertEqual(c2.lineage, {'en': 2, 'fr': 1, 'de': 3, 'cy': 1})
        self.assertEqual(d5.lineage, {'en': 2, 'fr': 2, 'de': 4, 'cy': 1})
        self.assertEqual(c3.lineage, {'en': 2, 'fr': 2, 'de': 5, 'cy': 2})
        self.assertEqual(d6.lineage, {'en': 2, 'fr': 2, 'de': 5, 'cy': 3})
        self.assertEqual(e3.lineage, {'en': 2})
        self.assertEqual(c4.lineage, {'en': 3, 'fr': 2, 'de': 5, 'cy': 3})
        self.assertEqual(d7.lineage, {'en': 3, 'fr': 2, 'de': 6, 'cy': 4})
        self.assertEqual(c5.lineage, {'en': 3, 'fr': 2, 'de': 7, 'cy': 4})
        self.assertEqual(f3.lineage, {'fr': 2})


class TestCollaborator(TestCase):
    def setUp(self):
        self.video = make_video()

        self.sl = SubtitleLanguage(video=self.video, language_code='en')
        self.sl.save()


    def test_create_collaborators(self):
        users = User.objects.all()

        u1 = users[0]
        u2 = users[1]

        c1 = Collaborator(subtitle_language=self.sl, user=u1)
        c2 = Collaborator(subtitle_language=self.sl, user=u2)

        c1.save()
        c2.save()

        # Make sure basic defaults are correct.
        self.assertEqual(c1.user_id, u1.id)
        self.assertEqual(c1.subtitle_language.language_code, 'en')
        self.assertEqual(c1.signoff, False)
        self.assertEqual(c1.signoff_is_official, False)
        self.assertEqual(c1.expired, False)

        self.assertEqual(c2.user_id, u2.id)
        self.assertEqual(c2.subtitle_language.language_code, 'en')
        self.assertEqual(c2.signoff, False)
        self.assertEqual(c2.signoff_is_official, False)
        self.assertEqual(c2.expired, False)

        # Make sure both objects got created properly, and get_for finds them.
        cs = Collaborator.objects.get_for(self.sl)
        self.assertEqual(cs.count(), 2)

        # Make sure we can't create two Collaborators for the same
        # language/video combination.
        self.assertRaises(IntegrityError,
                          lambda: Collaborator(subtitle_language=self.sl,
                                               user=u1).save())

    def test_signoff_retrieval(self):
        users = User.objects.all()

        u1 = users[0]
        u2 = users[1]

        c1 = Collaborator(subtitle_language=self.sl, user=u1)
        c2 = Collaborator(subtitle_language=self.sl, user=u2)

        c1.save()
        c2.save()

        cs = Collaborator.objects
        sl = self.sl

        # collab signoff is_official expired
        # 1
        # 2
        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 2)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 0)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 0)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 0)

        # collab signoff is_official expired
        # 1      x
        # 2
        c1.signoff = True
        c1.save()

        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 1)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 1)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 1)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 0)

        # collab signoff is_official
        # 1      x
        # 2      x
        c2.signoff = True
        c2.save()

        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 0)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 2)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 2)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 0)

        # collab signoff is_official expired
        # 1      x       x
        # 2      x
        c1.signoff_is_official = True
        c1.save()

        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 0)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 2)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 1)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 1)

        # collab signoff is_official expired
        # 1      x       x
        # 2      x       x
        c2.signoff_is_official = True
        c2.save()

        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 0)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 2)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 0)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 2)

        # collab signoff is_official expired
        # 1
        # 2
        c1.signoff = False
        c1.signoff_is_official = False
        c1.save()

        c2.signoff = False
        c2.signoff_is_official = False
        c2.save()

        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl, include_expired=True).count(), 2)

        # collab signoff is_official expired
        # 1                          x
        # 2
        c1.expired = True
        c1.save()

        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 1)
        self.assertEqual(cs.get_unsignedoff_for(sl, include_expired=True).count(), 2)

        # collab signoff is_official expired
        # 1                          x
        # 2                          x
        c2.expired = True
        c2.save()

        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 0)
        self.assertEqual(cs.get_unsignedoff_for(sl, include_expired=True).count(), 2)

        # collab signoff is_official expired
        # 1      x       x           x
        # 2      x                   x
        c1.signoff = True
        c1.signoff_is_official = True
        c1.save()

        c2.signoff = True
        c2.signoff_is_official = False
        c2.save()

        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 0)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 2)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 1)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 1)
