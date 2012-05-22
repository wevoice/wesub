from celery.decorators import periodic_task
from celery.schedules import timedelta

from apps.auth.models import CustomUser
from utils.metrics import Gauge

@periodic_task(run_every=timedelta(seconds=5))
def gauge_auth():
    Gauge('auth.CustomUser').report(CustomUser.objects.count())
