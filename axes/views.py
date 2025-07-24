from django.shortcuts import render, get_object_or_404, redirect
from .models import Axe, Transaction, Contact, Manufacturer, ManufacturerImage, ManufacturerLink, NextAxeID, AxeImage, Platform, Measurement, MeasurementType
from django.db.models import Sum, Q, Max, Count, Avg
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
from django.contrib.auth.decorators import login_required

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

def global_search(request):
    """AJAX-endpoint för global sökning i yxor, kontakter, tillverkare och transaktioner"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': {}})
    
    results = {
        'axes': [],
        'contacts': [],
        'manufacturers': [],
        'transactions': []
    }
    
    # Sök i yxor (respektera "endast mottagna yxor" inställning)
    text_query = Q(manufacturer__name__icontains=query) | Q(model__icontains=query) | Q(comment__icontains=query)
    
    # Applicera publik filtrering om användaren inte är inloggad
    if not request.user.is_authenticated:
        from .models import Settings
        try:
            settings = Settings.get_settings()
            if settings.show_only_received_axes_public:
                text_query &= Q(status='MOTTAGEN')
        except:
            # Fallback om Settings-modellen inte finns ännu
            pass
    
    # Kontrollera om query är ett nummer för ID-sökning
    try:
        id_query = int(query)
        axes = Axe.objects.filter(text_query | Q(id=id_query)).select_related('manufacturer')[:5]
    except ValueError:
        # Om query inte är ett nummer, sök bara i textfält
        axes = Axe.objects.filter(text_query).select_related('manufacturer')[:5]
    
    for axe in axes:
        results['axes'].append({
            'id': axe.id,
            'title': f"{axe.manufacturer.name} - {axe.model}",
            'subtitle': f"ID: {axe.id}",
            'url': f'/yxor/{axe.id}/',
            'type': 'axe'
        })
    
    # Sök i kontakter (endast om användaren är inloggad eller kontakter visas publikt)
    if request.user.is_authenticated or getattr(request, 'public_settings', {}).get('show_contacts', False):
        contacts = Contact.objects.filter(
            Q(name__icontains=query) |
            Q(alias__icontains=query) |
            Q(email__icontains=query)
        )[:5]
        
        for contact in contacts:
            flag_emoji = f"🇸🇪" if contact.country_code == 'SE' else f"🇫🇮" if contact.country_code == 'FI' else ""
            results['contacts'].append({
                'id': contact.id,
                'title': contact.name,
                'subtitle': f"{contact.alias or ''} {flag_emoji}".strip(),
                'url': f'/kontakter/{contact.id}/',
                'type': 'contact'
            })
    
    # Sök i tillverkare
    manufacturers = Manufacturer.objects.filter(
        Q(name__icontains=query) |
        Q(information__icontains=query)
    )[:5]
    
    for manufacturer in manufacturers:
        axe_count = manufacturer.axes.count()
        results['manufacturers'].append({
            'id': manufacturer.id,
            'title': manufacturer.name,
            'subtitle': f"{axe_count} yxor",
            'url': f'/tillverkare/{manufacturer.id}/',
            'type': 'manufacturer'
        })
    
    # Sök i transaktioner (respektera publika inställningar)
    transaction_query = Q(axe__manufacturer__name__icontains=query) | Q(axe__model__icontains=query)
    
    # Lägg till kontaktsökning endast om kontakter visas publikt
    if request.user.is_authenticated or getattr(request, 'public_settings', {}).get('show_contacts', False):
        transaction_query |= Q(contact__name__icontains=query)
    
    # Lägg till plattformssökning endast om plattformar visas publikt
    if request.user.is_authenticated or getattr(request, 'public_settings', {}).get('show_platforms', True):
        transaction_query |= Q(platform__name__icontains=query)
    
    transactions = Transaction.objects.filter(transaction_query).select_related('axe__manufacturer', 'contact', 'platform')[:5]
    
    for transaction in transactions:
        axe_title = f"{transaction.axe.manufacturer.name} - {transaction.axe.model}" if transaction.axe else "Okänd yxa"
        
        # Skapa subtitle baserat på publika inställningar
        if request.user.is_authenticated or getattr(request, 'public_settings', {}).get('show_prices', True):
            subtitle_parts = [f"{transaction.price} kr", transaction.transaction_date.strftime('%Y-%m-%d')]
        else:
            subtitle_parts = ["***", transaction.transaction_date.strftime('%Y-%m-%d')]
        
        # Lägg till kontaktinfo endast om kontakter visas publikt
        if request.user.is_authenticated or getattr(request, 'public_settings', {}).get('show_contacts', False):
            if transaction.contact:
                subtitle_parts.append(transaction.contact.name)
        
        # Lägg till plattformsinfo endast om plattformar visas publikt
        if request.user.is_authenticated or getattr(request, 'public_settings', {}).get('show_platforms', True):
            if transaction.platform:
                subtitle_parts.append(transaction.platform.name)
        
        results['transactions'].append({
            'id': transaction.id,
            'title': f"{transaction.type} - {axe_title}",
            'subtitle': ' - '.join(subtitle_parts),
            'url': f'/yxor/{transaction.axe.id}/' if transaction.axe else '#',
            'type': 'transaction'
        })
    
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

# --- Yx-relaterade vyer ---

def axe_list(request):
    # Hämta filter från URL-parametrar
    status_filter = request.GET.get('status', '')
    manufacturer_filter = request.GET.get('manufacturer', '')
    platform_filter = request.GET.get('platform', '')
    
    # Starta med alla yxor
    axes = Axe.objects.all().select_related('manufacturer').prefetch_related('measurements', 'images', 'transactions')
    
    # Applicera publik filtrering om användaren inte är inloggad
    if not request.user.is_authenticated:
        from .models import Settings
        try:
            settings = Settings.get_settings()
            if settings.show_only_received_axes_public:
                axes = axes.filter(status='MOTTAGEN')
        except:
            # Fallback om Settings-modellen inte finns ännu
            pass
    
    # Applicera filter
    if status_filter:
        axes = axes.filter(status=status_filter)
    
    if manufacturer_filter:
        axes = axes.filter(manufacturer_id=manufacturer_filter)
    
    if platform_filter:
        axes = axes.filter(transactions__platform_id=platform_filter).distinct()
    
    # Sortera efter ID (senaste först)
    axes = axes.order_by('-id')
    
    # Hämta alla tillverkare för filter-dropdown
    manufacturers = Manufacturer.objects.all().order_by('name')
    
    # Hämta alla plattformar för filter-dropdown
    platforms = Platform.objects.all().order_by('name')
    
    # Statistik för filtrerade yxor
    filtered_axe_ids = list(axes.values_list('id', flat=True))
    filtered_transactions = Transaction.objects.filter(axe_id__in=filtered_axe_ids)
    
    total_buys = filtered_transactions.filter(type='KÖP').count()
    total_sales = filtered_transactions.filter(type='SÄLJ').count()
    total_buy_value = filtered_transactions.filter(type='KÖP').aggregate(total=Sum('price'))['total'] or 0
    total_sale_value = filtered_transactions.filter(type='SÄLJ').aggregate(total=Sum('price'))['total'] or 0
    total_buy_shipping = filtered_transactions.filter(type='KÖP').aggregate(total=Sum('shipping_cost'))['total'] or 0
    total_sale_shipping = filtered_transactions.filter(type='SÄLJ').aggregate(total=Sum('shipping_cost'))['total'] or 0
    total_profit = total_sale_value - total_buy_value
    total_profit_with_shipping = (total_sale_value + total_sale_shipping) - (total_buy_value + total_buy_shipping)
    
    # Hitta sålda yxor bland filtrerade yxor (de som har minst en SÄLJ-transaktion)
    sold_axe_ids = set(filtered_transactions.filter(type='SÄLJ').values_list('axe_id', flat=True))
    
    # Statistik för filtrerade yxor
    filtered_count = axes.count()
    bought_count = axes.filter(status='KÖPT').count()
    received_count = axes.filter(status='MOTTAGEN').count()
    
    return render(request, 'axes/axe_list.html', {
        'axes': axes,
        'manufacturers': manufacturers,
        'platforms': platforms,
        'status_filter': status_filter,
        'manufacturer_filter': manufacturer_filter,
        'platform_filter': platform_filter,
        'filtered_count': filtered_count,
        'bought_count': bought_count,
        'received_count': received_count,
        'total_buys': total_buys,
        'total_sales': total_sales,
        'total_buy_value': total_buy_value,
        'total_sale_value': total_sale_value,
        'total_buy_shipping': total_buy_shipping,
        'total_sale_shipping': total_sale_shipping,
        'total_profit': total_profit,
        'total_profit_with_shipping': total_profit_with_shipping,
        'sold_axe_ids': sold_axe_ids,
    })

def statistics_dashboard(request):
    """Dedikerad statistik-sida för hela samlingen"""
    
    # Grundläggande statistik
    total_axes = Axe.objects.count()
    total_manufacturers = Manufacturer.objects.count()
    total_contacts = Contact.objects.count()
    total_transactions = Transaction.objects.count()
    
    # Status-statistik
    bought_axes = Axe.objects.filter(status='KÖPT').count()
    received_axes = Axe.objects.filter(status='MOTTAGEN').count()
    
    # Transaktionsstatistik
    buy_transactions = Transaction.objects.filter(type='KÖP')
    sale_transactions = Transaction.objects.filter(type='SÄLJ')
    
    total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_buy_shipping = buy_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
    total_sale_shipping = sale_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
    
    total_profit = total_sale_value - total_buy_value
    total_profit_with_shipping = (total_sale_value + total_sale_shipping) - (total_buy_value + total_buy_shipping)
    
    # Mest populära tillverkare (top 5)
    top_manufacturers = Manufacturer.objects.annotate(
        axe_count=Count('axe')
    ).order_by('-axe_count')[:5]
    
    # Dyraste köp (top 5)
    most_expensive_buys = Transaction.objects.filter(
        type='KÖP'
    ).select_related('axe__manufacturer').order_by('-price')[:5]
    
    # Dyraste försäljningar (top 5)
    most_expensive_sales = Transaction.objects.filter(
        type='SÄLJ'
    ).select_related('axe__manufacturer').order_by('-price')[:5]
    
    # Mest aktiva plattformar (top 5)
    top_platforms = Platform.objects.annotate(
        transaction_count=Count('transaction')
    ).order_by('-transaction_count')[:5]
    
    # Mest aktiva kontakter (top 5)
    top_contacts = Contact.objects.annotate(
        transaction_count=Count('transaction')
    ).order_by('-transaction_count')[:5]
    
    # Genomsnittsstatistik
    avg_price_per_axe = total_buy_value / total_axes if total_axes > 0 else 0
    avg_profit_per_axe = total_profit / total_axes if total_axes > 0 else 0
    avg_transactions_per_axe = total_transactions / total_axes if total_axes > 0 else 0
    
    # Sålda yxor
    sold_axes = Axe.objects.filter(transactions__type='SÄLJ').distinct().count()
    sold_axes_percentage = (sold_axes / total_axes * 100) if total_axes > 0 else 0
    
    # NAJ-medlemmar
    naj_members = Contact.objects.filter(is_naj_member=True).count()
    naj_percentage = (naj_members / total_contacts * 100) if total_contacts > 0 else 0
    
    context = {
        # Grundläggande statistik
        'total_axes': total_axes,
        'total_manufacturers': total_manufacturers,
        'total_contacts': total_contacts,
        'total_transactions': total_transactions,
        
        # Status-statistik
        'bought_axes': bought_axes,
        'received_axes': received_axes,
        
        # Transaktionsstatistik
        'buy_transactions': buy_transactions.count(),
        'sale_transactions': sale_transactions.count(),
        'total_buy_value': total_buy_value,
        'total_sale_value': total_sale_value,
        'total_buy_shipping': total_buy_shipping,
        'total_sale_shipping': total_sale_shipping,
        'total_profit': total_profit,
        'total_profit_with_shipping': total_profit_with_shipping,
        
        # Topplistor
        'top_manufacturers': top_manufacturers,
        'most_expensive_buys': most_expensive_buys,
        'most_expensive_sales': most_expensive_sales,
        'top_platforms': top_platforms,
        'top_contacts': top_contacts,
        
        # Genomsnitt
        'avg_price_per_axe': avg_price_per_axe,
        'avg_profit_per_axe': avg_profit_per_axe,
        'avg_transactions_per_axe': avg_transactions_per_axe,
        
        # Procentuell statistik
        'sold_axes': sold_axes,
        'sold_axes_percentage': sold_axes_percentage,
        'naj_members': naj_members,
        'naj_percentage': naj_percentage,
    }
    
    return render(request, 'axes/statistics_dashboard.html', context)

def settings_view(request):
    """Vy för att hantera systeminställningar och backup"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    from .models import Settings
    import os
    import json
    import zipfile
    import subprocess
    from django.contrib import messages
    from django.conf import settings as django_settings
    
    # Backup-hantering
    if request.method == 'POST' and request.POST.get('action') == 'backup':
        return handle_backup_action(request)
    
    # Backup-uppladdning
    if request.method == 'POST' and request.POST.get('action') == 'upload_backup':
        return handle_backup_upload(request)
    
    # Vanlig settings-hantering
    if request.method == 'POST':
        settings = Settings.get_settings()
        
        # Uppdatera inställningar från formuläret
        settings.show_contacts_public = request.POST.get('show_contacts_public') == 'on'
        settings.show_prices_public = request.POST.get('show_prices_public') == 'on'
        settings.show_platforms_public = request.POST.get('show_platforms_public') == 'on'
        settings.show_only_received_axes_public = request.POST.get('show_only_received_axes_public') == 'on'
        
        # Visningsinställningar för publika användare
        settings.default_axes_rows_public = request.POST.get('default_axes_rows_public', '20')
        settings.default_transactions_rows_public = request.POST.get('default_transactions_rows_public', '15')
        settings.default_manufacturers_rows_public = request.POST.get('default_manufacturers_rows_public', '25')
        
        # Visningsinställningar för inloggade användare
        settings.default_axes_rows_private = request.POST.get('default_axes_rows_private', '50')
        settings.default_transactions_rows_private = request.POST.get('default_transactions_rows_private', '30')
        settings.default_manufacturers_rows_private = request.POST.get('default_manufacturers_rows_private', '50')
        
        # Systeminställningar
        settings.site_title = request.POST.get('site_title', 'AxeCollection')
        settings.site_description = request.POST.get('site_description', '')
        
        # Extern host-konfiguration
        settings.external_hosts = request.POST.get('external_hosts', '')
        settings.external_csrf_origins = request.POST.get('external_csrf_origins', '')
        
        settings.save()
        
        # Uppdatera host-konfigurationen om den ändrades
        if (request.POST.get('external_hosts') != settings.external_hosts or 
            request.POST.get('external_csrf_origins') != settings.external_csrf_origins):
            try:
                from django.core.management import call_command
                call_command('update_hosts')
                messages.success(request, 'Inställningar sparade och host-konfiguration uppdaterad!')
            except Exception as e:
                messages.warning(request, f'Inställningar sparade men host-konfiguration kunde inte uppdateras: {e}')
        else:
            messages.success(request, 'Inställningar sparade!')
        
        return redirect('settings')
    
    # Hämta nuvarande inställningar
    settings = Settings.get_settings()
    
    # Hämta backup-information
    backup_info = get_backup_info(django_settings.BASE_DIR)
    
    context = {
        'settings': settings,
        'backup_info': backup_info,
        'page_title': 'Inställningar'
    }
    
    return render(request, 'axes/settings.html', context)

