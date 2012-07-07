import os
import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
application = newrelic.agent.wsgi_application()(application)