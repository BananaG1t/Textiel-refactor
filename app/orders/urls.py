from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.view_orders, name='view_orders'),
    path('errors', views.view_errors, name='view_orders_errors'),
    path('create', views.create_order, name='create_order'),
]