def handle_backup_action(request):
    """Hantera backup-åtgärder"""
    from django.contrib import messages
    
    action = request.POST.get('backup_action')
    
    if action == 'create_backup':
        return create_backup(request)
    elif action == 'delete_backup':
        return delete_backup(request)
    elif action == 'restore_backup':
        return restore_backup(request)
    else:
        messages.error(request, 'Ogiltig åtgärd')
        return redirect('settings')

def handle_backup_upload(request):
    """Hantera backup-uppladdning"""
    from django.contrib import messages
    from .forms import BackupUploadForm
    from django.http import JsonResponse
    import os
    from django.conf import settings
    
    if request.method == 'POST':
        form = BackupUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['backup_file']
            
            # Skapa backup-mapp om den inte finns
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Spara filen
            file_path = os.path.join(backup_dir, uploaded_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Fixa behörigheter för Unraid
            try:
                os.chown(file_path, 99, 100)  # nobody:users
                os.chmod(file_path, 0o644)
            except:
                pass  # Ignorera om behörigheter inte kan sättas
            
            # Kontrollera om det är en AJAX-request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Backup-fil "{uploaded_file.name}" laddades upp framgångsrikt!'
                })
            else:
                messages.success(request, f'Backup-fil "{uploaded_file.name}" laddades upp framgångsrikt!')
        else:
            error_message = ' '.join([' '.join(errors) for errors in form.errors.values()])
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=400)
            else:
                for error in form.errors.values():
                    messages.error(request, error)
    
    return redirect('settings')

