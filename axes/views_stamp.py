from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator
from django.contrib import messages
from .models import (
    Stamp, 
    StampTranscription, 
    StampTag, 
    StampImage, 
    AxeStamp, 
    AxeImageStamp,
    StampVariant, 
    StampUncertaintyGroup,
    Axe,
    Manufacturer,
    AxeImage
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
    stamps = Stamp.objects.select_related('manufacturer').prefetch_related(
        'transcriptions', 
        Prefetch('images', queryset=StampImage.objects.order_by('order', '-uploaded_at')),
        Prefetch('axe_image_marks', queryset=AxeImageStamp.objects.select_related('axe_image').order_by('-is_primary', '-created_at'))
    )
    
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
    
    # Hämta alla AxeImageStamp-kopplingar för denna stämpel
    axe_image_marks = AxeImageStamp.objects.filter(
        stamp=stamp
    ).select_related('axe_image__axe').order_by('-is_primary', '-created_at')
    
    context = {
        'stamp': stamp,
        'related_stamps': related_stamps,
        'axe_image_marks': axe_image_marks,
    }
    
    return render(request, 'axes/stamp_detail.html', context)


@login_required
def stamp_create(request):
    """Skapa ny stämpel"""
    
    # Hämta manufacturer från URL-parametern
    manufacturer_id = request.GET.get('manufacturer')
    initial_data = {}
    
    if manufacturer_id:
        try:
            manufacturer = Manufacturer.objects.get(id=manufacturer_id)
            initial_data['manufacturer'] = manufacturer
        except Manufacturer.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = StampForm(request.POST)
        if form.is_valid():
            stamp = form.save()
            messages.success(request, f'Stämpel "{stamp.name}" skapades framgångsrikt.')
            return redirect('stamp_detail', stamp_id=stamp.id)
    else:
        form = StampForm(initial=initial_data)
    
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
    manufacturer_filter = request.GET.get('manufacturer', '')
    stamp_type_filter = request.GET.get('stamp_type', '')
    
    if not query and not manufacturer_filter and not stamp_type_filter:
        return JsonResponse({'results': []})
    
    stamps = Stamp.objects.select_related('manufacturer').prefetch_related('transcriptions')
    
    # Sökning
    if query:
        stamps = stamps.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(transcriptions__text__icontains=query) |
            Q(manufacturer__name__icontains=query)
        ).distinct()
    
    # Filtrering
    if manufacturer_filter:
        stamps = stamps.filter(manufacturer_id=manufacturer_filter)
    
    if stamp_type_filter:
        stamps = stamps.filter(stamp_type=stamp_type_filter)
    
    # Begränsa resultat
    stamps = stamps[:20]
    
    results = []
    for stamp in stamps:
        # Hitta bästa matchande transkription
        best_transcription = ''
        if query:
            transcriptions = stamp.transcriptions.all()
            for transcription in transcriptions:
                if query.lower() in transcription.text.lower():
                    best_transcription = transcription.text
                    break
            if not best_transcription and transcriptions.exists():
                best_transcription = transcriptions.first().text
        
        results.append({
            'id': stamp.id,
            'name': stamp.name,
            'manufacturer': stamp.manufacturer.name if stamp.manufacturer else 'Okänd',
            'type': stamp.get_stamp_type_display(),
            'status': stamp.get_status_display(),
            'description': stamp.description[:100] + '...' if stamp.description and len(stamp.description) > 100 else stamp.description,
            'transcription': best_transcription[:100] + '...' if best_transcription and len(best_transcription) > 100 else best_transcription,
            'url': f'/stamplar/{stamp.id}/',
        })
    
    return JsonResponse({'results': results})


@login_required
def stamp_image_upload(request, stamp_id):
    """Ladda upp bild för stämpel"""
    
    stamp = get_object_or_404(Stamp, id=stamp_id)
    
    if request.method == 'POST':
        form = StampImageForm(request.POST, request.FILES)
        if form.is_valid():
            stamp_image = form.save(commit=False)
            stamp_image.stamp = stamp
            stamp_image.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Bild laddades upp framgångsrikt.',
                    'image_id': stamp_image.id,
                    'image_url': stamp_image.image_url_with_cache_busting,
                    'webp_url': stamp_image.webp_url,
                })
            
            messages.success(request, 'Bild laddades upp framgångsrikt.')
            return redirect('stamp_detail', stamp_id=stamp.id)
    else:
        form = StampImageForm()
    
    context = {
        'stamp': stamp,
        'form': form,
        'title': f'Ladda upp bild för {stamp.name}',
    }
    
    return render(request, 'axes/stamp_image_form.html', context)


