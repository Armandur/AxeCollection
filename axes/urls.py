from django.urls import path
from . import views
from . import views_axe
from . import views_contact
from . import views_manufacturer
from . import views_transaction

urlpatterns = [
    path('', views_axe.axe_list, name='axe_list'),
    path('yxor/', views_axe.axe_list, name='axe_list'),
    path('yxor/ny/', views_axe.axe_create, name='axe_create'),
    path('yxor/<int:pk>/', views_axe.axe_detail, name='axe_detail'),
    path('yxor/<int:pk>/redigera/', views_axe.axe_edit, name='axe_edit'),
    path('yxor/<int:pk>/mottagning/', views_axe.receiving_workflow, name='receiving_workflow'),
    path('yxor/<int:pk>/matt/', views_axe.add_measurement, name='add_measurement'),
    path('yxor/<int:pk>/matt/mall/', views_axe.add_measurements_from_template, name='add_measurements_from_template'),
    path('yxor/<int:pk>/matt/<int:measurement_id>/', views_axe.delete_measurement, name='delete_measurement'),
    path('yxor/<int:pk>/matt/<int:measurement_id>/update/', views_axe.update_measurement, name='update_measurement'),
    path('galleri/', views_axe.axe_gallery, name='axe_gallery'),
    path('galleri/<int:pk>/', views_axe.axe_gallery, name='axe_gallery_detail'),
    path('kontakter/', views_contact.contact_list, name='contact_list'),
    path('kontakter/<int:pk>/', views_contact.contact_detail, name='contact_detail'),
    path('tillverkare/', views_manufacturer.manufacturer_list, name='manufacturer_list'),
    path('tillverkare/<int:pk>/', views_manufacturer.manufacturer_detail, name='manufacturer_detail'),
    path('transaktioner/', views_transaction.transaction_list, name='transaction_list'),
    path('api/transaction/<int:pk>/', views_transaction.api_transaction_detail, name='api_transaction_detail'),
    path('api/transaction/<int:pk>/update/', views_transaction.api_transaction_update, name='api_transaction_update'),
    path('api/search/contacts/', views.search_contacts, name='search_contacts'),
    path('api/search/platforms/', views.search_platforms, name='search_platforms'),
] 