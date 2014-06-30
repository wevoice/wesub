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
import logging
import re
from urlparse import urlparse
import babelsubs
import requests
import time

import gdata.youtube.client
from gdata.youtube.client import YouTubeError
import httplib
import httplib2
from celery.task import task
from django.conf import settings
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from gdata.service import RequestError
from gdata.youtube.service import YouTubeService
from lxml import etree

from base import VideoType, VideoTypeError
from utils.translation import SUPPORTED_LANGUAGE_CODES
from utils.metrics import Meter, Occurrence
from utils.subtitles import load_subtitles
from utils import youtube

from unilangs import LanguageCode


logger = logging.getLogger("videos.types.youtube")

YOUTUBE_API_SECRET  = getattr(settings, "YOUTUBE_API_SECRET", None)
YOUTUBE_ALWAYS_PUSH_USERNAME = getattr(settings,
    'YOUTUBE_ALWAYS_PUSH_USERNAME', None)


_('Private video')
_('Undefined error')

FROM_YOUTUBE_MARKER = u'From youtube'
class TooManyRecentCallsException(Exception):
    """
    Raised when the Youtube API responds with yt:quota too_many_recent_calls.
    """

    def __init__(self, *args, **kwargs):
        super(TooManyRecentCallsException, self).__init__(*args, **kwargs)
        logger.info('too_many_calls', extra={
            'exception_args': args,
            'exception_kwargs': kwargs})
        Occurrence('youtube.api_too_many_calls').mark()


from atom.http_core import Uri
import atom

def monkeypatch_class(name, bases, namespace):
    assert len(bases) == 1, "Exactly one base class required"
    base = bases[0]
    for name, value in namespace.iteritems():
        if name != "__metaclass__":
            setattr(base, name, value)
    return base

class HttpClient(atom.http_core.HttpClient):
    __metaclass__ = monkeypatch_class
    debug = None

    def Request(self, http_request):
        return self._http_request(http_request.method, http_request.uri,
                              http_request.headers, http_request._body_parts)

    def _get_connection(self, uri, headers=None):
        """Opens a socket connection to the server to set up an HTTP request.

        Args:
        uri: The full URL for the request as a Uri object.
        headers: A dict of string pairs containing the HTTP headers for the
            request.
        """
        connection = None
        if uri.scheme == 'https':
            if not uri.port:
                connection = httplib.HTTPSConnection(uri.host)
            else:
                connection = httplib.HTTPSConnection(uri.host, int(uri.port))
        else:
            if not uri.port:
                connection = httplib.HTTPConnection(uri.host)
            else:
                connection = httplib.HTTPConnection(uri.host, int(uri.port))
        return connection

    def _http_request(self, method, uri, headers=None, body_parts=None):
        """Makes an HTTP request using httplib.

        Args:
        method: str example: 'GET', 'POST', 'PUT', 'DELETE', etc.
        uri: str or atom.http_core.Uri
        headers: dict of strings mapping to strings which will be sent as HTTP
                headers in the request.
        body_parts: list of strings, objects with a read method, or objects
                    which can be converted to strings using str. Each of these
                    will be sent in order as the body of the HTTP request.
        """

        extra = {
            'youtube_headers': headers,
            'youtube_uri': {
                'host': uri.host,
                'port': uri.port,
                'scheme': uri.scheme,
                'path': uri.path,
                'query': uri.query
            },
            'youtube_method': method,
            'youtube_body_parts': body_parts
        }
        logger.info('youtube api request', extra=extra)

        if isinstance(uri, (str, unicode)):
            uri = Uri.parse_uri(uri)

        connection = self._get_connection(uri, headers=headers)

        if self.debug:
            connection.debuglevel = 1

        if connection.host != uri.host:
            connection.putrequest(method, str(uri))
        else:
            connection.putrequest(method, uri._get_relative_path())

        # Overcome a bug in Python 2.4 and 2.5
        # httplib.HTTPConnection.putrequest adding
        # HTTP request header 'Host: www.google.com:443' instead of
        # 'Host: www.google.com', and thus resulting the error message
        # 'Token invalid - AuthSub token has wrong scope' in the HTTP response.
        if (uri.scheme == 'https' and int(uri.port or 443) == 443 and
            hasattr(connection, '_buffer') and
            isinstance(connection._buffer, list)):

            header_line = 'Host: %s:443' % uri.host
            replacement_header_line = 'Host: %s' % uri.host
            try:
                connection._buffer[connection._buffer.index(header_line)] = (
                    replacement_header_line)
            except ValueError:  # header_line missing from connection._buffer
                pass

        # Send the HTTP headers.
        for header_name, value in headers.iteritems():
            connection.putheader(header_name, value)
        connection.endheaders()

        # If there is data, send it in the request.
        if body_parts and filter(lambda x: x != '', body_parts):
            for part in body_parts:
                _send_data_part(part, connection)

        # Return the HTTP Response from the server.
        return connection.getresponse()


def _send_data_part(data, connection):
    if isinstance(data, (str, unicode)):
        # I might want to just allow str, not unicode.
        connection.send(data)
        return
    # Check to see if data is a file-like object that has a read method.
    elif hasattr(data, 'read'):
        # Read the file and send it a chunk at a time.
        while 1:
            binarydata = data.read(100000)
            if binarydata == '': break
            connection.send(binarydata)
        return
    else:
        # The data object was not a file.
        # Try to convert to a string and send the data.
        connection.send(str(data))
        return


def get_youtube_service():
    """
    Gets instance of youtube service with the proper developer key
    this is needed, else our quota is serverly damaged.
    """
    yt_service = YouTubeService(developer_key=YOUTUBE_API_SECRET)
    yt_service.ssl = False
    return yt_service


yt_service = get_youtube_service()