@login_required
def stamp_image_delete(request, stamp_id, image_id):
    """Ta bort stämpelbild"""
    
    stamp = get_object_or_404(Stamp, id=stamp_id)
    stamp_image = get_object_or_404(StampImage, id=image_id, stamp=stamp)
    
    if request.method == 'POST':
        image_name = stamp_image.caption or 'Bild'
        stamp_image.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Bild "{image_name}" togs bort.'
            })
        
        messages.success(request, f'Bild "{image_name}" togs bort.')
        return redirect('stamp_detail', stamp_id=stamp.id)
    
    context = {
        'stamp': stamp,
        'stamp_image': stamp_image,
        'title': f'Ta bort bild från {stamp.name}',
    }
    
    return render(request, 'axes/stamp_image_delete.html', context)


@login_required
def add_axe_stamp(request, axe_id):
    """Lägg till stämpel på yxa - integrerat flöde med bildval och markering"""
    
    axe = get_object_or_404(Axe, id=axe_id)
    existing_images = axe.images.all()
    
    # Om inga bilder finns, omdirigera till redigera-sidan
    if not existing_images.exists():
        messages.warning(request, 'Denna yxa har inga bilder än. Lägg till bilder först via redigera-sidan.')
        return redirect('axe_edit', pk=axe.id)
    
    if request.method == 'POST':
        # Hantera olika typer av POST-requests
        action = request.POST.get('action', '')
        
        if action == 'select_image':
            # Användaren har valt en bild - visa markering
            selected_image_id = request.POST.get('selected_image')
            if selected_image_id:
                selected_image = get_object_or_404(AxeImage, id=selected_image_id, axe=axe)
                context = {
                    'axe': axe,
                    'existing_images': existing_images,
                    'selected_image': selected_image,
                    'available_stamps': Stamp.objects.select_related('manufacturer').order_by('manufacturer__name', 'name'),
                    'title': f'Markera stämpel på bild - {axe}',
                }
                return render(request, 'axes/axe_stamp_form.html', context)
        
        elif action == 'save_stamp':
            # Användaren har markerat en bild och vill spara stämpeln
            selected_image_id = request.POST.get('selected_image')
            stamp_id = request.POST.get('stamp')
            x_coord = request.POST.get('x_coordinate')
            y_coord = request.POST.get('y_coordinate')
            width = request.POST.get('width')
            height = request.POST.get('height')
            position = request.POST.get('position', '')
            uncertainty_level = request.POST.get('uncertainty_level', '')
            comment = request.POST.get('comment', '')
            
            if selected_image_id and stamp_id:
                selected_image = get_object_or_404(AxeImage, id=selected_image_id, axe=axe)
                stamp = get_object_or_404(Stamp, id=stamp_id)
                
                # Skapa AxeImageStamp
                axe_image_stamp = AxeImageStamp.objects.create(
                    axe_image=selected_image,
                    stamp=stamp,
                    x_coordinate=x_coord if x_coord else None,
                    y_coordinate=y_coord if y_coord else None,
                    width=width if width else None,
                    height=height if height else None,
                    show_full_image=False,
                    is_primary=False,
                    comment=comment
                )
                
                # Skapa även AxeStamp för att koppla stämpeln till yxan
                axe_stamp = AxeStamp.objects.create(
                    axe=axe,
                    stamp=stamp,
                    position=position,
                    uncertainty_level=uncertainty_level,
                    comment=comment
                )
                
                messages.success(request, f'Stämpel "{stamp.name}" markerades på bilden och kopplades till yxan.')
                return redirect('axe_detail', pk=axe.id)
            else:
                messages.error(request, 'Bild och stämpel måste väljas.')
    
    # GET-request - visa bildval
    context = {
        'axe': axe,
        'existing_images': existing_images,
        'title': f'Välj bild för stämpelmarkering - {axe}',
    }
    
    return render(request, 'axes/axe_stamp_form.html', context)


