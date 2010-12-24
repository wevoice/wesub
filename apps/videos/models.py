# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
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

from django.db import models
import string
import random
from auth.models import CustomUser as User, Awards
from datetime import datetime, date, timedelta
from django.db.models.signals import post_save
from django.utils.dateformat import format as date_format
from gdata.youtube.service import YouTubeService
from comments.models import Comment
from videos import EffectiveSubtitle
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from videos.types import video_type_registrar
from utils.amazon import default_s3_store
from statistic.models import SubtitleFetchStatistic
from widget import video_cache
from datetime import datetime
from utils.redis_utils import RedisSimpleField
from django.template.defaultfilters import slugify
from utils.amazon import S3EnabledImageField
import time

yt_service = YouTubeService()
yt_service.ssl = False

NO_SUBTITLES, SUBTITLES_FINISHED = range(2)
VIDEO_TYPE_HTML5 = 'H'
VIDEO_TYPE_YOUTUBE = 'Y'
VIDEO_TYPE_BLIPTV = 'B'
VIDEO_TYPE_GOOGLE = 'G'
VIDEO_TYPE_FORA = 'F'
VIDEO_TYPE_USTREAM = 'U'
VIDEO_TYPE_VIMEO = 'V'
VIDEO_TYPE_DAILYMOTION = 'D'
VIDEO_TYPE_FLV = 'L'
VIDEO_TYPE = (
    (VIDEO_TYPE_HTML5, 'HTML5'),
    (VIDEO_TYPE_YOUTUBE, 'Youtube'),
    (VIDEO_TYPE_BLIPTV, 'Blip.tv'),
    (VIDEO_TYPE_GOOGLE, 'video.google.com'),
    (VIDEO_TYPE_FORA, 'Fora.tv'),
    (VIDEO_TYPE_USTREAM, 'Ustream.tv'),
    (VIDEO_TYPE_VIMEO, 'Vimeo.com'),
    (VIDEO_TYPE_DAILYMOTION, 'dailymotion.com'),
    (VIDEO_TYPE_FLV, 'FLV')
)
WRITELOCK_EXPIRATION = 30 # 30 seconds
VIDEO_SESSION_KEY = 'video_session'

ALL_LANGUAGES = [(val, _(name))for val, name in settings.ALL_LANGUAGES]

