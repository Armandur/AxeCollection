# Stämpelregister för AxeCollection

## Översikt

Stämpelregister-funktionen är en omfattande lösning för att kategorisera, dokumentera och söka bland stämplar som finns på yxor i samlingen. Funktionen möjliggör systematisk hantering av textbaserade och visuella stämplar med sökbarhet och kategorisering.

## Bakgrund

Många yxor har stämplar som innehåller viktig information om tillverkare, kvalitet, land, år, etc. Dessa stämplar kan vara svåra att läsa eller tolka, och det finns behov av ett systematiskt sätt att dokumentera och söka bland dem.

## Funktioner

### 1. Datamodeller

#### Stamp (Stämpel)
- **Namn**: Unikt namn för stämpeln
- **Beskrivning**: Detaljerad beskrivning av stämpeln
- **Tillverkare**: Koppling till tillverkare (kan vara okänd)
- **Typ**: text/symbol/text_symbol/etikett
- **Status**: känd/okänd
- **Användningsår**: Tidsperiod när stämpeln användes (exakt år, årtionde, eller osäker)
- **Årtalsosäkerhet**: Flagga för osäker årtalsinformation (t.ex. "cirka")
- **Variant av**: Koppling till huvudstämpel om detta är en variant
- **Osäkerhet**: Flagga för stämplar med osäker identifiering
- **Källa**: Källkategori för stämpeln (egen samling, extern, etc.)
- **Källhänvisning**: Specifik hänvisning till källan (t.ex. "eBay-auktion 2023")

#### StampTranscription (Stämpeltranskribering)
- **Text**: Textbaserad beskrivning av stämpeln (t.ex. 'GRÄNSFORS', 'MADE IN SWEDEN', 'HULTS BRUK')
- **Symboler**: Koppling till fördefinierade eller användardefinierade symboler (t.ex. Krona, Kanon, Stjärna)
- **Sökbarhet**: Fulltextsökning i transkriberingar och symboler
- **Kvalitet**: Bedömning av hur säker transkriberingen är
- **Obligatorisk**: Transkribering krävs för alla stämplar
- **Komplett transkribering**: Kombinerar text och symboler för fullständig beskrivning

#### StampSymbol (Stämpelsymbol)
- **Namn**: Unikt namn för symbolen
- **Typ**: Kategorisering av symboltyp (krona, kanon, stjärna, kors, sköld, ankare, blomma, löv, övrigt)
- **Beskrivning**: Detaljerad beskrivning av symbolen
- **Fördefinierad**: Flagga för systemdefinierade vs användardefinierade symboler
- **Visningsnamn**: Automatisk formatering med symboltyp och namn

#### StampTag (Stämpeltagg)
- **Namn**: Kategorinamn (t.ex. 'tillverkarnamn', 'land', 'kvalitet', 'år', 'serienummer')
- **Beskrivning**: Förklaring av vad taggen representerar
- **Färg**: Visuell identifiering av taggtypen

#### StampImage (Stämpelbild)
- **Bild**: Fysisk bild av stämpeln (vald från yxans befintliga bilder)
- **Kvalitet**: Bedömning av bildkvalitet för identifiering
- **Markering**: Möjlighet att markera vilka av yxans bilder som visar stämplar

#### AxeStamp (Yxstämpel)
- **Koppling**: Länk mellan yxa och stämpel
- **Kommentar**: Användarkommentar om stämpeln (kvalitet, synlighet, etc.)
- **Position**: Var på yxan stämpeln finns (valfritt)

### 2. Mottagningsflöde-integration

#### Stämpeldefinition i mottagningsflödet
- **Bildval**: Markera vilka bilder som visar stämplar (befintliga eller nya från mottagningsflödet)
- **Transkribering**: Obligatorisk transkribering av varje stämpel
- **Tillverkarkoppling**: Automatisk koppling till vald tillverkare (eller okänd)
- **Flera stämplar**: Stöd för att definiera flera stämplar per yxa
- **Flexibilitet**: Möjlighet att hoppa över stämpeldefinition och återkomma senare
- **Fältarbete**: Enkel markering av stämpelbilder för senare definition
- **Realtidsfotografering**: Möjlighet att fota stämplar direkt i mottagningsflödet
- **Befintliga stämplar**: Visa alla stämplar från vald tillverkare för koppling
- **Sökning**: Sök bland befintliga stämplar när tillverkare är okänd
- **Varianter**: Möjlighet att markera stämplar som varianter av befintliga
- **Osäkerhetskoppling**: Tillfälliga kopplingar för stämplar med osäker identifiering
- **Externa stämplar**: Föreslå externa stämplar baserat på transkribering/tillverkare
- **Bildtillägg**: Lägg till nya bilder till befintliga stämplar från externa källor

### 3. Användargränssnitt

#### Stämpelregister-vy
- **Sökfunktion**: Fulltextsökning i stämpelnamn och transkriberingar
- **Filtrering**: Filtrera på tillverkare, typ, taggar, källa
- **Gruppering**: Gruppera okända stämplar separat
- **Sortering**: Sortera på namn, tillverkare, antal kopplade yxor, årtal
- **Årtalsfiltrering**: Filtrera stämplar på tidsperiod
- **Källmarkering**: Visuell markering av stämplar från egen samling vs externa