@login_required
def remove_axe_stamp(request, axe_id, stamp_id):
    """Ta bort stämpel från yxa"""
    
    axe_stamp = get_object_or_404(AxeStamp, axe_id=axe_id, stamp_id=stamp_id)
    stamp_name = axe_stamp.stamp.name
    
    if request.method == 'POST':
        # Ta bort alla stämpelmarkeringar för denna stämpel på denna yxa
        AxeImageStamp.objects.filter(
            axe_image__axe_id=axe_id,
            stamp_id=stamp_id
        ).delete()
        
        # Ta bort själva stämpelkopplingen
        axe_stamp.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Stämpel "{stamp_name}" togs bort från yxan.'
            })
        
        messages.success(request, f'Stämpel "{stamp_name}" togs bort från yxan.')
        return redirect('axe_detail', pk=axe_id)
    
    # För AJAX GET-anrop, returnera modal-innehåll
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = {
            'axe_stamp': axe_stamp,
            'axe': axe_stamp.axe,
            'stamp': axe_stamp.stamp,
        }
        return render(request, 'axes/axe_stamp_confirm_delete_modal.html', context)
    
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


@login_required
def mark_axe_image_as_stamp(request, axe_id, image_id):
    """Markera en AxeImage som innehåller en stämpel"""
    
    axe_image = get_object_or_404(AxeImage, id=image_id, axe_id=axe_id)
    
    if request.method == 'POST':
        stamp_id = request.POST.get('stamp')
        x_coord = request.POST.get('x_coordinate')
        y_coord = request.POST.get('y_coordinate')
        width = request.POST.get('width')
        height = request.POST.get('height')
        comment = request.POST.get('comment', '')
        
        if stamp_id:
            stamp = get_object_or_404(Stamp, id=stamp_id)
            
            # Skapa eller uppdatera AxeImageStamp
            axe_image_stamp, created = AxeImageStamp.objects.get_or_create(
                axe_image=axe_image,
                stamp=stamp,
                defaults={
                    'x_coordinate': x_coord if x_coord else None,
                    'y_coordinate': y_coord if y_coord else None,
                    'width': width if width else None,
                    'height': height if height else None,
                    'show_full_image': False,  # Standardvärde
                    'is_primary': False,  # Standardvärde
                    'comment': comment
                }
            )
            
            if not created:
                # Uppdatera befintlig
                axe_image_stamp.x_coordinate = x_coord if x_coord else None
                axe_image_stamp.y_coordinate = y_coord if y_coord else None
                axe_image_stamp.width = width if width else None
                axe_image_stamp.height = height if height else None
                axe_image_stamp.comment = comment
                axe_image_stamp.save()
            
            messages.success(request, f'Bild markerad som stämpel: {stamp.name}')
            return redirect('axe_detail', pk=axe_id)
    
    # Hämta tillgängliga stämplar (prioritera tillverkarens stämplar)
    available_stamps = Stamp.objects.select_related('manufacturer').order_by(
        'manufacturer__name', 'name'
    )
    
    # Befintlig markering
    existing_mark = AxeImageStamp.objects.filter(axe_image=axe_image).first()
    
    context = {
        'axe_image': axe_image,
        'axe': axe_image.axe,
        'available_stamps': available_stamps,
        'existing_mark': existing_mark,
    }
    
    return render(request, 'axes/mark_axe_image_as_stamp.html', context)


@login_required
def unmark_axe_image_stamp(request, axe_id, image_id):
    """Ta bort markering av stämpel från AxeImage"""
    
    axe_image = get_object_or_404(AxeImage, id=image_id, axe_id=axe_id)
    stamp_mark = get_object_or_404(AxeImageStamp, axe_image=axe_image)
    
    if request.method == 'POST':
        stamp_name = stamp_mark.stamp.name
        stamp_mark.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Stämpelmarkering borttagen: {stamp_name}'
            })
        
        messages.success(request, f'Stämpelmarkering borttagen: {stamp_name}')
        return redirect('axe_detail', pk=axe_id)
    
    # För AJAX GET-anrop, returnera modal-innehåll
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = {
            'axe_image': axe_image,
            'axe': axe_image.axe,
            'stamp_mark': stamp_mark,
        }
        return render(request, 'axes/unmark_axe_image_stamp_modal.html', context)
    
    context = {
        'axe_image': axe_image,
        'axe': axe_image.axe,
        'stamp_mark': stamp_mark,
    }
    
    return render(request, 'axes/unmark_axe_image_stamp.html', context)