class Video(models.Model):
    """Central object in the system"""
    video_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=2048, blank=True)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    view_count = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(null=True, blank=True)
    allow_community_edits = models.BooleanField()
    allow_video_urls_edit = models.BooleanField(default=True)
    writelock_time = models.DateTimeField(null=True, editable=False)
    writelock_session_key = models.CharField(max_length=255, editable=False)
    writelock_owner = models.ForeignKey(User, null=True, editable=False,
                                        related_name="writelock_owners")
    subtitles_fetched_count = models.IntegerField(default=0)
    widget_views_count = models.IntegerField(default=0)
    is_subtitled = models.BooleanField(default=False)
    was_subtitled = models.BooleanField(default=False)
    thumbnail = models.CharField(max_length=500, blank=True)
    s3_thumbnail = S3EnabledImageField(blank=True, upload_to='video/thumbnail/')
    edited = models.DateTimeField(null=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True)
    followers = models.ManyToManyField(User, blank=True, related_name='followed_videos')

    subtitles_fetchec_counter = RedisSimpleField('video_id')
    widget_views_counter = RedisSimpleField('video_id')
    
    def __unicode__(self):
        title = self.title_display()
        if len(title) > 70:
            title = title[:70]+'...'
        return title
    
    def update_subtitles_fetched(self, lang=None):
        self.subtitles_fetchec_counter.incr()
        #Video.objects.filter(pk=self.pk).update(subtitles_fetched_count=models.F('subtitles_fetched_count')+1)
        st_obj = SubtitleFetchStatistic(video=self)
        sub_lang = self.subtitle_language(lang)
        if sub_lang:
            st_obj.language = lang or ''
            SubtitleLanguage.subtitles_fetched_counter(sub_lang.pk).incr()
            #SubtitleLanguage.objects.filter(pk=sub_lang.pk).update(subtitles_fetched_count=models.F('subtitles_fetched_count')+1)
        st_obj.save()
        
    def get_thumbnail(self):
        if self.s3_thumbnail:
            return self.s3_thumbnail.thumb_url(100, 100)
        
        if self.thumbnail:
            return self.thumbnail
        
        return ''
    
    def get_small_thumbnail(self):
        if self.s3_thumbnail:
            return self.s3_thumbnail.thumb_url(50, 50)
        
        return ''        
    
    @models.permalink
    def video_link(self):
        return ('videos:history', [self.video_id])
    
    def thumbnail_link(self):
        if not self.thumbnail:
            return ''

        if self.thumbnail.startswith('http://'):
            return self.thumbnail
        
        return settings.MEDIA_URL+self.thumbnail
        
    def is_html5(self):
        try:
            return self.videourl_set.filter(original=True)[:1].get().is_html5()
        except models.ObjectDoesNotExist:
            return False
    
    def title_display(self):
        if self.title:
            return self.title
        
        try:
            url = self.videourl_set.all()[:1].get().url
            if not url:
                return 'No title'
        except models.ObjectDoesNotExist:
            return 'No title'
        
        url = url.strip('/')

        if url.startswith('http://'):
            url = url[7:]

        parts = url.split('/')
        if len(parts) > 1:
            return '%s/.../%s' % (parts[0], parts[-1])
        else:
            return url

    def search_page_url(self):
        return self.get_absolute_url()

    @models.permalink
    def get_absolute_url(self):
        return ('videos:video', [self.video_id])

    def get_video_url(self):
        try:
            return self.videourl_set.filter(primary=True).all()[:1].get().effective_url
        except models.ObjectDoesNotExist:
            pass

    @classmethod
    def get_or_create_for_url(cls, video_url=None, vt=None, user=None):
        vt = vt or video_type_registrar.video_type_for_url(video_url)
        if not vt:
            return None, False

        try:
            video_url_obj = VideoUrl.objects.get(
                url=vt.convert_to_video_url())
            return video_url_obj.video, False
        except models.ObjectDoesNotExist:
            pass
        
        try:
            video_url_obj = VideoUrl.objects.get(
                type=vt.abbreviation, **vt.create_kwars())
            if user:
                Action.create_video_handler(video_url_obj.video, user)
            return video_url_obj.video, False
        except models.ObjectDoesNotExist:
            obj = Video()
            obj = vt.set_values(obj)
            if obj.title:
                obj.slug = slugify(obj.title)
            obj.user = user
            obj.save()
            
            Action.create_video_handler(obj, user)
            
            SubtitleLanguage(video=obj, is_original=True).save()
            #Save video url
            video_url_obj = VideoUrl()
            if vt.video_id:
                video_url_obj.videoid = vt.video_id
            video_url_obj.url = vt.convert_to_video_url()
            video_url_obj.type = vt.abbreviation
            video_url_obj.original = True
            video_url_obj.primary = True
            video_url_obj.added_by = user
            video_url_obj.video = obj
            video_url_obj.save()
            
            return obj, True
    
    @property
    def filename(self):
        from django.utils.text import get_valid_filename
        
        return get_valid_filename(self.__unicode__())
            
    def lang_filename(self, language):
        name = self.filename
        lang = language.language or u'original'
        return u'%s.%s' % (name, lang)
    
    @property
    def subtitle_state(self):
        """Subtitling state for this video 
        """
        return NO_SUBTITLES if self.latest_version() \
            is None else SUBTITLES_FINISHED

    def _original_subtitle_language(self):
        if not hasattr(self, '_original_subtitle'):
            try:
                original = self.subtitlelanguage_set.filter(is_original=True)[:1].get()
            except models.ObjectDoesNotExist:
                original = None

            setattr(self, '_original_subtitle', original)

        return getattr(self, '_original_subtitle')       

    def subtitle_language(self, language_code=None):
        try:
            if language_code is None:
                return self._original_subtitle_language()
            else:
                return self.subtitlelanguage_set.filter(
                    language=language_code)[:1].get()
        except models.ObjectDoesNotExist:
            return None

    def version(self, version_no=None, language_code=None):
        language = self.subtitle_language(language_code)
        return None if language is None else language.version(version_no)

    def latest_version(self, language_code=None):
        language = self.subtitle_language(language_code)
        return None if language is None else language.latest_version()

    def subtitles(self, version_no=None, language_code=None):
        version = self.version(version_no, language_code)
        if version:
            return version.subtitles()
        else:
            return Subtitle.objects.none()

    def latest_subtitles(self, language_code=None):
        version = self.latest_version(language_code)
        return [] if version is None else version.subtitles()

    def translation_language_codes(self):
        """All iso language codes with finished translations."""
        return set([sl.language for sl 
                    in self.subtitlelanguage_set.filter(
                    is_complete=True).filter(is_original=False)])

    @property
    def writelock_owner_name(self):
        """The user who currently has a subtitling writelock on this video."""
        if self.writelock_owner == None:
            return "anonymous"
        else:
            return self.writelock_owner.__unicode__()

    @property
    def is_writelocked(self):
        """Is this video writelocked for subtitling?"""
        if self.writelock_time == None:
            return False
        delta = datetime.now() - self.writelock_time
        seconds = delta.days * 24 * 60 * 60 + delta.seconds
        return seconds < WRITELOCK_EXPIRATION

    def can_writelock(self, request):
        """Can I place a writelock on this video for subtitling?"""
        if VIDEO_SESSION_KEY not in request.session:
            return False
        return self.writelock_session_key == \
            request.session[VIDEO_SESSION_KEY] or \
            not self.is_writelocked

    def writelock(self, request):
        """Writelock this video for subtitling."""
        self._make_writelock(request.user, request.session[VIDEO_SESSION_KEY])
    
    def _make_writelock(self, user, key):
        if user.is_authenticated():
            self.writelock_owner = user
        else:
            self.writelock_owner = None
        self.writelock_session_key = key
        self.writelock_time = datetime.now()        
    
    def release_writelock(self):
        """Writelock this video for subtitling."""
        self.writelock_owner = None
        self.writelock_session_key = ''
        self.writelock_time = None

    def notification_list(self, exclude=None):
        if self.subtitle_language():
            nl = self.subtitle_language().notification_list(exclude)
        else:
            nl = []
        for user in self.followers.all():
            if not user in nl: 
                nl.append(user)
        return nl
    
    def notification_list_all(self, exclude=None):
        users = []
        for language in self.subtitlelanguage_set.all():
            for u in language.notification_list(exclude):
                if not u in users:
                    users.append(u) 
        for user in self.followers.all():
            if not user in users: 
                users.append(user)                    
        return users
        
    def update_complete_state(self):
        language = self.subtitle_language()
        if not language.is_complete:
            self.is_subtitled = False
        else:
            self.is_subtitled = True
            self.was_subtitled = True


