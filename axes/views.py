from django.shortcuts import render, get_object_or_404
from .models import Axe, Transaction, Contact, Manufacturer, ManufacturerImage, ManufacturerLink
from django.db.models import Sum, Q

# Create your views here.

def axe_list(request):
    axes = Axe.objects.all().select_related('manufacturer').prefetch_related('measurements', 'images', 'transaction_set').order_by('-id')
    
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
    
    return render(request, 'axes/axe_list.html', {
        'axes': axes,
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
    axe = get_object_or_404(Axe.objects.select_related('manufacturer').prefetch_related('measurements', 'images'), pk=pk)
    
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
    }
    
    return render(request, 'axes/axe_detail.html', context)

def contact_list(request):
    """Visa alla kontakter i systemet"""
    contacts = Contact.objects.all().order_by('name')
    
    # Beräkna statistik för varje kontakt
    for contact in contacts:
        transactions = Transaction.objects.filter(contact=contact)
        contact.total_transactions = transactions.count()
        contact.buy_count = transactions.filter(type='KÖP').count()
        contact.sale_count = transactions.filter(type='SÄLJ').count()
        
        # Beräkna ekonomisk statistik
        buy_transactions = transactions.filter(type='KÖP')
        sale_transactions = transactions.filter(type='SÄLJ')
        
        contact.total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
        contact.total_buy_shipping = buy_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
        contact.total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
        contact.total_sale_shipping = sale_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
        contact.net_value = contact.total_sale_value - contact.total_buy_value

    total_contacts = contacts.count()
    total_transactions_count = Transaction.objects.count()
    total_naj_members = Contact.objects.filter(is_naj_member=True).count()
    
    context = {
        'contacts': contacts,
        'total_contacts': total_contacts,
        'total_transactions': total_transactions_count,
        'total_naj_members': total_naj_members
    }
    
    return render(request, 'axes/contact_list.html', context)

def contact_detail(request, pk):
    """Visa detaljerad information om en kontakt"""
    contact = get_object_or_404(Contact, pk=pk)
    
    # Hämta alla transaktioner för denna kontakt
    transactions = Transaction.objects.filter(contact=contact).select_related('axe__manufacturer', 'platform').order_by('-transaction_date')
    
    # Beräkna statistik
    total_transactions = transactions.count()
    buy_transactions = transactions.filter(type='KÖP')
    sale_transactions = transactions.filter(type='SÄLJ')
    
    total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_profit = total_sale_value - total_buy_value
    
    # Hämta unika yxor som kontaktens transaktioner gäller
    unique_axes = set()
    for transaction in transactions:
        unique_axes.add(transaction.axe)
    
    context = {
        'contact': contact,
        'transactions': transactions,
        'total_transactions': total_transactions,
        'total_buy_value': total_buy_value,
        'total_sale_value': total_sale_value,
        'total_profit': total_profit,
        'unique_axes': unique_axes,
        'buy_count': buy_transactions.count(),
        'sale_count': sale_transactions.count(),
    }
    
    return render(request, 'axes/contact_detail.html', context)

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

def manufacturer_list(request):
    """Visa alla tillverkare i systemet"""
    manufacturers = Manufacturer.objects.all()
    
    # Beräkna statistik för varje tillverkare
    for manufacturer in manufacturers:
        axes = Axe.objects.filter(manufacturer=manufacturer)
        manufacturer.axe_count = axes.count()
        
        # Hämta alla transaktioner för denna tillverkare
        transactions = Transaction.objects.filter(axe__manufacturer=manufacturer)
        manufacturer.total_transactions = transactions.count()
        manufacturer.buy_count = transactions.filter(type='KÖP').count()
        manufacturer.sale_count = transactions.filter(type='SÄLJ').count()
        
        # Beräkna ekonomisk statistik
        buy_transactions = transactions.filter(type='KÖP')
        sale_transactions = transactions.filter(type='SÄLJ')
        
        manufacturer.total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
        manufacturer.total_buy_shipping = buy_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
        manufacturer.total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
        manufacturer.total_sale_shipping = sale_transactions.aggregate(total=Sum('shipping_cost'))['total'] or 0
        manufacturer.net_value = manufacturer.total_sale_value - manufacturer.total_buy_value

    # Sortera tillverkare efter antal yxor (flest först)
    manufacturers = sorted(manufacturers, key=lambda m: m.axe_count, reverse=True)

    total_manufacturers = len(manufacturers)
    total_axes_count = Axe.objects.count()
    total_transactions_count = Transaction.objects.count()
    
    # Beräkna genomsnitt antal yxor per tillverkare
    average_axes_per_manufacturer = total_axes_count / total_manufacturers if total_manufacturers > 0 else 0
    
    context = {
        'manufacturers': manufacturers,
        'total_manufacturers': total_manufacturers,
        'total_axes': total_axes_count,
        'total_transactions': total_transactions_count,
        'average_axes_per_manufacturer': average_axes_per_manufacturer
    }
    
    return render(request, 'axes/manufacturer_list.html', context)

def manufacturer_detail(request, pk):
    """Visa detaljerad information om en tillverkare"""
    manufacturer = get_object_or_404(Manufacturer, pk=pk)
    
    # Hämta alla yxor för denna tillverkare
    axes = Axe.objects.filter(manufacturer=manufacturer).order_by('model')
    
    # Beräkna status för varje yxa
    for axe in axes:
        # Hämta den senaste transaktionen för varje yxa
        last_transaction = Transaction.objects.filter(axe=axe).order_by('-transaction_date').first()
        if last_transaction:
            if last_transaction.type == 'SÄLJ':
                axe.status = 'SÅLD'
                axe.status_class = 'bg-secondary'
            else:
                axe.status = 'ÄGES'
                axe.status_class = 'bg-primary'
        else:
            axe.status = 'ÄGES'
            axe.status_class = 'bg-primary'
    
    # Hämta alla transaktioner för denna tillverkare
    transactions = Transaction.objects.filter(axe__manufacturer=manufacturer).select_related('axe', 'contact', 'platform').order_by('-transaction_date')
    
    # Hämta tillverkarens bilder
    manufacturer_images = ManufacturerImage.objects.filter(manufacturer=manufacturer)
    
    # Hämta tillverkarens länkar
    manufacturer_links = ManufacturerLink.objects.filter(manufacturer=manufacturer, is_active=True)
    
    # Gruppera länkar efter typ
    links_by_type = {}
    for link in manufacturer_links:
        if link.link_type not in links_by_type:
            links_by_type[link.link_type] = []
        links_by_type[link.link_type].append(link)
    
    # Beräkna statistik
    total_axes = axes.count()
    total_transactions = transactions.count()
    buy_transactions = transactions.filter(type='KÖP')
    sale_transactions = transactions.filter(type='SÄLJ')
    
    total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_profit = total_sale_value - total_buy_value
    
    # Beräkna genomsnitt vinst per yxa
    average_profit_per_axe = total_profit / total_axes if total_axes > 0 else 0
    
    # Hämta unika kontakter som har transaktioner med denna tillverkare
    unique_contacts = set()
    for transaction in transactions:
        if transaction.contact:
            unique_contacts.add(transaction.contact)
    
    context = {
        'manufacturer': manufacturer,
        'axes': axes,
        'transactions': transactions,
        'total_axes': total_axes,
        'total_transactions': total_transactions,
        'total_buy_value': total_buy_value,
        'total_sale_value': total_sale_value,
        'total_profit': total_profit,
        'average_profit_per_axe': average_profit_per_axe,
        'unique_contacts': unique_contacts,
        'buy_count': buy_transactions.count(),
        'sale_count': sale_transactions.count(),
        'manufacturer_images': manufacturer_images,
        'manufacturer_links': manufacturer_links,
        'links_by_type': links_by_type,
    }
    
    return render(request, 'axes/manufacturer_detail.html', context)
