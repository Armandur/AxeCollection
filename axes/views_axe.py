from django.shortcuts import render, get_object_or_404, redirect
from .models import Axe, AxeImage, Measurement, NextAxeID, MeasurementTemplate, Transaction, Contact, Platform, Manufacturer
from .forms import AxeForm, MeasurementForm, TransactionForm
from django.db.models import Sum, Q, Max, Count
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import requests
import uuid
import os
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from urllib.parse import urlparse

# --- Yx-relaterade vyer ---

def axe_list(request):
    # Hämta filter från URL-parametrar
    status_filter = request.GET.get('status', '')
    manufacturer_filter = request.GET.get('manufacturer', '')
    platform_filter = request.GET.get('platform', '')
    
    # Starta med alla yxor
    axes = Axe.objects.all().select_related('manufacturer').prefetch_related('measurements', 'images', 'transactions')
    
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
    if request.method == 'POST' and 'addTransactionForm' in request.POST.get('form_id', 'addTransactionForm'):
        transaction_form = TransactionForm(request.POST)
        if transaction_form.is_valid():
            transaction = transaction_form.save(commit=False)
            transaction.axe = axe
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
        'breadcrumbs': [
            {'text': 'Yxsamling', 'url': '/yxor/'},
            {'text': axe.manufacturer.name, 'url': f'/tillverkare/{axe.manufacturer.id}/'},
            {'text': f'{axe.display_id} - {axe.model}'}
        ],
    }
    return render(request, 'axes/axe_detail.html', context)

def axe_create(request):
    if request.method == 'POST':
        form = AxeForm(request.POST, request.FILES)
        if form.is_valid():
            axe = form.save(commit=False)
            axe.created_by = request.user
            axe.save()

            # Hantera nya bilder
            if 'images' in request.FILES:
                for image_file in request.FILES.getlist('images'):
                    try:
                        axe_image = AxeImage(axe=axe, image=image_file)
                        axe_image.save()
                    except Exception as e:
                        pass

            # Hantera URL-bilder
            if 'image_urls' in request.POST:
                for image_url in request.POST.getlist('image_urls'):
                    if image_url and image_url.startswith('http'):
                        try:
                            response = requests.get(image_url, timeout=10)
                            if response.status_code == 200:
                                file_extension = os.path.splitext(urlparse(image_url).path)[1] or '.jpg'
                                filename = f"{axe.id}_{uuid.uuid4().hex[:8]}{file_extension}"
                                image_file = ContentFile(response.content, name=filename)
                                axe_image = AxeImage(axe=axe, image=image_file)
                                axe_image.save()
                        except Exception as e:
                            pass

            # Omnumrera och döp om alla bilder enligt standard efter uppladdning (endast om det finns bilder)
            remaining_images = list(axe.images.all().order_by('order', 'id'))
            if remaining_images:
                from django.core.files.storage import default_storage
                from django.conf import settings
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
                        except Exception:
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
                        except Exception:
                            pass
                    # Uppdatera databasen
                    image.image = final_path
                    image.order = idx
                    image.description = f'Bild {chr(96 + idx).upper()} av {axe.manufacturer.name} {axe.model}'
                    image.save()

            # Hantera kontakt
            contact = None
            contact_search = form.cleaned_data.get('contact_search', '').strip()
            if contact_search:
                # Försök hitta befintlig kontakt
                try:
                    contact = Contact.objects.get(name__iexact=contact_search)
                except Contact.DoesNotExist:
                    # Skapa ny kontakt
                    contact_name = form.cleaned_data.get('contact_name', '').strip()
                    if contact_name:
                        contact, created = Contact.objects.get_or_create(
                            name=contact_name,
                            defaults={
                                'alias': form.cleaned_data.get('contact_alias', ''),
                                'email': form.cleaned_data.get('contact_email', ''),
                                'phone': form.cleaned_data.get('contact_phone', ''),
                                'comment': form.cleaned_data.get('contact_comment', ''),
                                'is_naj_member': form.cleaned_data.get('is_naj_member', False)
                            }
                        )
                    else:
                        # Använd sökvärdet som namn
                        contact, created = Contact.objects.get_or_create(
                            name=contact_search,
                            defaults={
                                'alias': form.cleaned_data.get('contact_alias', ''),
                                'email': form.cleaned_data.get('contact_email', ''),
                                'phone': form.cleaned_data.get('contact_phone', ''),
                                'comment': form.cleaned_data.get('contact_comment', ''),
                                'is_naj_member': form.cleaned_data.get('is_naj_member', False)
                            }
                        )
            
            # Hantera plattform
            platform = None
            platform_name = form.cleaned_data.get('platform_name', '').strip()
            platform_url = form.cleaned_data.get('platform_url', '').strip()
            platform_comment = form.cleaned_data.get('platform_comment', '').strip()
            platform_search = form.cleaned_data.get('platform_search', '').strip()
            if platform_name:
                # Skapa ny plattform med endast namn (url och comment finns ej i modellen)
                platform, created = Platform.objects.get_or_create(
                    name=platform_name
                )
            elif platform_search:
                try:
                    platform = Platform.objects.get(name=platform_search)
                except Platform.DoesNotExist:
                    platform = None
            
            # Hantera transaktion
            transaction_price = form.cleaned_data.get('transaction_price')
            transaction_shipping = form.cleaned_data.get('transaction_shipping')
            transaction_date = form.cleaned_data.get('transaction_date')
            transaction_comment = form.cleaned_data.get('transaction_comment', '')
            
            if transaction_price is not None or transaction_shipping is not None or transaction_date:
                # Skapa transaktion
                if transaction_price is None:
                    transaction_price = 0
                if transaction_shipping is None:
                    transaction_shipping = 0
                if not transaction_date:
                    transaction_date = timezone.now().date()
                
                # Bestäm transaktionstyp baserat på tecken
                if transaction_price < 0 or transaction_shipping < 0:
                    transaction_type = 'KÖP'
                    transaction_price = abs(transaction_price)
                    transaction_shipping = abs(transaction_shipping)
                else:
                    transaction_type = 'SÄLJ'
                    transaction_shipping = abs(transaction_shipping)
                
                Transaction.objects.create(
                    axe=axe,
                    contact=contact,
                    platform=platform,
                    transaction_date=transaction_date,
                    type=transaction_type,
                    price=transaction_price,
                    shipping_cost=transaction_shipping,
                    comment=transaction_comment
                )
            
            return redirect('axe_detail', pk=axe.pk)
    else:
        form = AxeForm()
    
    # Hämta nästa ID utan att öka räknaren
    next_id = NextAxeID.peek_next_id()
    
    # Skicka samma context som i edit
    context = {
        'form': form,
        'axe': None,
        'is_edit': False,
        'next_id': next_id,
        'measurements': [],
        'measurement_form': MeasurementForm(),
        'measurement_templates': {},
    }
    return render(request, 'axes/axe_form.html', context)

