Тестовое задание.

	Разработать веб сервис, который выполняет следующие функции:
	1. Постоянно сохраняет в базу данных историю величины загрузки процессора с интервалом в 5 секунд.
	2. Предоставляет страницу, которая изображает срез данных с историей загрузки процессора за последний час в виде двух графиков.
	Первый график отображает историю изменения моментальной загрузки процессора.
	Второй - отображает график усредненной загрузки процессора (среднее значение за 1 минуту)
	В случае, если сервис на какое-то время был выключен, на графиках должны видны пустые промежутки времени, для которых нет данных.

	В качестве базы данных можно использовать SQlite.
	На каком уровне рисовать графики (бек или фронт) решает разработчик, но вычисление значений второго графика должны быть произведены на беке.

	В результате решения задания хотелось бы увидеть обоснование выбора фреймворка и принятых решений при реализации задания.


Запуск решеня в системе Linux (как я делал у себя)
1 - устанавить Python 3.10 (https://www.python.org/downloads/release/python-31012/)
2 - импортировать необходимые зависимости из файла requerements.txt (команда терминала: pip install --no-cache-dir -r requirements.txt)
3 - запустить redis, например через Docker (команда терминала: sudo docker run -p 6379:6379 --name my-redis -d redis). Терминал отобразит что-то схожее:

	CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS         PORTS                                       NAMES
	f22183241b90   redis     "docker-entrypoint.s…"   7 seconds ago   Up 6 seconds   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp   my-redis


4 - перейти в директорию проекта ../WebService01/webservice 
5 - запустить веб-сервис (python3 manage.py runserver). Терминал отобразит что-то схожее:

	Watching for file changes with StatReloader
	Performing system checks...

	System check identified no issues (0 silenced).
	June 08, 2023 - 18:40:18
	Django version 4.2.2, using settings 'webservice.settings'
	Starting development server at http://127.0.0.1:8000/
	Quit the server with CONTROL-C.

6 - В новом окне терминала запустить планировщик celery worker (команда терминала: celery -A webservice worker -l info). Терминал отобразит что-то схожее:

	 -------------- celery@sm-HP-EliteBook-840-G1 v5.3.0 (emerald-rush)
	--- ***** ----- 
	-- ******* ---- Linux-5.19.0-43-generic-x86_64-with-glibc2.35 2023-06-08 19:18:44
	- *** --- * --- 
	- ** ---------- [config]
	- ** ---------- .> app:         webservice:0x7f07525a3b50
	- ** ---------- .> transport:   redis://0.0.0.0:6379/0
	- ** ---------- .> results:     redis://0.0.0.0:6379/0
	- *** --- * --- .> concurrency: 4 (prefork)
	-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
	--- ***** ----- 
	 -------------- [queues]
		        .> celery           exchange=celery(direct) key=celery
		        
	[tasks]
	  . main.tasks.repeat_cpuloading_record
	  . main.tasks.repeat_remove_old_records	

	[2023-06-08 19:18:44,437: INFO/MainProcess] Connected to redis://0.0.0.0:6379/0	
	[2023-06-08 19:18:44,439: INFO/MainProcess] mingle: searching for neighbors
	[2023-06-08 19:18:45,448: INFO/MainProcess] mingle: all alone
	[2023-06-08 19:18:45,472: INFO/MainProcess] celery@sm-HP-EliteBook-840-G1 ready.

7 - В новом окне терминала запустить выполнение периодических задач в планировщике celery beat (команда терминала: celery -A webservice beat -l info). Терминал отобразит что-то схожее:

	celery beat v5.3.0 (emerald-rush) is starting.
	__    -    ... __   -        _
	LocalTime -> 2023-06-08 19:22:02
	Configuration ->
	    . broker -> redis://0.0.0.0:6379/0
	    . loader -> celery.loaders.app.AppLoader
	    . scheduler -> celery.beat.PersistentScheduler
	    . db -> celerybeat-schedule
	    . logfile -> [stderr]@%INFO
	    . maxinterval -> 5.00 minutes (300s)
	[2023-06-08 19:22:02,224: INFO/MainProcess] beat: Starting...
	[2023-06-08 19:22:02,232: WARNING/MainProcess] Reset: Timezone changed from 'UTC' to 'Europe/Moscow'
	[2023-06-08 19:22:07,238: INFO/MainProcess] Scheduler: Sending due task every-5-seconds (main.tasks.repeat_cpuloading_record)
	[2023-06-08 19:22:12,234: INFO/MainProcess] Scheduler: Sending due task every-5-seconds (main.tasks.repeat_cpuloading_record)

8 - проверить работу сервиса http://127.0.0.1:8000 (в папке screenshots есть примеры отображаемого содержимого)
    Описание вкладок веб-страници:
    	Главная - отображает требуемые графики;
    	Информация - отображает задание, описание процесса запуска, выбора решений.


Описание выбора решений
# веб-фреймворк
Django - использовал как наиболее популярный и многофункциональный, и востребованный на рынке серверный веб-фреймворк. Тем более планировал его изучить в любом случае.

# планировщик задач
celery - использовал для фоновой обработки и периодического запуска задач (в нашем случае сбор данных с интервалом в 5 секунд, а также удаление устаревших (старше 1,5 часа) данных из БД с интервалом 60 минут).
redis - использовал в качестве брокера очередей для celery.

# графики
plotly - использовал для визуализации графиков. Библиотека мне показалась привлекательной - бесплатная,  можно делать красивые графики.
pandas - использовал для структурирования данных при подготовке графиков plotly.

# данные загрузки процессора
psutil - использовал кросс-платформенную библиотеку для получения информации о использовании системы, в частности загрузки процессора.
