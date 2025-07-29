# Model-uppdateringar och felkorrigeringar

## Översikt

Flera viktiga uppdateringar och felkorrigeringar har gjorts i modellerna och formulären för att förbättra funktionaliteten och lösa tekniska problem.

## Model-uppdateringar

### 1. AxeStamp - Borttagning av unique_together constraint
- **Problem**: Kunde inte lägga till flera instanser av samma stämpel på samma yxa
- **Lösning**: Borttagen `unique_together = ["axe", "stamp"]` constraint
- **Anledning**: Dubbelstämpling finns och ska tillåtas
- **Migration**: `0038_alter_axestamp_unique_together_and_more.py`

```python
# axes/models.py - AxeStamp model
class AxeStamp(models.Model):
    axe = models.ForeignKey(Axe, on_delete=models.CASCADE, related_name='stamps')
    stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE, related_name='axes')
    comment = models.TextField(blank=True)
    position = models.CharField(max_length=100, blank=True)
    uncertainty_level = models.CharField(
        max_length=20, 
        choices=UNCERTAINTY_CHOICES, 
        default='certain'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Borttagen: unique_together = ["axe", "stamp"]
    
    class Meta:
        ordering = ['stamp__name']
```

### 2. Uncertainty levels - "Tentativ" bytt till "Preliminär"
- **Problem**: Terminologi "Tentativ" var otydlig
- **Lösning**: Bytte till "Preliminär" för bättre förståelse
- **Påverkan**: Alla ställen där uncertainty levels visas

```python
# axes/models.py - UNCERTAINTY_CHOICES
UNCERTAINTY_CHOICES = [
    ("certain", "Säker"),
    ("uncertain", "Osäker"),
    ("tentative", "Preliminär"),  # Ändrat från "Tentativ"
]
```

### 3. AxeImageStamp - Förbättrad bildmarkering
- **Funktionalitet**: Sparar koordinater för stämpelområden på bilder
- **Fält**: x_coordinate, y_coordinate, width, height, comment
- **Användning**: För att markera exakt var stämpeln finns på bilden

```python
# axes/models.py - AxeImageStamp model
class AxeImageStamp(models.Model):
    axe_image = models.ForeignKey(AxeImage, on_delete=models.CASCADE, related_name='stamp_marks')
    stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE, related_name='axe_image_marks')
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ["axe_image", "stamp"]
        ordering = ['created_at']
```

## Form-uppdateringar

### 1. AxeStampForm - Borttagning av clean_stamp metod
- **Problem**: TypeError när formuläret skickades in
- **Felmeddelande**: `TypeError: Field 'id' expected a number but got <Stamp: HB 1884-1930>`
- **Orsak**: Django's ModelChoiceField konverterar automatiskt ID till objekt
- **Lösning**: Borttagen `clean_stamp` metod som försökte konvertera igen

```python
# axes/forms.py - AxeStampForm (före)
def clean_stamp(self):
    """Konvertera stamp ID till Stamp-objekt"""
    stamp_id = self.cleaned_data.get('stamp')
    if stamp_id:
        try:
            from .models import Stamp
            return Stamp.objects.get(id=stamp_id)  # Fel: försöker konvertera objekt till ID igen
        except Stamp.DoesNotExist:
            raise forms.ValidationError("Vald stämpel finns inte.")
    else:
        raise forms.ValidationError("Stämpel måste väljas.")

# axes/forms.py - AxeStampForm (efter)
# Borttagen clean_stamp metod - Django hanterar konvertering automatiskt
```

### 2. Förbättrad prioritering av stämplar
- **Funktionalitet**: Stämplar från yxans tillverkare visas först
- **Implementation**: Dynamisk skapning av choices i `__init__`
- **Separatorer**: Tydliga avdelare mellan prioriterade och andra stämplar

```python
# axes/forms.py - AxeStampForm.__init__
def __init__(self, *args, **kwargs):
    axe = kwargs.pop('axe', None)
    super().__init__(*args, **kwargs)
    
    if axe and axe.manufacturer:
        # Stämplar från yxans tillverkare (prioriterade)
        primary_stamps = Stamp.objects.filter(manufacturer=axe.manufacturer).order_by('name')
        
        # Alla andra stämplar (sekundära)
        other_stamps = Stamp.objects.exclude(manufacturer=axe.manufacturer).order_by('name')
        
        # Skapa choices med prioriterade stämplar först
        choices = [('', 'Välj stämpel...')]
        
        # Lägg till prioriterade stämplar med separator
        if primary_stamps.exists():
            choices.append(('', f'--- Stämplar från {axe.manufacturer.name} ---'))
            for stamp in primary_stamps:
                choices.append((stamp.id, f"{stamp.name} ({stamp.get_stamp_type_display()})"))
        
        # Lägg till separator för andra stämplar
        if other_stamps.exists():
            choices.append(('', '--- Andra stämplar ---'))
            for stamp in other_stamps:
                choices.append((stamp.id, f"{stamp.name} - {stamp.manufacturer.name if stamp.manufacturer else 'Okänd'} ({stamp.get_stamp_type_display()})"))
        
        self.fields['stamp'] = forms.ChoiceField(
            choices=choices,
            required=True,
            widget=forms.Select(attrs={'class': 'form-control'}),
            label='Stämpel',
            help_text=f'Prioriterade stämplar från {axe.manufacturer.name} visas först'
        )
```

