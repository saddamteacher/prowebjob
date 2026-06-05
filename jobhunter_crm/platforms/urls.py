from django.urls import path
from . import views

app_name = 'platforms'

urlpatterns = [
    path('', views.platform_list, name='list'),
    path('<int:pk>/toggle/', views.platform_toggle, name='toggle'),
    path('<int:pk>/test/', views.platform_test, name='test'),
]