@login_required
def edit_axe_image_stamp(request, axe_id, image_id):
    """Redigera stämpelmarkering på AxeImage"""
    
    axe_image = get_object_or_404(AxeImage, id=image_id, axe_id=axe_id)
    stamp_mark = get_object_or_404(AxeImageStamp, axe_image=axe_image)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete':
            # Ta bort stämpelmarkeringen
            stamp_name = stamp_mark.stamp.name
            stamp_mark.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Stämpelmarkering borttagen: {stamp_name}'
                })
            
            messages.success(request, f'Stämpelmarkering borttagen: {stamp_name}')
            return redirect('axe_detail', pk=axe_id)
        
        elif action == 'update':
            # Uppdatera stämpelmarkeringen
            stamp_id = request.POST.get('stamp')
            x_coord = request.POST.get('x_coordinate')
            y_coord = request.POST.get('y_coordinate')
            width = request.POST.get('width')
            height = request.POST.get('height')
            comment = request.POST.get('comment', '')
            
            if stamp_id:
                stamp = get_object_or_404(Stamp, id=stamp_id)
                
                # Uppdatera befintlig markering
                stamp_mark.stamp = stamp
                stamp_mark.x_coordinate = x_coord if x_coord else None
                stamp_mark.y_coordinate = y_coord if y_coord else None
                stamp_mark.width = width if width else None
                stamp_mark.height = height if height else None
                stamp_mark.comment = comment
                stamp_mark.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Stämpelmarkering uppdaterad: {stamp.name}'
                    })
                
                messages.success(request, f'Stämpelmarkering uppdaterad: {stamp.name}')
                return redirect('axe_detail', pk=axe_id)
    
    # Hämta alla tillgängliga stämplar för dropdown
    stamps = Stamp.objects.all().order_by('name')
    
    context = {
        'axe_image': axe_image,
        'axe': axe_image.axe,
        'stamp_mark': stamp_mark,
        'stamps': stamps,
    }
    
    return render(request, 'axes/edit_axe_image_stamp.html', context)


@login_required
def stamp_image_crop(request, stamp_id):
    """Visa och hantera beskärning av stämpelbilder"""
    
    stamp = get_object_or_404(Stamp.objects.select_related('manufacturer'))
    
    # Hämta alla AxeImageStamp-kopplingar för denna stämpel
    axe_image_marks = AxeImageStamp.objects.filter(
        stamp=stamp
    ).select_related('axe_image__axe').order_by('-is_primary', '-created_at')
    
    context = {
        'stamp': stamp,
        'axe_image_marks': axe_image_marks,
    }
    
    return render(request, 'axes/stamp_image_crop.html', context)


@login_required
def set_primary_stamp_image(request, stamp_id, mark_id):
    """Sätt en AxeImageStamp som huvudbild för stämpeln"""
    
    stamp = get_object_or_404(Stamp, id=stamp_id)
    mark = get_object_or_404(AxeImageStamp, id=mark_id, stamp=stamp)
    
    if request.method == 'POST':
        # Ta bort tidigare huvudbild
        AxeImageStamp.objects.filter(stamp=stamp, is_primary=True).update(is_primary=False)
        
        # Sätt ny huvudbild
        mark.is_primary = True
        mark.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Huvudbild satt för stämpel: {stamp.name}'
            })
        
        messages.success(request, f'Huvudbild satt för stämpel: {stamp.name}')
        return redirect('stamp_detail', stamp_id=stamp_id)
    
    return redirect('stamp_detail', stamp_id=stamp_id)


