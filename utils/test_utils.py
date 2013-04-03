import datetime
import urlparse

from uuid import uuid4


REQUEST_CALLBACKS = []

class Response(dict):

    status = 200
    content = ""

    def __getitem__(self, key):
        return getattr(self, key)

def reset_requests():
    global REQUEST_CALLBACKS
    REQUEST_CALLBACKS = []

def store_request_call(url, **kwargs):
    method = kwargs.pop('method', None)
    data = urlparse.parse_qs(kwargs.pop("body", ""))
    for k,v in data.items():
        data[k] = v[0]
    global REQUEST_CALLBACKS
    if not '/solr' in url:
        REQUEST_CALLBACKS.append([url, method, data])
    return Response(), ""

class TestCaseMessagesMixin(object):
    def _getMessagesCount(self, response, level=None):
        messages =  response.context['messages']
        if level:
            actual_num = len([x for x in messages if x.level==level])
        else:
            actual_num = len(messages)

        return actual_num

    def assertMessageCount(self, response, expect_num, level=None):
        """
        Asserts that exactly the given number of messages have been sent.
        """
        actual_num = self._getMessagesCount(response, level=level)
        if actual_num != expect_num:
            self.fail('Message count was %d, expected %d' %
                    (actual_num, expect_num)
                )

    def assertMessageEqual(self, response, text):
        """
        Asserts that the response includes the message text.
        """

        messages = [m.message for m in response.context['messages']]

        if text not in messages:
            self.fail(
                'No message with text "%s", messages were: %s' % 
                    (text, messages)
                )

    def assertMessageNotEqual(self, response, text):
        """
        Asserts that the response does not include the message text.
        """

        messages = [m.message for m in response.context['messages']]

        if text in messages:
            self.fail(
                'Message with text "%s" found, messages were: %s' % 
                    (text, messages)
                )

def add_subs(video, language_code, num_subs, is_synced=True,
             language_is_complete=True, language_is_original=False,
             translated_from=None, user=None, datetime_started=None):
    from apps.auth.models import CustomUser
    from apps.videos.models import (
        SubtitleLanguage, SubtitleVersion, Subtitle
        )
    language, created = SubtitleLanguage.objects.get_or_create(
        video=video,  language=language_code)
    language.is_complete = language_is_complete
    language.is_original = language_is_original
    translated_from_language = None
    if translated_from:
        translated_from_language = video.subtitlelanguage_set.get(language=translated_from)
    language.standard_language = translated_from_language
    if not translated_from_language:
        language.is_forked = True
    language.save()
    sv = None
    if num_subs:
        user = user if user else CustomUser.objects.get_or_create(username='test-user')[0]
        previous_version =  language.version(public_only=False)
        sv = SubtitleVersion.objects.create(
            version_no = previous_version.version_no +1 if previous_version else 1,
            language = language,
            user = user,
            datetime_started = datetime_started or datetime.datetime.now(),
            is_forked=language.is_forked,

        )
        source_subtiles = None
        if translated_from:
            source_subtiles = list(translated_from_language.version(public_only=False).subtitle_set.all())
        elif previous_version:
            source_subtiles = list(previous_version.subtitle_set.all())

        for sub_index in xrange(0, num_subs):

            if source_subtiles and len(source_subtiles) >= sub_index:
                id_ = source_subtiles[sub_index].subtitle_id
            else:
                id_ = str(uuid4())
            start_time = sub_index * 1000 if is_synced else None
            end_time = (sub_index * 1000) + 900 if is_synced else None
            Subtitle.objects.create(
                version = sv,
                subtitle_id = id_,
                subtitle_text = "Sub %s #%s" % (language_code, sub_index),
                subtitle_order = sub_index,
                start_time = start_time,
                end_time = end_time
            )

    return language, sv
