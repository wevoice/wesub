import datetime
import factory
from apps.videos.models import Video
from apps.videos.models import SubtitleLanguage
from apps.videos.models import Action
from apps.teams.models import Team, TeamMember
from apps.auth.models import CustomUser as User



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

class UserFactory(factory.Factory):
    FACTORY_FOR = User

class TeamFactory(factory.Factory):
    FACTORY_FOR = Team

class TeamMemberFactory(factory.Factory):
    FACTORY_FOR = TeamMember
    team = factory.SubFactory(TeamFactory)
    role = 'ROLE_OWNER'
    user = factory.SubFactory(UserFactory)

