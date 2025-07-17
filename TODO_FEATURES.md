# Projektidéer & förbättringsförslag

En checklista för vidareutveckling av AxeCollection. Bocka av med [x] när klart!

## Bildhantering

1. [x] Bildkomprimering/optimering vid uppladdning – Gör bilder snabbare att ladda på mobil.
2. [x] Stöd för flera bildformat (t.ex. webp) – För bättre prestanda och kompatibilitet.
3. [x] Lazy loading av bilder i galleriet – Ladda bara bilder som syns.
4. [x] Mobilvänlig bilduppladdning (kamera, filväljare, URL) – Stöd för att ta bilder direkt med mobilkamera.
5. [x] Förhandsvisning av bilder innan uppladdning – Se bilder innan de sparas.
6. [x] Automatisk hantering av filnamn och ordning på bilder – Bilder får konsekventa namn och ordning.
7. [x] Automatisk borttagning av .webp-filer vid radering – Ingen manuell hantering krävs.
8. [x] Visuell feedback vid borttagning av bilder (overlay med padding) – Tydlig indikation på vad som tas bort.
9. [x] Responsiv layout för bildhantering – Fungerar bra på alla enheter.
10. [x] Bugfix: Duplicering och förhandsvisning av bilder – Korrekt hantering av flera bilder.
11. [x] Bugfix: Felhantering vid bildborttagning – Robust hantering av borttagning.
12. [x] Motsvarande bildhantering för tillverkare – Implementera samma avancerade bildhantering (drag & drop, ordning, .webp-stöd) för tillverkarbilder som redan finns för yxbilder.
    - [x] 12.1 Kategorisering av bilder (Stämpel/Övrig bild)
    - [x] 12.2 Order-fält för sortering
    - [x] 12.3 Förbättrad admin med fieldsets
    - [x] 12.4 Drag & drop för bildordning (som för yxbilder)
13. [x] Drag & drop för bildordning i redigeringsläge.
14. [x] Hantera många stämpelbilder på tillverkarsidan (t.ex. paginering, grid, lightbox eller liknande UX-lösning).
    - [x] 14.1 Kategoriserad visning (Stämplar vs Övriga bilder)
    - [x] 14.2 Grid-layout med kort
    - [x] 14.3 Lightbox för bildförhandsvisning med navigationsknappar
15. [x] URL-uppladdning av bilder – Ladda ner bilder från URL:er med förhandsvisning och drag & drop.
    - [x] 15.1 Förhandsvisning av URL:er som riktiga bilder
    - [x] 15.2 Drag & drop för URL:er i förhandsvisning
    - [x] 15.3 Automatisk nedladdning och lagring av bilder från URL:er
    - [x] 15.4 Fallback för URL:er som inte kan laddas (CORS-problem)
    - [x] 15.5 Laddningsindikator under nedladdning av URL:er
    - [x] 15.6 Optimera omdöpningslogik - kör endast när nödvändigt

## Användarupplevelse

16. [x] Förbättrad responsivitet – Testa och förbättra för surfplattor och olika mobilstorlekar.
17. [x] Touchvänliga knappar även på desktop – T.ex. piltangenter för bildbyte.
18. [x] Mörkt läge (dark mode) för hela tjänsten – Respekterar operativsystemets tema automatiskt och har en sol/måne-knapp för manuell växling.
19. [x] Notifikationssystem – Snygga notifikationer för användarfeedback vid alla operationer.
20. [x] Laddningsindikatorer – Spinner och inaktiverade knappar under pågående operationer.
21. [x] AJAX-animationer – Smooth övergångar och animationer för bättre användarupplevelse.

## Sök och filtrering

22. [x] AJAX-sökning för kontakter – Realtidssökning med dropdown-resultat för befintliga kontakter.
23. [x] AJAX-sökning för plattformar – Realtidssökning med dropdown-resultat för befintliga plattformar.
24. [x] Moderniserad AJAX-sökning för kontakt och plattform i yxformuläret
    - [x] 24.1 Återställt och moderniserat JavaScript för AJAX-sökning
    - [x] 24.2 Lagt till saknade plattformsfält i forms.py (platform_name, platform_url, platform_comment)
    - [x] 24.3 Uppdaterat axe_create i views_axe.py med komplett formulärhantering för kontakt, plattform och transaktion
    - [x] 24.4 Lagt till dropdown-containers för sökresultat i axe_form.html
    - [x] 24.5 Implementerat funktioner för att visa/dölja sektioner för nya kontakter och plattformar
    - [x] 24.6 Lagt till next_id i context för att visa nästa yx-ID
    - [x] 24.7 Förbättrat felhantering och användarupplevelse
