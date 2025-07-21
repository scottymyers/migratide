"""
WSGI config for migrainetracker project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys

path = '/home/ragequit/migrainetracker'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'migrainetracker.settings'
#os.environ['OPENWEATHERMAP_API_KEY'] = 'ae414a7e0326be0b2b0f16193e2ca3ab'
os.environ['OPENWEATHERMAP_API_KEY'] = 'f555e075db9e374b16ab7d8d7b19d38e'

from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler
application = StaticFilesHandler(get_wsgi_application())