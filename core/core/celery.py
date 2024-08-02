from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
# from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.conf.enable_utc = False
app.conf.update(timezone="Asia/Kolkata")

app.config_from_object(settings, namespace="CELERY")

# Celery Beat Settings
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "Send_mail_to_Client": {
        "task": "trackmate.tasks.check_prices_and_notify",
        "schedule": 60.0,
    }
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