25. [x] Sökfunktion för yxor och tillverkare – Snabbt hitta yxor, tillverkare eller transaktioner.
26. [x] Filtrering på t.ex. tillverkare, typ, årtal, mm.
27. [x] Plattformsfilter och visning i yxlistan
    - [x] 27.1 Möjliggör filtrering av yxor på plattform i yxlistan
    - [x] 27.2 Visar alla plattformar för varje yxa direkt i tabellen
    - [x] 27.3 Varje plattform får en unik färg för ökad överskådlighet
    - [x] 27.4 Alla plattformsnamn visas med konsekvent fetstil för tydlighet
    - [x] 27.5 Förbättrar användarupplevelsen vid sortering och översikt av yxor
    - [x] 27.6 Fixat Django ORM-relationer med related_name='transactions'
    - [x] 27.7 Förbättrad CSV-export med hantering av radbrytningar
    - [x] 27.8 Fixat statistikkort som nu visar korrekt data för filtrerade yxor (tidigare visade alltid hela samlingen)
28. [x] Måttkolumn och filtrering i yxlistan
    - [x] 28.1 Lägg till "Mått"-kolumn i yxlistan med linjal-ikon för yxor med registrerade mått
    - [x] 28.2 Visa antalet registrerade mått bredvid linjal-ikonen (t.ex. "📏 3" för 3 mått)
    - [x] 28.3 Tooltip/popup som visar måtten vid hovring över ikonen
    - [x] 28.4 Filter för att visa endast yxor med/utan mått
    - [x] 28.5 Responsiv design för måttkolumnen på olika skärmstorlekar

## Yxhantering och inmatning

27. [x] Redigera transaktion, plattform och kontakt för en yxa via detaljvyn
    - [x] 27.1 Visa "Lägg till transaktion"-knapp om ingen transaktion finns
    - [x] 27.2 Visa "Redigera transaktioner"-knapp om en eller flera transaktioner finns
    - [x] 27.3 Bygg formulär för att lägga till/redigera transaktion (pris, frakt, kontakt, plattform, kommentar, datum)
    - [x] 27.4 Implementera AJAX-sökning för kontakt och plattform i formuläret
    - [x] 27.5 Möjlighet att skapa ny kontakt/plattform direkt i formuläret
    - [x] 27.6 Möjlighet att ta bort transaktion
28. [x] UI för att skapa nya yxor i samlingen – Användarvänligt formulär för att lägga till yxor.
29. [x] UI för att redigera befintliga yxor – Möjlighet att uppdatera information efter mottagning.
30. [x] Status-fält och filter – Status "Köpt" vs "Mottagen/Ägd" med filter och snabbåtgärder (markera som mottagen) i yxlistan.
31. [x] Arbetsflöde för inköp: 
    - Skapa/redigera yxa (tillverkare, modell, kommentar) ✅
    - Ladda upp bilder från auktion/annons ✅
    - Skapa/redigera kontakt (försäljare på Tradera etc.) ✅
    - Skapa transaktion (inköp med pris, frakt, datum) ✅
32. [x] Arbetsflöde för mottagning:
    - [x] Lägg till fler bilder av mottagen yxa (via befintlig redigeringsfunktionalitet)
    - [x] Mät och registrera mått (nytt måttinmatningsformulär med mallar)
    - [x] Uppdatera eventuell felaktig information (via befintlig redigeringsfunktionalitet)
    - [x] Dedikerat mottagningsarbetsflöde med steg-för-steg process
    - [x] Måttmallar för olika yxtyper (standard, fällkniv, köksyxa)
    - [x] AJAX-hantering för måttinmatning och borttagning
    - [x] Länkar till mottagningsarbetsflödet från yxlistan och yxdetail
