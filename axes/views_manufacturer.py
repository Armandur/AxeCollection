from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Manufacturer, ManufacturerImage, ManufacturerLink, Axe, Transaction
from django.db.models import Sum
import json

def manufacturer_list(request):
    manufacturers = Manufacturer.objects.all().order_by('name')
    # Ta bort all tilldelning av statistikfält, använd properties direkt i template/context
    total_manufacturers = manufacturers.count()
    total_axes = Axe.objects.count()
    total_transactions = Transaction.objects.count()
    average_axes_per_manufacturer = total_axes / total_manufacturers if total_manufacturers > 0 else 0
    context = {
        'manufacturers': manufacturers,
        'total_manufacturers': total_manufacturers,
        'total_axes': total_axes,
        'total_transactions': total_transactions,
        'average_axes_per_manufacturer': average_axes_per_manufacturer,
    }
    return render(request, 'axes/manufacturer_list.html', context)

def manufacturer_detail(request, pk):
    manufacturer = get_object_or_404(Manufacturer, pk=pk)
    axes = Axe.objects.filter(manufacturer=manufacturer).order_by('-id')
    images = ManufacturerImage.objects.filter(manufacturer=manufacturer).order_by('image_type', 'order')
    links = ManufacturerLink.objects.filter(manufacturer=manufacturer).order_by('link_type', 'title')
    # Statistik
    total_axes = axes.count()
    transactions = Transaction.objects.filter(axe__manufacturer=manufacturer)
    total_transactions = transactions.count()
    buy_transactions = transactions.filter(type='KÖP')
    sale_transactions = transactions.filter(type='SÄLJ')
    total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_profit = total_sale_value - total_buy_value
    average_profit_per_axe = total_profit / total_axes if total_axes > 0 else 0
    # Köp/sälj-antal
    buy_count = buy_transactions.count()
    sale_count = sale_transactions.count()
    # Status för varje yxa
    for axe in axes:
        # Prioritera statusfältet
        if axe.status == 'MOTTAGEN':
            axe.status_class = 'bg-success'
        elif axe.status == 'KÖPT':
            axe.status_class = 'bg-warning'
        elif axe.status == 'SÅLD':
            axe.status_class = 'bg-secondary'
        else:
            # Om statusfältet är tomt eller okänt, bestäm utifrån senaste transaktion
            last_transaction = Transaction.objects.filter(axe=axe).order_by('-transaction_date').first()
            if last_transaction:
                if last_transaction.type == 'SÄLJ':
                    axe.status = 'SÅLD'
                    axe.status_class = 'bg-secondary'
                elif last_transaction.type == 'KÖP':
                    axe.status = 'KÖPT'
                    axe.status_class = 'bg-warning'
                else:
                    axe.status = 'OKÄND'
                    axe.status_class = 'bg-light'
            else:
                axe.status = 'OKÄND'
                axe.status_class = 'bg-light'
    # Gruppera bilder efter typ
    images_by_type = {}
    for image in images:
        if image.image_type not in images_by_type:
            images_by_type[image.image_type] = []
        images_by_type[image.image_type].append(image)
    
    # Gruppera länkar efter typ
    links_by_type = {}
    for link in links:
        if link.link_type not in links_by_type:
            links_by_type[link.link_type] = []
        links_by_type[link.link_type].append(link)
    # Alla transaktioner
    transactions = Transaction.objects.filter(axe__manufacturer=manufacturer).select_related('axe', 'contact', 'platform').order_by('-transaction_date')
    # Unika kontakter
    unique_contacts = set()
    for transaction in transactions:
        if transaction.contact:
            unique_contacts.add(transaction.contact)
    context = {
        'manufacturer': manufacturer,
        'axes': axes,
        'images': images,
        'links': links,
        'images_by_type': images_by_type,
        'links_by_type': links_by_type,
        'transactions': transactions,
        'unique_contacts': unique_contacts,
        'total_axes': total_axes,
        'total_transactions': total_transactions,
        'total_buy_value': total_buy_value,
        'total_sale_value': total_sale_value,
        'total_profit': total_profit,
        'average_profit_per_axe': average_profit_per_axe,
        'buy_count': buy_count,
        'sale_count': sale_count,
    }
    return render(request, 'axes/manufacturer_detail.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def edit_manufacturer_information(request, pk):
    """AJAX-vy för att redigera tillverkarinformation"""
    try:
        manufacturer = get_object_or_404(Manufacturer, pk=pk)
        data = json.loads(request.body)
        new_information = data.get('information', '').strip()
        
        # Validering
        if len(new_information) > 10000:  # Max 10KB
            return JsonResponse({
                'success': False,
                'error': 'Informationen är för lång (max 10 000 tecken)'
            }, status=400)
        
        manufacturer.information = new_information
        manufacturer.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Information uppdaterad',
            'information': manufacturer.information
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Ogiltig JSON-data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ett fel uppstod: {str(e)}'
        }, status=500) 

