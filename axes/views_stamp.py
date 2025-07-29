from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib import messages
from .models import (
    Stamp, 
    StampTranscription, 
    StampTag, 
    StampImage, 
    AxeStamp, 
    StampVariant, 
    StampUncertaintyGroup,
    Axe,
    Manufacturer
)
from .forms import StampForm, StampTranscriptionForm, AxeStampForm
import json


@login_required
def stamp_list(request):
    """Lista alla stämplar med sökning och filtrering"""
    
    # Hämta filterparametrar
    search_query = request.GET.get('search', '')
    manufacturer_filter = request.GET.get('manufacturer', '')
    stamp_type_filter = request.GET.get('stamp_type', '')
    status_filter = request.GET.get('status', '')
    source_filter = request.GET.get('source', '')
    
    # Basqueryset
    stamps = Stamp.objects.select_related('manufacturer').prefetch_related('transcriptions', 'images')
    
    # Applicera filter
    if search_query:
        stamps = stamps.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(transcriptions__text__icontains=search_query) |
            Q(manufacturer__name__icontains=search_query)
        ).distinct()
    
    if manufacturer_filter:
        stamps = stamps.filter(manufacturer_id=manufacturer_filter)
    
    if stamp_type_filter:
        stamps = stamps.filter(stamp_type=stamp_type_filter)
    
    if status_filter:
        stamps = stamps.filter(status=status_filter)
    
    if source_filter:
        stamps = stamps.filter(source_category=source_filter)
    
    # Sortering
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'name':
        stamps = stamps.order_by('name')
    elif sort_by == 'manufacturer':
        stamps = stamps.order_by('manufacturer__name', 'name')
    elif sort_by == 'created':
        stamps = stamps.order_by('-created_at')
    elif sort_by == 'axes_count':
        stamps = stamps.annotate(axes_count=Count('axes')).order_by('-axes_count')
    
    # Paginering
    paginator = Paginator(stamps, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Context för filter
    manufacturers = Manufacturer.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'stamps': page_obj,
        'manufacturers': manufacturers,
        'stamp_types': Stamp.STAMP_TYPE_CHOICES,
        'status_choices': Stamp.STATUS_CHOICES,
        'source_choices': Stamp.SOURCE_CATEGORY_CHOICES,
        'filters': {
            'search': search_query,
            'manufacturer': manufacturer_filter,
            'stamp_type': stamp_type_filter,
            'status': status_filter,
            'source': source_filter,
            'sort': sort_by,
        }
    }
    
    return render(request, 'axes/stamp_list.html', context)


@login_required
def stamp_detail(request, stamp_id):
    """Detaljvy för en stämpel"""
    
    stamp = get_object_or_404(Stamp.objects.select_related('manufacturer').prefetch_related(
        'transcriptions', 'images', 'axes', 'axes__axe'
    ), id=stamp_id)
    
    # Hämta relaterade stämplar (varianter, osäkerhetsgrupper)
    related_stamps = Stamp.objects.filter(
        Q(variants__main_stamp=stamp) |
        Q(main_stamp__variant_stamp=stamp) |
        Q(uncertainty_groups__stamps=stamp)
    ).distinct()
    
    context = {
        'stamp': stamp,
        'related_stamps': related_stamps,
    }
    
    return render(request, 'axes/stamp_detail.html', context)


@login_required
def stamp_create(request):
    """Skapa ny stämpel"""
    
    if request.method == 'POST':
        form = StampForm(request.POST)
        if form.is_valid():
            stamp = form.save()
            messages.success(request, f'Stämpel "{stamp.name}" skapades framgångsrikt.')
            return redirect('stamp_detail', stamp_id=stamp.id)
    else:
        form = StampForm()
    
    context = {
        'form': form,
        'title': 'Skapa ny stämpel',
    }
    
    return render(request, 'axes/stamp_form.html', context)


@login_required
def stamp_edit(request, stamp_id):
    """Redigera stämpel"""
    
    stamp = get_object_or_404(Stamp, id=stamp_id)
    
    if request.method == 'POST':
        form = StampForm(request.POST, instance=stamp)
        if form.is_valid():
            stamp = form.save()
            messages.success(request, f'Stämpel "{stamp.name}" uppdaterades framgångsrikt.')
            return redirect('stamp_detail', stamp_id=stamp.id)
    else:
        form = StampForm(instance=stamp)
    
    context = {
        'form': form,
        'stamp': stamp,
        'title': f'Redigera stämpel: {stamp.name}',
    }
    
    return render(request, 'axes/stamp_form.html', context)