def get_backup_info(base_dir):
    """Hämta information om befintliga backuper"""
    import os
    from django.conf import settings
    
    backup_dir = os.path.join(base_dir, 'backups')
    backups = []
    
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                from datetime import datetime
                backup_info = {
                    'filename': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'path': file_path,
                    'stats': get_backup_stats(file_path)
                }
                backups.append(backup_info)
    
    # Sortera efter senast modifierad
    backups.sort(key=lambda x: x['modified'], reverse=True)
    
    return {
        'backups': backups,
        'backup_dir': backup_dir
    }

def get_backup_stats(backup_path):
    """Hämta statistik från backup-fil"""
    import zipfile
    import json
    import os
    
    try:
        if backup_path.endswith('.zip'):
            # Läs statistik från komprimerad backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if 'backup_stats.json' in zipf.namelist():
                    stats_content = zipf.read('backup_stats.json').decode('utf-8')
                    return json.loads(stats_content)

        elif backup_path.endswith('.sqlite3'):
            # För icke-komprimerade backuper, leta efter motsvarande stats-fil
            stats_path = backup_path.replace('.sqlite3', '_stats.json')
            if os.path.exists(stats_path):
                with open(stats_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
    except Exception as e:
        # Returnera None om statistik inte kan läsas
        pass
    return None

def create_backup(request):
    """Skapa ny backup"""
    import subprocess
    from django.conf import settings
    from django.contrib import messages
    
    try:
        include_media = request.POST.get('include_media') == 'on'
        compress = request.POST.get('compress') == 'on'
        
        cmd = ['python', 'manage.py', 'backup_database']
        if include_media:
            cmd.append('--include-media')
        if compress:
            cmd.append('--compress')
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=settings.BASE_DIR)
        
        if result.returncode == 0:
            messages.success(request, 'Backup skapad framgångsrikt!')
        else:
            messages.error(request, f'Fel vid backup: {result.stderr}')
            
    except Exception as e:
        messages.error(request, f'Fel vid backup: {str(e)}')
    
    return redirect('settings')

