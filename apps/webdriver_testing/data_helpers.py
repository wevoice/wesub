from apps.videos.models import Video
from django.core.urlresolvers import reverse
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.teams.models import TeamMember
import simplejson
import requests
from apps.testhelpers.views import _create_videos
from tastypie.models import ApiKey
from django.http import HttpResponse
from django.test.client import RequestFactory


def create_user_api_key(self, user_obj):
    self.client.login(username=user_obj.username, password='password')
    factory = RequestFactory()
    request = factory.get('/profiles/edit')
    key, created = ApiKey.objects.get_or_create(user=user_obj)
    if not created:
        key.key = key.generate_key()
        key.save()
    response =  HttpResponse(simplejson.dumps({"key":key.key}))
    return response


def response_data(response):
    if response.json == None:
        return response.status_code, response.content
    else:
        return response.status_code, response.json

def post_api_request(self, url_part, data):
    print 'posting new data' 
    url = self.base_url + 'api2/partners/' + url_part
    headers = { 'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-apikey': self.user.api_key.key,
                'X-api-username': self.user.username,
              } 
    r = requests.post(url, data=simplejson.dumps(data), headers=headers)
    return response_data(r) 


def put_api_request(self, url_part, data):
    url = self.base_url + 'api2/partners/' + url_part
    headers = { 'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-apikey': self.user.api_key.key,
                'X-api-username': self.user.username,
              } 

    r = requests.put(url, data=simplejson.dumps(data), headers=headers)
    return response_data(r) 

def delete_api_request(self, url_part):
    url = self.base_url + 'api2/partners/' + url_part
    headers = { 'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-apikey': self.user.api_key.key,
                'X-api-username': self.user.username,
              } 

    r = requests.delete(url, headers=headers)
    return r.status_code, r.content

def api_get_request(self, url_part, output_type='json'):
    url = self.base_url + 'api2/partners/' + url_part
    headers = { 'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-apikey': self.user.api_key.key,
                'X-api-username': self.user.username,
              }
    r = requests.get(url, headers=headers)
    return r.status_code, getattr(r, output_type)


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
        'language_code': 'en',
        'video_language': 'en',
        'video': video.pk,
        'draft': open('apps/videos/fixtures/test.srt'),
        'is_complete': True
    }
    response = self.client.post(reverse('videos:upload_subtitles'), data)
    #print response
    return video


def create_several_team_videos_with_subs(self, team, teamowner, data=None):
    """Uses the helper data from the apps.videos.fixtures to create data.

       The test vidoes are then assigned to the specified team.
       Returns the list of video.

    """
    if not data:
        testdata = simplejson.load(open('apps/videos/fixtures/teams-list.json'))
    else:
        testdata = simplejson.load(open(data))
    videos = _create_videos(testdata, [])
    for video in videos:
        TeamVideoFactory.create(
            team=team, 
            video=video, 
            added_by=teamowner)
    return videos


def create_videos_with_fake_subs(self, testdata=None):
    if testdata is None:
        testdata = simplejson.load(open('apps/videos/fixtures/teams-list.json'))
    else:
        testdata = simplejson.load(open(testdata))
    videos = _create_videos(testdata, [])
    return videos


    

