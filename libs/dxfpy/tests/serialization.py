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

from unittest import TestCase
from dxfpy.dxfpy import SubtitleSet
from dxfpy.tests.data import sample_ttml


def splitns(lxml_tag):
    ns, tag = lxml_tag.split('}', 1)
    return [ns.lstrip('{'), tag]

class TestSerialization(TestCase):
    def _round_trip(self, subs):
        """Serialize and deserialize a set of subtitles."""
        return SubtitleSet.from_zip(subs.to_zip())


    def test_serialization(self):
        xml = sample_ttml
        subs = SubtitleSet(xml)
        serialized_subs = subs.to_zip()
        deserialized_subs = self._round_trip(serialized_subs)

        # Make sure the XML representations are the same.
        self.assertEqual(subs.to_xml(), deserialized_subs.to_xml())

        # Check the top-level tag.
        self.assertEqual(splitns(deserialized_subs._ttml.tag),
                         ['http://www.w3.org/ns/ttml', 'tt'])

        # Check the first-level tags.
        tags = [splitns(el.tag) for el in deserialized_subs._ttml]
        self.assertEqual(tags,
                         [['http://www.w3.org/ns/ttml', 'head'],
                          ['http://www.w3.org/ns/ttml', 'body']])

    def test_creation(self):
        data = [(   0,  100, "hello, world!"),
                ( 100,  200, "foo"),
                ( 300, None, '<span xmlns="http://www.w3.org/ns/ttml">x</span>'),
                (None, None, "baz")]

        subs = SubtitleSet.from_list(data)

        self.assertEqual(list(subs.subtitle_items()), data)
        subs = self._round_trip(subs)
        self.assertEqual(list(subs.subtitle_items()), data)

    def test_appending(self):
        # Empty set
        subs = SubtitleSet()
        self.assertEqual(list(subs.subtitle_items()),
                         [])
        subs = self._round_trip(subs)
        self.assertEqual(list(subs.subtitle_items()),
                         [])

        # One subtitle
        subs.append_subtitle(0, 1000, "hello, world!")
        self.assertEqual(list(subs.subtitle_items()),
                         [(0, 1000, "hello, world!")])
        subs = self._round_trip(subs)
        self.assertEqual(list(subs.subtitle_items()),
                         [(0, 1000, "hello, world!")])

        # Many subtitles
        subs.append_subtitle(1100, 2000, "foo")
        subs.append_subtitle(3000, None, "a <span>bar</span> z")
        subs.append_subtitle(None, None, "baz")

        self.assertEqual(
            list(subs.subtitle_items()),
            [(   0, 1000, "hello, world!"),
             (1100, 2000, "foo"),
             (3000, None,
              'a <span xmlns="http://www.w3.org/ns/ttml">bar</span> z'),
             (None, None, "baz"),
             ])

        subs = self._round_trip(subs)

        self.assertEqual(
            list(subs.subtitle_items()),
            [(   0, 1000, "hello, world!"),
             (1100, 2000, "foo"),
             (3000, None,
              'a <span xmlns="http://www.w3.org/ns/ttml">bar</span> z'),
             (None, None, "baz"),
             ])