33. [x] Förbättrad mått-UX i redigeringsvyn:
    - [x] Batch-läggning av mått med tydlig info och notifikation
    - [x] Inline-redigering av mått (värde och enhet) via AJAX
    - [x] Borttagning av mått med snygg animation (utan sidladdning)
    - [x] Visuell feedback vid alla måttoperationer (notifikationer, laddningsindikatorer)
    - [x] Förbättrad felhantering och återställning av UI
    - [x] Fördröjd sidladdning för att visa notifikationer
    - [x] Möjlighet att ta bort enskilda rader från batch-måttformuläret (soptunne-ikon per rad)
    - [x] Förbättrad DRY-princip med återanvändbar JavaScript-kod
    - [x] Automatisk UI-uppdatering vid borttagning av mått (tomt tillstånd, räknare)
    - [x] Event listener-baserad hantering istället för inline onclick
    - [x] Korrekt omindexering av batch-formulärrader vid borttagning
34. [x] Snabbval av tillverkare – Dropdown för att välja tillverkare.
35. [x] Kontakthantering – Skapa nya kontakter direkt från yxformuläret med smart matchning.
36. [x] Transaktionshantering – Koppla yxor till köp/försäljning med pris, frakt och datum.
37. [x] Plattformshantering – Skapa nya plattformar direkt från yxformuläret med smart matchning.
38. [x] Automatisk transaktionstypbestämning – Baserat på pris (negativ = köp, positiv = sälj).
39. [x] Separata formulär för skapande vs redigering – Olika fält visas beroende på om yxa skapas eller redigeras.

## Admin och datahantering

40. [x] Förbättrad admin-raderingsvy för yxor – Tydlig lista över vad som tas bort, bockruta för bildradering.
41. [ ] Batchuppladdning av yxor – Möjlighet att ladda upp flera yxor samtidigt. **(Pausad – kräver vidare diskussion och behovsanalys innan implementation)**
42. [x] Export/import av data (CSV, Excel) direkt från admin.
43. [ ] Automatiska backuper av databasen.
44. [x] Eget administratörsgränssnitt för tillverkare
    - [x] 44.1 Redigera tillverkare-knapp kvar på nuvarande plats (endast namnändring)
    - [x] 44.2 Ny redigera-knapp i Informations-gruppen för att redigera information
    - [x] 44.3 Flytta "Lägg till bild"-knapp till Bildgalleri-gruppen
    - [x] 44.4 Flytta "Lägg till länk"-knapp till Länkar-gruppen
    - [x] 44.5 Implementera formulär för redigering av tillverkarnamn
    - [x] 44.6 Implementera formulär för redigering av information
    - [x] 44.7 WYSIWYG markdown-redigerare för informationsfält (EasyMDE)
    - [x] 44.8 AJAX-hantering för snabb redigering utan sidladdning
    - [x] 44.9 Validering och felhantering för alla formulär
    - [x] 44.10 Notifikationer för framgångsrika redigeringar
    - [x] 44.11 Döpa om fält från "comment" till "information"
    - [x] 44.12 Inline-redigering av tillverkarnamn med AJAX
    - [x] 44.13 Markdown-stöd för bildbeskrivningar med EasyMDE
    - [x] 44.14 Lightbox med redigeringsmöjligheter för tillverkarbilder
    - [x] 44.15 Drag & drop-funktionalitet för bildordning
    - [x] 44.16 Navigationsknappar i lightbox för att bläddra mellan bilder i samma grupp
    - [x] 44.17 Semi-bold styling för bildtext för bättre läsbarhet
    - [x] 44.18 Vänsterställd text i lightbox för bättre läsbarhet av längre beskrivningar
    - [x] 44.19 Inline-redigering, borttagning och drag & drop-sortering för tillverkarlänkar
    - [x] 44.20 Klickbara kort för bilder (öppnar lightbox) och aktiva länkar (öppnar i ny flik)
    - [x] 44.21 Visuell hantering för inaktiva länkar (gråtonad styling, URL som text, "Inaktiv"-badge)
    - [x] 44.22 Hover-effekter på bild- och länkkort för bättre användarupplevelse
    - [x] 44.23 Template filter för att visa information i tillverkarlistan (strippa markdown, begränsa längd)

