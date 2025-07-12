from django.shortcuts import render, get_object_or_404
from .models import Manufacturer, ManufacturerImage, ManufacturerLink, Axe, Transaction
from django.db.models import Sum

def manufacturer_list(request):
    manufacturers = Manufacturer.objects.all().order_by('name')
    for manufacturer in manufacturers:
        axes = Axe.objects.filter(manufacturer=manufacturer)
        manufacturer.axe_count = axes.count()
        manufacturer.image_count = ManufacturerImage.objects.filter(manufacturer=manufacturer).count()
        manufacturer.link_count = ManufacturerLink.objects.filter(manufacturer=manufacturer).count()
        # Beräkna transaktionsstatistik
        transactions = Transaction.objects.filter(axe__manufacturer=manufacturer)
        buy_transactions = transactions.filter(type='KÖP')
        sale_transactions = transactions.filter(type='SÄLJ')
        manufacturer.buy_count = buy_transactions.count()
        manufacturer.sale_count = sale_transactions.count()
        manufacturer.total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
        manufacturer.total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
        manufacturer.net_value = manufacturer.total_sale_value - manufacturer.total_buy_value
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
    images = ManufacturerImage.objects.filter(manufacturer=manufacturer).order_by('id')
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
    manufacturer_images = images
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
        'manufacturer_images': manufacturer_images,
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