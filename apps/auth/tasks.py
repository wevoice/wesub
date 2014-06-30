from celery.decorators import task
from celery.schedules import timedelta

from auth.models import CustomUser
from utils.metrics import Gauge

@task
def gauge_auth():
    Gauge('auth.CustomUser').report(CustomUser.objects.count())
