from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'splitwise.settings')

app = Celery('splitwise')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'send_weekly_summary_email_on_monday':{
        'task': 'expense.tasks.send_weekly_summary_email',
        'schedule' : crontab(minute = 0, hour= 12, day_of_week='monday') # Runs a task every Monday at 12:00 PM (noon)
}
}

app.autodiscover_tasks()

app.conf.timezone = 'UTC' 