def create_video_id(sender, instance, **kwargs):
    instance.edited = datetime.now()
    if not instance or instance.video_id:
        return
    alphanum = string.letters+string.digits
    instance.video_id = ''.join([alphanum[random.randint(0, len(alphanum)-1)] 
                                                           for i in xrange(12)])
models.signals.pre_save.connect(create_video_id, sender=Video)

class SubtitleLanguage(models.Model):
    video = models.ForeignKey(Video)
    is_original = models.BooleanField()
    language = models.CharField(max_length=16, choices=ALL_LANGUAGES, blank=True)
    writelock_time = models.DateTimeField(null=True)
    writelock_session_key = models.CharField(max_length=255, blank=True)
    writelock_owner = models.ForeignKey(User, null=True)
    is_complete = models.BooleanField(default=False)
    was_complete = models.BooleanField(default=False)
    is_forked = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    subtitles_fetched_count = models.IntegerField(default=0)
    followers = models.ManyToManyField(User, blank=True, related_name='followed_languages')
    
    subtitles_fetched_counter = RedisSimpleField()
    
    class Meta:
        unique_together = (('video', 'language'),)
    
    def __unicode__(self):
        return u'%s(%s)' % (self.video, self.language_display())

    def update_complete_state(self):
        version = self.latest_version()
        if version.subtitle_set.count() == 0:
            self.is_complete = False
        else:
            self.is_complete = True
            self.was_complete = True
    
    @models.permalink
    def get_absolute_url(self):
        if self.is_original:
            return ('videos:history', [self.video.video_id])
        else:
            return ('videos:translation_history', [self.video.video_id, self.language])
    
    def language_display(self):
        if self.is_original and not self.language:
            return 'Original'
        return self.get_language_display()

    @property
    def writelock_owner_name(self):
        if self.writelock_owner == None:
            return "anonymous"
        else:
            return self.writelock_owner.__unicode__()

    @property
    def is_writelocked(self):
        if self.writelock_time == None:
            return False
        delta = datetime.now() - self.writelock_time
        seconds = delta.days * 24 * 60 * 60 + delta.seconds
        return seconds < WRITELOCK_EXPIRATION
    
    def can_writelock(self, request):
        if VIDEO_SESSION_KEY not in request.session:
            return False
        return self.writelock_session_key == \
            request.session[VIDEO_SESSION_KEY] or \
            not self.is_writelocked

    def writelock(self, request):
        if request.user.is_authenticated():
            self.writelock_owner = request.user
        else:
            self.writelock_owner = None
        self.writelock_session_key = request.session[VIDEO_SESSION_KEY]
        self.writelock_time = datetime.now()

    def release_writelock(self):
        self.writelock_owner = None
        self.writelock_session_key = ''
        self.writelock_time = None

    def version(self, version_no=None):
        if version_no is None:
            return self.latest_version()
        try:
            return self.subtitleversion_set.get(version_no=version_no)
        except models.ObjectDoesNotExist:
            pass
    
    def latest_version(self):
        try:
            return self.subtitleversion_set.all()[:1].get()
        except models.ObjectDoesNotExist:
            pass        
    
    def latest_subtitles(self):
        version = self.latest_version()
        if version:
            return version.subtitles()
        return []
        
    @property
    def percent_done(self):
        if not self.is_original and not self.is_forked:
            # FIXME: this calculation is incorrect. where are the unit tests?
            # for example, subtitles can be deleted, so it's quite easy 
            # for this to come up with a number greater than 100%
            try:
                translation_count = 0
                for item in self.latest_subtitles():
                    if item.text:
                        translation_count += 1
            except AttributeError:
                translation_count = 0
            last_version = self.video.latest_version()
            if last_version:
                subtitles_count = last_version.subtitle_set.count()
            else:
                subtitles_count = 0
            try:
                val = int(translation_count / 1. / subtitles_count * 100)
                return val <= 100 and val or 100
            except ZeroDivisionError:
                return 0 
        else:
            return 100

    def notification_list(self, exclude=None):
        qs = self.subtitleversion_set.all()
        not_send = StopNotification.objects.filter(video=self.video) \
            .values_list('user_id', flat=True)
        for_check = [item.user for item in qs]
        users = []
        for user in for_check:
            if user and user.is_active and user.changes_notification \
                and not user in users and not user.id in not_send \
                and not exclude == user:
                users.append(user)
        for user in self.followers.all():
            if not user in users:
                users.append(user)
        return users

