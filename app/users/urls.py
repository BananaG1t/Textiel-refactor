from django.urls import path
from django.contrib.auth.views import PasswordResetConfirmView
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.view_users, name='view_users'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('profile', views.profile, name='profile'),
    path('reset_password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name="reset_password.html", post_reset_login=True, success_url="/"), name='password_reset_confirm'),
]