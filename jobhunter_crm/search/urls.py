from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search_index, name='index'),
    path('start/', views.search_start, name='start'),
    path('<int:pk>/', views.search_detail, name='detail'),
    path('<int:pk>/status/', views.search_status, name='status'),
]
