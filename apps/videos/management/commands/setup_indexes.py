from django.core.management.base import BaseCommand
from south.db import db

class Command(BaseCommand):
    help = "Adds indexes that have to be defined with raw SQL commands"
    def handle(self, **options):
        db.execute('alter table videos_videourl add unique url_type (url(255), type);')
