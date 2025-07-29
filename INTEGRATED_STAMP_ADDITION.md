# Integrerad stämpeltillägg - Ny funktionalitet

## Översikt

En ny integrerad stämpeltillägg-funktionalitet har implementerats som ersätter den tidigare ologiska flödet för att lägga till stämplar på yxor. Den nya funktionen ger ett enkelt, tvåstegs flöde som kombinerar bildval, stämpelmarkering och stämpeldefinition i ett enda formulär.

## Ny funktionalitet

### 1. Förenklad "Lägg till stämpel" knapp
- **Plats**: Yxdetaljsidan (`/yxor/NN`)
- **Ändring**: Ersatt dropdown-meny med en enkel "+" knapp
- **Text**: "Ange stämpel"
- **Funktion**: Dirigerar till det nya integrerade formuläret

### 2. Integrerat tvåstegs formulär
- **URL**: `/yxor/NN/stampel/lagg-till/`
- **Steg 1**: Bildval
  - Visar alla befintliga bilder för yxan som kort
  - Om inga bilder finns: Varning och omdirigering till `/redigera`
  - "Välj denna bild" knapp för varje bild
- **Steg 2**: Stämpelmarkering och definition
  - Vald bild visas större med interaktiv markering
  - JavaScript-driven beskärning för att markera stämpelområde
  - Formulär för stämpeldetaljer (stämpeltyp, position, osäkerhet, kommentar)

### 3. Bildmarkering med JavaScript
- **Interaktiv markering**: Klicka och dra för att markera stämpelområde
- **Koordinater**: Automatisk sparning av x, y, width, height
- **Rensa markering**: Knapp för att rensa markering
- **Visuell feedback**: Tydlig overlay som visar markerat område

### 4. Stämpeldetaljer
- **Stämpelval**: Dropdown med prioriterade stämplar från yxans tillverkare
- **Position**: Textfält för var på yxan stämpeln finns
- **Osäkerhetsnivå**: "Säker", "Osäker", "Preliminär" (tidigare "Tentativ")
- **Kommentar**: Textarea för användarkommentarer
- **Bildkommentar**: Separat kommentar för bildmarkeringen

## Teknisk implementation

### Views
```python
@login_required
def add_axe_stamp(request, axe_id):
    """Lägg till stämpel på yxa - integrerat flöde med bildval och markering"""
    
    axe = get_object_or_404(Axe, id=axe_id)
    existing_images = axe.images.all().order_by('order')
    
    if not existing_images.exists():
        messages.warning(request, 'Yxan har inga bilder. Lägg till bilder först via redigera.')
        return redirect('axe_edit', pk=axe.id)
    
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
                    'selected_image': selected_image,
                    'available_stamps': available_stamps,
                    'title': f'Lägg till stämpel - {axe.display_id}',
                }
                return render(request, 'axes/axe_stamp_form.html', context)
        
        elif action == 'save_stamp':
            # Steg 2: Spara stämpel med bildmarkering
            form = AxeStampForm(request.POST)
            if form.is_valid():
                # Skapa AxeStamp
                axe_stamp = form.save(commit=False)
                axe_stamp.axe = axe
                axe_stamp.save()
                
                # Hantera AxeImageStamp
                selected_image_id = request.POST.get('selected_image_id')
                if selected_image_id:
                    selected_image = get_object_or_404(AxeImage, id=selected_image_id, axe=axe)
                    
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
                
                messages.success(request, f'Stämpel "{axe_stamp.stamp.name}" lades till.')
                return redirect('axe_detail', pk=axe.id)
    
    # GET request - visa bildval
    context = {
        'axe': axe,
        'existing_images': existing_images,
        'title': f'Lägg till stämpel - {axe.display_id}',
    }
    return render(request, 'axes/axe_stamp_form.html', context)
```