@task
def save_subtitles_for_lang(lang, video_pk, youtube_id):
    from django.utils.encoding import force_unicode
    from videos.models import Video
    from videos.tasks import video_changed_tasks
    from subtitles.pipeline import add_subtitles
    from subtitles.models import ORIGIN_IMPORTED

    yt_lc = lang.get('lang_code')

    # TODO: Make sure we can store all language data given to us by Youtube.
    # Right now, the bcp47 codec will refuse data it can't reliably parse.
    try:
        lc  = LanguageCode(yt_lc, "bcp47").encode("unisubs")
    except KeyError:
        logger.warn("Youtube import did not find language code", extra={
            "data":{
                "language_code": yt_lc,
                "youtube_id": youtube_id,
            }
        })
        return

    if not lc in SUPPORTED_LANGUAGE_CODES:
        logger.warn("Youtube import did not find language code", extra={
            "data":{
                "language_code": lc,
                "youtube_id": youtube_id,
            }
        })
        return

    try:
        video = Video.objects.get(pk=video_pk)
    except Video.DoesNotExist:
        return

    url = u'http://www.youtube.com/api/timedtext?v=%s&lang=%s&name=%s&fmt=srt'
    url = url % (youtube_id, yt_lc, urlquote(lang.get('name', u'')))

    xml = YoutubeVideoType._get_response_from_youtube(url, return_string=True)

    if not bool(xml):
        return

    xml = force_unicode(xml, 'utf-8')

    subs = load_subtitles(lc, xml, 'srt')
    version = add_subtitles(video, lc, subs, note="From youtube", complete=True, origin=ORIGIN_IMPORTED)

    # do not pass a version_id else, we'll trigger emails for those edits
    video_changed_tasks.delay(video.pk)
    Meter('youtube.lang_imported').inc()
    from teams.models import BillingRecord
    # there is a caveat here, if running with CELERY_ALWAYS_EAGER,
    # this is called before there's a team video, and the billing records won't
    # be created. On the real world, it should be safe to assume that between
    # calling the youtube api and the db insertion, we'll get this called
    # when the video is already part of a team
    BillingRecord.objects.insert_record(version)


class YoutubeVideoType(VideoType):

    _url_patterns = [re.compile(x) for x in [
        r'youtube.com/.*?v[/=](?P<video_id>[\w-]+)',
        r'youtu.be/(?P<video_id>[\w-]+)',
    ]]

    HOSTNAMES = ( "youtube.com", "youtu.be", "www.youtube.com",)

    abbreviation = 'Y'
    name = 'Youtube'
    site = 'youtube.com'

    # changing this will cause havock, let's talks about this first
    URL_TEMPLATE = 'http://www.youtube.com/watch?v=%s'

    CAN_IMPORT_SUBTITLES = True

    def __init__(self, url):
        self.url = url
        self.videoid = self._get_video_id(self.url)

    @property
    def video_id(self):
        return self.videoid

    def convert_to_video_url(self):
        return 'http://www.youtube.com/watch?v=%s' % self.video_id

    @classmethod
    def video_url(cls, obj):
        """
        This method can be called with wither a VideoType object or
        an actual VideoURL object, therefore the if statement
        """
        if obj.videoid:
            return YoutubeVideoType.url_from_id(obj.videoid)
        else:
            return obj.url

    @classmethod
    def matches_video_url(cls, url):
        hostname = urlparse(url).netloc
        return (hostname in YoutubeVideoType.HOSTNAMES and
                any(pattern.search(url) for pattern in cls._url_patterns))

    def get_video_info(self):
        if not hasattr(self, '_video_info'):
            self._video_info = youtube.get_video_info(self.video_id)
        return self._video_info

    def set_values(self, video, fetch_subs_async=True):
        video_info = self.get_video_info()
        video.title = video_info.title
        video.description = video_info.description
        video.duration = video_info.duration
        video.thumbnail = video_info.thumbnail_url

        try:
            self.get_subtitles(video, async=fetch_subs_async)
        except :
            logger.exception("Error getting subs from youtube:" )

    def owner_username(self):
        return self.get_video_info().channel_id

    @classmethod
    def url_from_id(cls, video_id):
        return YoutubeVideoType.URL_TEMPLATE % video_id

    @classmethod
    def _get_video_id(cls, video_url):
        for pattern in cls._url_patterns:
            match = pattern.search(video_url)
            video_id = match and match.group('video_id')
            if bool(video_id):
                return video_id
        raise ValueError("Unknown video id")

    @classmethod
    def _get_response_from_youtube(cls, url, return_string=False):
        h = httplib2.Http()
        resp, content = h.request(url, "GET")

        if resp.status < 200 or resp.status >= 400:
            logger.error("Youtube subtitles error", extra={
                    'data': {
                        "url": url,
                        "status_code": resp.status,
                        "response": content
                        }
                    })
            return

        try:
            if return_string:
                return content
            return etree.fromstring(content)
        except etree.XMLSyntaxError:
            logger.error("Youtube subtitles error. Failed to parse response.", extra={
                    'data': {
                        "url": url,
                        "response": content
                        }
                    })
            return

    def get_subtitled_languages(self):
        url = "http://www.youtube.com/api/timedtext?type=list&v=%s" % self.video_id
        xml = self._get_response_from_youtube(url)

        if  xml is None:
            return []

        output = []
        for lang in xml.xpath('track'):
            item = dict(
                lang_code=lang.get('lang_code'),
                name=lang.get('name', u'')
            )
            output.append(item)

        return output

    def get_subtitles(self, video_obj, async=True):
        langs = self.get_subtitled_languages()

        if async:
            func = save_subtitles_for_lang.delay
        else:
            func = save_subtitles_for_lang.run
        for item in langs:
            func(item, video_obj.pk, self.video_id)
