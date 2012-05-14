# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
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

from utils.rpc import add_request_to_kwargs
from search.forms import SearchForm
from videos.search_indexes import VideoSearchResult, VideoIndex

from videos.models import Video
from django.template.loader import render_to_string
from videos.rpc import render_page
from django.template import RequestContext
from django.core.cache import cache

class SearchApiClass(object):

    def search(self, rdata, user, testing=False):
        sqs = VideoIndex.public()

        rdata['q'] = rdata['q'] or u' '
        q = rdata.get('q')

        if q:
            sqs = SearchForm.apply_query(q, sqs)
            form = SearchForm(rdata, sqs=sqs)
        else:
            form = SearchForm(rdata)

        if form.is_valid():
            qs = form.search_qs(sqs)
        else:
            qs = VideoIndex.public().none()

        #result = [item.object for item in qs]
        #qs1 = Video.objects.filter(title__contains=rdata['q'])
        #for o in qs1:
        #    if not o in result:
        #        print o.title

        display_views = form.get_display_views()
        output = render_page(rdata.get('page', 1), qs, 20, display_views=display_views)
        output['sidebar'] = render_to_string('search/_sidebar.html', dict(form=form, rdata=rdata))

        # Assume we're currently indexing if the number of public
        # indexed vids differs from the count of video objects by
        # more than 1000
        is_indexing = cache.get('is_indexing')
        if is_indexing is None:
            is_indexing = Video.objects.all().count() - VideoIndex.public().count() > 1000
            cache.set('is_indexing', is_indexing, 300)

        output['is_indexing'] = is_indexing

        if testing:
            output['sqs'] = qs

        return output