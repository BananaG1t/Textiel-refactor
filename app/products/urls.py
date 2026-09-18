from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.view_products, name='view_products'),
    path('details/<int:sku>', views.productDetails, name='productDetails'),
    path('create', views.create_product, name='create_product')
]