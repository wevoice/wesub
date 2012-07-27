# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.html.

"""Tests for the subtitle objects implementation."""

from django.test import TestCase

from apps.subtitles.objects import Subtitle, SubtitleSet


class TestSubtitle(TestCase):
    def test_creation(self):
        s1 = Subtitle(1000, 2000, "Hello")

        self.assertEqual(s1.start_ms, 1000)
        self.assertEqual(s1.end_ms, 2000)
        self.assertEqual(s1.content, "Hello")
        self.assertEqual(s1.starts_paragraph, False)

        s2 = Subtitle(123, 456, "World", starts_paragraph=True)

        self.assertEqual(s2.start_ms, 123)
        self.assertEqual(s2.end_ms, 456)
        self.assertEqual(s2.content, "World")
        self.assertEqual(s2.starts_paragraph, True)

        # Blank start/ends are alright.
        s3 = Subtitle(1000, None, "Has start")
        s4 = Subtitle(None, 1000, "Has end")
        s5 = Subtitle(None, None, "Has neither")

        self.assertEqual(s3.end_ms, None)
        self.assertEqual(s4.start_ms, None)
        self.assertEqual(s5.start_ms, None)
        self.assertEqual(s5.end_ms, None)

        # But nonsensical times raise an error.
        self.assertRaises(AssertionError, lambda: Subtitle(9, 8, ''))

    def test_serialization(self):
        s = Subtitle(1000, 2000, "Hello", starts_paragraph=False)

        self.assertEqual(s.to_dict(),
                         {'start_ms': 1000, 'end_ms': 2000,
                          'content': 'Hello', 'meta': {}})

        s.starts_paragraph = True

        self.assertEqual(s.to_dict(),
                         {'start_ms': 1000, 'end_ms': 2000,
                          'content': 'Hello', 'meta': {
                              'starts_paragraph': True,
                          }})

    def test_deserialization(self):
        s = Subtitle.from_dict({
            'start_ms': 1000,
            'end_ms': 2000,
            'content': "Sample",
            'meta': {},
        })

        self.assertEqual(s.start_ms, 1000)
        self.assertEqual(s.end_ms, 2000)
        self.assertEqual(s.content, "Sample")
        self.assertEqual(s.starts_paragraph, False)

        s = Subtitle.from_dict({
            'start_ms': 14223,
            'end_ms': None,
            'content': "Sample",
            'meta': {
                'starts_paragraph': True,
            },
        })

        self.assertEqual(s.start_ms, 14223)
        self.assertEqual(s.end_ms, None)
        self.assertEqual(s.content, "Sample")
        self.assertEqual(s.starts_paragraph, True)

    def test_equality(self):
        s1 = Subtitle.from_dict({
            'start_ms': 1000,
            'end_ms': 2000,
            'content': "Sample",
            'meta': {},
        })
        s2 = Subtitle(1000, 2000, "Sample")

        self.assertEqual(s1, s2)

        s2.end_ms += 100
        self.assertNotEqual(s1, s2)

    def test_is_synced(self):
        s1 = Subtitle(1000, 2000, "Sample")
        s2 = Subtitle(None, 2000, "Sample")
        s3 = Subtitle(1000, None, "Sample")
        s4 = Subtitle(None, None, "Sample")

        self.assertEqual(s1.is_synced(), True)
        self.assertEqual(s2.is_synced(), False)
        self.assertEqual(s3.is_synced(), False)
        self.assertEqual(s4.is_synced(), False)

    def test_duration(self):
        s1 = Subtitle(1000, 5000, "")

        self.assertEqual(s1.duration(), 4000)
        s1.start_ms -= 100
        self.assertEqual(s1.duration(), 4100)
        s1.start_ms += 200
        self.assertEqual(s1.duration(), 3900)
        s1.end_ms += 1000
        self.assertEqual(s1.duration(), 4900)
        s1.end_ms -= 400
        self.assertEqual(s1.duration(), 4500)
        s1.end_ms = s1.start_ms
        self.assertEqual(s1.duration(), 0)

        s2 = Subtitle(None, 5000, "")
        s3 = Subtitle(1000, None, "")
        s4 = Subtitle(None, None, "")

        self.assertEqual(s2.duration(), None)
        self.assertEqual(s3.duration(), None)
        self.assertEqual(s4.duration(), None)


