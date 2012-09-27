from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.db.models import Q, Count
from statistic.models import SubtitleFetchCounters
from datetime import date, datetime, timedelta
from videos.models import SubtitleLanguage
import urllib2
from django.utils import simplejson
from django.utils.http import urlquote_plus

ALARM_EMAIL = settings.ALARM_EMAIL

if not isinstance(ALARM_EMAIL, (list, tuple)):
    ALARM_EMAIL = [ALARM_EMAIL]


def send_alarm_email(version, type):
        subject = u'Alert: %s [%s]' % (version.language.video, type)
        url = version.language.get_absolute_url()
        message = u'Language: http://%s%s' % (Site.objects.get_current().domain, url)
        if version.user:
            message += u'User: %s' % version.user
        send_mail(subject, message, from_email=settings.SERVER_EMAIL, recipient_list=ALARM_EMAIL,
                  fail_silently=True)

def check_other_languages_changes(version, ignore_statistic=False):
    if not ALARM_EMAIL:
        return
    
    if not ignore_statistic:
        fetch_count = SubtitleFetchCounters.objects.filter(video=version.video, date=date.today()) \
            .aggregate(fetch_count=Count('count'))['fetch_count']
        
        if fetch_count < 100:
            return
    
    d = datetime.now() - timedelta(hours=1)
    
    changed_langs_count = SubtitleLanguage.objects.filter(video=version.video) \
        .filter(subtitleversion__datetime_started__gte=d).count()
        
    all_langs_count = SubtitleLanguage.objects.filter(video=version.video).count()
    
    if (float(changed_langs_count) / all_langs_count) >= 0.5:
        send_alarm_email(version, u'A video had changes made two more than 50% of its languages in the last hour')
