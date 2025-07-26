from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from .models import Platform, Transaction
from .forms import PlatformForm


@login_required
def platform_list(request):
    """Lista alla plattformar med statistik"""
    platforms = Platform.objects.annotate(
        transaction_count=Count("transaction"),
        buy_count=Count(
            "transaction",
            filter=Transaction.objects.filter(type="KÖP").values("id").query,
        ),
        sale_count=Count(
            "transaction",
            filter=Transaction.objects.filter(type="SÄLJ").values("id").query,
        ),
        total_buy_value=Sum(
            "transaction__price",
            filter=Transaction.objects.filter(type="KÖP").values("id").query,
        ),
        total_sale_value=Sum(
            "transaction__price",
            filter=Transaction.objects.filter(type="SÄLJ").values("id").query,
        ),
    ).order_by("name")

    context = {"platforms": platforms, "page_title": "Plattformar"}

    return render(request, "axes/platform_list.html", context)


@login_required
def platform_detail(request, pk):
    """Detaljsida för en plattform"""
    platform = get_object_or_404(Platform, pk=pk)

    # Hämta transaktioner för denna plattform
    transactions = (
        Transaction.objects.filter(platform=platform)
        .select_related("axe__manufacturer", "contact")
        .order_by("-transaction_date")
    )

    # Statistik
    buy_transactions = transactions.filter(type="KÖP")
    sale_transactions = transactions.filter(type="SÄLJ")

    total_buy_value = buy_transactions.aggregate(total=Sum("price"))["total"] or 0
    total_sale_value = sale_transactions.aggregate(total=Sum("price"))["total"] or 0
    total_buy_shipping = (
        buy_transactions.aggregate(total=Sum("shipping_cost"))["total"] or 0
    )
    total_sale_shipping = (
        sale_transactions.aggregate(total=Sum("shipping_cost"))["total"] or 0
    )

    profit_loss = total_sale_value - total_buy_value
    profit_loss_with_shipping = (total_sale_value + total_sale_shipping) - (
        total_buy_value + total_buy_shipping
    )

    # Unika yxor
    unique_axes = transactions.values(
        "axe__manufacturer__name", "axe__model", "axe__id"
    ).distinct()

    context = {
        "platform": platform,
        "transactions": transactions,
        "buy_transactions": buy_transactions,
        "sale_transactions": sale_transactions,
        "total_buy_value": total_buy_value,
        "total_sale_value": total_sale_value,
        "total_buy_shipping": total_buy_shipping,
        "total_sale_shipping": total_sale_shipping,
        "profit_loss": profit_loss,
        "profit_loss_with_shipping": profit_loss_with_shipping,
        "unique_axes": unique_axes,
        "page_title": f"Plattform: {platform.name}",
    }

    return render(request, "axes/platform_detail.html", context)


@login_required
def platform_create(request):
    """Skapa ny plattform"""
    if request.method == "POST":
        form = PlatformForm(request.POST)
        if form.is_valid():
            platform = form.save()
            messages.success(request, f'Plattformen "{platform.name}" skapades!')
            return redirect("platform_detail", pk=platform.pk)
    else:
        form = PlatformForm()

    context = {"form": form, "page_title": "Skapa ny plattform"}

    return render(request, "axes/platform_form.html", context)


@login_required
def platform_edit(request, pk):
    """Redigera plattform"""
    platform = get_object_or_404(Platform, pk=pk)

    if request.method == "POST":
        form = PlatformForm(request.POST, instance=platform)
        if form.is_valid():
            platform = form.save()
            messages.success(request, f'Plattformen "{platform.name}" uppdaterades!')
            return redirect("platform_detail", pk=platform.pk)
    else:
        form = PlatformForm(instance=platform)

    context = {
        "form": form,
        "platform": platform,
        "page_title": f"Redigera: {platform.name}",
    }

    return render(request, "axes/platform_form.html", context)


@login_required
def platform_delete(request, pk):
    """Ta bort plattform"""
    platform = get_object_or_404(Platform, pk=pk)

    # Kontrollera om plattformen används i transaktioner
    transaction_count = platform.transaction_set.count()

    if request.method == "POST":
        if transaction_count > 0:
            messages.error(
                request,
                f'Kan inte ta bort plattformen "{platform.name}" eftersom den används i {transaction_count} transaktioner.',
            )
            return redirect("platform_detail", pk=platform.pk)

        platform_name = platform.name
        platform.delete()
        messages.success(request, f'Plattformen "{platform_name}" togs bort!')
        return redirect("platform_list")

    # Hämta kopplade transaktioner för att visa i bekräftelsen
    linked_transactions = platform.transaction_set.select_related(
        "axe__manufacturer", "contact"
    ).order_by("-transaction_date")[:10]

    context = {
        "platform": platform,
        "transaction_count": transaction_count,
        "linked_transactions": linked_transactions,
        "page_title": f"Ta bort: {platform.name}",
    }

    return render(request, "axes/platform_delete.html", context)