## View-uppdateringar

### 1. Prefetch-optimering för axe_detail
- **Problem**: N+1 queries när stämpelbilder laddades
- **Lösning**: Lagt till prefetch_related för effektiv dataladdning
- **Påverkan**: Förbättrad prestanda på yxdetaljsidan

```python
# views_axe.py - axe_detail view
def axe_detail(request, pk):
    axe = get_object_or_404(
        Axe.objects.prefetch_related(
            "stamps__stamp__images",
            "stamps__stamp__axe_image_marks__axe_image"
        ),
        pk=pk
    )
    # ... resten av view-koden
```

### 2. Integrerad stämpeltillägg med felhantering
- **Funktionalitet**: Kontrollerar om yxan har bilder innan stämpeltillägg
- **Felhantering**: Omdirigerar till redigera om inga bilder finns
- **Användarupplevelse**: Tydliga meddelanden om vad som behöver göras

```python
# views_stamp.py - add_axe_stamp view
@login_required
def add_axe_stamp(request, axe_id):
    axe = get_object_or_404(Axe, id=axe_id)
    existing_images = axe.images.all().order_by('order')
    
    if not existing_images.exists():
        messages.warning(request, 'Yxan har inga bilder. Lägg till bilder först via redigera.')
        return redirect('axe_edit', pk=axe.id)
    
    # ... resten av view-koden
```

## Template-uppdateringar

### 1. Förenklad "Lägg till stämpel" knapp
- **Ändring**: Ersatt dropdown-meny med enkel knapp
- **Design**: Konsistent med resten av gränssnittet
- **Funktionalitet**: Dirigerar till integrerat formulär

```html
<!-- axe_detail.html - Före -->
<div class="dropdown">
    <button class="btn btn-primary dropdown-toggle" type="button" data-bs-toggle="dropdown">
        Lägg till stämpel
    </button>
    <ul class="dropdown-menu">
        <li><a class="dropdown-item" href="...">Markera befintlig stämpel</a></li>
        <li><a class="dropdown-item" href="...">Koppla stämpel</a></li>
    </ul>
</div>

<!-- axe_detail.html - Efter -->
<a href="{% url 'add_axe_stamp' axe.id %}" class="btn btn-primary btn-sm">
    <i class="fas fa-plus"></i> Ange stämpel
</a>
```

### 2. Kortbaserad stämpelvisning
- **Layout**: Bootstrap-kort istället för tabell
- **Responsiv**: Anpassar sig efter skärmstorlek
- **Interaktiv**: Hover-effekter och åtgärdsknappar

```html
<!-- axe_detail.html - Stämpelkort -->
<div class="col-md-6 col-lg-4 mb-3">
    <div class="card stamp-card h-100">
        <div class="stamp-image-container">
            <!-- Bildhantering med fallback -->
        </div>
        <div class="card-body">
            <!-- Stämpelinformation -->
        </div>
        <div class="card-footer">
            <!-- Åtgärdsknappar -->
        </div>
    </div>
</div>
```

## Felkorrigeringar

### 1. TypeError i AxeStampForm
- **Problem**: `TypeError: Field 'id' expected a number but got <Stamp: HB 1884-1930>`
- **Orsak**: `clean_stamp` metod försökte konvertera redan konverterat objekt
- **Lösning**: Borttagen `clean_stamp` metod
- **Status**: ✅ Löst

### 2. RuntimeWarning vid app-initialisering
- **Problem**: `RuntimeWarning: Accessing the database during app initialization`
- **Orsak**: Queries körs under app-initialisering
- **Påverkan**: Varning men inget funktionellt problem
- **Status**: ⚠️ Varning kvarstår men påverkar inte funktionalitet

### 3. Unique constraint för AxeStamp
- **Problem**: Kunde inte lägga till flera instanser av samma stämpel
- **Lösning**: Borttagen `unique_together` constraint
- **Status**: ✅ Löst

## Migrationer

### 1. AxeStamp unique_together borttagning
```python
# migrations/0038_alter_axestamp_unique_together_and_more.py
class Migration(migrations.Migration):
    dependencies = [
        ('axes', '0037_...'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='axestamp',
            unique_together=set(),  # Borttagen constraint
        ),
        migrations.AlterField(
            model_name='axestamp',
            name='uncertainty_level',
            field=models.CharField(
                choices=[
                    ('certain', 'Säker'),
                    ('uncertain', 'Osäker'),
                    ('tentative', 'Preliminär')  # Ändrat från "Tentativ"
                ],
                default='certain',
                max_length=20
            ),
        ),
    ]
```

## Fördelar med uppdateringarna

1. **Förbättrad användarupplevelse**: Logiskt flöde för stämpeltillägg
2. **Teknisk stabilitet**: Löst TypeError-problem
3. **Flexibilitet**: Tillåter flera instanser av samma stämpel
4. **Prestanda**: Optimerad dataladdning med prefetch
5. **Tydlighet**: Bättre terminologi ("Preliminär" istället för "Tentativ")
6. **Visuell förbättring**: Kortbaserad layout istället för tabell

## Status
- ✅ Alla felkorrigeringar implementerade
- ✅ Model-uppdateringar testade
- ✅ Form-uppdateringar fungerar
- ✅ Template-uppdateringar implementerade
- ✅ Migrationer skapade och applicerade
- ✅ Prestanda-optimeringar implementerade 