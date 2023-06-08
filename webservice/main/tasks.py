from webservice.celery import app
from .models import CPULoading
import datetime
from django.utils import timezone
import psutil


# функция получения Текущего времени и значения загрузки процессора
# возвращает кортеж значений формата : (datatime, float)
def get_cpu_loading():
    return timezone.now(), psutil.cpu_percent()


# описываем задачу для периодического выполнения(регистрация данных о загрузке процессора)
@app.task  # регистриуем задачу
def repeat_cpuloading_record():
    try:
        date_time, cpu_loading = get_cpu_loading()  # получаем необходимые данные
        record = CPULoading(date_time=date_time, cpu_loading=cpu_loading)  # формируем запись в соответствии с моделью
        record.save()  # записываем в БД
    except Exception as e:
        pass


# описываем задачу на удаление устаревших записей из БД
@app.task  # регистриуем задачу
def repeat_remove_old_records():
    try:
        filter_dt = timezone.now() - datetime.timedelta(minutes=90)  # задаём точку фильтрации, время
        CPULoading.objects.filter(date_time__lt=filter_dt).delete()  # выполняем запрос на удаление записей из БД
    except Exception as e:
        pass