def axe_edit(request, pk):
    axe = get_object_or_404(Axe, pk=pk)
    if request.method == 'POST':
        form = AxeForm(request.POST, request.FILES, instance=axe)
        if form.is_valid():
            axe = form.save(commit=False)
            axe.updated_by = request.user
            axe.save()

            # Hantera borttagning av befintliga bilder
            if 'remove_images' in request.POST:
                for image_id in request.POST.getlist('remove_images'):
                    try:
                        image = AxeImage.objects.get(id=image_id, axe=axe)
                        image.delete()
                    except AxeImage.DoesNotExist:
                        pass



            # Hantera nya bilder
            if 'images' in request.FILES:
                max_order = axe.images.aggregate(Max('order'))['order__max'] or 0
                for i, image_file in enumerate(request.FILES.getlist('images'), 1):
                    try:
                        axe_image = AxeImage(axe=axe, image=image_file, order=max_order + i)
                        axe_image.save()
                    except Exception as e:
                        pass

            # Hantera URL-bilder
            if 'image_urls' in request.POST:
                max_order = axe.images.aggregate(Max('order'))['order__max'] or 0
                for i, image_url in enumerate(request.POST.getlist('image_urls'), 1):
                    if image_url and image_url.startswith('http'):
                        try:
                            response = requests.get(image_url, timeout=10)
                            if response.status_code == 200:
                                file_extension = os.path.splitext(urlparse(image_url).path)[1] or '.jpg'
                                filename = f"{axe.id}_{uuid.uuid4().hex[:8]}{file_extension}"
                                image_file = ContentFile(response.content, name=filename)
                                axe_image = AxeImage(axe=axe, image=image_file, order=max_order + i)
                                axe_image.save()
                        except Exception as e:
                            pass

            # Hantera bildordning från drag & drop (före omnumrering)
            image_orders = request.POST.getlist('image_order')
            if image_orders:
                for order_data in image_orders:
                    if ':' in order_data:
                        image_id, new_order = order_data.split(':', 1)
                        try:
                            image = AxeImage.objects.get(id=image_id, axe=axe)
                            image.order = int(new_order)
                            image.save()
                        except (AxeImage.DoesNotExist, ValueError):
                            pass

            # Kontrollera om omdöpning behövs
            # Omdöpning behövs när:
            # 1. Nya bilder laddas upp
            # 2. Nya URL:er laddas ner
            # 3. Bildordning ändras via drag & drop
            # 4. Bilder tas bort (men inte om den sista bilden tas bort)
            has_new_images = 'images' in request.FILES or 'image_urls' in request.POST
            has_order_changes = bool(image_orders)
            has_removals = 'remove_images' in request.POST
            
            # Om det finns borttagningar, kontrollera om den sista bilden tas bort
            skip_renaming_for_removals = False
            if has_removals:
                remaining_count = axe.images.count() - len(request.POST.getlist('remove_images'))
                if remaining_count == 0:
                    # Alla bilder tas bort, ingen omdöpning behövs
                    skip_renaming_for_removals = True
            
            needs_renaming = (
                has_new_images or 
                has_order_changes or 
                (has_removals and not skip_renaming_for_removals)
            )
            
            # Omnumrera och döp om alla bilder endast om det behövs
            if needs_renaming:
                from django.core.files.storage import default_storage
                from django.conf import settings
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
                        except Exception:
                            pass
                    temp_webps.append(temp_webp)
                # Steg 2: Döp om till slutgiltiga namn baserat på den nya ordningen
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
                        except Exception:
                            pass
                    # Uppdatera databasen med den nya ordningen
                    image.image = final_path
                    image.order = idx
                    image.description = f'Bild {chr(96 + idx).upper()} av {axe.manufacturer.name} {axe.model}'
                    image.save()

            return redirect('axe_detail', pk=axe.pk)
    else:
        form = AxeForm(instance=axe)
    # Hämta måttdata för templaten
    measurements = axe.measurements.all().order_by('name') if hasattr(axe, 'measurements') else []
    measurement_form = MeasurementForm()
    measurement_templates = {}
    templates = MeasurementTemplate.objects.filter(is_active=True).prefetch_related('items__measurement_type')
    for template in templates:
        measurement_templates[template.name] = [
            {
                'name': item.measurement_type.name,
                'unit': item.measurement_type.unit
            }
            for item in template.items.all()
        ]
    context = {
        'form': form,
        'axe': axe,
        'is_edit': True,
        'measurements': measurements,
        'measurement_form': measurement_form,
        'measurement_templates': measurement_templates,
    }
    return render(request, 'axes/axe_form.html', context)

