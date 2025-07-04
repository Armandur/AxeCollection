from django import forms
from .models import Transaction, Contact, Platform

class TransactionForm(forms.ModelForm):
    transaction_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Transaktionsdatum',
        help_text='Datum för transaktionen'
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
        label='Pris (kr)',
        help_text='Pris för yxan (negativt för köp, positivt för sälj)'
    )
    shipping_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
        label='Fraktkostnad (kr)',
        help_text='Fraktkostnad'
    )
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Kontakt',
        help_text='Välj försäljare/köpare (eller skapa ny)'
    )
    platform = forms.ModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Plattform',
        help_text='Välj plattform (eller skapa ny)'
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Lägg till kommentar om transaktionen...'}),
        label='Kommentar',
        help_text='Kommentar om transaktionen'
    )

    class Meta:
        model = Transaction
        fields = ['transaction_date', 'price', 'shipping_cost', 'contact', 'platform', 'comment'] 