def delete_backup(request):
    """Ta bort backup"""
    import os
    from django.conf import settings
    from django.contrib import messages
    
    filename = request.POST.get('filename')
    if filename:
        backup_path = os.path.join(settings.BASE_DIR, 'backups', filename)
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                messages.success(request, f'Backup {filename} raderad')
            else:
                messages.error(request, 'Backup-filen finns inte')
        except Exception as e:
            messages.error(request, f'Fel vid radering: {str(e)}')
    
    return redirect('settings')

def restore_backup(request):
    """Återställ från backup"""
    import os
    import subprocess
    from django.conf import settings
    from django.contrib import messages
    
    filename = request.POST.get('filename')
    if not filename:
        messages.error(request, 'Ingen backup-fil vald')
        return redirect('settings')
    
    backup_path = os.path.join(settings.BASE_DIR, 'backups', filename)
    if not os.path.exists(backup_path):
        messages.error(request, 'Backup-filen finns inte')
        return redirect('settings')
    
    try:
        # Kör återställningskommandot
        cmd = ['python', 'manage.py', 'restore_backup', backup_path, '--confirm', '--include-media']
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=settings.BASE_DIR)
        
        if result.returncode == 0:
            messages.success(request, f'Backup {filename} återställd framgångsrikt!')
        else:
            messages.error(request, f'Fel vid återställning: {result.stderr}')
            
    except Exception as e:
        messages.error(request, f'Fel vid återställning: {str(e)}')
    
    return redirect('settings')

