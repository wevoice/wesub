from apps.videos.models import Video
from django.core.urlresolvers import reverse
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.teams.models import TeamMember
import json
from apps.testhelpers.views import _create_videos
from tastypie.models import ApiKey
from django.http import Http404, HttpResponse
from django.test.client import RequestFactory

def create_user_api_key(self, user_obj):
    self.client.login(username=user_obj.username, password='password')
    factory = RequestFactory()
    request = factory.get('/profiles/edit')
    key, created = ApiKey.objects.get_or_create(user=user_obj)
    if not created:
        key.key = key.generate_key()
        key.save()
    response =  HttpResponse(json.dumps({"key":key.key}))
    print response
    return response


def create_video(self, video_url=None):
    if not video_url:
        video_url = 'http://www.youtube.com/watch?v=WqJineyEszo'
    video, _ = Video.get_or_create_for_url(video_url)
    return video


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


def create_videos_with_fake_subs(self):
    testdata = json.load(open('apps/videos/fixtures/teams-list.json'))
    videos = _create_videos(testdata, [])
    return videos


    

