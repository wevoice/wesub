# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.

from django.core.management.base import BaseCommand
from django.conf import settings
from utils.redis_utils import default_connection
from haystack import backend
from haystack.query import SearchQuerySet
from pysolr import SolrError
from django.core.cache import cache
from utils.celery_search_index import update_search_index
from videos.models import Video
from videos.tasks import add
import random
import base64

class Command(BaseCommand):
    help = u'Test if Solr, Redis and Memcached are available'
    
    def handle(self, *args, **kwargs):
        
        from django.core.mail import send_mail
        send_mail('test from fabric', 'should be here', 'noreply@pculture.org', [args[0]], fail_silently=False)
