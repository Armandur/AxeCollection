from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Contact, Transaction
from .forms import ContactForm
from django.db.models import Sum


def contact_list(request):
    sort = request.GET.get('sort')
    contacts = list(Contact.objects.all())
    # Lägg till latest_transaction_date som attribut för sortering
    for c in contacts:
        c._latest_transaction_date = c.latest_transaction_date
    if sort == 'senast':
        contacts.sort(key=lambda c: (c._latest_transaction_date is not None, c._latest_transaction_date), reverse=True)
    else:
        contacts.sort(key=lambda c: c.name.lower())
    total_contacts = len(contacts)
    total_transactions_count = Transaction.objects.count()
    total_naj_members = Contact.objects.filter(is_naj_member=True).count()
    context = {
        'contacts': contacts,
        'total_contacts': total_contacts,
        'total_transactions': total_transactions_count,
        'total_naj_members': total_naj_members,
        'sort': sort,
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

@login_required
def contact_create(request):
    """Vy för att skapa en ny kontakt"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f'Kontakten "{contact.name}" har skapats framgångsrikt.')
            return redirect('contact_detail', pk=contact.pk)
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'is_edit': False,
        'contact': None
    }
    return render(request, 'axes/contact_form.html', context)

@login_required
def contact_edit(request, pk):
    """Vy för att redigera en befintlig kontakt"""
    contact = get_object_or_404(Contact, pk=pk)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f'Kontakten "{contact.name}" har uppdaterats framgångsrikt.')
            return redirect('contact_detail', pk=contact.pk)
    else:
        form = ContactForm(instance=contact)
    
    context = {
        'form': form,
        'is_edit': True,
        'contact': contact
    }
    return render(request, 'axes/contact_form.html', context) 

@login_required
@require_POST
def contact_delete(request, pk):
    """Vy för att ta bort en kontakt"""
    contact = get_object_or_404(Contact, pk=pk)
    contact_name = contact.name
    
    # Kontrollera om användaren vill ta bort transaktionerna också
    delete_transactions = request.POST.get('delete_transactions') == 'true'
    transactions_count = contact.transactions.count()
    
    if delete_transactions:
        # Ta bort alla transaktioner kopplade till kontakten
        contact.transactions.all().delete()
        # Ta bort kontakten
        contact.delete()
        messages.success(request, f'Kontakten "{contact_name}" och {transactions_count} transaktioner har tagits bort.')
    else:
        # Ta bara bort kopplingen mellan transaktioner och kontakt
        contact.transactions.all().update(contact=None)
        # Ta bort kontakten
        contact.delete()
        messages.success(request, f'Kontakten "{contact_name}" har tagits bort. {transactions_count} transaktioner har behållits men kopplingen till kontakten har tagits bort.')
    
    return redirect('contact_list') 