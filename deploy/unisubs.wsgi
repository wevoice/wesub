import sys
import os

import django.core.handlers.wsgi

import startup

DEFAULT_LANGUAGE = 'en'

sys.stdout = sys.stderr
os.environ['DJANGO_SETTINGS_MODULE'] = 'unisubs.unisubs_settings'

startup.startup()

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
application = django.core.handlers.wsgi.WSGIHandler()

handler = django.core.handlers.wsgi.WSGIHandler()

disabled_file_path = os.path.join(PROJECT_ROOT, 'disabled')

# instrumenting for tracelytics
try:
    import oboeware.djangoware
    from oboeware import OboeMiddleware
    handler = OboeMiddleware(application, {'oboe.tracing_mode': 'always'}, layer="wsgi")
except ImportError:
    # production, dev and local installs shouldn have that
    pass
    
import uwsgi
def application(environ, start_response):
    try:
        uwsgi.set_logvar('body', environ['wsgi.input'].read(request_body_size))
    except:
        uwsgi.set_logvar('body', '(unknown)')

    if os.path.exists(disabled_file_path):
        start_response('503 Service Unavailable', [('Content-type', 'text/html; charset=utf-8')])
        
        langs = environ.get('HTTP_ACCEPT_LANGUAGE', 'en').split(',')
        langs.append(DEFAULT_LANGUAGE)

        for lang in langs:
            lang = lang.split(';')[0].split('-')[0].lower()
            off_tpl_path = rel('unisubs', 'templates', 'off_template', '%s.html' % lang)
            if os.path.exists(off_tpl_path):
                break

        return open(off_tpl_path).read()        
    else:    
        return handler(environ, start_response)
