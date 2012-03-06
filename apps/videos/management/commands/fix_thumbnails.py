from django.core.management import BaseCommand
from utils.amazon.fields import create_thumbnails
from boto.exception import S3ResponseError
from auth.models import CustomUser

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        """
        Reubilds thumbnails for the given model.
        Usage:
        python manage.py fix_thumbnails [ModelName,] # for one model
        python manage.py fix_thumbnails # for all model
        
        """
        from teams.models import Team, TeamVideo
        from videos.models import Video
            
        if 'Team' in args or len(args) ==0:
            for team in Team.objects.exclude(logo=''):
                print team.logo, 
                try:
                    create_thumbnails(team.logo, team.logo.file)
                    print 'FIXED'
                except S3ResponseError:
                    team.logo = ''
                    team.save()
                    print 'S3 ERROR'
                    
        if 'User' in args or len(args) ==0:
            for user in CustomUser.objects.exclude(picture=''):
                print user.picture,
                try:
                    create_thumbnails(user.picture, user.picture.file)
                    print 'FIXED'
                except S3ResponseError:
                    user.picture = ''
                    user.save()
                    print 'S3 ERROR'                

        if 'Video' in args or len(args) ==0:
            for video in Video.objects.exclude(s3_thumbnail=''):
                print video.s3_thumbnail, 
                try:
                    create_thumbnails(video.s3_thumbnail, video.s3_thumbnail.file, (260, 165))
                    create_thumbnails(video.s3_thumbnail, video.s3_thumbnail.file, (120, 90))
                    print 'FIXED'
                except S3ResponseError:
                    video.s3_thumbnail = ''
                    video.save()
                    print 'S3 ERROR'
                    
        if 'TeamVideo' in args or len(args) ==0:
            for tv in TeamVideo.objects.exclude(thumbnail=''):
                print tv.thumbnail, 
                try:
                    create_thumbnails(tv.thumbnail, tv.thumbnail.file)
                    print 'FIXED'
                except S3ResponseError:
                    tv.thumbnail = ''
                    tv.save()
                    print 'S3 ERROR'
