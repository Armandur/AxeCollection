from django.shortcuts import render, get_object_or_404, redirect
from .models import Axe, Transaction, Contact, Manufacturer, ManufacturerImage, ManufacturerLink, NextAxeID, AxeImage
from django.db.models import Sum, Q, Max
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django import forms
import requests
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import uuid
import os
from django.core.files.storage import default_storage

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
    """Redigera en befintlig yxa och lägg till bilder"""
    axe = get_object_or_404(Axe.objects.select_related('manufacturer').prefetch_related('images'), pk=pk)
    
    if request.method == 'POST':
        form = AxeForm(request.POST, request.FILES, instance=axe)
        if form.is_valid():
            axe = form.save()
            
            # Hantera bilduppladdning med MultipleFileField
            images = form.cleaned_data.get('images', [])
            image_urls = request.POST.getlist('image_urls')
            removed_images = request.POST.getlist('removed_images')
            
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
            remaining_images = axe.images.all().order_by('order')
            for index, image in enumerate(remaining_images, 1):
                # Generera nytt filnamn
                old_path = image.image.name
                file_ext = os.path.splitext(old_path)[1]
                new_filename = f"{axe.id}{chr(96 + index)}{file_ext}"  # a, b, c, etc.
                new_path = f'axe_images/{new_filename}'
                
                # Flytta filen till nytt namn om det behövs
                if old_path != new_path:
                    if default_storage.exists(old_path):
                        with default_storage.open(old_path, 'rb') as old_file:
                            default_storage.save(new_path, old_file)
                        # Ta bort gammal fil
                        default_storage.delete(old_path)
                    
                    # Uppdatera databasen
                    image.image = new_path
                    image.order = index
                    image.description = f'Bild {chr(96 + index).upper()} av {axe.manufacturer.name} {axe.model}'
                    image.save()
            
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
    
    return render(request, 'axes/axe_form.html', {
        'form': form,
        'axe': axe,
        'is_edit': True
    })
