from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Transaction, Contact, Platform


def transaction_list(request):
    """Visa alla transaktioner i systemet"""
    # Hämta filter från URL-parametrar
    type_filter = request.GET.get("type", "")
    platform_filter = request.GET.get("platform", "")
    contact_filter = request.GET.get("contact", "")

    # Starta med alla transaktioner
    transactions = (
        Transaction.objects.all()
        .select_related("axe__manufacturer", "contact", "platform")
        .order_by("-transaction_date")
    )

    # Applicera filter
    if type_filter:
        transactions = transactions.filter(type=type_filter)

    if platform_filter:
        transactions = transactions.filter(platform_id=platform_filter)

    if contact_filter == "with_contact":
        transactions = transactions.filter(contact__isnull=False)
    elif contact_filter == "without_contact":
        transactions = transactions.filter(contact__isnull=True)

    # Beräkna totala statistik för filtrerade transaktioner
    filtered_transactions = transactions
    total_buys = filtered_transactions.filter(type="KÖP").count()
    total_sales = filtered_transactions.filter(type="SÄLJ").count()
    total_buy_value = (
        filtered_transactions.filter(type="KÖP").aggregate(total=Sum("price"))["total"]
        or 0
    )
    total_sale_value = (
        filtered_transactions.filter(type="SÄLJ").aggregate(total=Sum("price"))["total"]
        or 0
    )
    total_profit = total_sale_value - total_buy_value

    # Hämta data för filter-dropdowns
    from .models import Platform

    platforms = Platform.objects.all().order_by("name")

    # Hämta inställningar för DataTables
    from .models import Settings

    settings = Settings.get_settings()
    if request.user.is_authenticated:
        default_page_length = int(settings.default_transactions_rows_private)
    else:
        default_page_length = int(settings.default_transactions_rows_public)

    context = {
        "transactions": transactions,
        "platforms": platforms,
        "type_filter": type_filter,
        "platform_filter": platform_filter,
        "contact_filter": contact_filter,
        "total_buys": total_buys,
        "total_sales": total_sales,
        "total_buy_value": total_buy_value,
        "total_sale_value": total_sale_value,
        "total_profit": total_profit,
        "filtered_count": transactions.count(),
        "default_page_length": default_page_length,
    }
    return render(request, "axes/transaction_list.html", context)


def api_transaction_detail(request, pk):
    """Returnerar JSON-data för en enskild transaktion (för AJAX-redigering)"""
    try:
        transaction = Transaction.objects.select_related("contact", "platform").get(
            pk=pk
        )
    except Transaction.DoesNotExist:
        raise Http404("Transaktion finns inte")
    data = {
        "id": transaction.id,
        "axe_id": transaction.axe_id,
        "contact_id": transaction.contact.id if transaction.contact else None,
        "contact_name": transaction.contact.name if transaction.contact else "",
        "contact_alias": transaction.contact.alias if transaction.contact else "",
        "contact_email": transaction.contact.email if transaction.contact else "",
        "contact_phone": transaction.contact.phone if transaction.contact else "",
        "platform_id": transaction.platform.id if transaction.platform else None,
        "platform_name": transaction.platform.name if transaction.platform else "",
        "price": float(transaction.price) if transaction.price is not None else "",
        "shipping_cost": (
            float(transaction.shipping_cost)
            if transaction.shipping_cost is not None
            else ""
        ),
        "transaction_date": (
            transaction.transaction_date.strftime("%Y-%m-%d")
            if transaction.transaction_date
            else ""
        ),
        "comment": transaction.comment or "",
        "type": transaction.type,
    }
    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["POST"])
def api_transaction_update(request, pk):
    """Uppdatera en transaktion via AJAX (POST)."""
    try:
        transaction = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Transaktion finns inte."}, status=404
        )

    # Hämta data
    data = request.POST
    errors = {}

    # Datum
    transaction.transaction_date = (
        data.get("transaction_date") or transaction.transaction_date
    )

    # Pris och frakt
    try:
        price = float(data.get("price", ""))
        shipping = float(data.get("shipping_cost", ""))
    except (TypeError, ValueError):
        errors["price"] = "Ogiltigt pris eller frakt."
        price = transaction.price
        shipping = transaction.shipping_cost

    # Typ: negativt = KÖP, positivt = SÄLJ
    if price < 0 or shipping < 0:
        transaction.type = "KÖP"
        transaction.price = abs(price)
        transaction.shipping_cost = abs(shipping)
    else:
        transaction.type = "SÄLJ"
        transaction.price = abs(price)
        transaction.shipping_cost = abs(shipping)

    # Kommentar
    transaction.comment = data.get("comment", transaction.comment)

    # Kontakt
    selected_contact_id = data.get("selected_contact_id")
    if selected_contact_id:
        try:
            transaction.contact = Contact.objects.get(id=selected_contact_id)
        except Contact.DoesNotExist:
            errors["contact"] = "Kontakt finns inte."
    else:
        contact_name = data.get("contact_name")
        if contact_name:
            contact, created = Contact.objects.get_or_create(
                name=contact_name,
                defaults={
                    "alias": data.get("contact_alias", ""),
                    "email": data.get("contact_email", ""),
                    "phone": data.get("contact_phone", ""),
                    "comment": data.get("contact_comment", ""),
                    "is_naj_member": data.get("is_naj_member") == "on",
                },
            )
            transaction.contact = contact
        else:
            transaction.contact = None

    # Plattform
    selected_platform_id = data.get("selected_platform_id")
    if selected_platform_id:
        try:
            transaction.platform = Platform.objects.get(id=selected_platform_id)
        except Platform.DoesNotExist:
            errors["platform"] = "Plattform finns inte."
    else:
        platform_search = data.get("platform_search")
        if platform_search and platform_search.strip():
            platform, created = Platform.objects.get_or_create(
                name=platform_search.strip()
            )
            transaction.platform = platform
        else:
            transaction.platform = None

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    transaction.save()
    return JsonResponse({"success": True})


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_transaction_delete(request, pk):
    """Ta bort en transaktion via AJAX (POST)."""
    try:
        transaction = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Transaktion finns inte."}, status=404
        )

    try:
        transaction_id = transaction.id
        transaction.delete()
        return JsonResponse(
            {
                "success": True,
                "message": f"Transaktion {transaction_id} togs bort framgångsrikt.",
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "error": f"Fel vid borttagning av transaktion: {str(e)}",
            },
            status=500,
        )