## Säkerhet och användare

45. [ ] Inloggning/behörighet – Privata delar eller flera användare.
46. [ ] Loggning av ändringar (audit trail).
47. [ ] Inför inloggning/adminvy så att endast inloggade kan redigera, och visa en publik vy där känsliga uppgifter (t.ex. kontaktnamn, personuppgifter och ev. priser) maskeras eller döljs.

## Prestanda och kodkvalitet

48. [ ] Fler automatiska tester (unit/integration).
49. [ ] CI/CD – Automatiska tester vid push (GitHub Actions).
50. [ ] Kodgranskning – Linting och kodstil (t.ex. black, flake8).
51. [x] Periodvis kodgranskning: Gå igenom och granska koden stegvis för att identifiera behov av övergripande refaktorering, buggfixar och tillsnyggning. Gör detta processvis så att varje steg kan testas innan nästa påbörjas.
    - [x] 51.1 Refaktorera vyer till mindre filer (views_axe.py, views_contact.py, views_manufacturer.py, views_transaction.py)
    - [x] 51.2 Flytta statistik- och ekonomi-beräkning från vyer till model-properties
    - [x] 51.3 Skapa återanvändbara template-includes för statistik-kort (_stat_card.html, _axe_stats_cards.html, _contact_stats_cards.html, _transaction_stats_cards.html)
    - [x] 51.4 Uppdatera templates för att använda nya includes och model-properties
    - [x] 51.5 Förenkla fler templates med includes och templatetags (t.ex. transaktionsrader, status-badges, breadcrumbs)
    - [x] 51.5.1 Förbättrade breadcrumbs och rubrik på detaljsidan: ID - Tillverkare - Modell
    - [x] 51.6 Refaktorera formulär med återanvändbara komponenter
    - [x] Skapat och infört _form_field.html, _form_checkbox.html, _form_input_group.html
    - [x] Använt dessa i axe_form.html för kontakt, plattform, transaktion
    - [x] Förenklat och DRY:at markup för fält, checkboxar och input-grupper
    - [x] Förbättrat frontend-UX för dropdowns och sektioner
    - [x] Fixat buggar kring next_id och TemplateSyntaxError
    - [x] Dokumenterat vanliga fel och lösningar
    - [ ] 51.7 Lägg till tester för vyer, modeller och templatetags
    - [ ] 51.8 Prestandaoptimering (caching, lazy loading, etc.)
52. [x] Dokumentation av förbättringar - Uppdatera markdown-filer med genomförda förbättringar och lärdomar

## Design och presentation

53. [x] Bättre visuell presentation av galleriet, t.ex. lightbox för bilder.
54. [x] Förbättrad UI med badges och ikoner – Tydligare visning av transaktionstyper med ikoner.
55. [x] Förbättrad tillverkarsida – ID som badge, kommentar som egen sektion, hela bredden för korten.
56. [x] Visa statistik (t.ex. antal yxor, mest populära tillverkare, dyraste köp).
    - [x] 56.1 Dedikerad statistik-dashboard med samlingsöversikt
    - [x] 56.2 Topplistor för mest aktiva tillverkare, plattformar och kontakter
    - [x] 56.3 Ekonomisk översikt med totala köp- och försäljningsvärden
    - [x] 56.4 Realtidsstatistik som uppdateras baserat på aktiva filter
    - [x] 56.5 Fixat Django ORM-problem med annotate och properties
56.6 [x] Visa antal yxor i samlingen över tid (linje- eller stapeldiagram)
    - [x] 56.6.1 Kombinerad tidslinje med "Yxor köpta (total)" och "Yxor i samlingen"
    - [x] 56.6.2 Grupperad per månad baserat på transaktionsdatum
    - [x] 56.6.3 Visar tydligt skillnaden mellan köpta och kvarvarande yxor
    - [x] 56.6.4 Chart.js-implementation med två färgkodade linjer
