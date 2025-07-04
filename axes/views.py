from django.shortcuts import render, get_object_or_404, redirect
from .models import Axe, Transaction, Contact, Manufacturer, ManufacturerImage, ManufacturerLink, NextAxeID, AxeImage, Platform
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
from .forms import TransactionForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Create your views here.

def axe_list(request):
    # Hämta filter från URL-parametrar
    status_filter = request.GET.get('status', '')
    manufacturer_filter = request.GET.get('manufacturer', '')
    
    # Starta med alla yxor
    axes = Axe.objects.all().select_related('manufacturer').prefetch_related('measurements', 'images', 'transaction_set')
    
    # Applicera filter
    if status_filter:
        axes = axes.filter(status=status_filter)
    
    if manufacturer_filter:
        axes = axes.filter(manufacturer_id=manufacturer_filter)
    
    # Sortera efter ID (senaste först)
    axes = axes.order_by('-id')
    
    # Hämta alla tillverkare för filter-dropdown
    manufacturers = Manufacturer.objects.all().order_by('name')
    
    # Beräkna statistik för varje yxa
    for axe in axes:
        transactions = axe.transaction_set.all()
        buy_transactions = transactions.filter(type='KÖP')
        sale_transactions = transactions.filter(type='SÄLJ')
        
        # Summa köp
        axe.total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
        axe.total_buy_shipping = buy_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
        
        # Summa försäljning
        axe.total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
        axe.total_sale_shipping = sale_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
        
        # Netto (försäljning - köp)
        axe.net_value = axe.total_sale_value - axe.total_buy_value
    
    # Statistik för hela samlingen
    transactions = Transaction.objects.all()
    total_buys = transactions.filter(type='KÖP').count()
    total_sales = transactions.filter(type='SÄLJ').count()
    total_buy_value = transactions.filter(type='KÖP').aggregate(total=Sum('price'))['total'] or 0
    total_sale_value = transactions.filter(type='SÄLJ').aggregate(total=Sum('price'))['total'] or 0
    total_buy_shipping = transactions.filter(type='KÖP').aggregate(total=Sum('shipping_cost'))['total'] or 0
    total_sale_shipping = transactions.filter(type='SÄLJ').aggregate(total=Sum('shipping_cost'))['total'] or 0
    total_profit = total_sale_value - total_buy_value
    total_profit_with_shipping = (total_sale_value + total_sale_shipping) - (total_buy_value + total_buy_shipping)
    
    # Hitta sålda yxor (de som har minst en SÄLJ-transaktion)
    sold_axe_ids = set(transactions.filter(type='SÄLJ').values_list('axe_id', flat=True))
    
    # Statistik för filtrerade yxor
    filtered_count = axes.count()
    bought_count = axes.filter(status='KÖPT').count()
    received_count = axes.filter(status='MOTTAGEN').count()
    
    return render(request, 'axes/axe_list.html', {
        'axes': axes,
        'manufacturers': manufacturers,
        'status_filter': status_filter,
        'manufacturer_filter': manufacturer_filter,
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

def axe_detail(request, pk):
    axe = get_object_or_404(Axe.objects.select_related('manufacturer').prefetch_related('measurements', 'images').prefetch_related('images'), pk=pk)
    
    # Hämta transaktioner för denna yxa
    transactions = Transaction.objects.filter(axe=axe).select_related('contact', 'platform').order_by('-transaction_date')
    
    # Beräkna totala kostnader och intäkter
    total_cost = transactions.filter(type='KÖP').aggregate(total=Sum('price'))['total'] or 0
    total_shipping_cost = transactions.filter(type='KÖP').aggregate(total=Sum('shipping_cost'))['total'] or 0
    total_revenue = transactions.filter(type='SÄLJ').aggregate(total=Sum('price'))['total'] or 0
    total_shipping_revenue = transactions.filter(type='SÄLJ').aggregate(total=Sum('shipping_cost'))['total'] or 0
    
    # Beräkna vinst/förlust
    total_investment = total_cost + total_shipping_cost
    total_income = total_revenue + total_shipping_revenue
    profit_loss = total_income - total_investment

    # Hantera POST för att lägga till ny transaktion, oavsett om det finns transaktioner
    if request.method == 'POST' and 'addTransactionForm' in request.POST.get('form_id', 'addTransactionForm'):
        transaction_form = TransactionForm(request.POST)
        if transaction_form.is_valid():
            transaction = transaction_form.save(commit=False)
            transaction.axe = axe
            # Hantera kontakt
            selected_contact_id = request.POST.get('selected_contact_id')
            if selected_contact_id:
                try:
                    transaction.contact = Contact.objects.get(id=selected_contact_id)
                except Contact.DoesNotExist:
                    pass
            else:
                contact_name = request.POST.get('contact_name')
                if contact_name:
                    contact, created = Contact.objects.get_or_create(
                        name=contact_name,
                        defaults={
                            'alias': request.POST.get('contact_alias', ''),
                            'email': request.POST.get('contact_email', ''),
                            'phone': request.POST.get('contact_phone', ''),
                            'comment': request.POST.get('contact_comment', ''),
                            'is_naj_member': request.POST.get('is_naj_member') == 'on'
                        }
                    )
                    transaction.contact = contact
            # Hantera plattform
            selected_platform_id = request.POST.get('selected_platform_id')
            if selected_platform_id:
                try:
                    transaction.platform = Platform.objects.get(id=selected_platform_id)
                except Platform.DoesNotExist:
                    pass
            else:
                platform_search = request.POST.get('platform_search')
                if platform_search and platform_search.strip():
                    platform, created = Platform.objects.get_or_create(name=platform_search.strip())
                    transaction.platform = platform
            # Sätt typ automatiskt utifrån priset
            if transaction.price < 0 or transaction.shipping_cost < 0:
                transaction.type = 'KÖP'
                transaction.price = abs(transaction.price)
                transaction.shipping_cost = abs(transaction.shipping_cost)
            else:
                transaction.type = 'SÄLJ'
                transaction.shipping_cost = abs(transaction.shipping_cost)
            transaction.save()
            return redirect('axe_detail', pk=axe.pk)
    else:
        transaction_form = TransactionForm()

    context = {
        'axe': axe,
        'transactions': transactions,
        'total_cost': total_cost,
        'total_shipping_cost': total_shipping_cost,
        'total_revenue': total_revenue,
        'total_shipping_revenue': total_shipping_revenue,
        'total_investment': total_investment,
        'total_income': total_income,
        'profit_loss': profit_loss,
        'transaction_form': transaction_form,
    }
    
    return render(request, 'axes/axe_detail.html', context)

def contact_list(request):
    """Visa alla kontakter i systemet"""
    contacts = Contact.objects.all().order_by('name')
    
    # Beräkna statistik för varje kontakt
    for contact in contacts:
        transactions = Transaction.objects.filter(contact=contact)
        contact.total_transactions = transactions.count()
        contact.buy_count = transactions.filter(type='KÖP').count()
        contact.sale_count = transactions.filter(type='SÄLJ').count()
        
        # Beräkna ekonomisk statistik
        buy_transactions = transactions.filter(type='KÖP')
        sale_transactions = transactions.filter(type='SÄLJ')
        
        contact.total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
        contact.total_buy_shipping = buy_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
        contact.total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
        contact.total_sale_shipping = sale_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
        contact.net_value = contact.total_sale_value - contact.total_buy_value

    total_contacts = contacts.count()
    total_transactions_count = Transaction.objects.count()
    total_naj_members = Contact.objects.filter(is_naj_member=True).count()
    
    context = {
        'contacts': contacts,
        'total_contacts': total_contacts,
        'total_transactions': total_transactions_count,
        'total_naj_members': total_naj_members
    }
    
    return render(request, 'axes/contact_list.html', context)

def contact_detail(request, pk):
    """Visa detaljerad information om en kontakt"""
    contact = get_object_or_404(Contact, pk=pk)
    
    # Hämta alla transaktioner för denna kontakt
    transactions = Transaction.objects.filter(contact=contact).select_related('axe__manufacturer', 'platform').order_by('-transaction_date')
    
    # Beräkna statistik
    total_transactions = transactions.count()
    buy_transactions = transactions.filter(type='KÖP')
    sale_transactions = transactions.filter(type='SÄLJ')
    
    total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_profit = total_sale_value - total_buy_value
    
    # Hämta unika yxor som kontaktens transaktioner gäller
    unique_axes = set()
    for transaction in transactions:
        unique_axes.add(transaction.axe)
    
    context = {
        'contact': contact,
        'transactions': transactions,
        'total_transactions': total_transactions,
        'total_buy_value': total_buy_value,
        'total_sale_value': total_sale_value,
        'total_profit': total_profit,
        'unique_axes': unique_axes,
        'buy_count': buy_transactions.count(),
        'sale_count': sale_transactions.count(),
    }
    
    return render(request, 'axes/contact_detail.html', context)

def transaction_list(request):
    """Visa alla transaktioner i systemet"""
    transactions = Transaction.objects.all().select_related('axe__manufacturer', 'contact', 'platform').order_by('-transaction_date')
    
    # Beräkna totala statistik
    total_buys = transactions.filter(type='KÖP').count()
    total_sales = transactions.filter(type='SÄLJ').count()
    total_buy_value = transactions.filter(type='KÖP').aggregate(total=Sum('price'))['total'] or 0
    total_sale_value = transactions.filter(type='SÄLJ').aggregate(total=Sum('price'))['total'] or 0
    total_profit = total_sale_value - total_buy_value
    
    context = {
        'transactions': transactions,
        'total_buys': total_buys,
        'total_sales': total_sales,
        'total_buy_value': total_buy_value,
        'total_sale_value': total_sale_value,
        'total_profit': total_profit,
    }
    
    return render(request, 'axes/transaction_list.html', context)

def manufacturer_list(request):
    """Visa alla tillverkare i systemet"""
    manufacturers = Manufacturer.objects.all()
    
    # Beräkna statistik för varje tillverkare
    for manufacturer in manufacturers:
        axes = Axe.objects.filter(manufacturer=manufacturer)
        manufacturer.axe_count = axes.count()
        
        # Hämta alla transaktioner för denna tillverkare
        transactions = Transaction.objects.filter(axe__manufacturer=manufacturer)
        manufacturer.total_transactions = transactions.count()
        manufacturer.buy_count = transactions.filter(type='KÖP').count()
        manufacturer.sale_count = transactions.filter(type='SÄLJ').count()
        
        # Beräkna ekonomisk statistik
        buy_transactions = transactions.filter(type='KÖP')
        sale_transactions = transactions.filter(type='SÄLJ')
        
        manufacturer.total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
        manufacturer.total_buy_shipping = buy_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
        manufacturer.total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
        manufacturer.total_sale_shipping = sale_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
        manufacturer.net_value = manufacturer.total_sale_value - manufacturer.total_buy_value

    # Sortera tillverkare efter antal yxor (flest först)
    manufacturers = sorted(manufacturers, key=lambda m: m.axe_count, reverse=True)

    total_manufacturers = len(manufacturers)
    total_axes_count = Axe.objects.count()
    total_transactions_count = Transaction.objects.count()
    
    # Beräkna genomsnitt antal yxor per tillverkare
    average_axes_per_manufacturer = total_axes_count / total_manufacturers if total_manufacturers > 0 else 0
    
    context = {
        'manufacturers': manufacturers,
        'total_manufacturers': total_manufacturers,
        'total_axes': total_axes_count,
        'total_transactions': total_transactions_count,
        'average_axes_per_manufacturer': average_axes_per_manufacturer
    }
    
    return render(request, 'axes/manufacturer_list.html', context)

def manufacturer_detail(request, pk):
    """Visa detaljerad information om en tillverkare"""
    manufacturer = get_object_or_404(Manufacturer, pk=pk)
    
    # Hämta alla yxor för denna tillverkare
    axes = Axe.objects.filter(manufacturer=manufacturer).order_by('model')
    
    # Beräkna status för varje yxa
    for axe in axes:
        # Hämta den senaste transaktionen för varje yxa
        last_transaction = Transaction.objects.filter(axe=axe).order_by('-transaction_date').first()
        if last_transaction:
            if last_transaction.type == 'SÄLJ':
                axe.status = 'SÅLD'
                axe.status_class = 'bg-secondary'
            else:
                axe.status = 'ÄGES'
                axe.status_class = 'bg-primary'
        else:
            axe.status = 'ÄGES'
            axe.status_class = 'bg-primary'
    
    # Hämta alla transaktioner för denna tillverkare
    transactions = Transaction.objects.filter(axe__manufacturer=manufacturer).select_related('axe', 'contact', 'platform').order_by('-transaction_date')
    
    # Hämta tillverkarens bilder
    manufacturer_images = ManufacturerImage.objects.filter(manufacturer=manufacturer)
    
    # Hämta tillverkarens länkar
    manufacturer_links = ManufacturerLink.objects.filter(manufacturer=manufacturer, is_active=True)
    
    # Gruppera länkar efter typ
    links_by_type = {}
    for link in manufacturer_links:
        if link.link_type not in links_by_type:
            links_by_type[link.link_type] = []
        links_by_type[link.link_type].append(link)
    
    # Beräkna statistik
    total_axes = axes.count()
    total_transactions = transactions.count()
    buy_transactions = transactions.filter(type='KÖP')
    sale_transactions = transactions.filter(type='SÄLJ')
    
    total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_profit = total_sale_value - total_buy_value
    
    # Beräkna genomsnitt vinst per yxa
    average_profit_per_axe = total_profit / total_axes if total_axes > 0 else 0
    
    # Hämta unika kontakter som har transaktioner med denna tillverkare
    unique_contacts = set()
    for transaction in transactions:
        if transaction.contact:
            unique_contacts.add(transaction.contact)
    
    context = {
        'manufacturer': manufacturer,
        'axes': axes,
        'transactions': transactions,
        'total_axes': total_axes,
        'total_transactions': total_transactions,
        'total_buy_value': total_buy_value,
        'total_sale_value': total_sale_value,
        'total_profit': total_profit,
        'average_profit_per_axe': average_profit_per_axe,
        'unique_contacts': unique_contacts,
        'buy_count': buy_transactions.count(),
        'sale_count': sale_transactions.count(),
        'manufacturer_images': manufacturer_images,
        'manufacturer_links': manufacturer_links,
        'links_by_type': links_by_type,
    }
    
    return render(request, 'axes/manufacturer_detail.html', context)

def axe_gallery(request, pk=None):
    """Visa yxor i galleriformat med navigation mellan dem"""
    # Hämta alla yxor sorterade efter ID för enkel navigation
    all_axes = Axe.objects.all().select_related('manufacturer').prefetch_related('images').order_by('id')
    
    if pk:
        # Visa specifik yxa
        current_axe = get_object_or_404(Axe.objects.select_related('manufacturer').prefetch_related('images', 'measurements'), pk=pk)
        
        # Hitta position i listan för navigation
        axe_list = list(all_axes)
        try:
            current_index = axe_list.index(current_axe)
        except ValueError:
            current_index = 0
            
        # Hämta föregående och nästa yxa
        prev_axe = axe_list[current_index - 1] if current_index > 0 else None
        next_axe = axe_list[current_index + 1] if current_index < len(axe_list) - 1 else None
        
        # Hämta transaktioner för denna yxa
        transactions = Transaction.objects.filter(axe=current_axe).select_related('contact', 'platform').order_by('-transaction_date')
        
        # Beräkna ekonomisk statistik
        total_cost = transactions.filter(type='KÖP').aggregate(total=Sum('price'))['total'] or 0
        total_shipping_cost = transactions.filter(type='KÖP').aggregate(total=Sum('shipping_cost'))['total'] or 0
        total_revenue = transactions.filter(type='SÄLJ').aggregate(total=Sum('price'))['total'] or 0
        total_shipping_revenue = transactions.filter(type='SÄLJ').aggregate(total=Sum('shipping_cost'))['total'] or 0
        
        total_investment = total_cost + total_shipping_cost
        total_income = total_revenue + total_shipping_revenue
        profit_loss = total_income - total_investment
        
        context = {
            'current_axe': current_axe,
            'prev_axe': prev_axe,
            'next_axe': next_axe,
            'current_index': current_index + 1,  # 1-baserat index för visning
            'total_axes': len(axe_list),
            'transactions': transactions,
            'total_cost': total_cost,
            'total_shipping_cost': total_shipping_cost,
            'total_revenue': total_revenue,
            'total_shipping_revenue': total_shipping_revenue,
            'total_investment': total_investment,
            'total_income': total_income,
            'profit_loss': profit_loss,
        }
        
        return render(request, 'axes/axe_gallery.html', context)
    else:
        # Visa senaste yxan (högst id) som standard
        if all_axes.exists():
            last_axe = all_axes.last()
            return axe_gallery(request, last_axe.pk)
        else:
            # Inga yxor finns
            return render(request, 'axes/axe_gallery.html', {
                'current_axe': None,
                'prev_axe': None,
                'next_axe': None,
                'current_index': 0,
                'total_axes': 0,
            })

@require_POST
def update_axe_status(request, pk):
    """Uppdatera yxans status via AJAX"""
    try:
        axe = get_object_or_404(Axe, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in ['KÖPT', 'MOTTAGEN']:
            axe.status = new_status
            axe.save()
            
            return JsonResponse({
                'success': True,
                'status': new_status,
                'status_display': 'Köpt' if new_status == 'KÖPT' else 'Mottagen'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Ogiltig status'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

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

def axe_create(request):
    if request.method == 'POST':
        form = AxeForm(request.POST, request.FILES)
        if form.is_valid():
            axe = form.save()
            
            # Hantera kontakthantering
            contact_search = form.cleaned_data.get('contact_search')
            contact = None
            
            if contact_search:
                # Först försök hitta befintlig kontakt
                existing_contact = Contact.objects.filter(
                    Q(name__icontains=contact_search) | 
                    Q(alias__icontains=contact_search) |
                    Q(email__icontains=contact_search)
                ).first()
                
                if existing_contact:
                    # Använd befintlig kontakt
                    contact = existing_contact
                else:
                    # Skapa ny kontakt om namn anges
                    contact_name = form.cleaned_data.get('contact_name')
                    if contact_name:
                        contact = Contact.objects.create(
                            name=contact_name,
                            email=form.cleaned_data.get('contact_email', ''),
                            phone=form.cleaned_data.get('contact_phone', ''),
                            alias=form.cleaned_data.get('contact_alias', ''),
                            comment=form.cleaned_data.get('contact_comment', ''),
                            is_naj_member=form.cleaned_data.get('is_naj_member', False)
                        )
            
            # Hantera plattformshantering
            platform_search = form.cleaned_data.get('platform_search')
            platform = None
            
            if platform_search:
                # Försök hitta befintlig plattform
                existing_platform = Platform.objects.filter(
                    name__icontains=platform_search
                ).first()
                
                if existing_platform:
                    # Använd befintlig plattform
                    platform = existing_platform
                else:
                    # Skapa ny plattform med sökvärdet som namn
                    platform = Platform.objects.create(name=platform_search.strip())
            
            # Hantera transaktion
            if contact and (form.cleaned_data.get('transaction_price') or form.cleaned_data.get('transaction_shipping')):
                price = form.cleaned_data.get('transaction_price', 0)
                shipping = form.cleaned_data.get('transaction_shipping', 0)
                transaction_date = form.cleaned_data.get('transaction_date') or timezone.now().date()
                transaction_comment = form.cleaned_data.get('transaction_comment', '')
                
                # Bestäm transaktionstyp baserat på summan (negativ = köp, positiv = sälj)
                total_amount = (price or 0) + (shipping or 0)
                transaction_type = 'KÖP' if total_amount < 0 else 'SÄLJ'
                
                # Spara alltid pris och frakt som positiva värden
                def abs_decimal(val):
                    try:
                        return abs(val)
                    except Exception:
                        return 0

                price = abs_decimal(price)
                shipping = abs_decimal(shipping)
                
                # Skapa kommentar
                final_comment = transaction_comment  # Spara bara det användaren skriver
                
                Transaction.objects.create(
                    axe=axe,
                    contact=contact,
                    platform=platform,
                    transaction_date=transaction_date,
                    type=transaction_type,
                    price=price,
                    shipping_cost=shipping,
                    comment=final_comment
                )
            
            # Hantera bilduppladdning med MultipleFileField
            images = form.cleaned_data.get('images', [])
            image_counter = 0
            
            # Först hantera uppladdade filer
            for image in images:
                # Generera temporärt UUID-filnamn
                temp_filename = f"temp_{uuid.uuid4()}{os.path.splitext(image.name)[1]}"
                
                # Spara med temporärt namn
                temp_path = default_storage.save(f'axe_images/{temp_filename}', image)
                
                # Konvertera till permanent namn baserat på yxans ID och ordning
                image_counter += 1
                suffix = chr(96 + image_counter)  # a, b, c, etc.
                permanent_filename = f"{axe.id}{suffix}{os.path.splitext(image.name)[1]}"
                permanent_path = f'axe_images/{permanent_filename}'
                
                # Flytta filen till permanent namn
                if default_storage.exists(temp_path):
                    with default_storage.open(temp_path, 'rb') as temp_file:
                        default_storage.save(permanent_path, temp_file)
                    # Ta bort temporär fil
                    default_storage.delete(temp_path)
                
                # Skapa AxeImage med permanent sökväg
                AxeImage.objects.create(
                    axe=axe,
                    image=permanent_path,
                    description=f'Bild {suffix.upper()} av {axe.manufacturer.name} {axe.model}',
                    order=image_counter
                )
            
            # Hantera URL:er
            image_urls = request.POST.getlist('image_urls')
            for url in image_urls:
                if url.strip():
                    try:
                        # Hämta bilden från URL
                        response = requests.get(url, timeout=10)
                        response.raise_for_status()
                        
                        # Bestäm filändelse från Content-Type
                        content_type = response.headers.get('content-type', '')
                        if 'jpeg' in content_type or 'jpg' in content_type:
                            ext = '.jpg'
                        elif 'png' in content_type:
                            ext = '.png'
                        elif 'gif' in content_type:
                            ext = '.gif'
                        elif 'webp' in content_type:
                            ext = '.webp'
                        else:
                            ext = '.jpg'  # Standard
                        
                        # Generera temporärt UUID-filnamn
                        temp_filename = f"temp_{uuid.uuid4()}{ext}"
                        temp_path = f'axe_images/{temp_filename}'
                        
                        # Spara med temporärt namn
                        content_file = ContentFile(response.content, name=temp_filename)
                        default_storage.save(temp_path, content_file)
                        
                        # Konvertera till permanent namn
                        image_counter += 1
                        suffix = chr(96 + image_counter)  # a, b, c, etc.
                        permanent_filename = f"{axe.id}{suffix}{ext}"
                        permanent_path = f'axe_images/{permanent_filename}'
                        
                        # Flytta filen till permanent namn
                        if default_storage.exists(temp_path):
                            with default_storage.open(temp_path, 'rb') as temp_file:
                                default_storage.save(permanent_path, temp_file)
                            # Ta bort temporär fil
                            default_storage.delete(temp_path)
                        
                        # Skapa AxeImage med permanent sökväg
                        AxeImage.objects.create(
                            axe=axe,
                            image=permanent_path,
                            description=f'Bild {suffix.upper()} från URL: {axe.manufacturer.name} {axe.model}',
                            order=image_counter
                        )
                    except Exception as e:
                        # Logga fel men fortsätt med andra bilder
                        print(f"Kunde inte ladda bild från {url}: {e}")
            
            return redirect('axe_detail', pk=axe.pk)
    else:
        form = AxeForm()
    
    # Hämta nästa ID som ska användas
    next_id = NextAxeID.objects.get_or_create(id=1, defaults={'next_id': 1})[0].next_id
    
    return render(request, 'axes/axe_form.html', {
        'form': form,
        'next_id': next_id
    })

def axe_edit(request, pk):
    axe = get_object_or_404(Axe.objects.select_related('manufacturer').prefetch_related('images'), pk=pk)
    
    if request.method == 'POST':
        # Skapa formuläret utan transaktions-/kontakt-/plattformfält
        form = AxeForm(request.POST, request.FILES, instance=axe)
        # Ta bort transaktions-/kontakt-/plattformfält från form.fields
        for field in [
            'transaction_price', 'transaction_shipping', 'transaction_date', 'transaction_comment',
            'contact_search', 'contact_name', 'contact_email', 'contact_phone', 'contact_alias', 'contact_comment', 'is_naj_member',
            'platform_search']:
            if field in form.fields:
                form.fields.pop(field)
        if form.is_valid():
            axe = form.save()
            # Hantera endast bilder och bildordning
            images = form.cleaned_data.get('images', [])
            image_urls = request.POST.getlist('image_urls')
            removed_images = request.POST.getlist('removed_images')
            
            # Hantera bildordning från drag & drop
            image_orders = request.POST.getlist('image_order')
            print(f"Fick bildordning: {image_orders}")  # Debug
            if image_orders:
                for order_data in image_orders:
                    if ':' in order_data:
                        image_id, new_order = order_data.split(':', 1)
                        try:
                            image = AxeImage.objects.get(id=image_id, axe=axe)
                            print(f"Uppdaterar bild {image_id} till ordning {new_order}")  # Debug
                            image.order = int(new_order)
                            image.save()
                        except (AxeImage.DoesNotExist, ValueError) as e:
                            print(f"Kunde inte uppdatera bild {image_id}: {e}")  # Debug
                            pass  # Ignorera ogiltiga data
            
            # Ta bort markerade bilder först
            if removed_images:
                for image_id in removed_images:
                    try:
                        image_to_delete = AxeImage.objects.get(id=image_id, axe=axe)
                        # Ta bort filen från disk
                        if image_to_delete.image:
                            default_storage.delete(image_to_delete.image.name)
                        # Ta bort från databasen
                        image_to_delete.delete()
                    except AxeImage.DoesNotExist:
                        pass  # Bilden finns inte, ignorera
            
            # Omnumrera alla återstående bilder efter borttagning
            remaining_images = list(axe.images.all().order_by('order'))
            temp_paths = []
            temp_webps = []
            # Steg 1: Döp om till temporära namn
            for idx, image in enumerate(remaining_images, 1):
                old_path = image.image.name
                file_ext = os.path.splitext(old_path)[1]
                temp_filename = f"{axe.id}_tmp_{idx}{file_ext}"
                temp_path = f'axe_images/{temp_filename}'
                # Temporärt namn för .webp
                old_webp = os.path.splitext(old_path)[0] + '.webp'
                temp_webp = f'axe_images/{axe.id}_tmp_{idx}.webp'
                # Döp om originalfilen
                if old_path != temp_path and default_storage.exists(old_path):
                    with default_storage.open(old_path, 'rb') as old_file:
                        default_storage.save(temp_path, old_file)
                    default_storage.delete(old_path)
                temp_paths.append((image, temp_path, file_ext))
                # Döp om .webp om den finns
                if os.path.exists(os.path.join(settings.MEDIA_ROOT, old_webp)):
                    try:
                        os.rename(
                            os.path.join(settings.MEDIA_ROOT, old_webp),
                            os.path.join(settings.MEDIA_ROOT, temp_webp)
                        )
                    except Exception as e:
                        pass
                temp_webps.append(temp_webp)
            # Steg 2: Döp om till slutgiltiga namn
            for idx, (image, temp_path, file_ext) in enumerate(temp_paths, 1):
                final_filename = f"{axe.id}{chr(96 + idx)}{file_ext}"
                final_path = f'axe_images/{final_filename}'
                # Döp om originalfilen
                if temp_path != final_path and default_storage.exists(temp_path):
                    with default_storage.open(temp_path, 'rb') as temp_file:
                        default_storage.save(final_path, temp_file)
                    default_storage.delete(temp_path)
                # Döp om .webp om den finns
                temp_webp = temp_webps[idx-1]
                final_webp = f'axe_images/{axe.id}{chr(96 + idx)}.webp'
                if os.path.exists(os.path.join(settings.MEDIA_ROOT, temp_webp)):
                    try:
                        os.rename(
                            os.path.join(settings.MEDIA_ROOT, temp_webp),
                            os.path.join(settings.MEDIA_ROOT, final_webp)
                        )
                    except Exception as e:
                        pass
                # Uppdatera databasen
                image.image = final_path
                image.order = idx
                image.description = f'Bild {chr(96 + idx).upper()} av {axe.manufacturer.name} {axe.model}'
                image.save()  # Skapar även ny .webp om det behövs
            
            # Hämta nuvarande högsta ordning för denna yxa
            max_order = axe.images.aggregate(Max('order'))['order__max'] or 0
            image_counter = max_order
            
            # Hantera endast nya uppladdade filer
            # I redigeringsläge ska vi bara hantera faktiskt nya filer
            # Befintliga bilder hanteras inte via MultipleFileField
            for image in images:
                # Generera temporärt UUID-filnamn
                temp_filename = f"temp_{uuid.uuid4()}{os.path.splitext(image.name)[1]}"
                
                # Spara med temporärt namn
                temp_path = default_storage.save(f'axe_images/{temp_filename}', image)
                
                # Konvertera till permanent namn baserat på yxans ID och ordning
                image_counter += 1
                suffix = chr(96 + image_counter)  # a, b, c, etc.
                permanent_filename = f"{axe.id}{suffix}{os.path.splitext(image.name)[1]}"
                permanent_path = f'axe_images/{permanent_filename}'
                
                # Flytta filen till permanent namn
                if default_storage.exists(temp_path):
                    with default_storage.open(temp_path, 'rb') as temp_file:
                        default_storage.save(permanent_path, temp_file)
                    # Ta bort temporär fil
                    default_storage.delete(temp_path)
                
                # Skapa AxeImage med permanent sökväg
                AxeImage.objects.create(
                    axe=axe,
                    image=permanent_path,
                    description=f'Bild {suffix.upper()} av {axe.manufacturer.name} {axe.model}',
                    order=image_counter
                )
            
            # Hantera URL:er
            for url in image_urls:
                if url.strip():
                    try:
                        # Hämta bilden från URL
                        response = requests.get(url, timeout=10)
                        response.raise_for_status()
                        
                        # Bestäm filändelse från Content-Type
                        content_type = response.headers.get('content-type', '')
                        if 'jpeg' in content_type or 'jpg' in content_type:
                            ext = '.jpg'
                        elif 'png' in content_type:
                            ext = '.png'
                        elif 'gif' in content_type:
                            ext = '.gif'
                        elif 'webp' in content_type:
                            ext = '.webp'
                        else:
                            ext = '.jpg'  # Standard
                        
                        # Generera temporärt UUID-filnamn
                        temp_filename = f"temp_{uuid.uuid4()}{ext}"
                        temp_path = f'axe_images/{temp_filename}'
                        
                        # Spara med temporärt namn
                        content_file = ContentFile(response.content, name=temp_filename)
                        default_storage.save(temp_path, content_file)
                        
                        # Konvertera till permanent namn
                        image_counter += 1
                        suffix = chr(96 + image_counter)  # a, b, c, etc.
                        permanent_filename = f"{axe.id}{suffix}{ext}"
                        permanent_path = f'axe_images/{permanent_filename}'
                        
                        # Flytta filen till permanent namn
                        if default_storage.exists(temp_path):
                            with default_storage.open(temp_path, 'rb') as temp_file:
                                default_storage.save(permanent_path, temp_file)
                            # Ta bort temporär fil
                            default_storage.delete(temp_path)
                        
                        # Skapa AxeImage med permanent sökväg
                        AxeImage.objects.create(
                            axe=axe,
                            image=permanent_path,
                            description=f'Bild {suffix.upper()} från URL: {axe.manufacturer.name} {axe.model}',
                            order=image_counter
                        )
                    except Exception as e:
                        # Logga fel men fortsätt med andra bilder
                        print(f"Kunde inte ladda bild från {url}: {e}")
            
            return redirect('axe_detail', pk=axe.pk)
    else:
        form = AxeForm(instance=axe)
        for field in [
            'transaction_price', 'transaction_shipping', 'transaction_date', 'transaction_comment',
            'contact_search', 'contact_name', 'contact_email', 'contact_phone', 'contact_alias', 'contact_comment', 'is_naj_member',
            'platform_search']:
            if field in form.fields:
                form.fields.pop(field)
    return render(request, 'axes/axe_form.html', {
        'form': form,
        'axe': axe,
        'is_edit': True
    })

def api_transaction_detail(request, pk):
    """Returnerar JSON-data för en enskild transaktion (för AJAX-redigering)"""
    try:
        transaction = Transaction.objects.select_related('contact', 'platform').get(pk=pk)
    except Transaction.DoesNotExist:
        raise Http404("Transaktion finns inte")
    data = {
        'id': transaction.id,
        'axe_id': transaction.axe_id,
        'contact_id': transaction.contact.id if transaction.contact else None,
        'contact_name': transaction.contact.name if transaction.contact else '',
        'contact_alias': transaction.contact.alias if transaction.contact else '',
        'contact_email': transaction.contact.email if transaction.contact else '',
        'contact_phone': transaction.contact.phone if transaction.contact else '',
        'platform_id': transaction.platform.id if transaction.platform else None,
        'platform_name': transaction.platform.name if transaction.platform else '',
        'price': float(transaction.price) if transaction.price is not None else '',
        'shipping_cost': float(transaction.shipping_cost) if transaction.shipping_cost is not None else '',
        'transaction_date': transaction.transaction_date.strftime('%Y-%m-%d') if transaction.transaction_date else '',
        'comment': transaction.comment or '',
        'type': transaction.type,
    }
    return JsonResponse(data)

@csrf_exempt
@require_http_methods(["POST"])
def api_transaction_update(request, pk):
    """Uppdatera en transaktion via AJAX (POST)."""
    try:
        transaction = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Transaktion finns inte.'}, status=404)

    # Hämta data
    data = request.POST
    errors = {}

    # Datum
    transaction.transaction_date = data.get('transaction_date') or transaction.transaction_date

    # Pris och frakt
    try:
        price = float(data.get('price', ''))
        shipping = float(data.get('shipping_cost', ''))
    except (TypeError, ValueError):
        errors['price'] = 'Ogiltigt pris eller frakt.'
        price = transaction.price
        shipping = transaction.shipping_cost

    # Typ: negativt = KÖP, positivt = SÄLJ
    if price < 0 or shipping < 0:
        transaction.type = 'KÖP'
        transaction.price = abs(price)
        transaction.shipping_cost = abs(shipping)
    else:
        transaction.type = 'SÄLJ'
        transaction.price = abs(price)
        transaction.shipping_cost = abs(shipping)

    # Kommentar
    transaction.comment = data.get('comment', transaction.comment)

    # Kontakt
    selected_contact_id = data.get('selected_contact_id')
    if selected_contact_id:
        try:
            transaction.contact = Contact.objects.get(id=selected_contact_id)
        except Contact.DoesNotExist:
            errors['contact'] = 'Kontakt finns inte.'
    else:
        contact_name = data.get('contact_name')
        if contact_name:
            contact, created = Contact.objects.get_or_create(
                name=contact_name,
                defaults={
                    'alias': data.get('contact_alias', ''),
                    'email': data.get('contact_email', ''),
                    'phone': data.get('contact_phone', ''),
                    'comment': data.get('contact_comment', ''),
                    'is_naj_member': data.get('is_naj_member') == 'on'
                }
            )
            transaction.contact = contact
        else:
            transaction.contact = None

    # Plattform
    selected_platform_id = data.get('selected_platform_id')
    if selected_platform_id:
        try:
            transaction.platform = Platform.objects.get(id=selected_platform_id)
        except Platform.DoesNotExist:
            errors['platform'] = 'Plattform finns inte.'
    else:
        platform_search = data.get('platform_search')
        if platform_search and platform_search.strip():
            platform, created = Platform.objects.get_or_create(name=platform_search.strip())
            transaction.platform = platform
        else:
            transaction.platform = None

    if errors:
        return JsonResponse({'success': False, 'errors': errors}, status=400)

    transaction.save()
    return JsonResponse({'success': True})