@login_required
def axes_without_stamps(request):
    """Lista yxor som inte har stämplar definierade"""
    
    # Hämta yxor som inte har några stämplar
    axes_without_stamps = Axe.objects.filter(stamps__isnull=True).select_related('manufacturer')
    
    # Filtrering
    manufacturer_filter = request.GET.get('manufacturer', '')
    if manufacturer_filter:
        axes_without_stamps = axes_without_stamps.filter(manufacturer_id=manufacturer_filter)
    
    # Sortering
    sort_by = request.GET.get('sort', 'manufacturer')
    if sort_by == 'manufacturer':
        axes_without_stamps = axes_without_stamps.order_by('manufacturer__name', 'model')
    elif sort_by == 'created':
        axes_without_stamps = axes_without_stamps.order_by('-id')
    elif sort_by == 'model':
        axes_without_stamps = axes_without_stamps.order_by('model')
    
    # Paginering
    paginator = Paginator(axes_without_stamps, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistik
    total_axes = Axe.objects.count()
    axes_with_stamps = Axe.objects.filter(stamps__isnull=False).distinct().count()
    axes_without_stamps_count = total_axes - axes_with_stamps
    
    context = {
        'page_obj': page_obj,
        'axes': page_obj,
        'total_axes': total_axes,
        'axes_with_stamps': axes_with_stamps,
        'axes_without_stamps_count': axes_without_stamps_count,
        'manufacturers': Manufacturer.objects.all().order_by('name'),
        'filters': {
            'manufacturer': manufacturer_filter,
            'sort': sort_by,
        }
    }
    
    return render(request, 'axes/axes_without_stamps.html', context)


@login_required
def stamp_search(request):
    """AJAX-sökning för stämplar"""
    
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'results': []})
    
    stamps = Stamp.objects.filter(
        Q(name__icontains=query) |
        Q(transcriptions__text__icontains=query) |
        Q(manufacturer__name__icontains=query)
    ).select_related('manufacturer').distinct()[:10]
    
    results = []
    for stamp in stamps:
        results.append({
            'id': stamp.id,
            'name': stamp.name,
            'manufacturer': stamp.manufacturer.name if stamp.manufacturer else 'Okänd',
            'type': stamp.get_stamp_type_display(),
            'status': stamp.get_status_display(),
        })
    
    return JsonResponse({'results': results})


@login_required
def add_axe_stamp(request, axe_id):
    """Lägg till stämpel på yxa"""
    
    axe = get_object_or_404(Axe, id=axe_id)
    
    if request.method == 'POST':
        form = AxeStampForm(request.POST)
        if form.is_valid():
            axe_stamp = form.save(commit=False)
            axe_stamp.axe = axe
            axe_stamp.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Stämpel "{axe_stamp.stamp.name}" lades till på yxan.'
                })
            
            messages.success(request, f'Stämpel "{axe_stamp.stamp.name}" lades till på yxan.')
            return redirect('axe_detail', axe_id=axe.id)
    else:
        form = AxeStampForm()
    
    context = {
        'axe': axe,
        'form': form,
        'title': f'Lägg till stämpel på {axe}',
    }
    
    return render(request, 'axes/axe_stamp_form.html', context)


@login_required
def remove_axe_stamp(request, axe_id, stamp_id):
    """Ta bort stämpel från yxa"""
    
    axe_stamp = get_object_or_404(AxeStamp, axe_id=axe_id, stamp_id=stamp_id)
    stamp_name = axe_stamp.stamp.name
    
    if request.method == 'POST':
        axe_stamp.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Stämpel "{stamp_name}" togs bort från yxan.'
            })
        
        messages.success(request, f'Stämpel "{stamp_name}" togs bort från yxan.')
        return redirect('axe_detail', axe_id=axe_id)
    
    context = {
        'axe_stamp': axe_stamp,
        'axe': axe_stamp.axe,
        'stamp': axe_stamp.stamp,
    }
    
    return render(request, 'axes/axe_stamp_confirm_delete.html', context)


@login_required
def stamp_statistics(request):
    """Statistik för stämplar"""
    
    # Grundläggande statistik
    total_stamps = Stamp.objects.count()
    known_stamps = Stamp.objects.filter(status='known').count()
    unknown_stamps = Stamp.objects.filter(status='unknown').count()
    
    # Stämplar per tillverkare
    stamps_by_manufacturer = Stamp.objects.values('manufacturer__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Stämplar per typ
    stamps_by_type = Stamp.objects.values('stamp_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Yxor med stämplar vs utan
    total_axes = Axe.objects.count()
    axes_with_stamps = Axe.objects.filter(stamps__isnull=False).distinct().count()
    axes_without_stamps = total_axes - axes_with_stamps
    
    context = {
        'total_stamps': total_stamps,
        'known_stamps': known_stamps,
        'unknown_stamps': unknown_stamps,
        'stamps_by_manufacturer': stamps_by_manufacturer,
        'stamps_by_type': stamps_by_type,
        'total_axes': total_axes,
        'axes_with_stamps': axes_with_stamps,
        'axes_without_stamps': axes_without_stamps,
    }
    
    return render(request, 'axes/stamp_statistics.html', context) 