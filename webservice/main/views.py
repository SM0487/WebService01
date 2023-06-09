import datetime
from django.utils import timezone
from django.shortcuts import render
from .models import CPULoading
import pandas as pd
from plotly.offline import plot
import plotly.express as px

# Create your views here.
# функция построения графиков, возвращает словарь с HTML-кодами графиков
def view_graph():
    try:
        # фиксируем текущее время как конечную точку
        filter_dt_finish = timezone.now()

        # вычисляем время старта для выборки из БД
        filter_dt_start = filter_dt_finish - datetime.timedelta(minutes=60)

        # получаем данные из БД в соответствии с фильтром (время date_time позже чем filter_dt_start)
        qs = CPULoading.objects.all().filter(date_time__gt=filter_dt_start)

        # подготавливаем список данных для экспорта в график
        if len(qs) != 0:
            stat_data = [
                {
                    'DateTime': elem.date_time,
                    'Loading, %': elem.cpu_loading
                } for elem in qs
            ]
        else:
            # добавляем в список данных начальную и конечную точки графика, иначе будет ошибка если данных нет
            stat_data = [{'DateTime': filter_dt_start, 'Loading, %': 0},
                         {'DateTime': filter_dt_finish, 'Loading, %': 0}]

        # --> формируем таблицу 5 секундных данных, где 0-значения не работающего сервиса
        # преобразуем список в DataFrame, исходную таблицу, для дальнейшей обработки
        df5 = pd.DataFrame(stat_data).sort_values('DateTime')
        # генерируем таблицу 5 секундных интервалов в указанном промежутке заполненную 0
        df0 = pd.DataFrame({"DateTime": pd.date_range(filter_dt_start, filter_dt_finish, freq="5S"), 'Loading, %': 0})
        df_5sec = pd.concat([df0, df5])  # объединяем данные 2-х таблиц
        df_5sec = df_5sec.sort_values('DateTime')  # сортируем по ДатеВремени
        df_5sec['_DateTime'] = df_5sec['DateTime']  # добавляем столбец для объединения в 5сек интервалы
        stat_data_moment = df_5sec.resample('5S', on='_DateTime').max()  # заполняем интервалы реальными значениями
        # <-- конец, формируем таблицу 5 секундных данных, где 0-значения не работающего сервиса

        # формируем первый график, из ранее подготовленных данных, в виде гистограммы
        plot1 = px.bar(
            stat_data_moment,
            title='Активность ЦП за последний час, каждые 5 сек.',
            x="DateTime",
            y="Loading, %",
            range_x=[filter_dt_start, filter_dt_finish],
        )
        plot1.update_traces(marker_color='#00CC66')  # указывам цвет столбцов графика

        # --> формируем таблицу с поминутными средними значениями, где 0-значения не работающего сервиса
        df_mean = df5.copy()  # копируем исходную таблицу
        df_mean['_DateTime'] = df_mean['DateTime']  # добавляем столбец для объединения в 1мин интервалы
        df_mean = df_mean.resample('1T', on='_DateTime').mean()  # заполняем интервалы средними значениями
        # генерируем таблицу 1 минутных интервалов в указанном промежутке заполненную 0
        df0 = pd.DataFrame({"DateTime": pd.date_range(filter_dt_start, filter_dt_finish, freq="1T"), 'Loading, %': 0})
        df_mean = pd.concat([df0, df_mean])  # объединяем данные 2-х таблиц
        df_mean = df_mean.sort_values('DateTime')  # сортируем по ДатеВремени
        df_mean['_DateTime'] = df_mean['DateTime']  # добавляем столбец для объединения в 5сек интервалы
        stat_data_mid = df_mean.resample('1T', on='_DateTime').max()  # заполняем интервалы реальными значениями
        # <-- конец, формируем таблицу с поминутными средними значениями, где 0-значения не работающего сервиса

        # формируем второй график, из ранее подготовленных данных, в виде гистограммы
        plot2 = px.bar(
            stat_data_mid,
            title='Активность ЦП за последний час, среднее за 1 мин.',
            x="DateTime",
            y="Loading, %",
            range_x=[filter_dt_start, filter_dt_finish]
        )
        plot2.update_traces(marker_color='#00CC66')  # указывам цвет столбцов графика

        # создаем HTML-код для отображения первого графика, с помощью plotly.offline.plot()
        t_plot_moment = plot(plot1, output_type="div")

        # создаем HTML-код для отображения второго графика, с помощью plotly.offline.plot()
        t_plot_mid = plot(plot2, output_type="div")

        # формируем словарь из графиков и возвращаем его
        context = {'plot_moment': t_plot_moment, 'plot_mid': t_plot_mid}

    except Exception as e:
        # если возникло исключение, формируем строку с информацией
        context = f'Возникло исключение : {e}'

    return context


# возвращаем главную страницу
def index(request):
    # определяем список графиков в виде HTML-кодировок
    context = view_graph()
    # проверяем, что принятое значение это список и содержит заданные ключи
    if (type(context) is dict) & ('plot_moment' in context) & ('plot_mid' in context):
        # отображаем страницу графиков
        return render(request, 'main/index.html', context)
    else:
        # отображаем страницу ошибки
        return render(request, 'main/error.html', {'error_info': context})


# возвращаем страницу описания
def description(request):
    return render(request, 'main/description.html')


# возвращаем страницу ошибки
def error(request):
    return render(request, 'main/error.html')

