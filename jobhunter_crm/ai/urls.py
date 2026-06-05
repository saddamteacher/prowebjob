from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('', views.ai_dashboard, name='index'),
    path('check-company/', views.check_company, name='check_company'),
    path('check-all/', views.check_all_companies, name='check_all'),
]
