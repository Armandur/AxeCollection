# Kortbaserad stämpelvisning - Ny funktionalitet

## Översikt

Stämpelvisningen på yxdetaljsidan har omarbetats från en enkel listvy till en visuell kortbaserad layout som visar stämplar med bilder och förbättrad information. Den nya designen ger bättre översikt och möjlighet att redigera befintliga stämplar.

## Ny funktionalitet

### 1. Kortbaserad layout
- **Plats**: Yxdetaljsidan (`/yxor/NN`) i "Stämplar"-sektionen
- **Ändring**: Ersatt tabellvy med Bootstrap-kort
- **Layout**: Responsiv grid med `col-md-6 col-lg-4 mb-3`
- **Visuell design**: Hover-effekter och moderna kort

### 2. Stämpelkort-innehåll
Varje stämpelkort visar:
- **Bild**: Stämpelbild från `stamp.images` eller `axe_image_marks` med koordinater
- **Stämpelnamn**: Tydlig rubrik med stämpelns namn
- **Tillverkare**: Tillverkarens namn
- **Typ**: Stämpeltyp (text, symbol, text_symbol, etikett)
- **Osäkerhetsnivå**: Badge som visar "Preliminär" (tidigare "Tentativ")
- **Position**: Var på yxan stämpeln finns
- **Kommentar**: Användarkommentar om stämpeln
- **Åtgärdsknappar**: "Redigera" och "Ta bort"

### 3. Bildhantering
- **Prioritering**: Först `stamp.images`, sedan `axe_image_marks` med koordinater
- **Fallback**: Stämpelikon om ingen bild finns
- **Koordinatvisning**: Visar beskärningsområde från AxeImageStamp
- **Hover-effekt**: Bilden förstoras vid hover

### 4. Redigeringsfunktionalitet
- **Redigera-knapp**: Länk till `/yxor/NN/stampel/NN/redigera/`
- **Integrerad redigering**: Samma tvåstegs flöde som för nya stämplar
- **Bildmarkering**: Möjlighet att ändra bildmarkering på befintliga stämplar

## Teknisk implementation

### View-uppdateringar
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

### Template-struktur
```html
<!-- axe_detail.html - Stämplarsektion -->
<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Stämplar</h5>
        <a href="{% url 'add_axe_stamp' axe.id %}" class="btn btn-primary btn-sm">
            <i class="fas fa-plus"></i> Ange stämpel
        </a>
    </div>
    <div class="card-body">
        {% if axe.stamps.all %}
            <div class="row">
                {% for axe_stamp in axe.stamps.all %}
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card stamp-card h-100">
                            <div class="stamp-image-container">
                                {% if axe_stamp.stamp.images.first %}
                                    <img src="{{ axe_stamp.stamp.images.first.image.url }}" 
                                         class="card-img-top" alt="{{ axe_stamp.stamp.name }}">
                                {% elif axe_stamp.stamp.axe_image_marks.first %}
                                    <!-- Visa beskärningsområde från AxeImageStamp -->
                                    <div class="stamp-crop-area">
                                        <img src="{{ axe_stamp.stamp.axe_image_marks.first.axe_image.image.url }}" 
                                             class="card-img-top" alt="{{ axe_stamp.stamp.name }}">
                                    </div>
                                {% else %}
                                    <div class="stamp-placeholder">
                                        <i class="fas fa-stamp fa-3x text-muted"></i>
                                    </div>
                                {% endif %}
                            </div>
                            <div class="card-body">
                                <h6 class="card-title">{{ axe_stamp.stamp.name }}</h6>
                                <p class="card-text">
                                    <small class="text-muted">
                                        {{ axe_stamp.stamp.manufacturer.name|default:"Okänd tillverkare" }}
                                    </small>
                                </p>
                                <p class="card-text">
                                    <span class="badge bg-secondary">{{ axe_stamp.stamp.get_stamp_type_display }}</span>
                                    {% if axe_stamp.uncertainty_level == 'tentative' %}
                                        <span class="badge bg-warning">Preliminär</span>
                                    {% endif %}
                                </p>
                                {% if axe_stamp.position %}
                                    <p class="card-text">
                                        <small class="text-muted">Position: {{ axe_stamp.position }}</small>
                                    </p>
                                {% endif %}
                                {% if axe_stamp.comment %}
                                    <p class="card-text">{{ axe_stamp.comment }}</p>
                                {% endif %}
                            </div>
                            <div class="card-footer">
                                <div class="btn-group btn-group-sm w-100">
                                    <a href="{% url 'edit_axe_stamp' axe.id axe_stamp.id %}" 
                                       class="btn btn-outline-primary">
                                        <i class="fas fa-edit"></i> Redigera
                                    </a>
                                    <button type="button" class="btn btn-outline-danger" 
                                            onclick="confirmDeleteStamp({{ axe_stamp.id }})">
                                        <i class="fas fa-trash"></i> Ta bort
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="text-center py-4">
                <i class="fas fa-stamp fa-3x text-muted mb-3"></i>
                <p class="text-muted">Inga stämplar definierade</p>
                <a href="{% url 'add_axe_stamp' axe.id %}" class="btn btn-primary">
                    <i class="fas fa-plus"></i> Lägg till stämpel
                </a>
            </div>
        {% endif %}
    </div>
</div>
```

