# UX Design Diskussion - AxeCollection

## Arbetsflöden för yxhantering

### Grundläggande status på yxor
- **Köpt** - Yxa köpt men inte mottagen än
- **Mottagen/Ägd** - Yxa är i samlingen och kan visas

### Arbetsflöde för inköp
1. **Steg 1: Grundinfo** (tillverkare, modell, kommentar)
2. **Steg 2: Bilder från auktion** (drag & drop, förhandsvisning)
3. **Steg 3: Försäljare** (sök befintlig eller skapa ny kontakt)
4. **Steg 4: Transaktion** (pris, frakt, datum)

### Arbetsflöde för mottagning
**Primärt via telefon/mobil enhet:**
1. **Ta mottagningsbilder** (kvalitetsbilder av mottagen yxa direkt med kameran)
2. **Mät mått** (med hjälp av telefonens kamera + mätguide/linjal)
3. **Uppdatera eventuell info** (tillverkare, modell, etc.)
4. **Markera som "Mottagen/Ägd"**

**Mobilfokus:**
- Kamera-integration för att ta bilder direkt
- Touch-vänligt gränssnitt för måttinmatning
- Offline-funktionalitet för att spara data lokalt
- Synkronisering när internet finns tillgängligt

## Implementerade förbättringar

### Bildhantering och mobilupplevelse ✅
- **Mobilvänlig bilduppladdning**: Stöd för att ta bilder direkt med mobilkamera, välja från galleri eller klistra in URL
- **URL-uppladdning av bilder**: Ladda ner bilder från URL:er med förhandsvisning och drag & drop
- **Förhandsvisning av bilder**: Se bilder innan de sparas med möjlighet att ta bort dem
- **Automatisk filnamnshantering**: Bilder får konsekventa namn (`[id]a.jpg`, `[id]b.webp` osv) och ordning
- **Automatisk .webp-generering**: Skapar optimerade .webp-versioner automatiskt
- **Visuell feedback vid borttagning**: Tydlig overlay med "KOMMER ATT TAS BORT" och padding
- **Responsiv layout**: Fungerar bra på alla enheter med touch-vänliga knappar
- **Robust felhantering**: Korrekt hantering av flera bilder och borttagning
- **Optimerad omdöpningslogik**: Kör endast när nödvändigt för bättre prestanda

### Smart funktioner
- **Auto-save** - spara automatiskt under processen
- **Bildförhandsvisning** - se bilderna direkt när du laddar upp
- **Smart sökning** - "Hultafors" ger förslag på "Hultafors AB"
- **Kontaktförslag** - om försäljaren redan finns, föreslå den
- **Prisberäkning** - visa total kostnad (pris + frakt)

### Mallar för vanliga tillverkare/mått
- **Tillverkarmallar**: När du väljer "Hultafors" fylls automatiskt i:
  - Vanliga mått som brukar finnas (bladlängd, skaftlängd, etc.)
  - Typiska kommentarer ("Svensk kvalitet", "Made in Sweden")
  - Föreslagna bildkategorier (hela yxan, stämpel, skaft, etc.)

- **Måttmallar**: För olika yxtyper (fällkniv, köksyxa, etc.) fylls vanliga mått automatiskt:
  - Bladlängd, bladbredd, skaftlängd
  - Vikt, material
  - Skaftmaterial, handtag

## UI-komponenter

### Smart formulär
```
Välj tillverkare: [Hultafors ▼] → Fyller automatiskt i vanliga mått
Modell: [_________]
Status: [Köpt ▼] [Mottagen/Ägd]
```

### Filter i yxlistan
```
Visa: [Alla] [Köpta] [Mottagna] [Tillverkare ▼]
```

### Snabbåtgärder
- "Markera som mottagen" knapp direkt i listan
- "Lägg till mått" knapp för köpta yxor
- "Lägg till bilder" knapp för mottagna yxor

## Tekniska förbättringar
- **Drag & drop** för bilder ✅
- **Bildkomprimering** automatiskt ✅
- **Mobilvänligt** - mät mått direkt på telefonen ✅
- **Backup** - automatiskt spara utkast

## Prioritering
1. Status-fält på yxor (Köpt/Mottagen)
2. Filter i yxlistan
3. Grundläggande formulär för att skapa/redigera yxor ✅
4. Smart funktioner (mallar, auto-save, etc.)

## Beslut tagna
- ✅ Ingen dashboard för mottagning (filter räcker)
- ✅ Enkla status: Köpt och Mottagen/Ägd
- ✅ Mallar för vanliga tillverkare/mått
- ✅ Snabbåtgärder i yxlistan
- ✅ Smart formulär med auto-fill
- ✅ Mobilvänlig bilduppladdning med kamerastöd
- ✅ Förhandsvisning och borttagning av bilder
- ✅ Automatisk filnamnshantering och .webp-generering
- ✅ Gruppbaserad navigering i lightbox (endast inom samma bildtyp)
- ✅ Vänsterställd text i lightbox för bättre läsbarhet av längre beskrivningar
- ✅ Semi-bold styling för bildtext för bättre framträdande
- ✅ Navigationsknappar med bra kontrast (`btn-outline-dark` med vit bakgrund)
- ✅ Inline-redigering och drag & drop för tillverkarbilder och -länkar
- ✅ Klickbara kort för bilder (lightbox) och aktiva länkar (ny flik)
- ✅ Visuell hantering för inaktiva länkar (gråtonad, URL som text, "Inaktiv"-badge)
- ✅ Hover-effekter på bild- och länkkort för bättre användarupplevelse
- ✅ Template filter för att visa information i tillverkarlistan (strippa markdown, begränsa längd)

## UX-principer för lightbox och bildhantering
- **Navigationslogik:** Bläddra endast inom samma bildtyp (Stämplar eller Övriga bilder) för bättre användarupplevelse
- **Kontrast:** Använd mörka knappar med vit bakgrund för bra synlighet på alla bakgrunder
- **Text-justering:** Längre beskrivningar är vänsterställda för bättre läsbarhet
- **Visuell feedback:** Bildräknare visar position i gruppen ("X av Y")
- **Responsiv design:** Navigationsknappar anpassas för olika skärmstorlekar

## Nästa steg
Implementera status-fält och filter i yxlistan som första prioritet. 