#### Yxor utan stämplar
- **Lista yxor**: Visa alla yxor som inte har stämplar definierade
- **Prioritering**: Sortera efter tillverkare, datum tillagd, eller användardefinierad prioritet
- **Bildstatus**: Markera yxor som har bilder men inte stämplar definierade
- **Snabbkoppling**: Direktlänk till yxdetaljsida för stämpeldefinition
- **Bulk-operationer**: Markera flera yxor för stämpeldefinition
- **Förloppsindikator**: Visa hur många yxor som saknar stämplar vs totalt antal

#### Stämpeldetalj-vy
- **Bildgalleri**: Visa alla bilder av stämpeln
- **Transkriberingar**: Lista alla textbaserade beskrivningar
- **Taggar**: Visa kategorisering av stämpeln
- **Kopplade yxor**: Lista alla yxor som har denna stämpel
- **Statistik**: Antal kopplade yxor, tillverkare, etc.

#### Yxdetaljsida-integration
- **Stämpelvisning**: Visa alla stämplar på yxan
- **Koppling/avkoppling**: Möjlighet att koppla/avkoppla stämplar
- **Kommentarer**: Lägg till användarkommentarer per stämpel
- **Snabbidentifiering**: Förslag på stämplar baserat på tillverkare
- **Tillverkningsår**: Visa tillverkningsår baserat på stämpelns årtalsinformation
- **Årtalsosäkerhet**: Visa osäkerhetsfaktor för tillverkningsår

### 4. Sökfunktionalitet

#### AJAX-sökning
- **Live-sökning**: Realtidssökning med debouncing (300ms)
- **Förbättrad sökning**: Sök i namn, beskrivning, transkriberingar och tillverkare
- **Filtrering**: Kombinera sökning med tillverkare och stämpeltyp
- **Resultatvisning**: Dropdown med detaljerad information om varje stämpel
- **Formulärintegration**: AJAX-sökning i add_axe_stamp formuläret
- **Prioritering**: Stämplar från yxans tillverkare visas först
- **Responsiv design**: Dropdown som anpassar sig efter innehåll

#### Textbaserad sökning
- **Transkriberingar**: Sök i textbeskrivningar av stämplar
- **Taggar**: Sök på kategorier och taggar
- **Tillverkare**: Filtrera på tillverkare
- **Fuzzy search**: Tolerans för stavfel och variationer

#### Visuell sökning (framtida funktion)
- **OCR**: Automatisk textigenkänning från stämpelbilder
- **Mönsterigenkänning**: Identifiera vanliga stämpelmönster

### 5. Admin-funktioner

#### Stämpelhantering
- **Skapa/redigera**: Hantera stämplar och deras egenskaper
- **Transkriberingar**: Lägg till och redigera textbeskrivningar
- **Taggar**: Hantera kategorisering och taggar
- **Bilder**: Ladda upp och hantera stämpelbilder

#### Kopplingar
- **Yxstämplar**: Hantera kopplingar mellan yxor och stämplar
- **Bulk-operationer**: Massredigering av kopplingar
- **Validering**: Kontrollera konsistens i data

#### Okända tillverkare
- **Stämpelgruppering**: Gruppera stämplar från okända tillverkare
- **Identifiering**: Möjlighet att identifiera gemensamma stämplar mellan yxor
- **Tillverkarskapning**: Skapa nya tillverkare baserat på stämpelanalys
- **Osäkerhetskoppling**: Koppling mellan stämpelgrupper med osäker identifiering

#### Externa stämplar
- **Källkategorier**: Hantera olika typer av externa källor (eBay, museum, etc.)
- **Källhänvisning**: Spåra specifika källor för externa stämplar
- **Dupliceringshantering**: Föreslå befintliga stämplar när nya yxor köps
- **Bildtillägg**: Lägg till nya bilder till befintliga externa stämplar
- **Redigering**: Möjlighet att redigera alla stämplar oavsett källa

#### Import/Export
- **CSV-export**: Exportera stämpeldata för delning
- **JSON-import**: Importera stämpeldata från andra samlare
- **Backup**: Säkerhetskopiera stämpelregister

## Teknisk implementation

