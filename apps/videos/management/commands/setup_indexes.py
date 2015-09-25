from django.core.management.base import BaseCommand
from south.db import db

import optionalapps

class Command(BaseCommand):
    help = "Adds indexes that have to be defined with raw SQL commands"
    def handle(self, **options):
        db.execute('alter table videos_videourl add unique url_type (url(255), type);')
        optionalapps.exec_repository_scripts('setup_indexes.py',
                                             globals(), locals())
