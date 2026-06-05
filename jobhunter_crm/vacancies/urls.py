from django.urls import path
from . import views

app_name = 'vacancies'

urlpatterns = [
    path('', views.vacancy_list, name='list'),
    path('<int:pk>/', views.vacancy_detail, name='detail'),
    path('<int:pk>/delete/', views.vacancy_delete, name='delete'),
    path('<int:pk>/check-ai/', views.check_company_ai, name='check_ai'),
    path('categories/', views.category_list, name='categories'),
    path('categories/<int:pk>/toggle/', views.category_toggle, name='category_toggle'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
]