56.7 [x] Visa totala inköpskostnader och försäljningsintäkter över tid (diagram)
    - [x] 56.7.1 Stapeldiagram med transaktionsvärden per månad
    - [x] 56.7.2 Röda staplar för köpvärde, gröna för försäljningsvärde
    - [x] 56.7.3 Visar aktivitet över tid istället för kumulativa värden
    - [x] 56.7.4 Svensk formatering av belopp i tooltips och axlar
56.8 [x] Visa dyraste och billigaste köp/sälj i topplistan, med länk till respektive yxa
    - [x] 56.8.1 Länkar till yxorna från alla transaktionslistor
    - [x] 56.8.2 Förbättrad layout med radbrytning för långa yxnamn
    - [x] 56.8.3 Flexbox-layout för bättre "tabb-avstånd" och läsbarhet
    - [x] 56.8.4 Billigaste köp och försäljningar tillagda
56.9 [x] Visa mest aktiva månader (när köps/säljs flest yxor)
    - [x] 56.9.1 Staplat stapeldiagram som visar antal köp/sälj per månad
    - [x] 56.9.2 Färgkodning: röd för köp, blå för sälj
    - [x] 56.9.3 Tooltip med exakt antal transaktioner per typ
    - [x] 56.9.4 Placerat efter ekonomiska diagrammen på statistiksidan
56.10 [x] Visa senaste aktivitet (senaste köp, sälj, tillagd yxa)
    - [x] 56.10.1 Tre kort för senaste köp, försäljningar och tillagda yxor
    - [x] 56.10.2 Visar de 5 senaste aktiviteterna per kategori
    - [x] 56.10.3 Länkar till respektive yxas detaljsida
    - [x] 56.10.4 Färgkodning: grön för köp, röd för sälj, blå för tillagda yxor
    - [x] 56.10.5 Visar datum och pris/tillverkare för varje aktivitet
57. [ ] QR-kod för att snabbt visa en yxa på mobilen. **(Pausad – kräver vidare diskussion och behovsanalys innan implementation)**

## Framtida förbättringar

58. [ ] Förbättrad felhantering och validering i formulär.
59. [ ] Snabbare AJAX-sökningar med caching.
60. [ ] Tangentbordsnavigering i lightbox (piltangenter för att bläddra mellan bilder).
61. [ ] Touch-gester för mobil navigering i lightbox (swipe för att bläddra).
62. [ ] Zoom-funktionalitet i lightbox för att se bilder i full storlek.
63. [ ] Automatisk bildrotation baserat på EXIF-data.
64. [ ] Bulk-redigering av bilder (redigera flera bilder samtidigt).
65. [ ] Bildkommentarer med @-mentions för att länka till tillverkare eller yxor.

## Tekniska lärdomar från utveckling

### Django ORM och databasfält
- **created_at vs id för sortering**: När `created_at`-fält saknas i modellen, använd `id` för att sortera efter skapandedatum (högre ID = nyare objekt)
- **FieldError-hantering**: Validera att fältnamn finns i modellen innan användning i `order_by()` eller andra ORM-operationer

### Datumformatering
- **Konsekvent ISO-format**: Använd `Y-m-d` (ÅÅÅÅ-MM-DD) för konsekvent datumformatering i hela applikationen
- **Django template filters**: `{{ date|date:"Y-m-d" }}` för ISO-formatering

### Statistik och visualisering
- **Chart.js för staplade diagram**: Använd `stacked: true` för att visa köp och sälj i samma stapel
- **Färgkodning**: Röd för köp, blå för sälj, grön för köp-aktivitet, röd för sälj-aktivitet, blå för tillagda objekt
- **Responsiv design**: Använd Bootstrap-kort med `h-100` för jämn höjd på olika skärmstorlekar

### Användarupplevelse
- **Senaste aktivitet**: Visa de 5 senaste aktiviteterna per kategori för snabb överblick
- **Länkar till detaljsidor**: Alla transaktionslistor och topplistor ska länka till respektive yxas detaljsida
- **Tydlig kategorisering**: Använd färgkodade headers och badges för enkel identifiering

### Felhantering
- **Django server errors**: Kontrollera terminalen för detaljerade felmeddelanden vid 500-fel
- **Linter-fel**: Åtgärda syntaxfel och saknade imports innan testning
- **Git återställning**: Använd `git restore .` för att snabbt återställa oönskade ändringar

 