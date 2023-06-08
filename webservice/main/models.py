from django.db import models


# Create your models here.
# модель данных хранимых в БД
class CPULoading(models.Model):
    date_time = models.DateTimeField("Date_Time")  # Дата и время
    cpu_loading = models.FloatField("CPU_Loading")  # значение загрузки ЦП

    def __str__(self):
        return f'{self.date_time} : {self.cpu_loading}'
