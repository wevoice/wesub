# Amara, universalsubtitles.org
#
# Copyright (C) 2014 Participatory Culture Foundation
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

import os

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils.translation import activate
from django.views import static

from staticmedia import bundles
from staticmedia import oldembedder
from staticmedia import utils
from staticmedia.jsi18ncompat import (get_javascript_catalog,
                                      render_javascript_catalog)
from staticmedia.jslanguagedata import render_js_language_script

def js_bundle(request, bundle_name):
    return _bundle(request, bundle_name, bundles.JavascriptBundle)

def css_bundle(request, bundle_name):
    return _bundle(request, bundle_name, bundles.CSSBundle)

def _bundle(request, bundle_name, correct_type):
    try:
        bundle = bundles.get_bundle(bundle_name)
    except KeyError:
        raise Http404()
    if not isinstance(bundle, correct_type):
        raise Http404()
    return HttpResponse(bundle.get_contents(), bundle.mime_type)

def js_i18n_catalog(request, locale):
    catalog, plural = get_javascript_catalog(locale, 'djangojs', [])
    return render_javascript_catalog(catalog, plural)

def js_language_data(request, locale):
    activate(locale)
    return HttpResponse(render_js_language_script(), 'application/javascript')

def old_embedder_js(request):
    return HttpResponse(oldembedder.js_code(), 'text/javascript')

def embedder_test(request):
    return render(request, 'staticmedia/embedder-test.html')

def old_embedder_test(request):
    if not settings.STATIC_MEDIA_USES_S3:
        old_embedder_url = "/media/embed.js"
    else:
        old_embedder_url = settings.STATIC_MEDIA_S3_URL_BASE + 'embed.js'
    return render(request, 'staticmedia/old-embedder-test.html', {
        'old_embedder_url': old_embedder_url,
    })

def serve_add_static_media(request, path):
    for root_dir in utils.app_static_media_dirs():
        if os.path.exists(os.path.join(root_dir, path)):
            return static.serve(request, path, document_root=root_dir)
    raise Http404("'%s' could not be found" % path)
