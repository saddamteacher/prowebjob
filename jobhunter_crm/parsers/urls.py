from django.urls import path
from . import views

app_name = 'parser'

urlpatterns = [
    path('', views.parser_monitor, name='monitor'),
    path('run/', views.parser_run, name='run'),
]
