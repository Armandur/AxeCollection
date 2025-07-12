from django import forms
from .models import Transaction, Contact, Platform, Measurement

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


class MeasurementForm(forms.ModelForm):
    """Formulär för att lägga till mått på en yxa"""
    
    # Fördefinierade måtttyper för yxor
    MEASUREMENT_TYPES = [
        ('', 'Välj måtttyp...'),
        ('Bladlängd', 'Bladlängd'),
        ('Bladbredd', 'Bladbredd'),
        ('Skaftlängd', 'Skaftlängd'),
        ('Skaftbredd', 'Skaftbredd'),
        ('Total längd', 'Total längd'),
        ('Vikt', 'Vikt'),
        ('Bladvikt', 'Bladvikt'),
        ('Skaftvikt', 'Skaftvikt'),
        ('Handtag', 'Handtag'),
        ('Övrigt', 'Övrigt'),
    ]
    
    # Fördefinierade enheter
    UNITS = [
        ('', 'Välj enhet...'),
        ('mm', 'mm'),
        ('cm', 'cm'),
        ('gram', 'gram'),
        ('kg', 'kg'),
        ('st', 'st'),
        ('Övrigt', 'Övrigt'),
    ]
    
    name = forms.ChoiceField(
        choices=MEASUREMENT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'measurement-name'
        }),
        label='Måtttyp',
        help_text='Välj typ av mått'
    )
    
    custom_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ange eget måttnamn...',
            'id': 'custom-measurement-name',
            'style': 'display: none;'
        }),
        label='Eget måttnamn',
        help_text='Ange eget måttnamn om "Övrigt" är valt'
    )
    
    value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        }),
        label='Värde',
        help_text='Mätvärde'
    )
    
    unit = forms.ChoiceField(
        choices=UNITS,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'measurement-unit'
        }),
        label='Enhet',
        help_text='Måttenhet'
    )
    
    custom_unit = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ange egen enhet...',
            'id': 'custom-measurement-unit',
            'style': 'display: none;'
        }),
        label='Egen enhet',
        help_text='Ange egen enhet om "Övrigt" är valt'
    )

    class Meta:
        model = Measurement
        fields = ['name', 'value', 'unit']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        custom_name = cleaned_data.get('custom_name')
        unit = cleaned_data.get('unit')
        custom_unit = cleaned_data.get('custom_unit')
        
        # Hantera anpassade namn
        if name == 'Övrigt' and not custom_name:
            raise forms.ValidationError('Ange ett namn för det anpassade måttet.')
        elif name == 'Övrigt':
            cleaned_data['name'] = custom_name
        
        # Hantera anpassade enheter
        if unit == 'Övrigt' and not custom_unit:
            raise forms.ValidationError('Ange en enhet för det anpassade måttet.')
        elif unit == 'Övrigt':
            cleaned_data['unit'] = custom_unit
        
        return cleaned_data 