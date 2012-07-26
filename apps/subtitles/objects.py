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

"""Subtitle wrapper objects."""

import zlib

from django.utils import simplejson as json


# Subtitle Objects ------------------------------------------------------------
class Subtitle(object):
    """A single subtitle."""

    def __init__(self, start_ms, end_ms, content, starts_paragraph=False):
        if start_ms != None and end_ms != None:
            assert start_ms <= end_ms, 'Subtitles cannot end before they start!'

        self.start_ms = start_ms
        self.end_ms = end_ms
        self.content = content
        self.starts_paragraph = starts_paragraph

    def __eq__(self, other):
        if type(self) is type(other):
            return (
                self.start_ms == other.start_ms
                and self.end_ms == other.end_ms
                and self.content == other.content
                and self.starts_paragraph == other.starts_paragraph
            )
        else:
            return False

    def __unicode__(self):
        return u"Subtitle (%s to %s): '%s'" % (self.start_ms, self.end_ms,
                                               self.content)
    def __str__(self):
        return unicode(self).encode('utf-8')


    # Serialization
    def to_dict(self):
        meta = {}

        if self.starts_paragraph:
            meta['starts_paragraph'] = True

        return {
            'start_ms': self.start_ms,
            'end_ms': self.end_ms,
            'content': self.content,
            'meta': meta,
        }


    # Deserialization
    @classmethod
    def from_dict(cls, data):
        start_ms = data['start_ms']
        end_ms = data['end_ms']
        content = data['content']

        meta = data.get('meta', {})
        starts_paragraph = meta.get('starts_paragraph', False)

        return Subtitle(start_ms, end_ms, content, starts_paragraph)


class SubtitleSet(list):
    """A set of subtitles for a video.

    SubtitleSets may only contain Subtitle objects.  This will be sanity-checked
    for you when using the editing functions.

    They inherit from vanilla Python lists, so they should support most listy
    functionality like slicing, append, insert, pop, etc.

    It's up to you to keep them in order.  Good luck.

    """
    TYPE_ERROR =  "SubtitleSets may only contain Subtitle objects!"

    # Creation
    def __init__(self, subtitles=None):
        if subtitles:
            subtitles = list(subtitles)
        else:
            subtitles = []

        for subtitle in subtitles:
            assert isinstance(subtitle, Subtitle), SubtitleSet.TYPE_ERROR

        return super(SubtitleSet, self).__init__(subtitles)


    # I am now a human type system.
    def append(self, subtitle):
        assert isinstance(subtitle, Subtitle), SubtitleSet.TYPE_ERROR
        return super(SubtitleSet, self).append(subtitle)

    def prepend(self, subtitle):
        return self.insert(0, subtitle)

    def insert(self, index, subtitle):
        assert isinstance(subtitle, Subtitle), SubtitleSet.TYPE_ERROR
        return super(SubtitleSet, self).insert(index, subtitle)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            for subtitle in value:
                assert isinstance(subtitle, Subtitle), SubtitleSet.TYPE_ERROR
        else:
            assert isinstance(value, Subtitle), SubtitleSet.TYPE_ERROR

        return super(SubtitleSet, self).__setitem__(key, value)


    # Serialization
    def to_list(self):
        return list(sub.to_dict() for sub in self)

    def to_json(self):
        return json.dumps(self.to_list())

    def to_zip(self):
        return zlib.compress(self.to_json())


    # Deserialization
    @classmethod
    def from_list(cls, data):
        subtitles = list(Subtitle.from_dict(sub) for sub in data)
        return SubtitleSet(subtitles=subtitles)

    @classmethod
    def from_json(cls, json_str):
        return SubtitleSet.from_list(json.loads(json_str))

    @classmethod
    def from_zip(cls, zip_data):
        return SubtitleSet.from_json(zlib.decompress(zip_data))

