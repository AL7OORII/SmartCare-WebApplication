# celery.py

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newproj.settings')

app = Celery('newproj')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app = Celery('newproj')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
