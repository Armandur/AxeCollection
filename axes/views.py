from django.shortcuts import render, get_object_or_404, redirect
from .models import Axe, Transaction, Contact, Manufacturer, ManufacturerImage, ManufacturerLink, NextAxeID, AxeImage, Platform, Measurement
from django.db.models import Sum, Q, Max
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django import forms
from django.utils import timezone
import requests
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import uuid
import os
from django.core.files.storage import default_storage
from django.conf import settings
from .forms import TransactionForm, MeasurementForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import MeasurementTemplate
from .views_axe import (
    axe_list, axe_detail, axe_create, axe_edit, axe_gallery, receiving_workflow,
    add_measurement, add_measurements_from_template, delete_measurement, update_measurement
)
from .views_contact import contact_list, contact_detail
from .views_manufacturer import manufacturer_list, manufacturer_detail

# Create your views here.

def search_contacts(request):
    """AJAX-endpoint för att söka efter kontakter"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    contacts = Contact.objects.filter(
        Q(name__icontains=query) | 
        Q(alias__icontains=query) |
        Q(email__icontains=query)
    )[:10]  # Begränsa till 10 resultat
    
    results = [{'id': c.id, 'name': c.name, 'alias': c.alias or '', 'email': c.email or ''} for c in contacts]
    return JsonResponse({'results': results})

def search_platforms(request):
    """AJAX-endpoint för att söka efter plattformar"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    platforms = Platform.objects.filter(name__icontains=query)[:10]  # Begränsa till 10 resultat
    results = [{'id': p.id, 'name': p.name} for p in platforms]
    return JsonResponse({'results': results})

# Egen widget för flera filer enligt Django-dokumentationen
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class ContactForm(forms.ModelForm):
    """Formulär för att skapa/redigera kontakter"""
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'alias', 'comment', 'is_naj_member']
        labels = {
            'name': 'Namn',
            'email': 'E-post',
            'phone': 'Telefon',
            'alias': 'Alias (Tradera/eBay)',
            'comment': 'Kommentar',
            'is_naj_member': 'NAJ-medlem',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ange namn'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'namn@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '070-123 45 67'}),
            'alias': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Användarnamn på Tradera/eBay'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Lägg till kommentar...'}),
            'is_naj_member': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AxeForm(forms.ModelForm):
    images = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='Bilder',
        help_text='Ladda upp bilder av yxan (drag & drop stöds)'
    )

    # Kontaktrelaterade fält
    contact_search = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sök efter befintlig kontakt eller ange ny...'
        }),
        label='Försäljare',
        help_text='Sök efter befintlig kontakt eller ange namn för ny kontakt'
    )
    
    contact_name = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ange försäljarens namn'
        }),
        label='Namn (ny kontakt)',
        help_text='Namn på försäljaren (t.ex. från Tradera, eBay)'
    )
    
    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'namn@example.com'
        }),
        label='E-post (ny kontakt)',
        help_text='Försäljarens e-postadress'
    )
    
    contact_phone = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '070-123 45 67'
        }),
        label='Telefon (ny kontakt)',
        help_text='Försäljarens telefonnummer'
    )
    
    contact_alias = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Användarnamn på Tradera/eBay'
        }),
        label='Alias (ny kontakt)',
        help_text='Användarnamn på plattformen (t.ex. Tradera, eBay)'
    )
    
    contact_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Lägg till kommentar om försäljaren...'
        }),
        label='Kommentar (ny kontakt)',
        help_text='Kommentar om försäljaren'
    )
    
    is_naj_member = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='NAJ-medlem (ny kontakt)',
        help_text='Är försäljaren medlem i Nordic Axe Junkies?'
    )
    
    # Transaktionsrelaterade fält
    transaction_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        }),
        label='Pris (kr)',
        help_text='Pris för yxan (negativt för köp, positivt för sälj)'
    )
    
    transaction_shipping = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        }),
        label='Fraktkostnad (kr)',
        help_text='Fraktkostnad (negativt för köp, positivt för sälj)'
    )
    
    transaction_date = forms.DateField(
        required=False,
        initial=timezone.now().date,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Transaktionsdatum',
        help_text='Datum för transaktionen'
    )
    
    transaction_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Lägg till kommentar om transaktionen...'
        }),
        label='Transaktionskommentar',
        help_text='Kommentar om transaktionen (t.ex. betalningsmetod)'
    )
    
    # Plattformsrelaterade fält
    platform_search = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sök efter befintlig plattform eller ange ny...'
        }),
        label='Plattform',
        help_text='Börja skriva för att söka efter befintlig plattform eller skapa ny'
    )

    class Meta:
        model = Axe
        fields = ['manufacturer', 'model', 'comment', 'status']
        labels = {
            'manufacturer': 'Tillverkare',
            'model': 'Modell',
            'comment': 'Kommentar',
            'status': 'Status',
        }
        widgets = {
            'manufacturer': forms.Select(attrs={'class': 'form-select'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ange modellnamn'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Lägg till kommentar om yxan...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
