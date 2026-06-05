from django.urls import path
from . import views

app_name = 'logs_app'

urlpatterns = [
    path('', views.log_list, name='list'),
    path('clear/', views.log_clear, name='clear'),
]