@login_required
def update_axe_image_stamp_show_full(request, mark_id):
    """Uppdatera show_full_image för en AxeImageStamp"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Endast POST-anrop tillåtet'})
    
    try:
        mark = get_object_or_404(AxeImageStamp, id=mark_id)
        
        # Läs JSON-data från request body
        import json
        data = json.loads(request.body)
        show_full_image = data.get('show_full_image', False)
        
        mark.show_full_image = show_full_image
        mark.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Inställning uppdaterad framgångsrikt'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }) 


@login_required
def edit_axe_stamp(request, axe_id, axe_stamp_id):
    """Redigera en befintlig yxstämpel med bildmarkering"""
    
    axe = get_object_or_404(Axe, id=axe_id)
    axe_stamp = get_object_or_404(AxeStamp, id=axe_stamp_id, axe=axe)
    
    # Hämta befintliga bilder för yxan
    existing_images = axe.images.all().order_by('order')
    
    # Hämta befintlig AxeImageStamp för denna stämpel
    existing_axe_image_stamp = AxeImageStamp.objects.filter(
        stamp=axe_stamp.stamp,
        axe_image__axe=axe
    ).first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'select_image':
            # Steg 1: Välj bild
            selected_image_id = request.POST.get('selected_image_id')
            if selected_image_id:
                selected_image = get_object_or_404(AxeImage, id=selected_image_id, axe=axe)
                available_stamps = Stamp.objects.all().order_by('name')
                
                # Hämta befintlig AxeImageStamp för den valda bilden
                selected_image_stamp = AxeImageStamp.objects.filter(
                    stamp=axe_stamp.stamp,
                    axe_image=selected_image
                ).first()
                
                context = {
                    'axe': axe,
                    'axe_stamp': axe_stamp,
                    'selected_image': selected_image,
                    'available_stamps': available_stamps,
                    'existing_axe_image_stamp': selected_image_stamp,
                    'title': f'Redigera stämpel - {axe.display_id}',
                }
                return render(request, 'axes/axe_stamp_edit.html', context)
        
        elif action == 'save_stamp':
            # Steg 2: Spara stämpel med bildmarkering
            form = AxeStampForm(request.POST, instance=axe_stamp)
            if form.is_valid():
                # Spara AxeStamp
                axe_stamp = form.save()
                
                # Hantera AxeImageStamp
                selected_image_id = request.POST.get('selected_image_id')
                if selected_image_id:
                    selected_image = get_object_or_404(AxeImage, id=selected_image_id, axe=axe)
                    
                    # Ta bort befintlig AxeImageStamp för samma stämpel på samma bild
                    AxeImageStamp.objects.filter(
                        stamp=axe_stamp.stamp,
                        axe_image=selected_image
                    ).delete()
                    
                    # Skapa ny AxeImageStamp
                    x_coord = request.POST.get('x_coordinate')
                    y_coord = request.POST.get('y_coordinate')
                    width = request.POST.get('width')
                    height = request.POST.get('height')
                    
                    if x_coord and y_coord and width and height:
                        AxeImageStamp.objects.create(
                            axe_image=selected_image,
                            stamp=axe_stamp.stamp,
                            x_coordinate=int(x_coord),
                            y_coordinate=int(y_coord),
                            width=int(width),
                            height=int(height),
                            comment=request.POST.get('image_comment', '')
                        )
                    else:
                        # Om inga koordinater finns, ta bort alla AxeImageStamp för denna stämpel
                        AxeImageStamp.objects.filter(
                            stamp=axe_stamp.stamp,
                            axe_image__axe=axe
                        ).delete()
                
                messages.success(request, f'Stämpel "{axe_stamp.stamp.name}" uppdaterades.')
                return redirect('axe_detail', pk=axe.id)
        else:
            # Vanlig formulärhantering (utan bildmarkering)
            form = AxeStampForm(request.POST, instance=axe_stamp)
            if form.is_valid():
                form.save()
                messages.success(request, f'Stämpel "{axe_stamp.stamp.name}" uppdaterades.')
                return redirect('axe_detail', pk=axe.id)
    else:
        form = AxeStampForm(instance=axe_stamp)
    
    context = {
        'axe': axe,
        'axe_stamp': axe_stamp,
        'existing_images': existing_images,
        'existing_axe_image_stamp': existing_axe_image_stamp,
        'form': form,
        'title': f'Redigera stämpel - {axe.display_id}',
    }
    
    # Om det finns en befintlig AxeImageStamp, förvalda den aktuella bilden
    if existing_axe_image_stamp:
        context['selected_image'] = existing_axe_image_stamp.axe_image
        context['available_stamps'] = Stamp.objects.all().order_by('name')
    
    return render(request, 'axes/axe_stamp_edit.html', context) 