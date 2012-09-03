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

"""Tests for the subtitle pipeline implementation."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.auth.models import CustomUser as User
from apps.subtitles import pipeline
from apps.subtitles.models import SubtitleLanguage, SubtitleVersion
from apps.subtitles.tests.utils import make_video, make_video_2
from libs.dxfpy import SubtitleSet


class TestHelperFunctions(TestCase):
    def setUp(self):
        self.video = make_video()
        self.video2 = make_video_2()

    def test_get_language(self):
        sl, needs_save = pipeline._get_language(self.video, 'en')
        self.assertEqual(sl.language_code, 'en')
        self.assertEqual(needs_save, True)

        sl, needs_save = pipeline._get_language(self.video, 'fr')
        self.assertEqual(sl.language_code, 'fr')
        self.assertEqual(needs_save, True)

        l = SubtitleLanguage(video=self.video, language_code='en')
        l.save()

        sl, needs_save = pipeline._get_language(self.video, 'en')
        self.assertEqual(sl.language_code, 'en')
        self.assertEqual(needs_save, False)
        self.assertEqual(sl.id, l.id)

        sl, needs_save = pipeline._get_language(self.video, 'fr')
        self.assertEqual(sl.language_code, 'fr')
        self.assertEqual(needs_save, True)

    def test_get_version(self):
        def _assert_eq(a, b):
            if (not a) or (not b):
                self.assertTrue((not a) and (not b))
            else:
                self.assertEqual(a.id, b.id)

        def _assert_notfound(l):
            self.assertRaises(SubtitleVersion.DoesNotExist, l)

        def _assert_badtype(l):
            self.assertRaises(ValueError, l)

        def _get_version(v):
            return pipeline._get_version(self.video, v)


        en = SubtitleLanguage.objects.create(video=self.video, language_code='en')
        fr = SubtitleLanguage.objects.create(video=self.video, language_code='fr')

        en1 = en.add_version()
        en2 = en.add_version()
        en3 = en.add_version()

        fr1 = fr.add_version()
        fr2 = fr.add_version()
        fr3 = fr.add_version()

        # Test passthrough.
        _assert_eq(en1, _get_version(en1))
        _assert_eq(en2, _get_version(en2))
        _assert_eq(en3, _get_version(en3))
        _assert_eq(fr1, _get_version(fr1))
        _assert_eq(fr2, _get_version(fr2))
        _assert_eq(fr3, _get_version(fr3))

        # Test version IDs (integers).
        _assert_eq(en1, _get_version(en1.id))
        _assert_eq(en2, _get_version(en2.id))
        _assert_eq(en3, _get_version(en3.id))
        _assert_eq(fr1, _get_version(fr1.id))
        _assert_eq(fr2, _get_version(fr2.id))
        _assert_eq(fr3, _get_version(fr3.id))

        # Test language_code, version_number pairs.
        _assert_eq(fr1, _get_version(('fr', 1)))
        _assert_eq(fr2, _get_version(('fr', 2)))
        _assert_eq(fr3, _get_version(('fr', 3)))
        _assert_eq(en1, _get_version(['en', 1]))
        _assert_eq(en2, _get_version(['en', 2]))
        _assert_eq(en3, _get_version(['en', 3]))

        # Test mismatching passthrough.
        _assert_notfound(lambda: pipeline._get_version(self.video2, en1))
        _assert_notfound(lambda: pipeline._get_version(self.video2, fr3))

        # Test bad version ID.
        _assert_notfound(lambda: _get_version(424242))

        # Test bad language_code, version_number pair.
        _assert_notfound(lambda: _get_version(('fr', 0)))
        _assert_notfound(lambda: _get_version(('fr', 4)))
        _assert_notfound(lambda: _get_version(('cats', 1)))

        # Test entirely invalid types.
        _assert_badtype(lambda: _get_version(u'squirrel'))
        _assert_badtype(lambda: _get_version(1.2))



class TestBasicAdding(TestCase):
    def setUp(self):
        self.video = make_video()
        users = User.objects.all()
        (self.u1, self.u2) = users[:2]
        self.anon = User.get_anonymous()


    def test_add_empty_versions(self):
        # Start with no SubtitleLanguages.
        self.assertEqual(
            SubtitleLanguage.objects.filter(video=self.video).count(), 0)

        # Put a version through the pipeline.
        pipeline.add_subtitles(self.video, 'en', None)

        # It should create the SubtitleLanguage automatically, with one version.
        self.assertEqual(
            SubtitleLanguage.objects.filter(video=self.video).count(), 1)
        self.assertEqual(
            SubtitleVersion.objects.filter(video=self.video).count(), 1)

        sl = SubtitleLanguage.objects.get(video=self.video, language_code='en')

        # Make sure the version seems sane.
        v = sl.get_tip()
        self.assertEqual(v.version_number, 1)
        self.assertEqual(v.language_code, 'en')

        # Put another version through the pipeline.
        pipeline.add_subtitles(self.video, 'en', None)

        # Now we should have two versions for a single language.
        self.assertEqual(
            SubtitleLanguage.objects.filter(video=self.video).count(), 1)
        self.assertEqual(
            SubtitleVersion.objects.filter(video=self.video).count(), 2)

        # Make sure it looks sane too.
        v = sl.get_tip()
        self.assertEqual(v.version_number, 2)
        self.assertEqual(v.language_code, 'en')

    def test_add_subtitles(self):
        def _get_tip_subs():
            sl = SubtitleLanguage.objects.get(video=self.video,
                                              language_code='en')
            return list(sl.get_tip().get_subtitles().subtitle_items())

        def _add(subs):
            pipeline.add_subtitles(self.video, 'en', subs)


        # Passing nil.
        _add(None)

        self.assertEqual(_get_tip_subs(), [])

        # Passing a list of tuples.
        _add([(100, 200, "foo"),
              (300, None, "bar")])

        self.assertEqual(_get_tip_subs(), [(100, 200, "foo"),
                                           (300, None, "bar")])

        # Passing an iterable of tuples.
        _add((s for s in [(101, 200, "foo"),
                          (300, None, "bar")]))

        self.assertEqual(_get_tip_subs(), [(101, 200, "foo"),
                                           (300, None, "bar")])

        # Passing a SubtitleSet.
        subs = SubtitleSet.from_list([(110, 210, "foo"),
                                      (310, 410, "bar"),
                                      (None, None, '"baz"')])

        _add(subs)

        self.assertEqual(_get_tip_subs(), [(110, 210, "foo"),
                                           (310, 410, "bar"),
                                           (None, None, '"baz"')])

        # Passing a hunk of XML.
        subs = SubtitleSet.from_list([(10000, 22000, "boots"),
                                      (23000, 29000, "cats")])

        _add(subs.to_xml())

        self.assertEqual(_get_tip_subs(), [(10000, 22000, "boots"),
                                           (23000, 29000, "cats")])


        # Passing nonsense should TypeError out.
        self.assertRaises(TypeError, lambda: _add(1))

        # Make sure all the versions are there.
        sl = SubtitleLanguage.objects.get(video=self.video, language_code='en')
        self.assertEqual(sl.subtitleversion_set.count(), 5)

    def test_title_description(self):
        def _get_tip_td():
            sl = SubtitleLanguage.objects.get(video=self.video,
                                              language_code='en')
            tip = sl.get_tip()
            return (tip.title, tip.description)

        def _add(*args, **kwargs):
            pipeline.add_subtitles(self.video, 'en', None, *args, **kwargs)


        # Not passing at all.
        _add()
        self.assertEqual(_get_tip_td(), ('', ''))

        # Passing nil.
        _add(title=None, description=None)
        self.assertEqual(_get_tip_td(), ('', ''))

        # Passing empty strings.
        _add(title='', description='')
        self.assertEqual(_get_tip_td(), ('', ''))

        # Passing title.
        _add(title='Foo')
        self.assertEqual(_get_tip_td(), ('Foo', ''))

        # Passing description.
        _add(description='Bar')
        self.assertEqual(_get_tip_td(), ('', 'Bar'))

        # Passing both.
        _add(title='Foo', description='Bar')
        self.assertEqual(_get_tip_td(), ('Foo', 'Bar'))

        # Passing unicode.
        _add(title=u'ಠ_ಠ', description=u'ಠ‿ಠ')
        self.assertEqual(_get_tip_td(), (u'ಠ_ಠ', u'ಠ‿ಠ'))

        # Passing nonsense.
        self.assertRaises(ValidationError, lambda: _add(title=1234))
        self.assertRaises(ValidationError, lambda: _add(title=['a', 'b']))

    def test_author(self):
        def _get_tip_author():
            sl = SubtitleLanguage.objects.get(video=self.video,
                                              language_code='en')
            return sl.get_tip().author

        def _add(*args, **kwargs):
            pipeline.add_subtitles(self.video, 'en', None, *args, **kwargs)


        # Not passing at all.
        _add()
        self.assertEqual(_get_tip_author(), self.anon)

        # Passing nil.
        _add(author=None)
        self.assertEqual(_get_tip_author(), self.anon)

        # Passing anonymous.
        _add(author=User.get_anonymous())
        self.assertEqual(_get_tip_author(), self.anon)

        # Passing u1.
        _add(author=self.u1)
        self.assertEqual(_get_tip_author().id, self.u1.id)

        # Passing u2.
        _add(author=self.u2)
        self.assertEqual(_get_tip_author().id, self.u2.id)

        # Passing nonsense
        self.assertRaises(ValueError, lambda: _add(author='dogs'))
        self.assertRaises(ValueError, lambda: _add(author=-1234))
        self.assertRaises(ValueError, lambda: _add(author=[self.u1]))

    def test_visibility(self):
        def _get_tip_vis():
            sl = SubtitleLanguage.objects.get(video=self.video,
                                              language_code='en')
            tip = sl.get_tip()
            return (tip.visibility, tip.visibility_override)

        def _add(*args, **kwargs):
            pipeline.add_subtitles(self.video, 'en', None, *args, **kwargs)


        # Not passing at all.
        _add()
        self.assertEqual(_get_tip_vis(), ('public', ''))

        # Passing nil.
        _add(visibility=None, visibility_override=None)
        self.assertEqual(_get_tip_vis(), ('public', ''))

        # Passing visibility.
        _add(visibility='public')
        self.assertEqual(_get_tip_vis(), ('public', ''))

        _add(visibility='private')
        self.assertEqual(_get_tip_vis(), ('private', ''))

        # Passing visibility_override.
        _add(visibility_override='')
        self.assertEqual(_get_tip_vis(), ('public', ''))

        _add(visibility_override='public')
        self.assertEqual(_get_tip_vis(), ('public', 'public'))

        _add(visibility_override='private')
        self.assertEqual(_get_tip_vis(), ('public', 'private'))

        # Passing nonsense.
        self.assertRaises(ValidationError, lambda: _add(visibility=42))
        self.assertRaises(ValidationError, lambda: _add(visibility='llamas'))
        self.assertRaises(ValidationError, lambda: _add(visibility_override=3.1415))
        self.assertRaises(ValidationError, lambda: _add(visibility_override='cats'))

    def test_parents(self):
        def _add(language_code, parents):
            return pipeline.add_subtitles(self.video, language_code, None,
                                          parents=parents)

        def _get_tip_parents(language_code):
            sl = SubtitleLanguage.objects.get(video=self.video,
                                              language_code=language_code)
            tip = sl.get_tip()
            return sorted(["%s%d" % (v.language_code, v.version_number)
                           for v in tip.parents.all()])

        def _assert_notfound(l):
            self.assertRaises(SubtitleVersion.DoesNotExist, l)

        def _assert_badtype(l):
            self.assertRaises(ValueError, l)


        # First, check the default parents.
        #
        # en fr
        #
        #    1
        # 2
        # |
        # 1
        en1 = _add('en', None)
        self.assertEqual(_get_tip_parents('en'), [])

        en2 = _add('en', None)
        self.assertEqual(_get_tip_parents('en'), ['en1'])

        fr1 = _add('fr', None)
        self.assertEqual(_get_tip_parents('fr'), [])

        # Parents can be SV objects directly.
        #
        # en fr de
        #       1
        #      /
        #     /
        #    3
        #    |
        #    2
        #   /|
        #  / 1
        # 2
        # |
        # 1
        fr2 = _add('fr', [en2])
        self.assertEqual(_get_tip_parents('fr'), ['en2', 'fr1'])

        fr3 = _add('fr', None)
        self.assertEqual(_get_tip_parents('fr'), ['fr2'])

        de1 = _add('de', [fr3])
        self.assertEqual(_get_tip_parents('de'), ['fr3'])

        # Parents can be given with just their IDs.
        #
        # cy en fr de
        # 2___
        # |   \
        # 1    \
        # |\____|_
        # |     | \
        # |     |  1
        # |     | /
        # |     |/
        # |     3
        # |     |
        # |     2
        #  \   /|
        #   \ / 1
        #    2
        #    |
        #    1
        cy1 = _add('cy', [en2.id, de1.id])
        self.assertEqual(_get_tip_parents('cy'), ['de1', 'en2'])

        cy2 = _add('cy', [fr3.id])
        self.assertEqual(_get_tip_parents('cy'), ['cy1', 'fr3'])

        # Parents can be language_code, version_number pairs for convenience.
        #
        # en fr de ja
        #       2
        #       |\
        #       | \
        #       |  1
        #       | /|
        #       |/ |
        #       1  |
        #      /   |
        #     /    |
        #    3-----+
        #    |
        #    2
        #   /|
        #  / 1
        # 2
        # |
        # 1
        ja1 = _add('ja', [('fr', 3), ['de', 1]])
        self.assertEqual(_get_tip_parents('ja'), ['de1', 'fr3'])

        de2 = _add('de', [('ja', 1)])
        self.assertEqual(_get_tip_parents('de'), ['de1', 'ja1'])

        # Parent specs can be mixed in a single add call.
        #
        # en fr de ja
        #      ____2
        #     / / /|
        #    / / / |
        #   / / |  |
        #  / |  2  |
        # |  |  |\ |
        # |  |  | \|
        # |  |  |  1
        # |  |  | /|
        # |  |  |/ |
        # |  |  1  |
        # |  | /   |
        # |  |/    |
        # |  3-----+
        # |  |
        # |  2
        # | /|
        # |/ 1
        # 2
        # |
        # 1
        ja2 = _add('ja', [de2, ('fr', 3), en2.id])
        self.assertEqual(_get_tip_parents('ja'), ['de2', 'en2', 'fr3', 'ja1'])

        # Check that nonsense IDs don't work.
        _assert_notfound(lambda: _add('en', [12345]))
        _assert_notfound(lambda: _add('en', [0]))
        _assert_notfound(lambda: _add('en', [-1]))

        # Check that nonsense pairs don't work.
        _assert_notfound(lambda: _add('en', [['en', 400]]))
        _assert_notfound(lambda: _add('en', [['fr', -10]]))
        _assert_notfound(lambda: _add('en', [['pt', 1]]))
        _assert_notfound(lambda: _add('en', [['puppies', 1]]))

        # Check that nonsense types don't work.
        _assert_badtype(lambda: _add('en', "Hello!"))
        _assert_badtype(lambda: _add('en', ["Hello!"]))
        _assert_badtype(lambda: _add('en', [{}]))

        # Shut up, Pyflakes.
        assert (en1 and en2 and fr1 and fr2 and fr3 and de1 and de2 and cy1 and
                cy2 and ja1 and ja2)

