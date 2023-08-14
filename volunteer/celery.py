import os
from celery import Celery
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volunteer.settings')

app = Celery('volunteer')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send': {
        'task': 'PersonalArea.tasks.send',
        'schedule': crontab(minute='*/1'),
    }
}