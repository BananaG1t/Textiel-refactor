from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.AuditLogListView.as_view(), name='view_audit_logs'),
    path('<int:pk>/', views.log_details, name='log_detail'),
]