# setup patch_reverse()
from localeurl import patch_reverse
patch_reverse()

# startup WSGI
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
