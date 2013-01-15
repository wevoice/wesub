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


def response_data(self, r):
    status = r.status_code
    json_resp = r.json
    content_resp = r.content
    if json_resp == None:
        self.logger.info('RESP: {0}, CONTENT: {1}'.format(status, content_resp))
        return status, content_resp
    else:
        self.logger.info('RESP: {0}, JSON: {1}'.format(status, content_resp))
        return status, json_resp

def api_url(base_url, url_part):
    if 'api2/partners' in url_part:
        url = base_url + url_part[1:]
    else:
        url = base_url + 'api2/partners/' + url_part
    return url


def post_api_request(self, url_part, data):
    r = requests.session()
    r.config['keep_alive'] = False
    self.logger.info('POST request: {0} to {1}'.format(data, url_part))
    url = api_url(self.base_url, url_part)
    headers = { 'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-apikey': self.user.api_key.key,
                'X-api-username': self.user.username,
              } 
    req = r.post(url, data=simplejson.dumps(data), headers=headers)
    return response_data(self, req) 


def put_api_request(self, url_part, data):
    self.logger.info('PUT request: {0} to {1}'.format(data, url_part))
    r = requests.session()
    r.config['keep_alive'] = False
    url = api_url(self.base_url, url_part)
    headers = { 'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-apikey': self.user.api_key.key,
                'X-api-username': self.user.username,
              } 

    req = r.put(url, data=simplejson.dumps(data), headers=headers)
    return response_data(self, req) 

def delete_api_request(self, url_part):
    self.logger.info('DELETE request: %s' %url_part)
 
    url = api_url(self.base_url, url_part)
    headers = { 'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-apikey': self.user.api_key.key,
                'X-api-username': self.user.username,
              } 

    r = requests.delete(url, headers=headers)
    self.logger.info('RESP CODE: '+ str(r.status_code))
    return r.status_code, r.content

def api_get_request(self, url_part, output_type='json'):
    url = api_url(self.base_url, url_part)
    self.logger.info('GET request: %s' %url)

    headers = { 'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-apikey': self.user.api_key.key,
                'X-api-username': self.user.username,
              }
    r = requests.get(url, headers=headers)
    self.logger.info('RESP CODE: '+ str(r.status_code))
    return r.status_code, getattr(r, output_type)



def create_video(self, video_url=None):
    if not video_url:
        video_url = 'http://www.youtube.com/watch?v=WqJineyEszo'
    self.logger.info('Add video: %s, using get_or_create_for_url' %video_url)

    video, _ = Video.get_or_create_for_url(video_url)
    return video

def upload_subs(self, video, data):
    self.logger.info('Uploading subs via client.post')
    self.client.login(**self.auth)
    response = self.client.post(reverse('videos:upload_subtitles'), data)
    self.logger.info('Uploading subs via client: %s' % response)

def create_video_with_subs(self, video_url=None, data=None):
    """Create a video and subtitles.

    """
    video = create_video(self, video_url)
    if not data:
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft':  open('apps/videos/fixtures/test.srt'),
                'is_complete': True,
                'complete': 1
                }
    upload_subs(self, video, data)
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
    self.logger.info('Adding team videos with subtitle data: %s' % testdata)
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
    self.logger.info('Adding video with fake sub data: %s' % testdata)
    videos = _create_videos(testdata, [])
    return videos


    

