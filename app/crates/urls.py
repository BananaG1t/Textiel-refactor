from django.urls import path
from . import views

urlpatterns = [
    path('', views.displayCrates, name='displayCrates'),
    path('details/<int:id>', views.crateDetails, name='crateDetails'),
    path('<int:crate_id>/assign/<int:order_id>/', views.assign_crate, name='assign_crate'),
    path('<int:crate_id>/complete/', views.complete_crate, name='complete_order'),
    path("<int:crate_id>/completePicking/", views.complete_picking, name='complete_picking'),
    path("<int:crate_id>/completePrinting/", views.complete_crate_printing, name='complete_picking'),

]