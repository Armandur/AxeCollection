from django import forms
from .models import Transaction, Contact, Platform, Measurement, MeasurementType, MeasurementTemplate
from django.utils import timezone
from .models import Axe

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

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class AxeForm(forms.ModelForm):
    images = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='Bilder',
        help_text='Ladda upp bilder av yxan (drag & drop stöds)'
    )

    # Kontaktrelaterade fält
    contact_search = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sök efter befintlig kontakt eller ange ny...'
        }),
        label='Försäljare',
        help_text='Sök efter befintlig kontakt eller ange namn för ny kontakt'
    )
    
    contact_name = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ange försäljarens namn'
        }),
        label='Namn (ny kontakt)',
        help_text='Namn på försäljaren (t.ex. från Tradera, eBay)'
    )
    
    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'namn@example.com'
        }),
        label='E-post (ny kontakt)',
        help_text='Försäljarens e-postadress'
    )
    
    contact_phone = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '070-123 45 67'
        }),
        label='Telefon (ny kontakt)',
        help_text='Försäljarens telefonnummer'
    )
    
    contact_alias = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Användarnamn på Tradera/eBay'
        }),
        label='Alias (ny kontakt)',
        help_text='Användarnamn på plattformen (t.ex. Tradera, eBay)'
    )
    
    contact_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Lägg till kommentar om försäljaren...'
        }),
        label='Kommentar (ny kontakt)',
        help_text='Kommentar om försäljaren'
    )
    
    is_naj_member = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='NAJ-medlem (ny kontakt)',
        help_text='Är försäljaren medlem i Nordic Axe Junkies?'
    )
    
    # Transaktionsrelaterade fält
    transaction_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        }),
        label='Pris (kr)',
        help_text='Pris för yxan (negativt för köp, positivt för sälj)'
    )
    
    transaction_shipping = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        }),
        label='Fraktkostnad (kr)',
        help_text='Fraktkostnad (negativt för köp, positivt för sälj)'
    )
    
    transaction_date = forms.DateField(
        required=False,
        initial=timezone.now().date,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Transaktionsdatum',
        help_text='Datum för transaktionen'
    )
    
    transaction_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Lägg till kommentar om transaktionen...'
        }),
        label='Transaktionskommentar',
        help_text='Kommentar om transaktionen (t.ex. betalningsmetod)'
    )
    
    # Plattformsrelaterade fält
    platform_search = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sök efter befintlig plattform eller ange ny...'
        }),
        label='Plattform',
        help_text='Börja skriva för att söka efter befintlig plattform eller skapa ny'
    )

    class Meta:
        model = Axe
        fields = ['manufacturer', 'model', 'comment', 'status']
        labels = {
            'manufacturer': 'Tillverkare',
            'model': 'Modell',
            'comment': 'Kommentar',
            'status': 'Status',
        }
        widgets = {
            'manufacturer': forms.Select(attrs={'class': 'form-select'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ange modellnamn'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Lägg till kommentar om yxan...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        } 