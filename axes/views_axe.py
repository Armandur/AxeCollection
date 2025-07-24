from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Axe, AxeImage, Measurement, NextAxeID, MeasurementTemplate, Transaction, Contact, Platform, Manufacturer
from .forms import AxeForm, MeasurementForm, TransactionForm
from django.db.models import Sum, Q, Max, Count
from django.db.models.functions import TruncMonth, TruncYear
from datetime import datetime, timedelta
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import requests
import uuid
import os
import shutil
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from urllib.parse import urlparse
from django.contrib import messages

def move_images_to_unlinked_folder(axe_images, delete_images=False):
    """
    Flyttar yxbilder till en 'okopplade bilder'-mapp med yx-ID och a-b-c-namngivning.
    
    Args:
        axe_images: QuerySet av AxeImage-objekt
        delete_images: Om True, ta bort bilderna istället för att flytta dem
    
    Returns:
        dict: Information om vad som hände med bilderna
    """
    if not axe_images.exists():
        return {'moved': 0, 'deleted': 0, 'errors': 0}
    
    if delete_images:
        # Ta bort alla bilder
        deleted_count = 0
        for image in axe_images:
            try:
                image.delete()
                deleted_count += 1
            except Exception as e:
                pass
        return {'moved': 0, 'deleted': deleted_count, 'errors': 0}
    
    # Skapa timestamp för borttagning
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    
    # Skapa mapp för okopplade yxbilder
    unlinked_folder = os.path.join(settings.MEDIA_ROOT, 'unlinked_images', 'axes')
    os.makedirs(unlinked_folder, exist_ok=True)
    
    moved_count = 0
    error_count = 0
    
    # Gruppera bilder efter yxa för att få rätt namngivning
    axes_with_images = {}
    for axe_image in axe_images.select_related('axe').order_by('axe__id', 'order'):
        axe_id = axe_image.axe.id
        if axe_id not in axes_with_images:
            axes_with_images[axe_id] = []
        axes_with_images[axe_id].append(axe_image)
    
    for axe_id, images in axes_with_images.items():
        for index, axe_image in enumerate(images):
            try:
                if axe_image.image and axe_image.image.name:
                    # Bestäm filnamn (a, b, c, etc.)
                    letter = chr(97 + index)  # 97 = 'a' i ASCII
                    
                    # Hämta filändelse från originalfilen
                    original_ext = os.path.splitext(axe_image.image.name)[1]
                    new_filename = f"yxa-{axe_id}-{timestamp}-{letter}{original_ext}"
                    new_path = os.path.join(unlinked_folder, new_filename)
                    
                    # Kopiera filen
                    if os.path.exists(axe_image.image.path):
                        shutil.copy2(axe_image.image.path, new_path)
                        
                        # Kopiera även .webp-filen om den finns
                        webp_path = os.path.splitext(axe_image.image.path)[0] + '.webp'
                        if os.path.exists(webp_path):
                            webp_new_path = os.path.join(unlinked_folder, f"yxa-{axe_id}-{timestamp}-{letter}.webp")
                            shutil.copy2(webp_path, webp_new_path)
                        
                        moved_count += 1
                    
                    # Ta bort originalbilden från databasen och filsystemet
                    axe_image.delete()
                    
            except Exception as e:
                error_count += 1
                # Logga felet om så önskas
                pass
    
    return {
        'moved': moved_count, 
        'deleted': 0, 
        'errors': error_count,
        'timestamp': timestamp,
        'folder_path': unlinked_folder
    }

# --- Yx-relaterade vyer ---