@login_required
def api_measurement_templates(request):
    """API för att hämta alla måttmallar"""
    try:
        templates = MeasurementTemplate.objects.filter(is_active=True).prefetch_related('items__measurement_type').order_by('sort_order', 'name')
        
        templates_data = []
        for template in templates:
            measurement_types = []
            for item in template.items.all():
                measurement_types.append({
                    'id': item.measurement_type.id,
                    'name': item.measurement_type.name,
                    'unit': item.measurement_type.unit,
                    'sort_order': item.sort_order
                })
            
            templates_data.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'sort_order': template.sort_order,
                'measurement_types': measurement_types
            })
        
        return JsonResponse({
            'success': True,
            'templates': templates_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def api_measurement_types(request):
    """API för att hämta alla måtttyper"""
    try:
        from .models import MeasurementType
        measurement_types = MeasurementType.objects.filter(is_active=True).order_by('sort_order', 'name')
        
        types_data = []
        for mt in measurement_types:
            types_data.append({
                'id': mt.id,
                'name': mt.name,
                'unit': mt.unit,
                'description': mt.description,
                'sort_order': mt.sort_order
            })
        
        return JsonResponse({
            'success': True,
            'measurement_types': types_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def api_create_measurement_template(request):
    """API för att skapa ny måttmall"""
    try:
        from .models import MeasurementTemplate, MeasurementTemplateItem, MeasurementType
        import json
        
        name = request.POST.get('template_name', '').strip()
        description = request.POST.get('template_description', '').strip()
        sort_order = int(request.POST.get('template_sort_order', 0))
        measurement_types_json = request.POST.get('measurement_types', '[]')
        
        if not name:
            return JsonResponse({
                'success': False,
                'error': 'Mallnamn är obligatoriskt'
            }, status=400)
        
        # Kontrollera om namnet redan finns
        if MeasurementTemplate.objects.filter(name=name).exists():
            return JsonResponse({
                'success': False,
                'error': 'En mall med detta namn finns redan'
            }, status=400)
        
        try:
            measurement_type_ids = json.loads(measurement_types_json)
        except:
            return JsonResponse({
                'success': False,
                'error': 'Ogiltiga måtttyper'
            }, status=400)
        
        if not measurement_type_ids:
            return JsonResponse({
                'success': False,
                'error': 'Du måste välja minst en måtttyp'
            }, status=400)
        
        # Skapa mallen
        template = MeasurementTemplate.objects.create(
            name=name,
            description=description,
            sort_order=sort_order
        )
        
        # Lägg till måtttyper till mallen
        for i, mt_id in enumerate(measurement_type_ids):
            try:
                measurement_type = MeasurementType.objects.get(id=mt_id, is_active=True)
                MeasurementTemplateItem.objects.create(
                    template=template,
                    measurement_type=measurement_type,
                    sort_order=i
                )
            except MeasurementType.DoesNotExist:
                # Ignorera ogiltiga måtttyper
                pass
        
        return JsonResponse({
            'success': True,
            'message': f'Måttmall "{name}" skapad framgångsrikt',
            'template_id': template.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def api_create_measurement_type(request):
    """API för att skapa ny måtttyp"""
    try:
        from .models import MeasurementType
        
        name = request.POST.get('measurement_type_name', '').strip()
        unit = request.POST.get('measurement_type_unit', '').strip()
        description = request.POST.get('measurement_type_description', '').strip()
        sort_order = int(request.POST.get('measurement_type_sort_order', 0))
        
        if not name or not unit:
            return JsonResponse({
                'success': False,
                'error': 'Namn och enhet är obligatoriska'
            }, status=400)
        
        # Kontrollera om namnet redan finns
        if MeasurementType.objects.filter(name=name).exists():
            return JsonResponse({
                'success': False,
                'error': 'En måtttyp med detta namn finns redan'
            }, status=400)
        
        # Skapa måtttypen
        measurement_type = MeasurementType.objects.create(
            name=name,
            unit=unit,
            description=description,
            sort_order=sort_order
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Måtttyp "{name}" skapad framgångsrikt',
            'measurement_type': {
                'id': measurement_type.id,
                'name': measurement_type.name,
                'unit': measurement_type.unit,
                'description': measurement_type.description,
                'sort_order': measurement_type.sort_order
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def api_update_measurement_type(request, type_id):
    """API för att uppdatera en befintlig måtttyp"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Endast POST-förfrågningar tillåtna'})
    
    try:
        measurement_type = get_object_or_404(MeasurementType, id=type_id)
        
        # Hämta data från formuläret
        name = request.POST.get('measurement_type_name', '').strip()
        unit = request.POST.get('measurement_type_unit', '').strip()
        description = request.POST.get('measurement_type_description', '').strip()
        sort_order = request.POST.get('measurement_type_sort_order', '0')
        
        # Validering
        if not name:
            return JsonResponse({'success': False, 'error': 'Namn är obligatoriskt'})
        if not unit:
            return JsonResponse({'success': False, 'error': 'Enhet är obligatorisk'})
        
        # Kontrollera om namnet redan finns (exklusive nuvarande måtttyp)
        if MeasurementType.objects.filter(name=name).exclude(id=type_id).exists():
            return JsonResponse({'success': False, 'error': f'En måtttyp med namnet "{name}" finns redan'})
        
        try:
            sort_order = int(sort_order)
        except ValueError:
            sort_order = 0
        
        # Uppdatera måtttypen
        measurement_type.name = name
        measurement_type.unit = unit
        measurement_type.description = description
        measurement_type.sort_order = sort_order
        measurement_type.save()
        
        return JsonResponse({
            'success': True,
            'measurement_type': {
                'id': measurement_type.id,
                'name': measurement_type.name,
                'unit': measurement_type.unit,
                'description': measurement_type.description,
                'sort_order': measurement_type.sort_order
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def api_delete_measurement_type(request, type_id):
    """API för att ta bort en måtttyp"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Endast POST-förfrågningar tillåtna'})
    
    try:
        from .models import MeasurementType, MeasurementTemplateItem
        
        measurement_type = get_object_or_404(MeasurementType, id=type_id)
        type_name = measurement_type.name
        
        # Kontrollera om måtttypen används i måttmallar
        template_items = MeasurementTemplateItem.objects.filter(measurement_type=measurement_type).count()
        if template_items > 0:
            return JsonResponse({
                'success': False, 
                'error': f'Måtttypen "{type_name}" kan inte tas bort eftersom den används i måttmallar. Ta bort den från mallarna först.'
            })
        
        # Ta bort måtttypen
        measurement_type.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Måtttypen "{type_name}" har tagits bort'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
