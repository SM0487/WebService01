from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('description-page', views.description, name='description'),
    path('error-page', views.error, name='error'),
]
