import hashlib
import logging
import re
import random
import sys
import time

import debug_toolbar
import django.db.backends.mysql.base
from debug_toolbar.middleware import DebugToolbarMiddleware
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date

from utils.dataprintout import DataPrinter

access_logger = logging.getLogger('access')
error_logger = logging.getLogger('unhandled_error')

SECTIONS = {
    'widget': 'widget',
    'api': 'api-v1',
    'api2': 'api-v2',
    'teams': 'teams',
}

data_printer = DataPrinter(
    max_size=1024, max_item_size=100, max_repr_size=50)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class P3PHeaderMiddleware(object):
    def process_response(self, request, response):
        response['P3P'] = settings.P3P_COMPACT
        return response


# Got this from CsrfViewMiddleware
# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange

_MAX_CSRF_KEY = 18446744073709551616L     # 2 << 63

UUID_COOKIE_NAME = getattr(settings, 'UUID_COOKIE_NAME', 'unisub-user-uuid')
UUID_COOKIE_DOMAIN = getattr(settings, 'UUID_COOKIE_DOMAIN', None)

def _get_new_csrf_key():
    return hashlib.sha1("%s%s"
                % (randrange(0, _MAX_CSRF_KEY), settings.SECRET_KEY)).hexdigest()

class UserUUIDMiddleware(object):
    def process_request(self, request):
        try:
            request.browser_id = request.COOKIES[UUID_COOKIE_NAME]
        except KeyError:
            # No cookie or it is empty, so create one.  This will be sent with the next
            # response.
            if not hasattr(request, 'browser_id'):
                request.browser_id = _get_new_csrf_key()

    def process_response(self, request, response):
        if hasattr(request, 'browser_id'):
            browser_id = request.browser_id
            if request.COOKIES.get(UUID_COOKIE_NAME) != browser_id:
                max_age = 60 * 60 * 24 * 365
                response.set_cookie(
                    UUID_COOKIE_NAME,
                    browser_id,
                    max_age=max_age,
                    expires=cookie_date(time.time() + max_age),
                    domain=UUID_COOKIE_DOMAIN)
        # Content varies with the CSRF cookie, so set the Vary header.
        patch_vary_headers(response, ('Cookie',))
        return response


# http://www.randallmorey.com/blog/2010/feb/17/django-cache-sessions-and-google-analytics/
class StripGoogleAnalyticsCookieMiddleware(object):
    strip_re = re.compile(r'(__utm.=.+?(?:; |$))')
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        return response

class AmaraSecurityMiddleware(object):
    """
    Middleware that sets various security-related headers.

    This should be replaced by the django standard SecurityMiddleware once we
    update our django version.
    """
    strip_re = re.compile(r'(__utm.=.+?(?:; |$))')
    def process_request(self, request):
        try:
            cookie = self.strip_re.sub('', request.META['HTTP_COOKIE'])
            request.META['HTTP_COOKIE'] = cookie
        except:
            pass

class LogRequest(object):
    MAX_BODY_SIZE = 2048

    def process_request(self, request):
        request._start_time = time.time()
    def process_exception(self, request, exception):
        try:
            msg = u'{}'.format(exception)
            error_logger.error(msg, extra=self.calc_extra(request),
                                exc_info=True)
        except Exception, e:
            error_logger.error(u'error logging exception: %s', e)

    def process_response(self, request, response):
        try:
            self.log_response(request, response)
        except Exception, e:
            error_logger.error(u'error logging request: %s', e)
        return response

    def log_response(self, request, response):
        total_time = time.time() - request._start_time
        msg = u'{} {} {} ({:.3f}s)'.format(request.method, request.path_info,
                                           response.status_code, total_time)
        extra = self.calc_extra(request, response)
        extra['time'] = total_time
        access_logger.info(msg, extra=extra)

    def calc_extra(self, request, response=None):
        extra = {
            'method': request.method,
            'path': request.path_info,
            'size': request.META.get('CONTENT_LENGTH'),
            'ip_address': get_client_ip(request),
        }
        if response is not None:
            extra['status_code'] = response.status_code
        try:
            extra['user'] = request.user.username
        except AttributeError:
            extra['user'] = '<null>'
        if request.GET:
            extra['query'] = data_printer.printout(request.GET)
        try:
            post_data = request.POST
        except StandardError, e:
            extra['post_data'] = 'parse error: {}'.format(e)
        else:
            if post_data:
                extra['post_data'] = data_printer.printout(
                    self.scrub_post_data(post_data))
        return extra

    def scrub_post_data(self, post_data):
        return dict((k, v if 'password' not in k else '*scrubbed')
                    for (k, v) in post_data.items())
