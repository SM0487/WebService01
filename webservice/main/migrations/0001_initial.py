# Generated by Django 4.2.2 on 2023-06-05 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CPULoading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(verbose_name='Date_Time')),
                ('cpu_loading', models.FloatField(verbose_name='CPU_Loading')),
            ],
        ),
    ]