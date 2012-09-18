from apps.videos.models import Video
from django.core.urlresolvers import reverse
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.teams.models import TeamMember
import json
from apps.testhelpers.views import _create_videos



def create_video_with_subs(self, video_url=None, data=None):
    """Create a video and subtitles.

    """
    self.client.login(**self.auth)
    if not video_url:
        video_url = 'http://www.youtube.com/watch?v=WqJineyEszo'
    video, _ = Video.get_or_create_for_url(video_url)
    if not data:
        data = {
        'language': 'en',
        'video_language': 'en',
        'video': video.pk,
        'draft': open('apps/videos/fixtures/test.srt'),
        'is_complete': True
    }
    response = self.client.post(reverse('videos:upload_subtitles'), data)
    print response
    return video


def create_several_team_videos_with_subs(self, team, teamowner, data=None):
    """Uses the helper data from the apps.videos.fixtures to create data.

       The test vidoes are then assigned to the specified team.
       Returns the list of video.

    """
    if not data:
        testdata = json.load(open('apps/videos/fixtures/teams-list.json'))
    else:
        testdata = json.load(open(data))
    videos = _create_videos(testdata, [])
    for video in videos:
        TeamVideoFactory.create(
            team=team, 
            video=video, 
            added_by=teamowner)
    return videos