def axe_gallery(request, pk=None):
    """Visa yxor i galleriformat med navigation mellan dem"""
    all_axes = Axe.objects.all().select_related('manufacturer').prefetch_related('images').order_by('id')
    if pk:
        current_axe = get_object_or_404(
            Axe.objects.select_related('manufacturer').prefetch_related('images', 'measurements'), pk=pk
        )
        axe_list = list(all_axes)
        try:
            current_index = axe_list.index(current_axe)
        except ValueError:
            current_index = 0
        prev_axe = axe_list[current_index - 1] if current_index > 0 else None
        next_axe = axe_list[current_index + 1] if current_index < len(axe_list) - 1 else None
        transactions = Transaction.objects.filter(axe=current_axe).select_related('contact', 'platform').order_by('-transaction_date')
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
        if all_axes.exists():
            last_axe = all_axes.last()
            return axe_gallery(request, last_axe.pk)
        else:
            return render(request, 'axes/axe_gallery.html', {
                'current_axe': None,
                'prev_axe': None,
                'next_axe': None,
                'current_index': 0,
                'total_axes': 0,
            })

def receiving_workflow(request, pk):
    axe = get_object_or_404(Axe, pk=pk)
    # Ladda måttmallar
    measurement_templates = {}
    templates = MeasurementTemplate.objects.filter(is_active=True).prefetch_related('items__measurement_type')
    for template in templates:
        measurement_templates[template.name] = [
            {
                'name': item.measurement_type.name,
                'unit': item.measurement_type.unit
            }
            for item in template.items.all()
        ]
    measurement_form = MeasurementForm()
    measurements = axe.measurements.all().order_by('name')
    if request.method == 'POST':
        if 'status' in request.POST:
            new_status = request.POST['status']
            if new_status in ['KÖPT', 'MOTTAGEN', 'SÄLJD']:
                axe.status = new_status
                axe.save()
                return redirect('axe_list')
            else:
                return render(request, 'axes/receiving_workflow.html', {
                    'axe': axe,
                    'error': 'Invalid status.',
                    'measurement_templates': measurement_templates,
                    'measurement_form': measurement_form,
                    'measurements': measurements,
                })
    return render(request, 'axes/receiving_workflow.html', {
        'axe': axe,
        'measurement_templates': measurement_templates,
        'measurement_form': measurement_form,
        'measurements': measurements,
    })

