from django import forms
from .models import Transaction, Contact, Platform, Measurement, MeasurementType, MeasurementTemplate

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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hämta aktiva måtttyper från databasen
        measurement_types = MeasurementType.objects.filter(is_active=True)
        choices = [('', 'Välj måtttyp...')] + [(mt.name, mt.name) for mt in measurement_types]
        choices.append(('Övrigt', 'Övrigt'))
        
        self.fields['name'] = forms.ChoiceField(
            choices=choices,
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
    
    unit = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'measurement-unit',
            'placeholder': 't.ex. mm, gram, cm'
        }),
        label='Enhet',
        help_text='Måttenhet'
    )

    class Meta:
        model = Measurement
        fields = ['name', 'value', 'unit']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        custom_name = cleaned_data.get('custom_name')
        
        # Hantera anpassade namn
        if name == 'Övrigt' and not custom_name:
            raise forms.ValidationError('Ange ett namn för det anpassade måttet.')
        elif name == 'Övrigt':
            cleaned_data['name'] = custom_name
        
        return cleaned_data 