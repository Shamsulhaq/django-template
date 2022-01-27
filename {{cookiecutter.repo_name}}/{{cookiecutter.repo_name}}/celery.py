# This celery configuration.
from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{cookiecutter.repo_name}}.settings")

app = Celery('{{cookiecutter.repo_name}}')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
print("Staring up celery...")