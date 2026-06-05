from django.urls import path
from . import views

app_name = 'scheduler'

urlpatterns = [
    path('', views.scheduler_dashboard, name='index'),
    path('run-parser/', views.run_parser_job, name='run_parser'),
    path('toggle/', views.toggle_scheduler, name='toggle'),
]
