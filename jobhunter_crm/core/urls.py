from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('setup/', views.setup_view, name='setup'),
    path('logout/', views.logout_view, name='logout'),
    path('set-language/', views.set_language, name='set_language'),
]
