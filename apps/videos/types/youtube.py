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
import logging
import re
from urlparse import urlparse
import babelsubs
import requests

import gdata.youtube.client
import httplib2
from celery.task import task
from django.conf import settings
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from gdata.service import RequestError
from gdata.youtube.service import YouTubeService
from lxml import etree

from base import VideoType, VideoTypeError
from utils.translation import SUPPORTED_LANGUAGE_CODES

from unilangs.unilangs import LanguageCode


logger = logging.getLogger("youtube")

YOUTUBE_API_SECRET  = getattr(settings, "YOUTUBE_API_SECRET", None)


_('Private video')
_('Undefined error')


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

    yt_lc = lang.get('lang_code')
    # TODO: Make sure we can store all language data given to us by Youtube.
    # Right now, the bcp47 codec will refuse data it can't reliably parse.
    lc  = LanguageCode(yt_lc, "bcp47").encode("unisubs")

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

    url = u'http://www.youtube.com/api/timedtext?v=%s&lang=%s&name=%s'
    url = url % (youtube_id, yt_lc, urlquote(lang.get('name', u'')))

    xml = YoutubeVideoType._get_response_from_youtube(url, return_string=True)

    if xml is None:
        return

    xml = force_unicode(xml, 'utf-8')

    subs = babelsubs.parsers.discover('youtube').parse(xml).to_internal()
    add_subtitles(video, lc, subs)

    video_changed_tasks.delay(video.pk)


def add_credit(subtitle_version, subs):
    # If there are no subtitles, don't add any credits.  This shouldn't really
    # happen since only completed subtitle versions can be synced to Youtube.
    # But a little precaution never hurt anyone.
    if len(subs) == 0:
        return subs

    from accountlinker.models import get_amara_credit_text

    language_code = subtitle_version.language_code
    dur = subtitle_version.video.duration

    last_sub = subs[-1]
    time_left_at_the_end = (dur * 1000) - last_sub[1]

    if time_left_at_the_end <= 0:
        return subs

    if time_left_at_the_end >= 3000:
        start = (dur - 3) * 1000
    else:
        start = (dur * 1000) - time_left_at_the_end

    subs.append_subtitle(
        start,
        dur * 1000,
        get_amara_credit_text(language_code),
        {}
    )

    return subs

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
    
    def __init__(self, url):
        self.url = url
        self.videoid = self._get_video_id(self.url)
        self.entry = self._get_entry(self.video_id)
        author = self.entry.author[0]
        self.username = author.name.text

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
        return  hostname in YoutubeVideoType.HOSTNAMES and  cls._get_video_id(url)

    def create_kwars(self):
        return {'videoid': self.video_id}

    def set_values(self, video_obj):
        video_obj.title = self.entry.media.title.text or ''
        if self.entry.media.description:
            video_obj.description = self.entry.media.description.text or ''
        if self.entry.media.duration:
            video_obj.duration = int(self.entry.media.duration.seconds)
        if self.entry.media.thumbnail:
            # max here will return the thumbnail with the biggest height
            thumbnail = max([(int(t.height), t) for t in self.entry.media.thumbnail]) 
            video_obj.thumbnail = thumbnail[1].url
        video_obj.small_thumbnail = 'http://i.ytimg.com/vi/%s/default.jpg' % self.video_id
        video_obj.save()

        try:
            self.get_subtitles(video_obj)
        except :
            logger.exception("Error getting subs from youtube:" )

        return video_obj

    def _get_entry(self, video_id):
        try:
            return yt_service.GetYouTubeVideoEntry(video_id=str(video_id))
        except RequestError, e:
            err = e[0].get('body', 'Undefined error')
            raise VideoTypeError('Youtube error: %s' % err)

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
        return False

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

    def get_subtitles(self, video_obj):
        langs = self.get_subtitled_languages()

        for item in langs:
            save_subtitles_for_lang.delay(item, video_obj.pk, self.video_id)

    def _get_bridge(self, third_party_account):

        return YouTubeApiBridge(third_party_account.oauth_access_token,
                                  third_party_account.oauth_refresh_token,
                                  self.videoid)

    def update_subtitles(self, subtitle_version, third_party_account):
        """
        Updated subtitles on Youtube. This method should not be called
        directly. See accountlinker.models.ThirdPartyAccounts.mirror_on_third_party
        That call will check if the video can be updated(must be synched,
        must be public, etc).
        """
        bridge = self._get_bridge(third_party_account)
        bridge.upload_captions(subtitle_version)

    def delete_subtitles(self, language, third_party_account):
        bridge = self._get_bridge(third_party_account)
        bridge.delete_subtitles(language)


def _prepare_subtitle_data_for_version(subtitle_version):
    """
    Given a subtitles.models.SubtitleVersion, return a tuple of srt content,
    title and language code.
    """
    language_code = subtitle_version.subtitle_language.language_code

    try:
        lc = LanguageCode(language_code.lower(), "unisubs")
        language_code = lc.encode("bcp47")
    except KeyError:
        error = "Couldn't encode LC %s to youtube" % language_code
        logger.error(error)
        raise KeyError(error)

    subs = subtitle_version.get_subtitles()
    subs = add_credit(subtitle_version, subs)
    content = babelsubs.generators.discover('srt').generate(subs)
    content = unicode(content).encode('utf-8')

    return content, "", language_code