def axe_list(request):
    # Hämta filter från URL-parametrar
    status_filter = request.GET.get('status', '')
    manufacturer_filter = request.GET.get('manufacturer', '')
    platform_filter = request.GET.get('platform', '')
    measurements_filter = request.GET.get('measurements', '')
    
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
    
    if measurements_filter == 'with':
        axes = axes.filter(measurements__isnull=False).distinct()
    elif measurements_filter == 'without':
        axes = axes.filter(measurements__isnull=True)
    
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
    
    # Hämta inställningar för DataTables
    from .models import Settings
    settings = Settings.get_settings()
    if request.user.is_authenticated:
        default_page_length = int(settings.default_axes_rows_private)
    else:
        default_page_length = int(settings.default_axes_rows_public)
    
    return render(request, 'axes/axe_list.html', {
        'axes': axes,
        'manufacturers': manufacturers,
        'platforms': platforms,
        'status_filter': status_filter,
        'manufacturer_filter': manufacturer_filter,
        'platform_filter': platform_filter,
        'measurements_filter': measurements_filter,
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
        'default_page_length': default_page_length,
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

@login_required
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
                    if default_storage.exists(old_webp):
                        try:
                            with default_storage.open(old_webp, 'rb') as old_webp_file:
                                default_storage.save(temp_webp, old_webp_file)
                            default_storage.delete(old_webp)
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
                    if default_storage.exists(temp_webp):
                        try:
                            with default_storage.open(temp_webp, 'rb') as temp_webp_file:
                                default_storage.save(final_webp, temp_webp_file)
                            default_storage.delete(temp_webp)
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
                                'street': form.cleaned_data.get('contact_street', ''),
                                'postal_code': form.cleaned_data.get('contact_postal_code', ''),
                                'city': form.cleaned_data.get('contact_city', ''),
                                'country': form.cleaned_data.get('contact_country', ''),
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
                                'street': form.cleaned_data.get('contact_street', ''),
                                'postal_code': form.cleaned_data.get('contact_postal_code', ''),
                                'city': form.cleaned_data.get('contact_city', ''),
                                'country': form.cleaned_data.get('contact_country', ''),
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

@login_required
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
                    if default_storage.exists(old_webp):
                        try:
                            with default_storage.open(old_webp, 'rb') as old_webp_file:
                                default_storage.save(temp_webp, old_webp_file)
                            default_storage.delete(old_webp)
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
                    if default_storage.exists(temp_webp):
                        try:
                            with default_storage.open(temp_webp, 'rb') as temp_webp_file:
                                default_storage.save(final_webp, temp_webp_file)
                            default_storage.delete(temp_webp)
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
    
    # Applicera publik filtrering om användaren inte är inloggad
    if not request.user.is_authenticated:
        from .models import Settings
        try:
            settings = Settings.get_settings()
            if settings.show_only_received_axes_public:
                all_axes = all_axes.filter(status='MOTTAGEN')
        except:
            # Fallback om Settings-modellen inte finns ännu
            pass
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

@login_required
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
    images = axe.images.all().order_by('order')
    
    if request.method == 'POST':
        # Hantera statusändringar
        if 'status' in request.POST:
            new_status = request.POST['status']
            if new_status in ['KÖPT', 'MOTTAGEN', 'SÄLJD']:
                axe.status = new_status
                axe.save()
                return redirect('axe_list')
        
        # Hantera bilduppladdning
        elif 'images' in request.FILES or 'image_urls' in request.POST:
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

            # Omdöpning av bilder (samma logik som i axe_edit)
            remaining_images = list(axe.images.all().order_by('order'))
            if remaining_images:
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
                    if default_storage.exists(old_webp):
                        try:
                            with default_storage.open(old_webp, 'rb') as old_webp_file:
                                default_storage.save(temp_webp, old_webp_file)
                            default_storage.delete(old_webp)
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
                    if default_storage.exists(temp_webp):
                        try:
                            with default_storage.open(temp_webp, 'rb') as temp_webp_file:
                                default_storage.save(final_webp, temp_webp_file)
                            default_storage.delete(temp_webp)
                        except Exception:
                            pass
                    # Uppdatera databasen
                    image.image = final_path
                    image.order = idx
                    image.description = f'Bild {chr(96 + idx).upper()} av {axe.manufacturer.name} {axe.model}'
                    image.save()

            # Omladda sidan för att visa nya bilder
            return redirect('receiving_workflow', pk=axe.pk)
    
    # Returnera template för GET-requests
    return render(request, 'axes/receiving_workflow.html', {
        'axe': axe,
        'measurement_templates': measurement_templates,
        'measurement_form': measurement_form,
        'measurements': measurements,
        'images': images,
    })

@login_required
@require_http_methods(["POST"])
def update_axe_status(request, pk):
    """Uppdatera status för en yxa"""
    try:
        axe = get_object_or_404(Axe, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in ['KÖPT', 'MOTTAGEN']:
            axe.status = new_status
            axe.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Ogiltig status'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    return render(request, 'axes/receiving_workflow.html', {
        'axe': axe,
        'measurement_templates': measurement_templates,
        'measurement_form': measurement_form,
        'measurements': measurements,
    })

@login_required
@require_POST
def add_measurement(request, pk):
    axe = get_object_or_404(Axe, pk=pk)
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
        # Returnera detaljerade felmeddelanden
        errors = []
        for field, field_errors in measurement_form.errors.items():
            for error in field_errors:
                errors.append(f"{field}: {error}")
        
        return JsonResponse({
            'success': False,
            'error': '; '.join(errors) if errors else 'Ogiltig måttdata.'
        }, status=400)

@login_required
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

@login_required
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

@login_required
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
    
    # Billigaste köp (top 5)
    cheapest_buys = Transaction.objects.filter(
        type='KÖP'
    ).select_related('axe__manufacturer').order_by('price')[:5]
    
    # Billigaste försäljningar (top 5)
    cheapest_sales = Transaction.objects.filter(
        type='SÄLJ'
    ).select_related('axe__manufacturer').order_by('price')[:5]
    
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
    
    # Data för kombinerad tidslinje - inköp vs samling över tid
    # Hämta alla transaktioner sorterade efter datum
    all_transactions = Transaction.objects.select_related('axe').order_by('transaction_date')
    
    # Skapa data för Chart.js
    chart_labels = []
    bought_data = []
    collection_data = []
    
    # Gruppera transaktioner per månad
    current_month = None
    monthly_buys = 0
    monthly_sales = 0
    cumulative_buys = 0
    cumulative_sales = 0
    
    for transaction in all_transactions:
        # Gruppera per månad
        transaction_month = transaction.transaction_date.replace(day=1)
        
        if current_month is None:
            current_month = transaction_month
        elif transaction_month != current_month:
            # Spara data för föregående månad
            month_str = current_month.strftime('%b %Y')
            chart_labels.append(month_str)
            bought_data.append(cumulative_buys)
            collection_data.append(cumulative_buys - cumulative_sales)
            
            # Nollställ månadsräknare
            monthly_buys = 0
            monthly_sales = 0
            current_month = transaction_month
        
        # Räkna transaktioner
        if transaction.type == 'KÖP':
            monthly_buys += 1
            cumulative_buys += 1
        elif transaction.type == 'SÄLJ':
            monthly_sales += 1
            cumulative_sales += 1
    
    # Lägg till sista månaden om det finns data
    if current_month is not None:
        month_str = current_month.strftime('%b %Y')
        chart_labels.append(month_str)
        bought_data.append(cumulative_buys)
        collection_data.append(cumulative_buys - cumulative_sales)
    
    # Om vi inte har någon data, skapa en tom graf
    if not chart_labels:
        chart_labels = ['Ingen data']
        bought_data = [0]
        collection_data = [0]
    
    # Data för ekonomisk stapeldiagram - transaktionsvärden per månad
    # Skapa en dictionary för att samla värden per månad
    monthly_data = {}
    
    for transaction in all_transactions:
        # Gruppera per månad
        month_key = transaction.transaction_date.strftime('%b %Y')
        
        if month_key not in monthly_data:
            monthly_data[month_key] = {'buy': 0, 'sale': 0}
        
        # Räkna ekonomiska värden per månad
        if transaction.type == 'KÖP':
            monthly_data[month_key]['buy'] += float(transaction.price)
        elif transaction.type == 'SÄLJ':
            monthly_data[month_key]['sale'] += float(transaction.price)
    
    # Skapa arrays för Chart.js
    financial_labels = []
    buy_values = []
    sale_values = []
    
    # Använd samma månader som yxgrafen för konsistens
    for month in chart_labels:
        financial_labels.append(month)
        if month in monthly_data:
            buy_values.append(monthly_data[month]['buy'])
            sale_values.append(monthly_data[month]['sale'])
        else:
            buy_values.append(0)
            sale_values.append(0)
    
    # Data för mest aktiva månader (antal transaktioner per månad, köp/sälj)
    monthly_activity = {}
    for transaction in all_transactions:
        month_key = transaction.transaction_date.strftime('%b %Y')
        if month_key not in monthly_activity:
            monthly_activity[month_key] = {'buy': 0, 'sale': 0}
        if transaction.type == 'KÖP':
            monthly_activity[month_key]['buy'] += 1
        elif transaction.type == 'SÄLJ':
            monthly_activity[month_key]['sale'] += 1
    # Skapa arrays för Chart.js (använd samma ordning som övriga diagram)
    activity_labels = []
    activity_buys = []
    activity_sales = []
    for month in chart_labels:
        activity_labels.append(month)
        if month in monthly_activity:
            activity_buys.append(monthly_activity[month]['buy'])
            activity_sales.append(monthly_activity[month]['sale'])
        else:
            activity_buys.append(0)
            activity_sales.append(0)
    
    # Data för senaste aktivitet
    latest_purchases = Transaction.objects.filter(type='KÖP').order_by('-transaction_date')[:5]
    latest_sales = Transaction.objects.filter(type='SÄLJ').order_by('-transaction_date')[:5]
    latest_axes = Axe.objects.all().order_by('-id')[:5]
    
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
        'cheapest_buys': cheapest_buys,
        'cheapest_sales': cheapest_sales,
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
        
        # Chart data
        'chart_labels': chart_labels,
        'bought_data': bought_data,
        'collection_data': collection_data,
        'financial_labels': financial_labels,
        'buy_values': buy_values,
        'sale_values': sale_values,
        'activity_labels': activity_labels,
        'activity_buys': activity_buys,
        'activity_sales': activity_sales,
        'latest_purchases': latest_purchases,
        'latest_sales': latest_sales,
        'latest_axes': latest_axes,
    }
    
    return render(request, 'axes/statistics_dashboard.html', context)