### Databasmodeller
```python
class Stamp(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, blank=True)
    stamp_type = models.CharField(max_length=20, choices=[('text', 'Text'), ('image', 'Bild'), ('symbol', 'Symbol')])
    status = models.CharField(max_length=20, choices=[('known', 'Känd'), ('unknown', 'Okänd')])
    # Årtalsinformation
    year_from = models.IntegerField(null=True, blank=True)  # Startår (t.ex. 1884)
    year_to = models.IntegerField(null=True, blank=True)    # Slutår (t.ex. 1900)
    year_uncertainty = models.BooleanField(default=False)   # Osäker årtalsinformation
    year_notes = models.TextField(blank=True)               # Anteckningar om årtal (t.ex. "cirka")
    # Källinformation
    source_category = models.CharField(max_length=20, choices=[
        ('own_collection', 'Egen samling'),
        ('ebay_auction', 'eBay/Auktion'),
        ('museum', 'Museum'),
        ('private_collector', 'Privat samlare'),
        ('book_article', 'Bok/Artikel'),
        ('internet', 'Internet'),
        ('unknown', 'Okänd')
    ], default='own_collection')
    source_reference = models.TextField(blank=True)  # Specifik källhänvisning
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StampTranscription(models.Model):
    stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE, related_name='transcriptions')
    text = models.CharField(max_length=500)
    quality = models.CharField(max_length=20, choices=[('high', 'Hög'), ('medium', 'Medium'), ('low', 'Låg')])
    symbols = models.ManyToManyField('StampSymbol', blank=True, verbose_name='Symboler')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def symbols_display(self):
        """Returnerar en formaterad sträng av alla symboler"""
        if self.symbols.exists():
            return ", ".join([symbol.display_name for symbol in self.symbols.all()])
        return ""
    
    @property
    def full_transcription(self):
        """Returnerar komplett transkribering med text och symboler"""
        parts = [self.text]
        if self.symbols.exists():
            symbols_part = " + ".join([symbol.display_name for symbol in self.symbols.all()])
            parts.append(symbols_part)
        return " + ".join(parts)

class StampSymbol(models.Model):
    """Symboler som kan förekomma i stämplar"""
    
    SYMBOL_TYPE_CHOICES = [
        ("crown", "Krona"),
        ("cannon", "Kanon"),
        ("star", "Stjärna"),
        ("cross", "Kors"),
        ("shield", "Sköld"),
        ("anchor", "Ankare"),
        ("flower", "Blomma"),
        ("leaf", "Löv"),
        ("other", "Övrigt"),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Namn")
    symbol_type = models.CharField(max_length=20, choices=SYMBOL_TYPE_CHOICES, default="other")
    description = models.TextField(blank=True, null=True, verbose_name="Beskrivning")
    is_predefined = models.BooleanField(default=False, verbose_name="Fördefinierad")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["symbol_type", "name"]
        verbose_name = "Stämpelsymbol"
        verbose_name_plural = "Stämpelsymboler"
        unique_together = ["name", "symbol_type"]
    
    def __str__(self):
        return f"{self.get_symbol_type_display()}: {self.name}"
    
    @property
    def display_name(self):
        """Returnerar visningsnamn för symbolen"""
        if self.symbol_type == "other":
            return self.name
        return f"{self.get_symbol_type_display()}: {self.name}"

class StampTag(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex-färg
    created_at = models.DateTimeField(auto_now_add=True)

class StampImage(models.Model):
    stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='stamps/')
    quality = models.CharField(max_length=20, choices=[('high', 'Hög'), ('medium', 'Medium'), ('low', 'Låg')])
    uploaded_at = models.DateTimeField(auto_now_add=True)

class AxeStamp(models.Model):
    axe = models.ForeignKey(Axe, on_delete=models.CASCADE, related_name='stamps')
    stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE, related_name='axes')
    comment = models.TextField(blank=True)
    position = models.CharField(max_length=100, blank=True)  # Var på yxan
    uncertainty_level = models.CharField(max_length=20, choices=[('certain', 'Säker'), ('uncertain', 'Osäker'), ('tentative', 'Tentativ')], default='certain')
    created_at = models.DateTimeField(auto_now_add=True)

class StampVariant(models.Model):
    main_stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE, related_name='variants')
    variant_stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE, related_name='main_stamp')
    description = models.TextField(blank=True)  # Beskrivning av skillnaden
    created_at = models.DateTimeField(auto_now_add=True)

class StampUncertaintyGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    stamps = models.ManyToManyField(Stamp, related_name='uncertainty_groups')
    confidence_level = models.CharField(max_length=20, choices=[('high', 'Hög'), ('medium', 'Medium'), ('low', 'Låg')])
    created_at = models.DateTimeField(auto_now_add=True)

### API-endpoints
- `GET /api/stamps/` - Lista stämplar med filtrering
- `GET /api/stamps/{id}/` - Stämpeldetaljer
- `POST /api/stamps/` - Skapa ny stämpel
- `PUT /api/stamps/{id}/` - Uppdatera stämpel
- `GET /api/stamps/search/` - Sök i stämplar
- `GET /api/axes/{id}/stamps/` - Stämplar för specifik yxa
- `POST /api/axes/{id}/stamps/` - Koppla stämpel till yxa
- `GET /api/axes/without-stamps/` - Lista yxor utan stämplar
- `GET /api/stamps/statistics/` - Stämpelstatistik

### Vyer och templates
- `stamp_list.html` - Stämpelregister-översikt
- `stamp_detail.html` - Stämpeldetaljer
- `stamp_form.html` - Skapa/redigera stämpel
- `axe_stamps.html` - Stämpelvisning på yxdetaljsida
- `axes_without_stamps.html` - Lista yxor utan stämplar
- `stamp_statistics.html` - Stämpelstatistik och analys

## Underuppgifter

### Fas 1: Grundläggande datamodeller
- [x] 105.1 Skapa Stamp-modell med fält för namn, beskrivning, tillverkare, typ (text/bild/symbol), och status (känd/okänd)
- [x] 105.2 Skapa StampTranscription-modell för textbaserad beskrivning av stämplar (t.ex. 'GRÄNSFORS', 'MADE IN SWEDEN', 'HULTS BRUK') med sökbarhet
- [x] 105.3 Skapa StampTag-modell för kategorisering (t.ex. 'tillverkarnamn', 'land', 'kvalitet', 'år', 'serienummer')
- [x] 105.4 Skapa StampImage-modell för att koppla bilder till stämplar (bygg vidare på befintlig ManufacturerImage med STAMP-typ)
- [x] 105.5 Skapa AxeStamp-modell för att koppla yxor till stämplar med kommentar-fält (t.ex. kvalitet på stämpeln, synlighet, etc.)

### Fas 2: Användargränssnitt
- [x] 105.6 Implementera stämpelregister-vy med sökfunktion, filtrering på tillverkare/typ/taggar, och gruppering av okända stämplar
- [x] 105.7 Skapa stämpeldetalj-vy som visar alla bilder, transkriberingar, taggar, och kopplade yxor för varje stämpel
- [x] 105.8 Lägg till stämpelvisning på yxdetaljsidan med möjlighet att koppla/avkoppla stämplar och lägga till kommentarer
- [x] 105.12 Skapa vy för yxor utan stämplar med prioritering och snabbkoppling till stämpeldefinition

### Fas 3: Avancerade funktioner
- [ ] 105.9 Implementera sökfunktion för stämplar baserat på transkribering, taggar, tillverkare, och visuell likhet (framtida AI-funktion)
- [x] 105.10 Skapa admin-gränssnitt för att hantera stämplar, transkriberingar, taggar, och kopplingar mellan stämplar och yxor
- [ ] 105.11 Implementera import/export-funktionalitet för stämpeldata (CSV/JSON) för att dela stämpelregister med andra samlare

### Fas 4: Saknade användargränssnitt (upptäckt 2025-01-27)
- [ ] 105.13 Implementera användargränssnitt för StampTranscription-hantering (views, templates, URLs)
- [ ] 105.14 Implementera användargränssnitt för StampTag-hantering (views, templates, URLs)
- [ ] 105.15 Implementera användargränssnitt för StampVariant-hantering (views, templates, URLs)
- [ ] 105.16 Implementera användargränssnitt för StampUncertaintyGroup-hantering (views, templates, URLs)

## Prioritering

1. **Hög prioritet**: Grundläggande datamodeller och enkel stämpelregistrering
2. **Medium prioritet**: Sökfunktioner och användargränssnitt
3. **Låg prioritet**: AI-funktioner och avancerad sökning

## Aktuell status (2025-01-27)

### Implementerat
- ✅ **Grundläggande stämpelfunktionalitet**: Stamp-modell, admin, views, templates
- ✅ **Stämpelkoppling**: Koppla stämplar till yxor med bildmarkering
- ✅ **Stämpelredigering**: Redigera befintliga stämplar med bildmarkering
- ✅ **Kortbaserad visning**: Visuell stämpelvisning på yxdetaljsidan
- ✅ **AJAX-sökning**: Realtidssökning i stämplar
- ✅ **Bildmarkering**: Integrerad stämpelmarkering på yxbilder med koordinater

### Saknat användargränssnitt
- ❌ **StampTranscription**: Modell finns men saknar användarvyer för hantering
- ❌ **StampTag**: Modell finns men saknar användarvyer för hantering  
- ❌ **StampVariant**: Modell finns men saknar användarvyer för hantering
- ❌ **StampUncertaintyGroup**: Modell finns men saknar användarvyer för hantering

### Prioriterade nästa steg
1. **StampTranscription-hantering** - Högst prioritet (obligatorisk för stämplar)
2. **StampTag-hantering** - Medium prioritet (för kategorisering)
3. **StampVariant-hantering** - Låg prioritet (avancerad funktion)
4. **StampUncertaintyGroup-hantering** - Låg prioritet (avancerad funktion)

## Framtida utveckling

- **OCR-integration**: Automatisk textigenkänning från stämpelbilder
- **Machine Learning**: Visuell likhetssökning mellan stämplar
- **Community-funktioner**: Delning av stämpelregister mellan samlare
- **Mobile app**: Stämpelidentifiering via mobilkamera
- **API för externa tjänster**: Integration med andra samlarplattformar

## Relaterade funktioner

- **Kommentarsystem** (96): Stöd för kommentarer på stämplar
- **Bildhantering** (1): Utbyggd bildhantering för stämpelbilder
- **Sök och filtrering** (3): Integration med global sökning
- **Tillverkarhantering** (7): Koppling mellan stämplar och tillverkare

## Förbättringsförslag och ytterligare funktioner

### Prioriterade förbättringar (baserat på användarfeedback)

#### Hög prioritet
- **Dupliceringsvarning**: Varna för potentiella duplicerade stämplar baserat på transkribering
- **Validering**: Kontrollera att obligatoriska fält är ifyllda innan sparning
- **Snabbstämpel**: Snabbregistrering av stämplar med minimal information - markera stämpelbild i mottagningsflödet och återkomma senare för fullständig definition
- **Favoritstämplar**: Markera ofta använda stämplar som favoriter
- **Stämpelbackup**: Automatisk säkerhetskopiering av stämpeldata (tillsammans med resten av axecollection-appen)
- **Användarstatistik**: Spåra användning av stämpelregister-funktioner

#### Medium prioritet
- **Export-funktioner**: Exportera stämpeldata för analys i externa verktyg (framtida behov)

#### Ej prioriterade (avfärdade)
- **Kvalitetsbedömning**: Automatisk bedömning av stämpelbildkvalitet (datakraftskrävande)
- **Konsistenscheck**: Varna för inkonsistenser (årtal hanteras centralt per stämpeldefinition)
- **Stämpelstatistik**: Statistik över stämplar per tillverkare (begränsat värde)
- **Trendanalys**: Visa trender i stämpelutveckling över tid (ej prioriterat)
- **Jämförelsevy**: Jämför stämplar från olika tillverkare eller tidsperioder (ej prioriterat)
- **Stämpelhistorik**: Spåra ändringar i stämpeldata över tid (ej prioriterat)
- **Stämpelnotifikationer**: Notifieringar när nya stämplar läggs till (ej prioriterat)
- **Bildanalys**: Automatisk identifiering av stämpelområden (tveksamt tekniskt genomförbart)
- **OCR-förslag**: Automatiska förslag på transkribering (stämplar för otydliga för OCR)
- **Stämpelimport**: Import av stämpeldata från externa källor (inga externa databaser tillgängliga)
- **API-integration**: Integration med externa stämpeldatabaser (inga externa databaser tillgängliga)
- **Datarening**: Verktyg för att rensa och konsolidera stämpeldata (ej prioriterat)
- **Stämpelarkiv**: Arkivering av gamla eller ersatta stämplar (ej prioriterat)

## Implementation Status

### Genomfört (2025-07-31)

#### Symbolfunktionalitet för stämplar (2025-07-31)
- [x] **StampSymbol-modell**: Skapad med symboltyper (krona, kanon, stjärna, kors, sköld, ankare, blomma, löv, övrigt)
- [x] **Fördefinierade symboler**: 22 fördefinierade symboler skapade via management command
- [x] **Transkribering-symbol koppling**: ManyToManyField mellan StampTranscription och StampSymbol
- [x] **Formulärintegration**: StampTranscriptionForm uppdaterad med symbolval
- [x] **Grupperad visning**: Symboler grupperade efter typ i dropdown
- [x] **Komplett transkribering**: Property som kombinerar text och symboler
- [x] **Databasmigrationer**: Migrationer skapade och applicerade för symbolfunktionalitet
- [x] **Management command**: `init_stamp_symbols` för att skapa fördefinierade symboler

### Genomfört (2025-07-29)

#### Datamodeller och databas
- [x] **Stamp-modell**: Implementerad med alla fält (namn, beskrivning, tillverkare, typ, status, årtal, källa)
- [x] **StampTranscription-modell**: Implementerad för textbaserade beskrivningar
- [x] **StampTag-modell**: Implementerad för kategorisering
- [x] **StampImage-modell**: Implementerad för bildhantering
- [x] **AxeStamp-modell**: Implementerad för koppling mellan yxor och stämplar
- [x] **StampVariant-modell**: Implementerad för stämpelvarianter
- [x] **StampUncertaintyGroup-modell**: Implementerad för osäkra identifieringar
- [x] **Databasmigrationer**: Skapade och körda för alla nya modeller

#### Admin-integration
- [x] **StampAdmin**: Implementerad med inline-klasser för transkriptioner och bilder
- [x] **Admin-registrering**: Alla nya modeller registrerade i Django admin
- [x] **List_display och filter**: Konfigurerade för alla admin-klasser

#### Views och URLs
- [x] **views_stamp.py**: Skapad med alla vyer för stämpelhantering
- [x] **URL-mönster**: Implementerade för alla stämpelrelaterade vyer
- [x] **stamp_list**: Lista stämplar med sök och filtrering
- [x] **stamp_detail**: Detaljerad vy för stämplar
- [x] **stamp_create/edit**: Skapa och redigera stämplar
- [x] **axes_without_stamps**: Lista yxor utan stämplar
- [x] **stamp_statistics**: Statistik för stämplar
- [x] **add_axe_stamp**: Koppla stämpel till yxa

#### Forms
- [x] **StampForm**: Formulär för stämplar
- [x] **StampTranscriptionForm**: Formulär för transkriptioner
- [x] **AxeStampForm**: Formulär för att koppla yxa och stämpel
- [x] **StampTagForm** och **StampImageForm**: Formulär för taggar och bilder

#### Templates
- [x] **stamp_list.html**: Lista över stämplar med sök och filtrering
- [x] **stamp_detail.html**: Detaljerad vy för stämplar
- [x] **stamp_form.html**: Formulär för att skapa/redigera stämplar
- [x] **axes_without_stamps.html**: Lista yxor utan stämplar
- [x] **stamp_statistics.html**: Statistik-vy för stämplar
- [x] **base.html**: Uppdaterad med navigation för stämplar

#### Navigation
- [x] **Huvudmeny**: Lagt till "Stämplar" i huvudnavigationen
- [x] **Breadcrumbs**: Implementerade för alla stämpelrelaterade sidor

### Pågående arbete

#### Nästa steg att implementera
- [x] **Yxdetaljsida-integration**: Visa stämplar på yxdetaljsidan
- [x] **Stämpelkoppling**: Möjlighet att koppla/avkoppla stämplar från yxdetaljsidan
- [x] **AJAX-sökning**: Implementera AJAX-funktionalitet för stämpelsökning
- [x] **Bildmarkering**: Integrerad stämpelmarkering på yxbilder med koordinater
- [x] **Stämpelredigering**: Möjlighet att redigera befintliga stämplar med bildmarkering
- [x] **Kortbaserad stämpelvisning**: Visuell stämpelvisning med bilder på yxdetaljsidan
- [ ] **Mottagningsflöde-integration**: Integrera stämpeldefinition i mottagningsarbetsflödet (SKIPPAD - fungerar bra som separat process)

#### Saknade användargränssnitt (upptäckt 2025-01-27)
- [ ] **StampTranscription-hantering**: Views, templates och URLs för att hantera stämpeltranskriberingar
- [ ] **StampTag-hantering**: Views, templates och URLs för att hantera stämpeltaggar
- [ ] **StampVariant-hantering**: Views, templates och URLs för att hantera stämpelvarianter
- [ ] **StampUncertaintyGroup-hantering**: Views, templates och URLs för att hantera osäkerhetsgrupper

#### Tekniska detaljer
- **Branch**: `feature/stamp-register`
- **Commit**: `066a4ae` - "Implementera Stamp Register-funktionalitet - Grundläggande modeller, admin, views, forms och templates"
- **Status**: Grundläggande funktionalitet implementerad och testad
- **Fel**: Inga kritiska fel, alla TemplateDoesNotExist-fel lösta

### Testning
- [x] **Servern startar**: Django-servern startar utan fel
- [x] **URLs fungerar**: Alla stämpelrelaterade URLs fungerar
- [x] **Admin-funktioner**: Admin-gränssnittet fungerar för alla nya modeller
- [x] **Templates renderas**: Alla templates renderas korrekt

### Kända begränsningar
- **Ingen data**: Databasen är tom för stämplar (förväntat)
- **Saknade användargränssnitt**: Flera stämpelmodeller har bara admin-gränssnitt men saknar användarvyer
- **Ingen mottagningsintegration**: Stämpeldefinition är inte integrerad i mottagningsflödet (medvetet val)

### Nyligen implementerat (2025-07-29)

#### Yxdetaljsida-integration
- [x] **Stämpelsektion**: Lagt till stämpelsektion på yxdetaljsidan som visar alla kopplade stämplar
- [x] **Stämpeltabell**: Tabell som visar stämpelnamn, tillverkare, typ, position, osäkerhet och kommentar
- [x] **Stämpelkoppling**: Knapp för att lägga till nya stämplar på yxan
- [x] **Stämpelavkoppling**: Möjlighet att ta bort stämplar från yxan med bekräftelsedialog
- [x] **Stämpelformulär**: Skapat `axe_stamp_form.html` för att lägga till stämplar på yxor
- [x] **View-uppdatering**: Uppdaterat `axe_detail` view för att inkludera stämpeldata
- [x] **Navigation**: Breadcrumbs och länkar mellan yxdetaljsida och stämpelfunktioner

#### Tekniska detaljer
- **Template**: `axe_detail.html` - Lagt till stämpelsektion efter transaktionshistoriken
- **View**: `views_axe.py` - Uppdaterat `axe_detail` för att hämta stämpeldata
- **Form**: `AxeStampForm` - Används för att koppla stämplar till yxor
- **URL**: `add_axe_stamp` och `remove_axe_stamp` - Hanterar stämpelkoppling/avkoppling
- **Styling**: Bootstrap-klasser för responsiv design och konsistent utseende

#### Stämpelprioritering (2025-07-29)
- [x] **Tillverkarprioritering**: Stämplar från yxans tillverkare visas först i dropdown-listan
- [x] **Separatorer**: Tydliga separatorer mellan prioriterade och andra stämplar
- [x] **Tillverkarinformation**: Andra stämplar visar tillverkarnamn för tydlighet
- [x] **Form-uppdatering**: `AxeStampForm` anpassad för att ta emot `axe`-parameter
- [x] **View-uppdatering**: `add_axe_stamp` view uppdaterad för att skicka `axe` till formuläret
- [x] **Validering**: `clean_stamp` metod tillagd för att konvertera ID till Stamp-objekt

#### AJAX-sökning (2025-07-29)
- [x] **Live-sökning**: Realtidssökning med debouncing (300ms) i stämpellistan
- [x] **Förbättrad sökning**: Sök i namn, beskrivning, transkriptioner och tillverkare
- [x] **Filtrering**: Kombinera sökning med tillverkare och stämpeltyp
- [x] **Resultatvisning**: Dropdown med detaljerad information om varje stämpel
- [x] **Formulärintegration**: AJAX-sökning i add_axe_stamp formuläret
- [x] **JavaScript-fil**: `stamp_search.js` skapad med fullständig AJAX-funktionalitet
- [x] **Template-uppdateringar**: `stamp_list.html` och `axe_stamp_form.html` uppdaterade
- [x] **Responsiv design**: Dropdown som anpassar sig efter innehåll
- [x] **Felhantering**: Visar laddningsindikator och felmeddelanden

#### Stämpelbilder och dokumentation (2025-07-29)
- [x] **Förbättrad StampImage-modell**: Lagt till caption, description, order och cache-busting
- [x] **WebP-stöd**: Automatisk konvertering till WebP-format för bättre prestanda
- [x] **Admin-förbättringar**: Uppdaterat StampImageInline och StampImageAdmin med nya fält
- [x] **Bilduppladdning**: Ny vy `stamp_image_upload` för att ladda upp bilder
- [x] **Bildborttagning**: Ny vy `stamp_image_delete` för att ta bort bilder
- [x] **Formulär**: Förbättrat `StampImageForm` med alla nya fält
- [x] **Templates**: Skapat `stamp_image_form.html` och `stamp_image_delete.html`
- [x] **Förhandsvisning**: JavaScript-förhandsvisning av bilder vid uppladdning
- [x] **Stämpeldetalj-vy**: Förbättrat bildvisning i `stamp_detail.html` med WebP-stöd
- [x] **URL-struktur**: Lagt till URL-mönster för bildhantering
- [x] **Responsiv design**: Bilder anpassar sig efter skärmstorlek
- [x] **Kvalitetsindikatorer**: Visuella badges för bildkvalitet
- [x] **Ordning**: Stöd för att sortera bilder med order-fält

#### Ersättning av ManufacturerImage för stämplar (2025-07-29)
- [x] **Tillverkardetaljsida**: Ersatt ManufacturerImage stämplar med Stamp-systemet
- [x] **Visa stämplar**: Tillverkardetaljsidan visar nu registrerade Stamp-objekt istället för ManufacturerImage
- [x] **Bildvisning**: Stämplar visar första bilden från StampImage-samlingen
- [x] **Länkar till detaljer**: Varje stämpel har länk till stamp_detail-sidan
- [x] **Skapa nya stämplar**: Knapp för att skapa nya stämplar direkt från tillverkarsidan
- [x] **Formulärintegration**: stamp_create vyn hanterar manufacturer-parameter från URL
- [x] **Responsiv design**: Stämplar visas i samma layout som tidigare bilder
- [x] **Fallback**: Visar stämpelikon om ingen bild finns tillgänglig
- [x] **Separat sektion**: Stämplar visas nu som en egen sektion, separerad från övriga bilder
- [x] **Tydlig gruppering**: "Stämplar för [tillverkare]" och "Bilder för [tillverkare]" som separata kort

### Kommande funktioner (TODO)

#### Saknade användargränssnitt (högsta prioritet)
- [ ] **StampTranscription-hantering**: Views, templates och URLs för att hantera stämpeltranskriberingar
- [ ] **StampTag-hantering**: Views, templates och URLs för att hantera stämpeltaggar
- [ ] **StampVariant-hantering**: Views, templates och URLs för att hantera stämpelvarianter
- [ ] **StampUncertaintyGroup-hantering**: Views, templates och URLs för att hantera osäkerhetsgrupper

#### Avancerad bildhantering
- [x] **Markera AxeImage som StampImage**: Möjlighet att markera befintliga AxeImage som StampImage för specifika stämplar
- [x] **Huvudbildsval**: På stämpeldetaljsidan kunna välja "bästa" bilden som stämpelns huvudbild
- [x] **Bildbeskärning**: Implementera beskärning eller definiera visningsområde för stämpel inom AxeImage
- [x] **Visa hela bilden**: Alternativ att visa hela AxeImage istället för bara stämpelområdet
- [x] **Bildkoordinater**: Spara x,y-koordinater för stämpelområdet inom bilden
- [ ] **Zoom-funktionalitet**: Möjlighet att zooma in på stämpelområdet

#### Mottagningsflöde-integration (SKIPPAD)
- [x] **Stämpeldefinition som separat process**: Stämpeldefinition fungerar bra som separat process efter mottagning
- [x] **Bildmarkering**: Integrerad stämpelmarkering på yxbilder med koordinater
- [x] **Stämpelredigering**: Möjlighet att redigera befintliga stämplar med bildmarkering
- [x] **Kortbaserad visning**: Visuell stämpelvisning på yxdetaljsidan

#### Avancerad sökning och filtrering
- [ ] **Visuell stämpelsökning**: Sök stämplar baserat på visuell likhet
- [ ] **OCR-integration**: Automatisk textigenkänning från stämpelbilder
- [ ] **Fuzzy matching**: Fuzzy matching för stämpeltranskriptioner
- [ ] **Geografisk filtrering**: Filtrera stämplar baserat på tillverkarens land

#### Dataimport/export
- [ ] **CSV-export**: Exportera stämpeldata för delning
- [ ] **JSON-import**: Importera stämpeldata från andra samlare
- [ ] **Backup-funktionalitet**: Säkerhetskopiera stämpelregister
- [ ] **Bildimport**: Massimport av stämpelbilder från externa källor

#### Användargränssnitt
- [ ] **Drag-and-drop**: Drag-and-drop för bildordning och stämpelkoppling
- [ ] **Lightbox för stämplar**: Förbättrad bildvisning för stämpelbilder
- [ ] **Mobiloptimering**: Förbättrad mobilupplevelse för stämpelfunktioner
- [ ] **Tema-anpassning**: Anpassa färger och stil för stämpelfunktioner

#### Stämpeltyper och etiketter (2025-07-29)
- [x] **Ny stämpeltyp**: Lagt till "Etikett" som ny typ i STAMP_TYPE_CHOICES
- [x] **Databasuppdatering**: Migration skapad och applicerad för nya stämpeltypen
- [x] **Dokumentation**: Uppdaterat STAMP_REGISTER_FEATURE.md med ny typ
- [x] **Stöd för etiketter**: Systemet kan nu hantera etiketter som en typ av märkning
- [x] **Konsistent terminologi**: "Etikett" används konsekvent i hela systemet

#### Stämpeltyper uppdaterade (2025-07-29)
- [x] **Ta bort "Bild"-typ**: "image"-typen har tagits bort från STAMP_TYPE_CHOICES
- [x] **Ny kombinationstyp**: Lagt till "text_symbol" för stämplar som innehåller både text och symbol
- [x] **Databasuppdatering**: Migration skapad och applicerad för uppdaterade stämpeltyper
- [x] **Dokumentation**: Uppdaterat STAMP_REGISTER_FEATURE.md med nya typer
- [x] **Förbättrad kategorisering**: Systemet kan nu bättre kategorisera stämplar baserat på innehåll

#### AxeImageStamp-funktionalitet (2025-07-29)
- [x] **Ny modell**: Skapat AxeImageStamp för att koppla AxeImage till Stamp med koordinater
- [x] **Bildkoordinater**: Stöd för x, y, width, height för stämpelområden
- [x] **Visningsinställningar**: show_full_image och is_primary för bildhantering
- [x] **Admin-integration**: AxeImageStampAdmin med fältgruppering och sökning
- [x] **Views**: mark_axe_image_as_stamp, unmark_axe_image_stamp, stamp_image_crop, set_primary_stamp_image
- [x] **URL-struktur**: Nya URL-patterns för AxeImageStamp-funktionalitet
- [x] **Templates**: mark_axe_image_as_stamp.html och unmark_axe_image_stamp.html
- [x] **Bildmarkering**: Visuell markering av stämpelområden på yxbilder
- [x] **Interaktiv beskärning**: Klicka och dra för att markera stämpelområden
- [x] **Yxdetaljsida-integration**: Uppdaterat axe_detail.html med stämpelmarkeringar
- [x] **Knappar för markering**: Lägg till/ta bort stämpelmarkering på bilder
- [x] **Huvudbildshantering**: Möjlighet att sätta huvudbild för stämplar
- [x] **Koordinatvalidering**: has_coordinates property för att kontrollera kompletta koordinater
- [x] **Crop-area**: crop_area property för enkel åtkomst till beskärningsområde
- [x] **Modal-bekräftelser**: Konverterat till modals istället för full-page bekräftelser
- [x] **AJAX-hantering**: Views stöder både AJAX och vanliga requests
- [x] **JavaScript-integration**: Dynamisk laddning av modal-innehåll och formulärhantering
- [x] **Template-uppdateringar**: axe_stamp_confirm_delete_modal.html och unmark_axe_image_stamp_modal.html
- [x] **Responsiv design**: Modaler anpassar sig efter innehåll och skärmstorlek
- [x] **Felhantering**: Visar laddningsindikator och felmeddelanden för modal-anrop
- [x] **Ikonfix**: Ändrat från bi bi-stamp till fas fa-stamp för korrekt ikonvisning
- [x] **Redigeringssida-integration**: Lagt till stämpelhantering på axe_form.html med knappar och modal-funktionalitet
- [x] **Prefetch-optimering**: Uppdaterat axe_edit view för att inkludera stamp_marks i prefetch
- [x] **Yxdetaljsida-rensning**: Tagit bort stämpelknappar från axe_detail.html - stämpelhantering visas endast på redigeringssidan
- [x] **Positionering**: Flyttat stämpelikonen från övre vänstra till övre högra hörnet på redigeringssidan för att undvika överlappning med filnamnsbadgen
- [x] **Stämpeldetaljsida-förbättringar**: Flyttat "Visa hela bilden" och "Markera som huvudbild" funktioner från /markera-stampel/ till stamp_detail.html
- [x] **Kombinerad bildvisning**: Stamp_detail.html visar nu både StampImage och AxeImageStamp bilder i samma sektion
- [x] **AJAX-funktionalitet**: Lagt till JavaScript-funktioner för att uppdatera show_full_image och is_primary via AJAX
- [x] **Nya views**: update_axe_image_stamp_show_full view för att hantera AJAX-anrop
- [x] **URL-uppdateringar**: Ny URL-mönster för update_axe_image_stamp_show_full
- [x] **Visuella förbättringar**: Stämpelområde overlay, badges för huvudbild och "Från yxa", länk till yxdetaljsida

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