@require_POST
def add_measurement(request, pk):
    axe = get_object_or_404(Axe, pk=pk)
    if request.method == 'POST':
        measurement_form = MeasurementForm(request.POST)
        if measurement_form.is_valid():
            measurement = measurement_form.save(commit=False)
            measurement.axe = axe
            measurement.save()
            return JsonResponse({
                'success': True,
                'message': 'Mått lades till framgångsrikt.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Ogiltig måttdata.'
            }, status=400)
    else:
        measurement_form = MeasurementForm()
    return render(request, 'axes/add_measurement.html', {'axe': axe, 'measurement_form': measurement_form})

@require_POST
def add_measurements_from_template(request, pk):
    axe = get_object_or_404(Axe, pk=pk)
    
    # Hämta measurements från POST-data
    measurements_data = []
    i = 0
    while f'measurements[{i}][name]' in request.POST:
        name = request.POST.get(f'measurements[{i}][name]')
        value = request.POST.get(f'measurements[{i}][value]')
        unit = request.POST.get(f'measurements[{i}][unit]')
        
        if name and value and unit:
            try:
                value = float(value)
                measurements_data.append({
                    'name': name,
                    'value': value,
                    'unit': unit
                })
            except ValueError:
                return JsonResponse({'error': f'Ogiltigt värde för {name}: {value}'}, status=400)
        i += 1
    
    if not measurements_data:
        return JsonResponse({'error': 'Inga giltiga mått att lägga till.'}, status=400)
    
    # Skapa mått
    created_count = 0
    for measurement_data in measurements_data:
        measurement = Measurement(
            axe=axe,
            name=measurement_data['name'],
            value=measurement_data['value'],
            unit=measurement_data['unit']
        )
        measurement.save()
        created_count += 1
    
    return JsonResponse({
        'success': True,
        'message': f'{created_count} mått lades till framgångsrikt.'
    })

@require_POST
def delete_measurement(request, pk, measurement_id):
    axe = get_object_or_404(Axe, pk=pk)
    try:
        measurement = Measurement.objects.get(id=measurement_id)
        if measurement.axe == axe:
            measurement.delete()
            return JsonResponse({
                'success': True,
                'message': 'Mått borttaget framgångsrikt.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Ogiltigt mått-ID.'
            }, status=400)
    except Measurement.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Mått hittades inte.'
        }, status=404)

@require_POST
def update_measurement(request, pk, measurement_id):
    axe = get_object_or_404(Axe, pk=pk)
    try:
        measurement = Measurement.objects.get(id=measurement_id)
        if measurement.axe == axe:
            measurement_form = MeasurementForm(request.POST, instance=measurement)
            if measurement_form.is_valid():
                measurement = measurement_form.save(commit=False)
                measurement.axe = axe
                measurement.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Mått uppdaterat framgångsrikt.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Ogiltig måttdata.'
                }, status=400)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Ogiltigt mått-ID.'
            }, status=400)
    except Measurement.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Mått hittades inte.'
        }, status=404)

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
        total_axes=Count('axe')
    ).order_by('-total_axes')[:5]
    
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