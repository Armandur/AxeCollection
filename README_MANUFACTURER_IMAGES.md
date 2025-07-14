# Tillverkarbilder och länkar - Stämplar och resurser

## Översikt
Denna funktionalitet låter dig lägga till bilder av tillverkarnas stämplar och länkar till resurser för respektive tillverkare. Varje bild kan ha en bildtext (caption) och en mer detaljerad beskrivning, medan länkar kan kategoriseras och beskrivas.

## Funktioner

### 1. Tillverkarbilder (Kategoriserade)
- **Via admin-gränssnittet**: Gå till Admin → Tillverkarbilder → Lägg till tillverkarbild
- **Via tillverkardetaljsidan**: Klicka på "Lägg till bild"-knappen
- **Inline-redigering**: Redigera tillverkare och lägg till bilder direkt

#### Bildkategorier
- **Stämpel**: Tillverkarens stämplar och märken
- **Övrig bild**: Smeder, fabriker, historiska bilder, produktbilder, etc.

#### Bildinformation
- **Bildfil**: Ladda upp bilden (stöds format: JPG, PNG, GIF, etc.)
- **Bildtyp**: Välj mellan "Stämpel" eller "Övrig bild"
- **Bildtext (Caption)**: Kort beskrivning som visas under bilden
- **Beskrivning**: Mer detaljerad information om bilden
- **Ordning**: Sorteringsordning inom samma bildtyp

### 2. Tillverkarlänkar (Resurser)
- **Via admin-gränssnittet**: Gå till Admin → Tillverkarlänkar → Lägg till tillverkarlänk
- **Via tillverkardetaljsidan**: Klicka på "Lägg till länk"-knappen
- **Inline-redigering**: Redigera tillverkare och lägg till länkar direkt

#### Länktyper
- **Hemsida**: Länkar till tillverkarens officiella hemsida
- **Katalog**: Länkar till produktkataloger och broschyrer
- **Video/Film**: Länkar till videor, dokumentärer, tillverkningsfilmer
- **Artikel**: Länkar till artiklar, recensioner, historik
- **Dokument**: Länkar till PDF:er, tekniska specifikationer
- **Övrigt**: Övriga relevanta länkar

#### Länkinformation
- **Titel**: Beskrivande titel för länken
- **URL**: Den faktiska länken
- **Typ**: Kategori för länken (se ovan)
- **Beskrivning**: Detaljerad beskrivning av innehållet
- **Aktiv**: Om länken fortfarande fungerar (kan inaktiveras utan att raderas)

### 3. Visning
- **Bilder**: Visas på tillverkardetaljsidan i ett snyggt kort-layout
- **Länkar**: Grupperade efter typ med ikoner och beskrivningar
- **Responsivt design**: Fungerar bra på både desktop och mobil

### 4. Admin-funktioner
- **Förhandsvisning**: Se bilder direkt i admin-gränssnittet
- **Sökning**: Sök efter tillverkare, titlar, beskrivningar
- **Filtrering**: Filtrera efter länktyp, aktiv status, datum
- **Redigering**: Enkelt redigera både bilder och länkar

## Användningsexempel

### Lägga till en katalog
1. Gå till tillverkardetaljsidan
2. Klicka på "Lägg till länk"
3. Fyll i:
   - Titel: "Hults Bruk Katalog 2024"
   - URL: "https://example.com/katalog.pdf"
   - Typ: "Katalog"
   - Beskrivning: "Officiell produktkatalog från Hults Bruk för 2024"

### Lägga till en bild
1. Gå till tillverkardetaljsidan
2. Klicka på "Lägg till bild"
3. Fyll i:
   - Bildfil: Ladda upp bilden
   - Bildtyp: Välj "Stämpel" eller "Övrig bild"
   - Bildtext: "Hults Bruk stämpel med kronan" eller "Smeden vid Hults Bruk 1950"
   - Beskrivning: "Klassisk stämpel från 1950-talet" eller "Historisk bild av smeden"
   - Ordning: Sätt sorteringsordning (valfritt)

## Teknisk information
- **Modeller**: `ManufacturerImage`, `ManufacturerLink`
- **Filsystem**: Bilder sparas i `media/manufacturer_images/`
- **Databas**: Länkar sparas med metadata och kategorisering
- **Säkerhet**: Externa länkar öppnas i nya flikar
- **Prestanda**: Bilder och länkar laddas endast vid behov
```python
class ManufacturerImage(models.Model):
    IMAGE_TYPES = [
        ('STAMP', 'Stämpel'),
        ('OTHER', 'Övrig bild'),
    ]
    manufacturer = models.ForeignKey(Manufacturer, related_name='images')
    image = models.ImageField(upload_to='manufacturer_images/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES, default='STAMP')
    caption = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
```

### Filer
- Bilder sparas i `media/manufacturer_images/`
- Automatisk generering av unika filnamn
- CASCADE-radering när tillverkare raderas

### Admin-funktioner
- Inline-redigering i tillverkare-admin
- Förhandsvisning av bilder
- Sökning och filtrering
- Listvy med tillverkare, bildtext och beskrivning

## Användning

### 1. Lägg till en ny bild
1. Gå till tillverkardetaljsidan
2. Klicka på "Lägg till bild"
3. Välj tillverkare (förfylls automatiskt)
4. Ladda upp bildfil
5. Välj bildtyp (Stämpel eller Övrig bild)
6. Fyll i bildtext, beskrivning och ordning
7. Spara

### 2. Redigera befintliga bilder
1. Gå till Admin → Tillverkarbilder
2. Klicka på bilden du vill redigera
3. Uppdatera information
4. Spara

### 3. Ta bort bilder
1. Gå till Admin → Tillverkarbilder
2. Välj bilden du vill ta bort
3. Klicka på "Ta bort"

## Tips
- Använd beskrivande bildtexter för att identifiera olika bilder
- Välj rätt bildtyp för enklare organisering
- Lägg till detaljerad beskrivning för historisk kontext
- Använd konsekvent namngivning för bilder
- Kontrollera att bilderna är av god kvalitet innan uppladdning
- Använd ordning-fältet för att styra sorteringen inom samma bildtyp 