### Template-struktur
```html
<!-- axe_stamp_form.html -->
{% if selected_image %}
    <!-- Steg 2: Stämpelmarkering och definition -->
    <div class="image-marking-section">
        <img src="{{ selected_image.image.url }}" id="stamp-image" />
        <div id="marking-overlay"></div>
        <input type="hidden" name="x_coordinate" id="x_coordinate" />
        <input type="hidden" name="y_coordinate" id="y_coordinate" />
        <input type="hidden" name="width" id="width" />
        <input type="hidden" name="height" id="height" />
        <!-- Stämpelformulär -->
    </div>
{% else %}
    <!-- Steg 1: Bildval -->
    <div class="image-selection-grid">
        {% for image in existing_images %}
            <div class="image-card">
                <img src="{{ image.image.url }}" />
                <form method="post">
                    {% csrf_token %}
                    <input type="hidden" name="action" value="select_image" />
                    <input type="hidden" name="selected_image_id" value="{{ image.id }}" />
                    <button type="submit">Välj denna bild</button>
                </form>
            </div>
        {% endfor %}
    </div>
{% endif %}
```

### JavaScript för bildmarkering
```javascript
// Bildmarkering med musinteraktion
let isMarking = false;
let startX, startY;

document.getElementById('stamp-image').addEventListener('mousedown', function(e) {
    isMarking = true;
    const rect = this.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
    
    // Skapa markering
    const overlay = document.getElementById('marking-overlay');
    overlay.style.left = startX + 'px';
    overlay.style.top = startY + 'px';
    overlay.style.width = '0px';
    overlay.style.height = '0px';
    overlay.style.display = 'block';
});

document.addEventListener('mousemove', function(e) {
    if (!isMarking) return;
    
    const rect = document.getElementById('stamp-image').getBoundingClientRect();
    const currentX = e.clientX - rect.left;
    const currentY = e.clientY - rect.top;
    
    const overlay = document.getElementById('marking-overlay');
    const width = Math.abs(currentX - startX);
    const height = Math.abs(currentY - startY);
    
    overlay.style.left = Math.min(startX, currentX) + 'px';
    overlay.style.top = Math.min(startY, currentY) + 'px';
    overlay.style.width = width + 'px';
    overlay.style.height = height + 'px';
    
    // Uppdatera hidden inputs
    document.getElementById('x_coordinate').value = Math.min(startX, currentX);
    document.getElementById('y_coordinate').value = Math.min(startY, currentY);
    document.getElementById('width').value = width;
    document.getElementById('height').value = height;
});

document.addEventListener('mouseup', function() {
    isMarking = false;
});
```

## Fördelar med den nya funktionen

1. **Logiskt flöde**: Bildval → Markering → Definition i ett enda formulär
2. **Visuell feedback**: Tydlig markering av stämpelområden
3. **Förbättrad UX**: Inga separata sidor eller ologiska hopp
4. **Felhantering**: Automatisk omdirigering om inga bilder finns
5. **Flexibilitet**: Möjlighet att rensa markering och börja om
6. **Konsistens**: Samma flöde för alla stämpeltillägg

## Relaterade ändringar

### Model-uppdateringar
- **AxeStamp**: Lagt till `uncertainty_level` med "Preliminär" istället för "Tentativ"
- **AxeImageStamp**: Används för att spara bildmarkeringar med koordinater

### Form-uppdateringar
- **AxeStampForm**: Förbättrad med prioriterade stämplar från tillverkare
- **clean_stamp metod**: Borttagen för att fixa TypeError (Django hanterar konvertering automatiskt)

### Template-uppdateringar
- **axe_detail.html**: Förenklad "Lägg till stämpel" knapp
- **axe_stamp_form.html**: Nytt integrerat tvåstegs formulär
- **axe_stamp_edit.html**: Liknande funktionalitet för redigering

## Status
- ✅ Implementerad och testad
- ✅ Felhantering för saknade bilder
- ✅ JavaScript-bildmarkering fungerar
- ✅ Formulärvalidering fungerar
- ✅ Responsiv design
- ✅ Prioriterade stämplar från tillverkare 