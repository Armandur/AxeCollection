from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_axe
from . import views_contact
from . import views_manufacturer
from . import views_transaction
from . import views_platform

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
    path('yxor/<int:pk>/status/', views_axe.update_axe_status, name='update_axe_status'),
    path('galleri/', views_axe.axe_gallery, name='axe_gallery'),
    path('galleri/<int:pk>/', views_axe.axe_gallery, name='axe_gallery_detail'),
    path('kontakter/', views_contact.contact_list, name='contact_list'),
    path('kontakter/ny/', views_contact.contact_create, name='contact_create'),
    path('kontakter/<int:pk>/', views_contact.contact_detail, name='contact_detail'),
    path('kontakter/<int:pk>/redigera/', views_contact.contact_edit, name='contact_edit'),
    path('kontakter/<int:pk>/ta-bort/', views_contact.contact_delete, name='contact_delete'),
    path('tillverkare/', views_manufacturer.manufacturer_list, name='manufacturer_list'),
    path('tillverkare/ny/', views_manufacturer.manufacturer_create, name='manufacturer_create'),
    path('tillverkare/<int:pk>/', views_manufacturer.manufacturer_detail, name='manufacturer_detail'),
    path('tillverkare/<int:pk>/redigera-information/', views_manufacturer.edit_manufacturer_information, name='edit_manufacturer_information'),
    path('tillverkare/<int:pk>/redigera-namn/', views_manufacturer.edit_manufacturer_name, name='edit_manufacturer_name'),
    path('tillverkare/bild/<int:image_id>/redigera/', views_manufacturer.edit_manufacturer_image, name='edit_manufacturer_image'),
    path('tillverkare/bild/<int:image_id>/ta-bort/', views_manufacturer.delete_manufacturer_image, name='delete_manufacturer_image'),
    path('tillverkare/bild/lagg-till/', views_manufacturer.add_manufacturer_image, name='add_manufacturer_image'),
    path('tillverkare/bild/ordning/', views_manufacturer.reorder_manufacturer_images, name='reorder_manufacturer_images'),
    path('tillverkare/lank/<int:link_id>/redigera/', views_manufacturer.edit_manufacturer_link, name='edit_manufacturer_link'),
    path('tillverkare/lank/<int:link_id>/ta-bort/', views_manufacturer.delete_manufacturer_link, name='delete_manufacturer_link'),
    path('tillverkare/lank/ordning/', views_manufacturer.reorder_manufacturer_links, name='reorder_manufacturer_links'),
    path('tillverkare/<int:pk>/ta-bort/', views_manufacturer.delete_manufacturer, name='delete_manufacturer'),
    path('tillverkare/dropdown/', views_manufacturer.get_manufacturers_for_dropdown, name='get_manufacturers_for_dropdown'),
    path('tillverkare/check-name/', views_manufacturer.check_manufacturer_name, name='check_manufacturer_name'),
    path('transaktioner/', views_transaction.transaction_list, name='transaction_list'),
    path('api/transaction/<int:pk>/', views_transaction.api_transaction_detail, name='api_transaction_detail'),
    path('api/transaction/<int:pk>/update/', views_transaction.api_transaction_update, name='api_transaction_update'),
    path('api/transaction/<int:pk>/delete/', views_transaction.api_transaction_delete, name='api_transaction_delete'),
    
    # Plattformar
    path('plattformar/', views_platform.platform_list, name='platform_list'),
    path('plattformar/ny/', views_platform.platform_create, name='platform_create'),
    path('plattformar/<int:pk>/', views_platform.platform_detail, name='platform_detail'),
    path('plattformar/<int:pk>/redigera/', views_platform.platform_edit, name='platform_edit'),
    path('plattformar/<int:pk>/ta-bort/', views_platform.platform_delete, name='platform_delete'),
    path('api/search/contacts/', views.search_contacts, name='search_contacts'),
    path('api/search/platforms/', views.search_platforms, name='search_platforms'),
    path('api/search/global/', views.global_search, name='global_search'),
    path('statistik/', views_axe.statistics_dashboard, name='statistics_dashboard'),
    path('yxor/senaste/info/', views_axe.get_latest_axe_info, name='get_latest_axe_info'),
    path('yxor/senaste/ta-bort/', views_axe.delete_latest_axe, name='delete_latest_axe'),
    path('okopplade-bilder/', views_axe.unlinked_images_view, name='unlinked_images'),
    path('okopplade-bilder/ta-bort/', views_axe.delete_unlinked_image, name='delete_unlinked_image'),
    path('okopplade-bilder/ladda-ner/', views_axe.download_unlinked_images, name='download_unlinked_images'),
    
    # Auth URLs
    path('login/', auth_views.LoginView.as_view(template_name='axes/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # Settings
    path('installningar/', views.settings_view, name='settings'),
] 