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
from django.test.client import RequestFactory, Client
from django.contrib.sites.models import Site



class DataHelpers(object):

    def create_user_api_key(self, user_obj):
        c = Client()
        c.login(username=user_obj.username, password='password')
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
            return status, content_resp
        else:
            return status, json_resp

    def api_url(self, url_part):
        base_url = 'http://%s/' % Site.objects.get_current().domain
        if 'api2/partners' in url_part:
            url = base_url + url_part[1:]
        else:
            url = base_url + 'api2/partners/' + url_part
        return url


    def post_api_request(self, user, url_part, data):
        r = requests.session()
        r.config['keep_alive'] = False
        url = self.api_url(url_part)
        headers = { 'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-apikey': user.api_key.key,
                    'X-api-username': user.username,
                  } 
        req = r.post(url, data=simplejson.dumps(data), headers=headers)
        return self.response_data(req) 


    def put_api_request(self, user, url_part, data):
        r = requests.session()
        r.config['keep_alive'] = False
        url = self.api_url(url_part)
        headers = { 'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-apikey': user.api_key.key,
                    'X-api-username': user.username,
                  } 

        req = r.put(url, data=simplejson.dumps(data), headers=headers)
        return self.response_data(req) 

    def delete_api_request(self, user, url_part):
 
        url = self.api_url(url_part)
        headers = { 'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-apikey': user.api_key.key,
                    'X-api-username': user.username,
                  } 

        r = requests.delete(url, headers=headers)
        return r.status_code, r.content

    def api_get_request(self, user, url_part, output_type='json'):
        url = self.api_url(url_part)
    
        headers = { 'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-apikey': user.api_key.key,
                    'X-api-username': user.username,
                  }
        r = requests.get(url, headers=headers)
        return r.status_code, getattr(r, output_type)



    def create_video(self, video_url=None):
        if not video_url:
            video_url = 'http://www.youtube.com/watch?v=WqJineyEszo'

        video, _ = Video.get_or_create_for_url(video_url)
        print video
        print video.title
        return video

    def super_user(self):
        superuser = UserFactory(is_partner=True, 
                                 is_staff=True, 
                                 is_superuser=True) 
        auth = dict(username=superuser.username, password='password')
        return auth


    def upload_subs(self, video, data):
        c = Client()
        c.login(**self.super_user())
        response = c.post(reverse('videos:upload_subtitles'), data)

    def create_video_with_subs(self, video_url=None, data=None):
        """Create a video and subtitles.
    
        """
        video = self.create_video(video_url)
        if not data:
            data = {'language_code': 'en',
                    'video': video.pk,
                    'primary_audio_language_code': 'en',
                    'draft':  open('apps/videos/fixtures/test.srt'),
                    'is_complete': True,
                    'complete': 1
                    }
        self.upload_subs(video, data)
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
        print videos
        return videos
        