@require_http_methods(["GET"])
def get_latest_axe_info(request):
    """Hämta information om den senaste yxan för att visa i modalen"""
    try:
        latest_axe = Axe.objects.select_related('manufacturer').prefetch_related('images', 'transactions').order_by('-id').first()
        
        if not latest_axe:
            return JsonResponse({
                'success': False,
                'message': 'Inga yxor att ta bort'
            })
        
        # Hämta kontakt från senaste transaktionen
        latest_transaction = latest_axe.transactions.order_by('-transaction_date').first()
        contact_name = latest_transaction.contact.name if latest_transaction and latest_transaction.contact else None
        
        return JsonResponse({
            'success': True,
            'axe': {
                'id': latest_axe.id,
                'manufacturer': latest_axe.manufacturer.name,
                'model': latest_axe.model,
                'image_count': latest_axe.images.count(),
                'transaction_count': latest_axe.transactions.count(),
                'contact_name': contact_name
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Fel vid hämtning av information: {str(e)}'
        })

@require_http_methods(["POST"])
def delete_latest_axe(request):
    """Ta bort en yxa med valfria kopplade data"""
    try:
        axe_id = request.POST.get('axe_id')
        if axe_id:
            # Ta bort specifik yxa
            axe = get_object_or_404(Axe.objects.select_related('manufacturer').prefetch_related('images', 'transactions__contact'), pk=axe_id)
        else:
            # Fallback: ta bort den senaste yxan
            axe = Axe.objects.select_related('manufacturer').prefetch_related('images', 'transactions__contact').order_by('-id').first()
        
        if not axe:
            messages.error(request, 'Inga yxor att ta bort')
            return redirect('axe_list')
        
        # Kontrollera att det är den senaste yxan
        if not axe.is_latest:
            messages.error(request, 'Endast den senaste yxan kan tas bort')
            return redirect('axe_detail', pk=axe.id)
        
        delete_images = request.POST.get('delete_images') == 'on'
        delete_transactions = request.POST.get('delete_transactions') == 'on'
        delete_contact = request.POST.get('delete_contact') == 'on'
        
        axe_info = f"{axe.manufacturer.name} - {axe.model} (ID: {axe.id})"
        
        # Samla kontakter som kan tas bort
        contacts_to_delete = set()
        if delete_contact:
            for transaction in axe.transactions.all():
                if transaction.contact:
                    # Kontrollera om kontakten är kopplad till andra yxor
                    if transaction.contact.unique_axes_count == 1:
                        contacts_to_delete.add(transaction.contact)
                    else:
                        messages.warning(request, f'Kontakt "{transaction.contact.name}" kunde inte tas bort eftersom den är kopplad till andra yxor.')
        
        # Hantera bilder - antingen ta bort eller flytta till okopplade bilder
        image_count = axe.images.count()
        if image_count > 0:
            if delete_images:
                # Ta bort bilderna
                result = move_images_to_unlinked_folder(axe.images, delete_images=True)
                if result['deleted'] > 0:
                    messages.info(request, f'{result["deleted"]} bilder togs bort.')
            else:
                # Flytta bilderna till okopplade bilder
                result = move_images_to_unlinked_folder(axe.images, delete_images=False)
                if result['moved'] > 0:
                    messages.info(request, f'{result["moved"]} bilder flyttades till okopplade bilder (timestamp: {result["timestamp"]}).')
                if result['errors'] > 0:
                    messages.warning(request, f'{result["errors"]} bilder kunde inte flyttas.')
        
        # Ta bort yxan (detta tar automatiskt bort mått och eventuellt kvarvarande bilder)
        deleted_axe_id = axe.id
        axe.delete()
        
        # Ta bort transaktioner om valt
        if not delete_transactions:
            # Återställ transaktionerna (de togs bort med yxan)
            # Detta är komplex, så vi varnar användaren
            messages.warning(request, f'Transaktioner togs bort med yxan. Detta kan inte ångras.')
        
        # Ta bort kontakter om valt
        for contact in contacts_to_delete:
            contact.delete()
            messages.info(request, f'Kontakt "{contact.name}" togs bort eftersom den inte användes av andra yxor.')
        
        # Återställ nästa ID om det var den senaste yxan
        NextAxeID.reset_if_last_axe_deleted(deleted_axe_id)
        
        messages.success(request, f'Yxa "{axe_info}" togs bort framgångsrikt.')
        
    except Exception as e:
        messages.error(request, f'Fel vid borttagning av yxa: {str(e)}')
    
    return redirect('axe_list')

def unlinked_images_view(request):
    """Visa och hantera okopplade bilder"""
    import glob
    import os
    from datetime import datetime
    
    unlinked_base_folder = os.path.join(settings.MEDIA_ROOT, 'unlinked_images')
    
    if not os.path.exists(unlinked_base_folder):
        return render(request, 'axes/unlinked_images.html', {
            'axe_groups': [],
            'manufacturer_groups': [],
            'total_count': 0,
            'total_size': 0
        })
    
    # Hämta alla bildfiler i båda mapparna (exkluderar .webp för webboptimering)
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
    
    # Yxbilder
    axe_folder = os.path.join(unlinked_base_folder, 'axes')
    axe_files = []
    if os.path.exists(axe_folder):
        for ext in image_extensions:
            axe_files.extend(glob.glob(os.path.join(axe_folder, ext)))
    
    # Tillverkarbilder
    manufacturer_folder = os.path.join(unlinked_base_folder, 'manufacturers')
    manufacturer_files = []
    if os.path.exists(manufacturer_folder):
        for ext in image_extensions:
            manufacturer_files.extend(glob.glob(os.path.join(manufacturer_folder, ext)))
    
    # Gruppera yxbilder efter yx-ID
    axe_groups = {}
    for file_path in axe_files:
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Extrahera yx-ID från filnamnet (t.ex. "yxa-123-20250717_225600-a.jpg" -> "123")
        if filename.startswith('yxa-'):
            parts = filename.split('-')
            if len(parts) >= 3:
                axe_id = parts[1]
                timestamp_part = parts[2]
                try:
                    timestamp_obj = datetime.strptime(timestamp_part, '%Y%m%d_%H%M%S')
                    formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    formatted_timestamp = timestamp_part
                
                if axe_id not in axe_groups:
                    axe_groups[axe_id] = {
                        'axe_id': axe_id,
                        'timestamp': formatted_timestamp,
                        'images': []
                    }
                
                axe_groups[axe_id]['images'].append({
                    'filename': filename,
                    'file_path': file_path,
                    'url': f'/media/unlinked_images/axes/{filename}',
                    'size': file_size,
                    'size_formatted': f'{file_size / 1024:.1f} KB' if file_size < 1024*1024 else f'{file_size / (1024*1024):.1f} MB'
                })
    
    # Gruppera tillverkarbilder efter tillverkare
    manufacturer_groups = {}
    for file_path in manufacturer_files:
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Extrahera tillverkarnamn och ID från filnamnet (t.ex. "Hults_bruk-15-20250717_225600-a.jpg")
        if '-' in filename:
            parts = filename.split('-')
            if len(parts) >= 4:
                manufacturer_name = parts[0].replace('_', ' ')
                manufacturer_id = parts[1]
                timestamp_part = parts[2]
                try:
                    timestamp_obj = datetime.strptime(timestamp_part, '%Y%m%d_%H%M%S')
                    formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    formatted_timestamp = timestamp_part
                
                group_key = f"{manufacturer_name}-{manufacturer_id}"
                if group_key not in manufacturer_groups:
                    manufacturer_groups[group_key] = {
                        'manufacturer_name': manufacturer_name,
                        'manufacturer_id': manufacturer_id,
                        'timestamp': formatted_timestamp,
                        'images': []
                    }
                
                manufacturer_groups[group_key]['images'].append({
                    'filename': filename,
                    'file_path': file_path,
                    'url': f'/media/unlinked_images/manufacturers/{filename}',
                    'size': file_size,
                    'size_formatted': f'{file_size / 1024:.1f} KB' if file_size < 1024*1024 else f'{file_size / (1024*1024):.1f} MB'
                })
    
    # Sortera grupper efter timestamp (nyaste först)
    sorted_axe_groups = sorted(axe_groups.values(), key=lambda x: x['timestamp'], reverse=True)
    sorted_manufacturer_groups = sorted(manufacturer_groups.values(), key=lambda x: x['timestamp'], reverse=True)
    
    # Beräkna total statistik
    total_count = len(axe_files) + len(manufacturer_files)
    total_size = sum(os.path.getsize(f) for f in axe_files + manufacturer_files)
    
    context = {
        'axe_groups': sorted_axe_groups,
        'manufacturer_groups': sorted_manufacturer_groups,
        'total_count': total_count,
        'total_size': total_size,
        'total_size_formatted': f'{total_size / 1024:.1f} KB' if total_size < 1024*1024 else f'{total_size / (1024*1024):.1f} MB',
        'axe_count': len(axe_files),
        'manufacturer_count': len(manufacturer_files)
    }
    
    return render(request, 'axes/unlinked_images.html', context)

@require_POST
def delete_unlinked_image(request):
    """Ta bort en okopplad bild (både original och .webp-version)"""
    try:
        filename = request.POST.get('filename')
        image_type = request.POST.get('type', 'axe')  # 'axe' eller 'manufacturer'
        if not filename:
            return JsonResponse({'success': False, 'error': 'Inget filnamn angivet'})
        
        # Bestäm rätt mapp baserat på bildtyp
        if image_type == 'manufacturer':
            folder = 'manufacturers'
        else:
            folder = 'axes'
        
        file_path = os.path.join(settings.MEDIA_ROOT, 'unlinked_images', folder, filename)
        
        if os.path.exists(file_path):
            # Ta bort originalfilen
            os.remove(file_path)
            
            # Ta bort även .webp-versionen om den finns
            name_without_ext = os.path.splitext(filename)[0]
            webp_path = os.path.join(settings.MEDIA_ROOT, 'unlinked_images', folder, f"{name_without_ext}.webp")
            if os.path.exists(webp_path):
                os.remove(webp_path)
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Filen hittades inte'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def download_unlinked_images(request):
    """Ladda ner valda eller alla okopplade bilder som ZIP-fil"""
    import zipfile
    import tempfile
    from django.http import HttpResponse
    
    try:
        unlinked_base_folder = os.path.join(settings.MEDIA_ROOT, 'unlinked_images')
        
        if not os.path.exists(unlinked_base_folder):
            return JsonResponse({'success': False, 'error': 'Inga okopplade bilder att ladda ner'})
        
        # Kontrollera om specifika filer är valda
        selected_files = request.POST.getlist('selected_files')
        selected_types = request.POST.getlist('selected_types')  # 'axe' eller 'manufacturer'
        
        # Skapa temporär ZIP-fil
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            with zipfile.ZipFile(tmp_file.name, 'w') as zipf:
                if selected_files and selected_types:
                    # Ladda ner endast valda filer
                    for i, filename in enumerate(selected_files):
                        if i < len(selected_types):
                            image_type = selected_types[i]
                            if image_type == 'manufacturer':
                                folder = 'manufacturers'
                            else:
                                folder = 'axes'
                            
                            file_path = os.path.join(unlinked_base_folder, folder, filename)
                            if os.path.exists(file_path) and not filename.endswith('.webp'):
                                # Lägg till i ZIP med mappstruktur
                                arcname = os.path.join(folder, filename)
                                zipf.write(file_path, arcname)
                else:
                    # Ladda ner alla filer (fallback för GET-requests)
                    for root, dirs, files in os.walk(unlinked_base_folder):
                        for file in files:
                            # Exkludera .webp-filer från ZIP-nedladdning
                            if not file.endswith('.webp'):
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, unlinked_base_folder)
                                zipf.write(file_path, arcname)
        
        # Läs ZIP-filen och skicka som response
        with open(tmp_file.name, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            if selected_files:
                response['Content-Disposition'] = 'attachment; filename="valda_bilder.zip"'
            else:
                response['Content-Disposition'] = 'attachment; filename="okopplade_bilder.zip"'
        
        # Ta bort temporär fil
        os.unlink(tmp_file.name)
        
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})