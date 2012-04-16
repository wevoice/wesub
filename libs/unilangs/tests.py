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

from django.test import TestCase
from .unilangs import LanguageCode


class LanguageCodeTest(TestCase):
    def test_encode(self):
        lc = LanguageCode('en', 'iso-639-1')

        self.assertEqual('en', lc.encode('iso-639-1'),
                         "Incorrect encoded value.")

        lc = LanguageCode('bm', 'iso-639-1')

        self.assertEqual('bm', lc.encode('iso-639-1'),
                         "Incorrect encoded value.")

        self.assertEqual('bam', lc.encode('unisubs'),
                         "Incorrect encoded value.")


    def test_aliases(self):
        lc = LanguageCode('bm', 'iso-639-1')
        aliases = lc.aliases()

        self.assertIn('iso-639-1', aliases,
                      "Alias not found.")
        self.assertIn('unisubs', aliases,
                      "Alias not found.")

        self.assertEqual('bm', aliases['iso-639-1'],
                         'Incorrect alias.')
        self.assertEqual('bam', aliases['unisubs'],
                         'Incorrect alias.')

