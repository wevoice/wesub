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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from string import printable as chars
from random import randint, choice

from django.test import TestCase
from videos.models import Video
from utils.multi_query_set import MultiQuerySet
from utils.compress import compress, decompress
from utils.chunkediter import chunkediter


class MultiQuerySetTest(TestCase):
    fixtures = ['test.json']

    def test_full(self):
        self.assertEqual(list(Video.objects.all()),
                         list(MultiQuerySet(Video.objects.all())),
                         "Full, single MQS didn't match full QS.")

        self.assertEqual(list(Video.objects.all()),
                         list(MultiQuerySet(Video.objects.none(),
                                            Video.objects.all(),
                                            Video.objects.none())),
                         "Full MQS with blanks didn't match full QS.")

        self.assertEqual(list(Video.objects.all()) + list(Video.objects.all()),
                         list(MultiQuerySet(Video.objects.none(),
                                            Video.objects.all(),
                                            Video.objects.none(),
                                            Video.objects.all())),
                         "Double MQS with blanks didn't match double full QS.")

    def test_slice(self):
        qs = Video.objects.all()
        mqs = MultiQuerySet(Video.objects.all())

        self.assertEqual(list(qs[0:1]),
                         list(mqs[0:1]),
                         "MQS[:1] failed.")

        self.assertEqual(list(qs[0:2]),
                         list(mqs[0:2]),
                         "MQS[:2] failed.")

        self.assertEqual(list(qs[0:3]),
                         list(mqs[0:3]),
                         "MQS[:3] (out-of-bounds endpoint) failed.")

        self.assertEqual(list(qs[1:3]),
                         list(mqs[1:3]),
                         "MQS[1:3] failed.")

        self.assertEqual(list(qs[2:3]),
                         list(mqs[2:3]),
                         "MQS[2:3] failed.")

        self.assertEqual(list(qs[1:1]),
                         list(mqs[1:1]),
                         "MQS[1:1] (empty slice) failed.")

    def test_slice_multiple(self):
        qs = list(Video.objects.all())
        qs = qs + qs + qs
        mqs = MultiQuerySet(Video.objects.all(),
                            Video.objects.all(),
                            Video.objects.all())

        self.assertEqual(qs[0:3],
                         list(mqs[0:3]),
                         "MQS[:3] failed.")

        self.assertEqual(qs[0:6],
                         list(mqs[0:6]),
                         "MQS[:6] (entire range) failed.")

        self.assertEqual(qs[0:7],
                         list(mqs[0:7]),
                         "MQS[:7] (out-of-bounds endpoint) failed.")

        self.assertEqual(qs[1:3],
                         list(mqs[1:3]),
                         "MQS[1:3] failed.")

        self.assertEqual(qs[1:6],
                         list(mqs[1:6]),
                         "MQS[1:6] (entire range) failed.")

        self.assertEqual(qs[1:7],
                         list(mqs[1:7]),
                         "MQS[1:7] (out-of-bounds endpoint) failed.")

        self.assertEqual(qs[3:3],
                         list(mqs[3:3]),
                         "MQS[3:3] failed.")

        self.assertEqual(qs[3:6],
                         list(mqs[3:6]),
                         "MQS[3:6] (entire range) failed.")

        self.assertEqual(qs[3:7],
                         list(mqs[3:7]),
                         "MQS[3:7] (out-of-bounds endpoint) failed.")


class CompressTest(TestCase):
    def test_compression(self):
        # Make sure the empty string is handled.
        self.assertEqual('', decompress(compress('')))

        # Make sure a bunch of random ASCII data compresses correctly.
        for _ in xrange(100):
            l = randint(1, 4096)
            data = ''.join(choice(chars) for _ in xrange(l))
            self.assertEqual(data, decompress(compress(data)))

        # Make sure a bunch of random bytes compress correctly.
        for _ in xrange(100):
            l = randint(1, 4096)
            data = ''.join(chr(randint(0, 255)) for _ in xrange(l))
            self.assertEqual(data, decompress(compress(data)))

        # Make sure a bunch of random Unicode data compresses correctly.
        for _ in xrange(100):
            l = randint(1, 1024)
            data = ''.join(choice(u'☃ಠ_ಠ✿☺☻☹♣♠♥♦⌘⌥✔★☆™※±×~≈÷≠π'
                                  u'αßÁáÀàÅåÄäÆæÇçÉéÈèÊêÍíÌìÎîÑñ'
                                  u'ÓóÒòÔôÖöØøÚúÙùÜüŽž')
                           for _ in xrange(l))

            encoded_data = data.encode('utf-8')
            round_tripped = decompress(compress(encoded_data)).decode('utf-8')

            self.assertEqual(data, round_tripped)


# TODO: Test chunking somehow.
class ChunkedIterTest(TestCase):
    def test_iterate(self):
        data = [1, 10, 100, 1000, 10000]

        sum = 0
        for i in chunkediter(data):
            sum += i
        self.assertEqual(sum, 11111)

        sum = 0
        for i in chunkediter(data, 2):
            sum += i
        self.assertEqual(sum, 11111)

        sum = 0
        for i in chunkediter(data, 1):
            sum += i
        self.assertEqual(sum, 11111)

    def test_empty(self):
        data = []

        sum = 0
        for i in chunkediter(data):
            sum += i
        self.assertEqual(sum, 0)

        sum = 0
        for i in chunkediter(data, 1):
            sum += i
        self.assertEqual(sum, 0)


class BleachSanityTest(TestCase):

    def test_weird_input(self):
        import bleach
        html = "<b>hello</b>"
        value = bleach.clean(html, strip=True, tags=[], attributes=[])
        self.assertEquals(u"hello", value)

        html = "<b></b>"
        value = bleach.clean(html, strip=True, tags=[], attributes=[])
        self.assertEquals(u"", value)

        html = '<p><iframe frameborder="0" height="315" src="http://www.youtube.com/embed/6ydeY0tTtF4" width="560"></iframe></p>'
        value = bleach.clean(html, strip=True, tags=[], attributes=[])
        self.assertEquals(u"", value)
