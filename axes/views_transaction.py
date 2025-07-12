from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Transaction, Contact, Platform


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