class YouTubeApiBridge(gdata.youtube.client.YouTubeClient):

    upload_uri_base = 'http://gdata.youtube.com/feeds/api/users/default/uploads/%s'

    def __init__(self, access_token, refresh_token, youtube_video_id):
        """
        A wrapper around the gdata client, to make life easier.
        In order to edit captions for a video, the oauth credentials
        must be that video's owner on youtube.
        """
        super(YouTubeApiBridge, self).__init__()
        self.access_token = access_token
        self.refresh_token = refresh_token

        self.token = gdata.gauth.OAuth2Token(
            client_id=settings.YOUTUBE_CLIENT_ID,
            client_secret=settings.YOUTUBE_CLIENT_SECRET,
            scope='https://gdata.youtube.com',
            user_agent='universal-subtitles',
            access_token=access_token,
            refresh_token=refresh_token
        )
        self.token.authorize(self)
        self.youtube_video_id  = youtube_video_id

    def refresh(self):
        """
        Refresh the access token
        """
        url = 'https://accounts.google.com/o/oauth2/token'

        data = {
            'client_id': settings.YOUTUBE_CLIENT_ID,
            'client_secret': settings.YOUTUBE_CLIENT_SECRET,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }

        r = requests.post(url, data=data)
        self.access_token = r.json.get('access_token')

    def _get_captions_info(self):
        """
        Retrieves a dictionary with the current caption data for this youtube video.
        Format is:
        {
            "lang_code": {
                   "url": [url for track]
                    "track": [track entry object, useful for other operations]
             }
        }
        """
        self.captions  = {}
        entry = self.GetVideoEntry(video_id=self.youtube_video_id)
        caption_track = entry.get_link(rel='http://gdata.youtube.com/schemas/2007#video.captionTracks')

        if not caption_track:
            # No tracks were returned.  This video doesn't have any existing
            # captions.
            return self.captions

        captions_feed = self.get_feed(caption_track.href, desired_class=gdata.youtube.data.CaptionFeed)
        captions = captions_feed.entry

        for entry in captions:
            lang = entry.get_elements(tag="content")[0].lang
            url = entry.get_edit_media_link().href
            self.captions[lang] = {
                "url": url,
                "track": entry
            }

        return self.captions

    def upload_captions(self, subtitle_version):
        """
        Will upload the subtitle version to this youtube video id.
        If the subtitle already exists, will delete it and recreate it.
        This subs should be synced! Else we upload might fail.
        """
        # TODO: The language_code here is in "unisubs" and should be encoded
        # to bcp47.
        content, title, language_code = \
                self._prepare_subtitle_data_for_version(subtitle_version)

        if hasattr(self, "captions") is False:
            self._get_captions_info()

        # We can't just update a subtitle track in place.  We need to delete
        # the old one and upload a new one.
        if language_code in self.captions:
            self._delete_track(self.captions[language_code]['track'])

        self.add_credit_to_description(subtitle_version)

        return self.create_track(self.youtube_video_id, title, language_code,
                content, settings.YOUTUBE_CLIENT_ID,
                settings.YOUTUBE_API_SECRET, self.token, {'fmt':'srt'})

    def add_credit_to_description(self, subtitle_version):
        """
        Get the entry information from Youtube, extract the original
        description, prepend the description with Amara credits and push it
        back to Youtube.

        If our update call doesn't succeed on the first try, we refresh the
        access token and try again.

        If the existing description starts with the credit text, we just
        return.
        """
        from accountlinker.models import add_amara_description_credit
        uri = self.upload_uri_base % self.youtube_video_id

        entry = self.GetVideoEntry(uri=uri)
        entry = entry.to_string()
        entry = gdata.youtube.YouTubeVideoEntryFromString(entry)

        old_description = entry.media.description.text

        video = subtitle_version.language.video

        current_site = Site.objects.get_current()
        video_url = video.get_absolute_url()
        video_url = u"http://%s%s" % (unicode(current_site.domain),
                video_url)

        language_code = video.language

        if not language_code:
            language_code = 'en'

        new_description = add_amara_description_credit(old_description,
                video_url, language_code)

        if new_description == old_description:
            return True

        entry.media.description.text = new_description
        entry = entry.ToString()

        status_code = self._make_update_request(uri, entry)

        if status_code == 401:
            self.refresh()
            status_code = self._make_update_request(uri, entry)

        if status_code == 200:
            return True

        return False

    def _make_update_request(self, uri, entry):
        headers = {
            'Content-Type': 'application/atom+xml',
            'Authorization': 'Bearer %s' % self.access_token,
            'GData-Version': '2',
            'X-GData-Key': 'key=%s' % YOUTUBE_API_SECRET
        }
        r = requests.put(uri, data=entry, headers=headers)
        return r.status_code

    def _delete_track(self, track):
        res = self.delete_track(self.youtube_video_id, track,
                settings.YOUTUBE_CLIENT_ID, settings.YOUTUBE_API_SECRET,
                self.token)
        return res

    def delete_subtitles(self, language):
        """
        Deletes the subtitles for this language on this YouTube video.
        Smart enought to determine if this video already has such subs

        """
        try:
            lc = LanguageCode(language, "unisubs")
            lang = lc.encode("youtube")
        except KeyError:
            logger.error("Couldn't encode LC %s to youtube" % language)
            return

        if hasattr(self, "captions") is False:
            self._get_captions_info()
        if lang in self.captions:
            self._delete_track(self.captions[lang]['track'])
        else:
            logger.error("Couldn't find LC %s in youtube" % lang)
