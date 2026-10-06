from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='view_users'),
    path('login/', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('profile', views.profile, name='profile'),
    path('reset_password/<uidb64>/<token>/', views.AuditedPasswordResetConfirmView.as_view(template_name="reset_password.html", post_reset_login=True, success_url="/"), name='password_reset_confirm'),
    path('users/<int:pk>/', views.user_details, name='user_details'),
]