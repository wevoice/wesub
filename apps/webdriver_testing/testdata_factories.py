import datetime
import factory
from apps.videos.models import Video, SubtitleLanguage
from apps.teams.models import Team, TeamMember, TeamVideo
from apps.auth.models import CustomUser as User



class VideoFactory(factory.Factory):
    FACTORY_FOR = Video
    title = factory.Sequence(lambda n: 'Test video number' + n)
    description = "Greatest Video ever made"

class SubtitleLanguageFactory(factory.Factory):
    FACTORY_FOR = SubtitleLanguage
    language = 'en'
    subtitle_count = 10
    is_complete = True
    is_original = True
    video = factory.SubFactory(VideoFactory)

class UserFactory(factory.Factory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: 'Test User' + n)
    password = 'sha1$pQQnrW0KJTHi$0000b329a889855361001a7e3bd113efbe818f7d'  # password = 'password' 
    email = 'testuser@example.com'

class TeamFactory(factory.Factory):
    FACTORY_FOR = Team
    name = factory.Sequence(lambda n: 'Test Team' + n)
    slug = factory.Sequence(lambda n: 'test-team-' +n)


class TeamMemberFactory(factory.Factory):
    FACTORY_FOR = TeamMember
    team = factory.SubFactory(TeamFactory)
    role = 'ROLE_OWNER'
    user = factory.SubFactory(UserFactory)


class TeamVideoFactory(factory.Factory):
    FACTORY_FOR = TeamVideo
    team = factory.SubFactory(TeamFactory)
    video = factory.SubFactory(VideoFactory)
    added_by = factory.SubFactory(UserFactory)
