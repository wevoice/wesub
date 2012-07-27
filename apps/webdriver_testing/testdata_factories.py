import datetime
import factory
from apps.videos.models import Video
from apps.videos.models import SubtitleLanguage
from apps.videos.models import Action

class SubtitleLanguageFactory(factory.Factory):
    FACTORY_FOR = SubtitleLanguage
    language = 'en'
    subtitle_count = 10
    is_complete = True
    is_original = True

class VideoFactory(factory.Factory):
    FACTORY_FOR = Video
    title = "Test Video"
    description = "Greatest Video ever made"


class ActionFactory(factory.Factory):
    FACTORY_FOR = Action
    video, _ = Video.get_or_create_for_url('http://www.youtube.com/watch?v=WqJineyEszo')
    created = datetime.datetime.now()

    