class TestSubtitleSet(TestCase):
    def setUp(self):
        self.s0 = Subtitle(1000, 2000, "Hello", starts_paragraph=True)
        self.s1 = Subtitle(5000, 8000, "World")
        self.s2 = Subtitle(10000, 12000, "foo", starts_paragraph=True)
        self.s3 = Subtitle(14000, 20000, "bar")
        self.s4 = Subtitle(26000, None, "baz")
        self.subs = [self.s0, self.s1, self.s2, self.s3, self.s4]


    def test_creation(self):
        ss = SubtitleSet(self.subs)

        self.assertEqual(len(ss), 5)
        self.assertEqual(ss[0], self.s0)
        self.assertEqual(ss[1], self.s1)
        self.assertEqual(ss[2], self.s2)
        self.assertEqual(ss[3], self.s3)
        self.assertEqual(ss[4], self.s4)

        self.assertEqual(list(s.start_ms for s in ss),
                         [1000, 5000, 10000, 14000, 26000])

        self.assertEqual(list(s.end_ms for s in ss),
                         [2000, 8000, 12000, 20000, None])

        self.assertEqual(list(s.content for s in ss),
                         ["Hello", "World", "foo", "bar", "baz"])

        self.assertEqual(list(s.starts_paragraph for s in ss),
                         [True, False, True, False, False])

    def test_typechecking(self):
        good = self.s0
        bare = "Subtitle!"
        raw = self.s0.to_dict()

        SubtitleSet([good])
        self.assertRaises(AssertionError, lambda: SubtitleSet([bare]))
        self.assertRaises(AssertionError, lambda: SubtitleSet([raw]))
        self.assertRaises(AssertionError, lambda: SubtitleSet([None]))

        ss = SubtitleSet(self.subs)

        ss.append(good)
        ss.pop(-1)
        self.assertRaises(AssertionError, lambda: ss.append(bare))
        self.assertRaises(AssertionError, lambda: ss.append(raw))
        self.assertRaises(AssertionError, lambda: ss.append(None))

        ss.prepend(good)
        ss.pop(0)
        self.assertRaises(AssertionError, lambda: ss.prepend(bare))
        self.assertRaises(AssertionError, lambda: ss.prepend(raw))
        self.assertRaises(AssertionError, lambda: ss.prepend(None))

        ss.insert(0, good)
        ss.pop(0)
        self.assertRaises(AssertionError, lambda: ss.insert(0, bare))
        self.assertRaises(AssertionError, lambda: ss.insert(0, raw))
        self.assertRaises(AssertionError, lambda: ss.insert(0, None))

        def _set(v):
            def _s():
                ss[0] = v
            return _s

        _set(good)
        self.assertRaises(AssertionError, _set(bare))
        self.assertRaises(AssertionError, _set(raw))
        self.assertRaises(AssertionError, _set(None))

        # TODO: Fix slice assignment.
        # def _set_slice(v):
        #     def _s():
        #         ss[0:1] = v
        #     return _s

        # _set_slice([good])
        # self.assertRaises(AssertionError, _set_slice([bare]))
        # self.assertRaises(AssertionError, _set_slice([raw]))
        # self.assertRaises(AssertionError, _set_slice([None]))

    def test_serialization(self):
        # For now just make sure that round-tripping works at each of the
        # various stages.  We can get more specific in the future if necessary.
        def _assertUnchanged(ss):
            self.assertEqual(list(s.start_ms for s in ss),
                            [1000, 5000, 10000, 14000, 26000])

            self.assertEqual(list(s.end_ms for s in ss),
                            [2000, 8000, 12000, 20000, None])

            self.assertEqual(list(s.content for s in ss),
                            ["Hello", "World", "foo", "bar", "baz"])

            self.assertEqual(list(s.starts_paragraph for s in ss),
                            [True, False, True, False, False])

        ss = SubtitleSet(self.subs)

        serialized = ss.to_list()
        deserialized = SubtitleSet.from_list(serialized)
        _assertUnchanged(deserialized)

        serialized = ss.to_json()
        deserialized = SubtitleSet.from_json(serialized)
        _assertUnchanged(deserialized)

        serialized = ss.to_zip()
        deserialized = SubtitleSet.from_zip(serialized)
        _assertUnchanged(deserialized)

    def test_paragraphs(self):
        def _p_to_strs(p):
            return [sub.content for sub in p]

        s1 = Subtitle(None, None, "1")
        s2 = Subtitle(None, None, "2")
        s3 = Subtitle(None, None, "3", starts_paragraph=True)
        s4 = Subtitle(None, None, "4")
        s5 = Subtitle(None, None, "5")
        s6 = Subtitle(None, None, "6", starts_paragraph=True)
        s7 = Subtitle(None, None, "7", starts_paragraph=True)
        s8 = Subtitle(None, None, "8")

        ss = SubtitleSet([s1, s2, s3, s4, s5, s6, s7, s8])
        ps = list(ss.as_paragraphs())

        self.assertEqual([_p_to_strs(p) for p in ps],
                         [["1", "2"],
                          ["3", "4", "5"],
                          ["6"],
                          ["7", "8"]
                          ])
        for p in ps:
            self.assertEqual(type(p), SubtitleSet)

        s1 = Subtitle(None, None, "1", starts_paragraph=True)
        s2 = Subtitle(None, None, "2")
        s3 = Subtitle(None, None, "3")
        s4 = Subtitle(None, None, "4")
        s5 = Subtitle(None, None, "5")
        s6 = Subtitle(None, None, "6")
        s7 = Subtitle(None, None, "7")
        s8 = Subtitle(None, None, "8", starts_paragraph=True)

        ss = SubtitleSet([s1, s2, s3, s4, s5, s6, s7, s8])
        ps = list(ss.as_paragraphs())

        self.assertEqual([_p_to_strs(p) for p in ps],
                         [["1", "2", "3", "4", "5", "6", "7"],
                          ["8"]
                          ])

        # Empty subtitle sets have no paragraphs.
        ss = SubtitleSet()
        ps = list(ss.as_paragraphs())
        self.assertEqual(ps, [])

        # A set with a single subtitle has one paragraph.
        ss = SubtitleSet([s1])
        ps = list(ss.as_paragraphs())
        self.assertEqual([_p_to_strs(p) for p in ps],
                         [["1"]])
