# UX Design Diskussion - AxeCollection

## Designprinciper och beslut

### Färgschema och visuell hierarki
- **Grön**: Används för status "Mottagen/Ägd" och positiva ekonomiska värden
- **Röd**: Används för status "Köpt" och negativa ekonomiska värden (köp)
- **Blå**: Används för neutrala element och sälj-transaktioner
- **Grå**: Används för inaktiva element och sekundär information
- **Färgkonfliktlösning**: Undvik att använda grön/röd för plattformar eftersom de redan används för status/ekonomi

### Typografi och läsbarhet
- **Fetstil för plattformsnamn**: Alla plattformsnamn visas med `<strong>` för tydlighet
- **Semi-bold för bildtext**: Bildbeskrivningar använder semi-bold för bättre framträdande
- **Vänsterställd text i lightbox**: Längre beskrivningar är vänsterställda för bättre läsbarhet
- **Konsekvent formatering**: Använd ISO-format (ÅÅÅÅ-MM-DD) för datum genom hela applikationen

### Responsiv design och mobilförst approach
- **Mobil-först design**: Designa för mobil först och anpassa sedan för desktop
- **Touch-vänliga knappar**: Minsta 44px touch-target för alla klickbara element
- **Text på mobil**: Dölj text på mobil för sekundära funktioner (endast ikon), men visa alltid text för viktiga funktioner
- **Responsiv layout**: Testa alltid på både mobil och desktop innan implementation anses klar

### Knappplacering och användarflöde
- **Logisk placering**: "Lägg till transaktion" visas under yxinformationen när inga transaktioner finns
- **Snabbåtgärder**: Kritiska funktioner som "Markera som mottagen" direkt i listor
- **Konsekvent mönster**: Använd samma mönster för liknande funktioner (t.ex. AJAX-sökning)
- **Visuell feedback**: Tydliga notifikationer och laddningsindikatorer för alla operationer

## UX-principer för bildhantering

### Lightbox och navigering
- **Navigationslogik**: Bläddra endast inom samma bildtyp (Stämplar eller Övriga bilder) för bättre användarupplevelse
- **Kontrast**: Använd mörka knappar med vit bakgrund för bra synlighet på alla bakgrunder
- **Visuell feedback**: Bildräknare visar position i gruppen ("X av Y")
- **Responsiv design**: Navigationsknappar anpassas för olika skärmstorlekar

### Drag & drop och interaktion
- **Visuell feedback vid borttagning**: Tydlig overlay med "KOMMER ATT TAS BORT" och padding
- **Hover-effekter**: Subtila hover-effekter på bild- och länkkort för bättre användarupplevelse
- **Klickbara kort**: Hela kortet är klickbart för bilder (lightbox) och aktiva länkar (ny flik)
- **Redigeringsknappar**: Placeras så de inte triggar klicket på kortet

## UX-principer för formulär och inmatning

### Smart formulär och auto-fill
- **Mallar för vanliga tillverkare**: När "Hultafors" väljs fylls automatiskt i vanliga mått och kommentarer
- **Måttmallar**: För olika yxtyper (fällkniv, köksyxa) fylls vanliga mått automatiskt
- **Smart sökning**: "Hultafors" ger förslag på "Hultafors AB"
- **Kontaktförslag**: Om försäljaren redan finns, föreslå den

### Validering och feedback
- **Tydlig felhantering**: Visa specifika felmeddelanden för varje fält
- **Realtidsvalidering**: Validera fält medan användaren skriver
- **Positiv feedback**: Visa bekräftelse när operationer lyckas
- **Laddningsindikatorer**: Visa spinner under pågående operationer

## UX-principer för statistik och visualisering

### Diagram och grafer
- **Staplade stapeldiagram**: Effektiva för att visa fördelning mellan kategorier (köp vs sälj)
- **Färgkodning**: Röd för köp/utgifter, blå för sälj/intäkter, grön för köp-aktivitet
- **Tooltips**: Exakta värden förbättrar användbarheten av diagram
- **Responsiv design**: Kritisk för diagram - Chart.js hanterar detta automatiskt

### Senaste aktivitet-sektion
- **Tre kort i rad**: Ger bra översikt utan att ta för mycket plats
- **Begränsa till 5 objekt**: Per kategori för att undvika överväldigande information
- **Länkar till detaljsidor**: Gör informationen användbar istället för bara informativ
- **Färgkodade headers**: Hjälper användaren att snabbt identifiera kategorier

## UX-principer för flaggemoji och internationell användning

### Konsekvent visning
- **Alla relevanta ställen**: Flaggemoji visas på alla ställen där kontakter visas
- **Responsiv design**: Anpassar sig för olika skärmstorlekar med lämplig marginal
- **Sökbara landsfält**: Flagg-emoji och landsnamn förbättrar användarvänligheten
- **ISO-standarder**: Använd ISO 3166-1 alpha-2 för landskoder för internationell kompatibilitet

## Designbeslut och kompromisser

### Enkel vs komplex lösning
- **KISS-princip**: Enkel lösning (dropdown) är ofta bättre än komplex (sökbar select) för grundläggande funktionalitet
- **Cross-browser kompatibilitet**: Standard HTML `<select>` fungerar på alla enheter och webbläsare
- **Underhållbarhet**: Enklare kod är lättare att underhålla och debugga

### Mobil vs desktop
- **Touch-vänliga knappar**: Även på desktop för konsekvent användarupplevelse
- **Responsiv layout**: Fungerar bra på alla enheter med touch-vänliga knappar
- **Text-visning**: Tydliga riktlinjer för när text ska döljas på mobil vs alltid visas

## Framtida UX-förbättringar

### Planerade förbättringar
- **Tangentbordsnavigering**: Piltangenter för att bläddra mellan bilder i lightbox
- **Touch-gester**: Swipe för att bläddra på mobil
- **Zoom-funktionalitet**: Se bilder i full storlek i lightbox
- **Bulk-operationer**: Redigera flera bilder samtidigt

### Önskade förbättringar
- **QR-kod**: Snabbt visa en yxa på mobilen
- **Offline-funktionalitet**: Spara data lokalt och synkronisera när internet finns
- **Auto-save**: Spara automatiskt under processen
- **Backup**: Automatiskt spara utkast 