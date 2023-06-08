from .celery import app as celery_app

# импортируем app, который указали в celery.py, в проект при его запуске
__all__ = ("celery_app",)
