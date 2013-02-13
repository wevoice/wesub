from haystack.indexes import *
from haystack.models import SearchResult
from haystack import site
from models import Video
from apps.subtitles.models import SubtitleLanguage, Collaborator
from utils.celery_search_index import CelerySearchIndex
from django.conf import settings
from haystack.query import SearchQuerySet
import datetime

from haystack.exceptions import AlreadyRegistered

class VideoIndex(CelerySearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField(model_attr='title_display', boost=2)
    languages = MultiValueField(faceted=True)
    video_language = CharField(faceted=True)
    languages_count = IntegerField()
    video_id = CharField(model_attr='video_id', indexed=False)
    thumbnail_url = CharField(model_attr='get_thumbnail', indexed=False)
    small_thumbnail = CharField(model_attr='get_small_thumbnail', indexed=False)
    created = DateTimeField(model_attr='created')
    edited = DateTimeField(model_attr='edited')
    subtitles_fetched_count = IntegerField(model_attr='subtitles_fetched_count')
    widget_views_count = IntegerField(model_attr='widget_views_count')
    comments_count = IntegerField()

    contributors_count = IntegerField()
    activity_count = IntegerField()
    featured = DateTimeField(model_attr='featured', null=True)

    today_views = IntegerField()
    week_views = IntegerField()
    month_views = IntegerField()
    year_views = IntegerField()
    total_views = IntegerField(model_attr='widget_views_count')

    # non public videos won't show up in any of the site's listing
    # not even for the owner
    is_public = BooleanField()

    IN_ROW = getattr(settings, 'VIDEO_IN_ROW', 6)

    def prepare(self, obj):
        self.prepared_data = super(VideoIndex, self).prepare(obj)

        languages = SubtitleLanguage.objects.having_nonempty_versions().filter(video=obj)
        collaborators = Collaborator.objects.filter(subtitle_language__video=obj).values("user").distinct().count()
        followers = obj.newsubtitlelanguage_set.all().values("followers").distinct().count()

        self.prepared_data['languages_count'] = languages.count()
        self.prepared_data['video_language'] = obj.primary_audio_language_code
        self.prepared_data['languages'] = [language.language_code for language in languages]
        self.prepared_data['contributors_count'] = collaborators + followers
        self.prepared_data['activity_count'] = obj.action_set.count()
        self.prepared_data['week_views'] = obj.views['week']
        self.prepared_data['month_views'] = obj.views['month']
        self.prepared_data['year_views'] = obj.views['year']
        self.prepared_data['today_views'] = obj.views['today']
        self.prepared_data['title'] = obj.title_display(truncate=False).strip()
        self.prepared_data['is_public'] = obj.is_public

        return self.prepared_data

    def _setup_save(self, model):
        pass


    def _teardown_save(self, model):
        pass

    def index_queryset(self):
        return self.model.objects.order_by('-id')

    @classmethod
    def public(self):
        """
        All regular queries should go through this method, as it makes
        sure we never display videos that should be hidden
        """
        return SearchQuerySet().result_class(VideoSearchResult) \
            .models(Video).filter(is_public=True)

    @classmethod
    def get_featured_videos(cls):
        return  VideoIndex.public().filter(featured__gt=datetime.datetime(datetime.MINYEAR, 1, 1)) \
            .order_by('-featured')

    @classmethod
    def get_popular_videos(cls, sort='-week_views'):
        return  VideoIndex.public().order_by(sort)

    @classmethod
    def get_latest_videos(cls):
        return VideoIndex.public().order_by('-created')

class VideoSearchResult(SearchResult):
    title_for_url = Video.__dict__['title_for_url']
    get_absolute_url = Video.__dict__['_get_absolute_url']

    def __unicode__(self):
        title = self.title

        if len(title) > 60:
            title = title[:60]+'...'

        return title

try:
    site.register(Video, VideoIndex)
except AlreadyRegistered:
    # i hate python imports with all my will.
    # i hope they die.
    pass