@csrf_exempt
@require_http_methods(["POST"])
def edit_manufacturer_name(request, pk):
    """AJAX-vy för att redigera tillverkarnamn"""
    try:
        manufacturer = get_object_or_404(Manufacturer, pk=pk)
        data = json.loads(request.body)
        new_name = data.get('name', '').strip()
        if not new_name:
            return JsonResponse({'success': False, 'error': 'Namnet får inte vara tomt.'}, status=400)
        if len(new_name) > 200:
            return JsonResponse({'success': False, 'error': 'Namnet får vara max 200 tecken.'}, status=400)
        manufacturer.name = new_name
        manufacturer.save()
        return JsonResponse({'success': True, 'name': manufacturer.name})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Ogiltig JSON-data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Ett fel uppstod: {str(e)}'}, status=500) 

@require_http_methods(["POST"])
def edit_manufacturer_image(request, image_id):
    """Redigera tillverkarbild via AJAX"""
    try:
        image = ManufacturerImage.objects.get(id=image_id)
        data = json.loads(request.body)
        
        # Uppdatera fält
        if 'caption' in data:
            image.caption = data['caption']
        if 'description' in data:
            image.description = data['description']
        if 'image_type' in data:
            image.image_type = data['image_type']
        
        image.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Bild uppdaterad'
        })
    except ManufacturerImage.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Bild hittades inte'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["POST"])
def delete_manufacturer_image(request, image_id):
    """Ta bort tillverkarbild via AJAX"""
    try:
        image = ManufacturerImage.objects.get(id=image_id)
        image.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Bild borttagen'
        })
    except ManufacturerImage.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Bild hittades inte'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["POST"])
def add_manufacturer_image(request):
    """Lägg till ny tillverkarbild via AJAX"""
    try:
        manufacturer_id = request.POST.get('manufacturer_id')
        image_file = request.FILES.get('image')
        caption = request.POST.get('caption', '')
        description = request.POST.get('description', '')
        image_type = request.POST.get('image_type', 'STAMP')
        
        if not manufacturer_id or not image_file:
            return JsonResponse({
                'success': False,
                'error': 'Tillverkare och bild krävs'
            }, status=400)
        
        manufacturer = Manufacturer.objects.get(id=manufacturer_id)
        
        # Skapa ny bild
        image = ManufacturerImage.objects.create(
            manufacturer=manufacturer,
            image=image_file,
            caption=caption,
            description=description,
            image_type=image_type
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Bild uppladdad',
            'image_id': image.id
        })
    except Manufacturer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Tillverkare hittades inte'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 

@require_http_methods(["POST"])
def reorder_manufacturer_images(request):
    """Ändra ordning på tillverkarbilder via AJAX"""
    try:
        data = json.loads(request.body)
        manufacturer_id = data.get('manufacturer_id')
        order_data = data.get('order_data', [])
        
        if not manufacturer_id or not order_data:
            return JsonResponse({
                'success': False,
                'error': 'Tillverkare och ordningsdata krävs'
            }, status=400)
        
        # Uppdatera ordningen för varje bild
        for item in order_data:
            image_id = item.get('image_id')
            new_order = item.get('order')
            
            if image_id and new_order is not None:
                try:
                    image = ManufacturerImage.objects.get(id=image_id, manufacturer_id=manufacturer_id)
                    image.order = new_order
                    image.save()
                except ManufacturerImage.DoesNotExist:
                    continue
        
        return JsonResponse({
            'success': True,
            'message': 'Bildordning uppdaterad'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Ogiltig JSON-data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 