post_save.connect(video_cache.on_subtitle_language_save, SubtitleLanguage)

class SubtitleCollection(models.Model):
    is_forked=models.BooleanField(default=False)

    class Meta:
        abstract = True

    def subtitles(self, subtitles_to_use=None):
        subtitles = subtitles_to_use or self.subtitle_set.all()
        if not self.is_dependent():
            return [EffectiveSubtitle.for_subtitle(s)
                    for s in subtitles]
        else:
            standard_collection = self._get_standard_collection()
            if not standard_collection:
                return []
            else:
                t_dict = \
                    dict([(s.subtitle_id, s) for s
                          in subtitles])
                subs = [s for s in standard_collection.subtitle_set.all()
                        if s.subtitle_id in t_dict]
                return [EffectiveSubtitle.for_dependent_translation(
                        s, t_dict[s.subtitle_id]) for s in subs]

class SubtitleVersion(SubtitleCollection):
    language = models.ForeignKey(SubtitleLanguage)
    version_no = models.PositiveIntegerField(default=0)
    datetime_started = models.DateTimeField()
    user = models.ForeignKey(User, null=True)
    note = models.CharField(max_length=512, blank=True)
    time_change = models.FloatField(null=True, blank=True)
    text_change = models.FloatField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-version_no']
        unique_together = (('language', 'version_no'),)
    
    def __unicode__(self):
        return u'%s #%s' % (self.language, self.version_no)
    
    def has_subtitles(self):
        return self.subtitle_set.exists()
    
    @models.permalink
    def get_absolute_url(self):
        return ('videos:revision', [self.pk])

    def is_dependent(self):
        return not self.language.is_original and not self.is_forked
    
    def revision_time(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        d = self.datetime_started.date()
        if d == today:
            return 'Today'
        elif d == yesterday:
            return 'Yesterday'
        else:
            d = d.strftime('%m/%d/%Y')
        return d
    
    def time_change_display(self):
        if not self.time_change:
            return '0%'
        else:
            return '%.0f%%' % (self.time_change*100)

    def text_change_display(self):
        if not self.text_change:
            return '0%'
        else:
            return '%.0f%%' % (self.text_change*100)

    def language_display(self):
        return self.language.language_display()

    @property
    def video(self):
        return self.language.video;

    def set_changes(self, old_version, new_subtitles=None):
        new_subtitles = self.subtitles(new_subtitles)
        subtitles_length = len(new_subtitles)

        if not old_version:
            #if it's first version set changes to 100
            #or it is forked subtitles version
            self.time_change = 1
            self.text_change = 1          
        elif subtitles_length == 0:
            old_subtitles_length = old_version.subtitle_set.count()
            if old_subtitles_length == 0:
                self.time_change = 0
                self.text_change = 0
            else:
                self.time_change = 1
                self.text_Change = 1
        else:
            old_subtitles = dict([(item.subtitle_id, item) 
                                  for item in old_version.subtitles()])
            time_count_changed, text_count_changed = 0, 0
            #compare subtitless one by one and count changes in time and text
            for subtitle in new_subtitles:
                try:
                    old_subtitle = old_subtitles[subtitle.subtitle_id]
                    if not old_subtitle.text == subtitle.text:
                        text_count_changed += 1
                    if not old_subtitle.start_time == subtitle.start_time or \
                            not old_subtitle.end_time == subtitle.end_time:
                        time_count_changed += 1
                except KeyError:
                    time_count_changed += 1
                    text_count_changed += 1
            self.time_change = time_count_changed / 1. / subtitles_length
            self.text_change = text_count_changed / 1. / subtitles_length

    def _get_standard_collection(self):
        return self.language.video.latest_version()

    def ordered_subtitles(self):
        subtitles = self.subtitles()
        subtitles.sort(key=lambda item: item.sub_order)
        return subtitles

    def prev_version(self):
        cls = self.__class__
        try:
            return cls.objects.filter(version_no__lt=self.version_no) \
                      .filter(language=self.language) \
                      .exclude(text_change=0, time_change=0)[:1].get()
        except models.ObjectDoesNotExist:
            pass
        
    def next_version(self):
        cls = self.__class__
        try:
            return cls.objects.filter(version_no__gt=self.version_no) \
                      .filter(language=self.language) \
                      .exclude(text_change=0, time_change=0) \
                      .order_by('version_no')[:1].get()
        except models.ObjectDoesNotExist:
            pass

    def rollback(self, user):
        cls = self.__class__
        latest_subtitles = self.language.latest_version()
        new_version_no = latest_subtitles.version_no + 1
        note = u'rollback to version #%s' % self.version_no
        new_version = cls(language=self.language, version_no=new_version_no, \
            datetime_started=datetime.now(), user=user, note=note)
        new_version.save()
        for item in self.subtitle_set.all():
            item.duplicate_for(version=new_version).save()
        return new_version

    def is_all_blank(self):
        for s in self.subtitles():
            if s.text.strip() != '':
                return False
        return True

post_save.connect(Awards.on_subtitle_version_save, SubtitleVersion)
post_save.connect(video_cache.on_subtitle_version_save, SubtitleVersion)

def update_video_edited_field(sender, instance, **kwargs):
    video = instance.language.video
    video.edited = datetime.now()
    video.save()

class SubtitleDraft(SubtitleCollection):
    language = models.ForeignKey(SubtitleLanguage)
    # null iff there is no SubtitleVersion yet.
    parent_version = models.ForeignKey(SubtitleVersion, null=True)
    datetime_started = models.DateTimeField()
    user = models.ForeignKey(User, null=True)
    browser_id = models.CharField(max_length=128, blank=True)
    last_saved_packet = models.PositiveIntegerField(default=0)

    @property
    def version_no(self):
        return 0 if self.parent_version is None else \
            self.parent_version.version_no + 1

    @property
    def video(self):
        return self.language.video

    def _get_standard_collection(self):
        return self.language.video.latest_version()

    def is_dependent(self):
        return not self.language.is_original and not self.is_forked

    def matches_request(self, request):
        if request.user.is_authenticated() and self.user and \
                self.user.pk == request.user.pk:
            return True
        else:
            return request.browser_id == self.browser_id

class Subtitle(models.Model):
    version = models.ForeignKey(SubtitleVersion, null=True)
    draft = models.ForeignKey(SubtitleDraft, null=True)
    subtitle_id = models.CharField(max_length=32, blank=True)
    subtitle_order = models.FloatField(null=True)
    subtitle_text = models.CharField(max_length=1024, blank=True)
    # in seconds
    start_time = models.FloatField(null=True)
    end_time = models.FloatField(null=True)
    
    class Meta:
        ordering = ['subtitle_order']
        unique_together = (('version', 'subtitle_id'),)

    def duplicate_for(self, version=None, draft=None):
        return Subtitle(version=version,
                        draft=draft,
                        subtitle_id=self.subtitle_id,
                        subtitle_order=self.subtitle_order,
                        subtitle_text=self.subtitle_text,
                        start_time=self.start_time,
                        end_time=self.end_time)

    @classmethod
    def trim_list(cls, subtitles):
        first_nonblank_index = -1
        last_nonblank_index = -1
        index = -1
        for subtitle in subtitles:
            index += 1
            if subtitle.subtitle_text.strip() != '':
                if first_nonblank_index == -1:
                    first_nonblank_index = index
                last_nonblank_index = index
        if first_nonblank_index != -1:
            return subtitles[first_nonblank_index:last_nonblank_index + 1]
        else:
            return []

    def update_from(self, caption_dict, is_dependent_translation=False):
        self.subtitle_text = caption_dict['text']
        if not is_dependent_translation:
            self.start_time = caption_dict['start_time']
            self.end_time = caption_dict['end_time']

    
class Action(models.Model):
    ADD_VIDEO = 1
    CHANGE_TITLE = 2
    COMMENT = 3
    ADD_VERSION = 4
    ADD_VIDEO_URL = 5
    TYPES = (
        (ADD_VIDEO, u'add video'),
        (CHANGE_TITLE, u'change title'),
        (COMMENT, u'comment'),
        (ADD_VERSION, u'add version'),
        (ADD_VIDEO_URL, u'add video url')
    )
    user = models.ForeignKey(User, null=True, blank=True)
    video = models.ForeignKey(Video)
    language = models.ForeignKey(SubtitleLanguage, blank=True, null=True)
    comment = models.ForeignKey(Comment, blank=True, null=True)
    action_type = models.IntegerField(choices=TYPES)
    new_video_title = models.CharField(max_length=2048, blank=True)
    created = models.DateTimeField()
    
    class Meta:
        ordering = ['-created']
        get_latest_by = 'created'
    
    def __unicode__(self):
        u = self.user and self.user.__unicode__() or 'Anonymous'
        return u'%s: %s(%s)' % (u, self.get_action_type_display(), self.created)
    
    def is_add_video_url(self):
        return self.action_type == self.ADD_VIDEO_URL
    
    def is_add_version(self):
        return self.action_type == self.ADD_VERSION
    
    def is_comment(self):
        return self.action_type == self.COMMENT
    
    def is_change_title(self):
        return self.action_type == self.CHANGE_TITLE
    
    def is_add_video(self):
        return self.action_type == self.ADD_VIDEO
    
    def type(self):
        if self.comment:
            return 'commented'
        return 'edited'
    
    def time(self):
        if self.created.date() == date.today():
            format = 'g:i A'
        else:
            format = 'g:i A, j M Y'
        return date_format(self.created, format)           
    
    def uprofile(self):
        try:
            return self.user.profile_set.all()[0]
        except IndexError:
            pass        
    
    @classmethod
    def create_comment_handler(cls, sender, instance, created, **kwargs):
        if created:
            model_class = instance.content_type.model_class()
            obj = cls(user=instance.user)
            obj.comment = instance
            obj.created = instance.submit_date
            obj.action_type = cls.COMMENT
            if issubclass(model_class, Video):
                obj.video_id = instance.object_pk
            if issubclass(model_class, SubtitleLanguage):
                obj.language_id = instance.object_pk
                obj.video = instance.content_object.video
            obj.save()
    
    @classmethod
    def create_caption_handler(cls, instance):
        user = instance.user
        video = instance.language.video
        language = instance.language
        
        obj = cls(user=user, video=video, language=language)
        obj.action_type = cls.ADD_VERSION
        obj.created = instance.datetime_started
        obj.save()            
    
    @classmethod
    def create_video_handler(cls, video, user=None):
        obj = cls(video=video)
        obj.action_type = cls.ADD_VIDEO
        obj.user = user
        obj.created = datetime.now()
        obj.save()
     
    @classmethod
    def create_video_url_handler(cls, sender, instance, created, **kwargs):
        if created:
            obj = cls(video=instance.video)
            obj.user = instance.added_by
            obj.action_type = cls.ADD_VIDEO_URL
            obj.created = instance.created
            obj.save()
                
post_save.connect(Action.create_comment_handler, Comment)        

class UserTestResult(models.Model):
    email = models.EmailField()
    browser = models.CharField(max_length=1024)
    task1 = models.TextField()
    task2 = models.TextField(blank=True)
    task3 = models.TextField(blank=True)
    get_updates = models.BooleanField(default=False)

class StopNotification(models.Model):
    video = models.ForeignKey(Video)
    user = models.ForeignKey(User)

class VideoUrlManager(models.Manager):
    
    def get_query_set(self):
        return super(VideoUrlManager, self).get_query_set().filter(deleted=False)

class VideoUrl(models.Model):
    video = models.ForeignKey(Video)
    type = models.CharField(max_length=1, choices=VIDEO_TYPE)
    url = models.URLField(max_length=255, unique=True)
    videoid = models.CharField(max_length=50, blank=True)
    primary = models.BooleanField(default=False)
    original = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, null=True, blank=True)
    deleted = models.BooleanField(default=False)
    
    objects = VideoUrlManager()
    all = models.Manager()
    
    def __unicode__(self):
        return self.url
    
    def is_html5(self):
        return self.type == VIDEO_TYPE_HTML5
    
    @models.permalink
    def get_absolute_url(self):
        return ('videos:video_url', [self.video.video_id, self.pk])
    
    def unique_error_message(self, model_class, unique_check):
        if unique_check[0] == 'url':
            return _('This URL already exists.')
        return super(VideoUrl, self).unique_error_message(model_class, unique_check)
    
    def created_as_time(self):
        #for sorting in js
        return time.mktime(self.created.timetuple())

    @property
    def effective_url(self):
        return video_type_registrar[self.type].video_url(self)

post_save.connect(Action.create_video_url_handler, VideoUrl)   
post_save.connect(video_cache.on_video_url_save, VideoUrl)
