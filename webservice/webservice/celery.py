import os
from celery import Celery
from celery.schedules import timedelta


os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'webservice.settings')

app = Celery('webservice')
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()

# заносим задачи в очередь выполнения
app.conf.beat_schedule = {
    'every-5-seconds': {
        'task': 'main.tasks.repeat_cpuloading_record',  # указываем задачу которую требуется выполнять
        'schedule': timedelta(seconds=5),  # настраиваем выполнение каждые 5 секунд
    },
    'every-60-minutes': {
        'task': 'main.tasks.repeat_remove_old_records',  # указываем задачу которую требуется выполнять
        'schedule': timedelta(minutes=60),  # настраиваем выполнение каждые 60 минит
    },
}

