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

from lxml import etree
from utils.compress import compress, decompress


def get_attr(el, attr):
    """Get the string of an attribute, or None if it's not present.

    Ignores namespaces to save your sanity.

    """
    for k, v in el.attrib.items():
        if k == attr or k.rsplit('}', 1)[-1] == attr:
            return v

def get_contents(el):
    """Get the contents of the given element as a string of XML.

    Based on
    http://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml
    but edited to actually work.

    I cannot believe this is not part of lxml.  Seriously, what are they
    thinking?  This is one of the most basic things people would need.

    """
    parts = ([el.text] +
             list(etree.tostring(c) for c in el.getchildren()) +
             [el.tail])
    return ''.join(filter(None, parts)).strip()


class SubtitleSet(object):
    BASE_TTML = r'''
        <tt xml:lang="" xmlns="http://www.w3.org/ns/ttml">
            <head>
                <metadata xmlns:ttm="http://www.w3.org/ns/ttml#metadata">
                    <ttm:title></ttm:title>
                    <ttm:copyright></ttm:copyright>
                </metadata>

                <styling xmlns:tts="http://www.w3.org/ns/ttml#styling">
                    <style xml:id="amara-style"
                        tts:color="white"
                        tts:fontFamily="proportionalSansSerif"
                        tts:fontSize="18px"
                        tts:textAlign="center"
                    />
                </styling>

                <layout xmlns:tts="http://www.w3.org/ns/ttml#styling">
                    <region xml:id="amara-subtitle-area"
                            style="amara-style"
                            tts:extent="560px 62px"
                            tts:padding="5px 3px"
                            tts:backgroundColor="black"
                            tts:displayAlign="after"
                    />
                </layout>
            </head>
            <body region="amara-subtitle-area">
                <div>
                </div>
            </body>
        </tt>
    '''

    SUBTITLE_XML = r'''
        <p xmlns="http://www.w3.org/ns/ttml" %s %s>
            %s
        </p>
    '''

    def __init__(self, data=None):
        """Create a new set of Subtitles, either empty or from a hunk of TTML.

        NO UNICODE ALLOWED!  USE XML ENTITIES TO REPRESENT UNICODE CHARACTERS!

        """
        if data == None:
            self._ttml = etree.fromstring(SubtitleSet.BASE_TTML)
        else:
            self._ttml = etree.fromstring(data)


    def get_subtitles(self):
        return self._ttml.xpath('/n:tt/n:body/n:div/n:p',
                                namespaces={'n': 'http://www.w3.org/ns/ttml'})

    def append_subtitle(self, from_ms, to_ms, content):
        """Append a subtitle to the end of the list.

        NO UNICODE ALLOWED!  USE XML ENTITIES TO REPRESENT UNICODE CHARACTERS!

        """
        begin = ('begin="%dms"' % from_ms) if from_ms != None else ''
        end = ('end="%dms"' % to_ms) if to_ms != None else ''

        p = etree.fromstring(SubtitleSet.SUBTITLE_XML % (begin, end, content))
        div = self._ttml.xpath('/n:tt/n:body/n:div',
                               namespaces={'n': 'http://www.w3.org/ns/ttml'})[0]
        div.append(p)

    def subtitle_items(self):
        """A generator over the subs, yielding (from_ms, to_ms, content) tuples.

        The from and to millisecond values may be None, and content is a string
        of XML.

        """
        for el in self.get_subtitles():
            begin = get_attr(el, 'begin')
            end = get_attr(el, 'end')

            to_ms = (int(begin.split('ms')[0])
                     if begin and begin.endswith('ms')
                     else None)
            from_ms = (int(end.split('ms')[0])
                       if end and end.endswith('ms')
                       else None)
            content = get_contents(el)

            yield (to_ms, from_ms, content)


    @classmethod
    def from_blob(cls, blob_data):
        """Return a SubtitleSet from a blob of base64'ed zip data."""
        return SubtitleSet(decompress(blob_data))

    @classmethod
    def from_list(cls, subtitles):
        """Return a SubtitleSet from a list of subtitle tuples.

        Each tuple should be (from_ms, to_ms, content).  See the docstring of
        append_subtitle for more information.

        """
        subs = SubtitleSet()

        for s in subtitles:
            subs.append_subtitle(*s)

        return subs


    def to_blob(self):
        return compress(self.to_xml())

    def to_xml(self):
        """Return a string containing the XML for this set of subtitles."""
        return etree.tostring(self._ttml, pretty_print=True)


    def __eq__(self, other):
        if type(self) == type(other):
            return self.to_xml() == other.to_xml()
        else:
            return False

