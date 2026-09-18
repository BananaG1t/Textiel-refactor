from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.view_users, name='view_users'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('password_reset', views.password_reset, name='password_reset'),
    path('profile', views.profile, name='profile'),
]