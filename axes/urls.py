from django.urls import path
from . import views

urlpatterns = [
    path('', views.axe_list, name='axe_list'),
    path('yxor/', views.axe_list, name='axe_list'),
    path('yxor/ny/', views.axe_create, name='axe_create'),
    path('yxor/<int:pk>/', views.axe_detail, name='axe_detail'),
    path('yxor/<int:pk>/redigera/', views.axe_edit, name='axe_edit'),
    path('yxor/<int:pk>/status/', views.update_axe_status, name='update_axe_status'),
    path('yxor/<int:pk>/mottagning/', views.receiving_workflow, name='receiving_workflow'),
    path('yxor/<int:pk>/matt/', views.add_measurement, name='add_measurement'),
    path('yxor/<int:pk>/matt/<int:measurement_id>/', views.delete_measurement, name='delete_measurement'),
    path('yxor/<int:pk>/transaktion/<int:transaction_id>/api/', views.api_transaction_update, name='api_transaction_update'),
    path('yxor/<int:pk>/transaktion/<int:transaction_id>/api/detail/', views.api_transaction_detail, name='api_transaction_detail'),
    path('galleri/', views.axe_gallery, name='axe_gallery'),
    path('galleri/<int:pk>/', views.axe_gallery, name='axe_gallery_detail'),
    path('kontakter/', views.contact_list, name='contact_list'),
    path('kontakter/<int:pk>/', views.contact_detail, name='contact_detail'),
    path('tillverkare/', views.manufacturer_list, name='manufacturer_list'),
    path('tillverkare/<int:pk>/', views.manufacturer_detail, name='manufacturer_detail'),
    path('transaktioner/', views.transaction_list, name='transaction_list'),
    path('api/search/contacts/', views.search_contacts, name='search_contacts'),
    path('api/search/platforms/', views.search_platforms, name='search_platforms'),
] 