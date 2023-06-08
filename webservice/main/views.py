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
            stat_data_moment = [
                {
                    'DateTime': elem.date_time,
                    'Loading, %': elem.cpu_loading
                } for elem in qs
            ]
        else:
            stat_data_moment = []

        # добавляем в список данных начальную и конечную точки графика
        #stat_data_moment.append({'DateTime': filter_dt_start, 'Loading, %': 0})
        #stat_data_moment.append({'DateTime': filter_dt_finish, 'Loading, %': 0})

        # структурируем данные для первого графика при помощи pandas.dataframe
        df_plot1 = pd.DataFrame(stat_data_moment)

        # формируем первый график, из ранее подготовленных данных, в виде гистограммы
        plot1 = px.bar(
            df_plot1,
            title='Активность ЦП за последний час, каждые 5 сек.',
            x="DateTime",
            y="Loading, %",
            range_x=[filter_dt_start, filter_dt_finish],
        )
        plot1.update_traces(marker_color='#00CC66')

        # --> вычисление среднего за каждую минуту и заполнение списка значений
        stat_data_mid = []  # список словарей
        _filter_interval = [filter_dt_start, filter_dt_start]  # временный фильтр для 5 секундного интервала [начало, конец]
        # в цикле анализируем значения в stat_data_moment
        while _filter_interval[1] < filter_dt_finish:
            # меняем конец интервала, увеличиваем на 1 минуту
            _filter_interval[1] = _filter_interval[0] + datetime.timedelta(minutes=1)
            _sum = 0  # временная переменная для суммы значений, для вычесления среднего
            _count = 0  # временная переменная для количества просуммированных значений, для вычесления среднего
            # проходимся по списку исходных значений
            for element in stat_data_moment:
                # выбираем значения попадающие в заданный интервал
                if _filter_interval[0] <= element["DateTime"] < _filter_interval[1]:
                    _count += 1
                    _sum += element["Loading, %"]
            # добавляем результаты вычислений по отфильтрованным значениям в список
            stat_data_mid.append({'DateTime': _filter_interval[1], 'Loading, %': (_sum / _count if _count != 0 else 0)})
            # меняем начало интервала
            _filter_interval[0] = _filter_interval[1]
        # <-- конец, вычисление среднего за каждую минуту и заполнение списка значений

        # структурируем данные для второго графика при помощи pandas.dataframe
        df_plot2 = pd.DataFrame(stat_data_mid)

        # формируем второй график, из ранее подготовленных данных, в виде гистограммы
        plot2 = px.bar(
            df_plot2,
            title='Активность ЦП за последний час, среднее за 1 мин.',
            x="DateTime",
            y="Loading, %",
            range_x = [filter_dt_start, filter_dt_finish]
        )
        plot2.update_traces(marker_color='#00CC66')

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