### CSS-styling
```css
/* axe_detail.html - Lagt till CSS */
<style>
.stamp-card {
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    border: 1px solid #dee2e6;
}

.stamp-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.stamp-image-container {
    position: relative;
    overflow: hidden;
    height: 200px;
}

.stamp-image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.2s ease-in-out;
}

.stamp-image-container:hover img {
    transform: scale(1.05);
}

.stamp-placeholder {
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f8f9fa;
}

.stamp-crop-area {
    position: relative;
    overflow: hidden;
}

.stamp-crop-area::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.1);
    pointer-events: none;
}
</style>
```

## Redigeringsfunktionalitet

### Edit view
```python
@login_required
def edit_axe_stamp(request, axe_id, axe_stamp_id):
    """Redigera en befintlig yxstämpel med bildmarkering"""
    
    axe = get_object_or_404(Axe, id=axe_id)
    axe_stamp = get_object_or_404(AxeStamp, id=axe_stamp_id, axe=axe)
    
    # Hämta befintliga bilder för yxan
    existing_images = axe.images.all().order_by('order')
    
    # Hämta befintlig AxeImageStamp för denna stämpel
    existing_axe_image_stamp = AxeImageStamp.objects.filter(
        stamp=axe_stamp.stamp,
        axe_image__axe=axe
    ).first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'select_image':
            # Steg 1: Välj bild
            selected_image_id = request.POST.get('selected_image_id')
            if selected_image_id:
                selected_image = get_object_or_404(AxeImage, id=selected_image_id, axe=axe)
                available_stamps = Stamp.objects.all().order_by('name')
                
                context = {
                    'axe': axe,
                    'axe_stamp': axe_stamp,
                    'selected_image': selected_image,
                    'available_stamps': available_stamps,
                    'existing_axe_image_stamp': existing_axe_image_stamp,
                    'title': f'Redigera stämpel - {axe.display_id}',
                }
                return render(request, 'axes/axe_stamp_edit.html', context)
        
        elif action == 'save_stamp':
            # Steg 2: Spara stämpel med bildmarkering
            form = AxeStampForm(request.POST, instance=axe_stamp)
            if form.is_valid():
                # Spara AxeStamp
                axe_stamp = form.save()
                
                # Hantera AxeImageStamp
                selected_image_id = request.POST.get('selected_image_id')
                if selected_image_id:
                    selected_image = get_object_or_404(AxeImage, id=selected_image_id, axe=axe)
                    
                    # Ta bort befintlig AxeImageStamp för samma stämpel på samma bild
                    AxeImageStamp.objects.filter(
                        stamp=axe_stamp.stamp,
                        axe_image=selected_image
                    ).delete()
                    
                    # Skapa ny AxeImageStamp
                    x_coord = request.POST.get('x_coordinate')
                    y_coord = request.POST.get('y_coordinate')
                    width = request.POST.get('width')
                    height = request.POST.get('height')
                    
                    if x_coord and y_coord and width and height:
                        AxeImageStamp.objects.create(
                            axe_image=selected_image,
                            stamp=axe_stamp.stamp,
                            x_coordinate=int(x_coord),
                            y_coordinate=int(y_coord),
                            width=int(width),
                            height=int(height),
                            comment=request.POST.get('image_comment', '')
                        )
                
                messages.success(request, f'Stämpel "{axe_stamp.stamp.name}" uppdaterades.')
                return redirect('axe_detail', pk=axe.id)
    
    # GET request - visa redigeringsformulär
    form = AxeStampForm(instance=axe_stamp)
    
    context = {
        'axe': axe,
        'axe_stamp': axe_stamp,
        'existing_images': existing_images,
        'existing_axe_image_stamp': existing_axe_image_stamp,
        'form': form,
        'title': f'Redigera stämpel - {axe.display_id}',
    }
    
    return render(request, 'axes/axe_stamp_edit.html', context)
```

### URL-mönster
```python
# urls.py
path("yxor/<int:axe_id>/stampel/<int:axe_stamp_id>/redigera/", 
     views_stamp.edit_axe_stamp, name="edit_axe_stamp"),
```

## Fördelar med den nya designen

1. **Visuell översikt**: Stämplar visas med bilder istället för bara text
2. **Bättre information**: All relevant information synlig på varje kort
3. **Redigeringsmöjlighet**: Enkel åtkomst till redigering av befintliga stämplar
4. **Responsiv design**: Kort anpassar sig efter skärmstorlek
5. **Hover-effekter**: Interaktiva element som förbättrar användarupplevelsen
6. **Konsistent design**: Samma stil som resten av applikationen

## Relaterade ändringar

### Model-uppdateringar
- **AxeStamp**: `unique_together` constraint borttagen för att tillåta flera instanser av samma stämpel
- **Uncertainty levels**: "Tentativ" bytt till "Preliminär"

### Template-uppdateringar
- **axe_detail.html**: Komplett omarbetning av stämpelsektionen
- **axe_stamp_edit.html**: Ny template för redigering av stämplar
- **Responsiv grid**: Bootstrap-klasser för responsiv layout

### JavaScript
- **Bildmarkering**: Samma JavaScript-funktionalitet som för nya stämplar
- **Bekräftelsedialoger**: För borttagning av stämplar

## Status
- ✅ Implementerad och testad
- ✅ Responsiv design fungerar
- ✅ Hover-effekter implementerade
- ✅ Redigeringsfunktionalitet fungerar
- ✅ Bildhantering med fallback
- ✅ Prioriterade stämplar från tillverkare
- ✅ Flera instanser av samma stämpel tillåtna 