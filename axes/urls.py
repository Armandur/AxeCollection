from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='yxor/', permanent=True)),
    path('yxor/', views.axe_list, name='axe_list'),
    path('yxor/<int:pk>/', views.axe_detail, name='axe_detail'),
    path('galleri/', views.axe_gallery, name='axe_gallery'),
    path('galleri/<int:pk>/', views.axe_gallery, name='axe_gallery_detail'),
    path('transaktioner/', views.transaction_list, name='transaction_list'),
    path('kontakter/', views.contact_list, name='contact_list'),
    path('kontakt/<int:pk>/', views.contact_detail, name='contact_detail'),
    path('tillverkare/', views.manufacturer_list, name='manufacturer_list'),
    path('tillverkare/<int:pk>/', views.manufacturer_detail, name='manufacturer_detail'),
] 