from django.shortcuts import render, get_object_or_404
from .models import Contact, Transaction
from django.db.models import Sum


def contact_list(request):
    contacts = Contact.objects.all().order_by('name')
    # Ta bort all tilldelning av statistikfält, använd properties direkt i template/context
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
    contact = get_object_or_404(Contact, pk=pk)
    transactions = Transaction.objects.filter(contact=contact).select_related('axe__manufacturer', 'platform').order_by('-transaction_date')
    total_transactions = transactions.count()
    buy_transactions = transactions.filter(type='KÖP')
    sale_transactions = transactions.filter(type='SÄLJ')
    total_buy_value = buy_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_sale_value = sale_transactions.aggregate(total=Sum('price'))['total'] or 0
    total_profit = total_sale_value - total_buy_value
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