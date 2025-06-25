# Tillverkarbilder och länkar - Stämplar och resurser

## Översikt
Denna funktionalitet låter dig lägga till bilder av tillverkarnas stämplar och länkar till resurser för respektive tillverkare. Varje bild kan ha en bildtext (caption) och en mer detaljerad beskrivning, medan länkar kan kategoriseras och beskrivas.

## Funktioner

### 1. Tillverkarbilder (Stämplar)
- **Via admin-gränssnittet**: Gå till Admin → Tillverkarbilder → Lägg till tillverkarbild
- **Via tillverkardetaljsidan**: Klicka på "Lägg till stämpel"-knappen
- **Inline-redigering**: Redigera tillverkare och lägg till bilder direkt

#### Bildinformation
- **Bildfil**: Ladda upp bilden (stöds format: JPG, PNG, GIF, etc.)
- **Bildtext (Caption)**: Kort beskrivning som visas under bilden
- **Beskrivning**: Mer detaljerad information om stämpeln

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

### Lägga till en stämpel
1. Gå till tillverkardetaljsidan
2. Klicka på "Lägg till stämpel"
3. Fyll i:
   - Bildfil: Ladda upp bilden
   - Bildtext: "Hults Bruk stämpel med kronan"
   - Beskrivning: "Klassisk stämpel från 1950-talet"

## Teknisk information
- **Modeller**: `ManufacturerImage`, `ManufacturerLink`
- **Filsystem**: Bilder sparas i `media/manufacturer_images/`
- **Databas**: Länkar sparas med metadata och kategorisering
- **Säkerhet**: Externa länkar öppnas i nya flikar
- **Prestanda**: Bilder och länkar laddas endast vid behov
```python
class ManufacturerImage(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, related_name='images')
    image = models.ImageField(upload_to='manufacturer_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
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

### 1. Lägg till en ny stämpel
1. Gå till tillverkardetaljsidan
2. Klicka på "Lägg till stämpel"
3. Välj tillverkare (förfylls automatiskt)
4. Ladda upp bildfil
5. Fyll i bildtext och beskrivning
6. Spara

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
- Använd beskrivande bildtexter för att identifiera olika stämplar
- Lägg till detaljerad beskrivning för historisk kontext
- Använd konsekvent namngivning för bilder
- Kontrollera att bilderna är av god kvalitet innan uppladdning 