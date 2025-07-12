from django.shortcuts import render, get_object_or_404, redirect
from .models import Axe, AxeImage, Measurement, NextAxeID, MeasurementTemplate, Transaction, Contact, Platform, Manufacturer
from .forms import AxeForm, MeasurementForm, TransactionForm
from django.db.models import Sum, Q, Max
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

# --- Yx-relaterade vyer ---

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
    }
    return render(request, 'axes/axe_detail.html', context)

def axe_create(request):
    if request.method == 'POST':
        form = AxeForm(request.POST)
        if form.is_valid():
            axe = form.save(commit=False)
            axe.created_by = request.user
            axe.save()
            return redirect('axe_list')
    else:
        form = AxeForm()
    # Skicka samma context som i edit
    context = {
        'form': form,
        'axe': None,
        'is_edit': False,
        'measurements': [],
        'measurement_form': MeasurementForm(),
        'measurement_templates': {},
    }
    return render(request, 'axes/axe_form.html', context)

def axe_edit(request, pk):
    axe = get_object_or_404(Axe, pk=pk)
    if request.method == 'POST':
        form = AxeForm(request.POST, instance=axe)
        if form.is_valid():
            axe = form.save(commit=False)
            axe.updated_by = request.user
            axe.save()
            return redirect('axe_list')
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
    if request.method == 'POST':
        if 'status' in request.POST:
            new_status = request.POST['status']
            if new_status in ['KÖPT', 'MOTTAGEN', 'SÄLJD']:
                axe.status = new_status
                axe.save()
                return redirect('axe_list')
            else:
                return render(request, 'axes/receiving_workflow.html', {'axe': axe, 'error': 'Invalid status.'})
    return render(request, 'axes/receiving_workflow.html', {'axe': axe})

@require_POST
def add_measurement(request, pk):
    axe = get_object_or_404(Axe, pk=pk)
    if request.method == 'POST':
        measurement_form = MeasurementForm(request.POST)
        if measurement_form.is_valid():
            measurement = measurement_form.save(commit=False)
            measurement.axe = axe
            measurement.save()
            return redirect('axe_detail', pk=axe.pk)
    else:
        measurement_form = MeasurementForm()
    return render(request, 'axes/add_measurement.html', {'axe': axe, 'measurement_form': measurement_form})

@require_POST
def add_measurements_from_template(request, pk):
    axe = get_object_or_404(Axe, pk=pk)
    template_id = request.POST.get('measurement_template_id')
    if not template_id:
        return JsonResponse({'error': 'No template selected.'}, status=400)
    
    try:
        template = MeasurementTemplate.objects.get(id=template_id)
    except MeasurementTemplate.DoesNotExist:
        return JsonResponse({'error': 'Template not found.'}, status=404)
    
    for measurement_data in template.measurements:
        measurement = Measurement(axe=axe, **measurement_data)
        measurement.save()
    
    return JsonResponse({'message': f'{len(template.measurements)} measurements added from template.'})

@require_POST
def delete_measurement(request, pk, measurement_id):
    axe = get_object_or_404(Axe, pk=pk)
    try:
        measurement = Measurement.objects.get(id=measurement_id)
        if measurement.axe == axe:
            measurement.delete()
            return JsonResponse({'message': 'Measurement deleted successfully.'})
        else:
            return JsonResponse({'error': 'Invalid measurement ID.'}, status=400)
    except Measurement.DoesNotExist:
        return JsonResponse({'error': 'Measurement not found.'}, status=404)

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
                return JsonResponse({'message': 'Measurement updated successfully.'})
            else:
                return JsonResponse({'error': 'Invalid measurement data.'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid measurement ID.'}, status=400)
    except Measurement.DoesNotExist:
        return JsonResponse({'error': 'Measurement not found.'}, status=404)