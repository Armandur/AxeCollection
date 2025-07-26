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
- **Typ**: text/bild/symbol
- **Status**: känd/okänd
- **Användningsår**: Tidsperiod när stämpeln användes (exakt år, årtionde, eller osäker)
- **Årtalsosäkerhet**: Flagga för osäker årtalsinformation (t.ex. "cirka")
- **Variant av**: Koppling till huvudstämpel om detta är en variant
- **Osäkerhet**: Flagga för stämplar med osäker identifiering
- **Källa**: Källkategori för stämpeln (egen samling, extern, etc.)
- **Källhänvisning**: Specifik hänvisning till källan (t.ex. "eBay-auktion 2023")

#### StampTranscription (Stämpeltranskribering)
- **Text**: Textbaserad beskrivning av stämpeln (t.ex. 'GRÄNSFORS', 'MADE IN SWEDEN', 'HULTS BRUK')
- **Sökbarhet**: Fulltextsökning i transkriberingar
- **Kvalitet**: Bedömning av hur säker transkriberingen är
- **Obligatorisk**: Transkribering krävs för alla stämplar

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
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
- [ ] 105.1 Skapa Stamp-modell med fält för namn, beskrivning, tillverkare, typ (text/bild/symbol), och status (känd/okänd)
- [ ] 105.2 Skapa StampTranscription-modell för textbaserad beskrivning av stämplar (t.ex. 'GRÄNSFORS', 'MADE IN SWEDEN', 'HULTS BRUK') med sökbarhet
- [ ] 105.3 Skapa StampTag-modell för kategorisering (t.ex. 'tillverkarnamn', 'land', 'kvalitet', 'år', 'serienummer')
- [ ] 105.4 Skapa StampImage-modell för att koppla bilder till stämplar (bygg vidare på befintlig ManufacturerImage med STAMP-typ)
- [ ] 105.5 Skapa AxeStamp-modell för att koppla yxor till stämplar med kommentar-fält (t.ex. kvalitet på stämpeln, synlighet, etc.)

### Fas 2: Användargränssnitt
- [ ] 105.6 Implementera stämpelregister-vy med sökfunktion, filtrering på tillverkare/typ/taggar, och gruppering av okända stämplar
- [ ] 105.7 Skapa stämpeldetalj-vy som visar alla bilder, transkriberingar, taggar, och kopplade yxor för varje stämpel
- [ ] 105.8 Lägg till stämpelvisning på yxdetaljsidan med möjlighet att koppla/avkoppla stämplar och lägga till kommentarer
- [ ] 105.12 Skapa vy för yxor utan stämplar med prioritering och snabbkoppling till stämpeldefinition

### Fas 3: Avancerade funktioner
- [ ] 105.9 Implementera sökfunktion för stämplar baserat på transkribering, taggar, tillverkare, och visuell likhet (framtida AI-funktion)
- [ ] 105.10 Skapa admin-gränssnitt för att hantera stämplar, transkriberingar, taggar, och kopplingar mellan stämplar och yxor
- [ ] 105.11 Implementera import/export-funktionalitet för stämpeldata (CSV/JSON) för att dela stämpelregister med andra samlare

## Prioritering

1. **Hög prioritet**: Grundläggande datamodeller och enkel stämpelregistrering
2. **Medium prioritet**: Sökfunktioner och användargränssnitt
3. **Låg prioritet**: AI-funktioner och avancerad sökning

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