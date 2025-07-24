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
16. [x] Fixa rearranging av yxbilder – Implementera drag & drop-funktionalitet för att ändra ordning på yxbilder i galleriet och redigeringsläge.
    - [x] 16.1 Drag & drop-API för att uppdatera bildordning
    - [x] 16.2 Visuell feedback under drag-operationer
    - [x] 16.3 Automatisk uppdatering av filnamn efter omordning
    - [x] 16.4 Testa funktionaliteten med demobilder

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
24. [x] Flaggemoji för kontakter – Visar landskod som flaggemoji bredvid kontaktnamn på alla relevanta ställen.
25. [x] Global sökning i navbar – Sökfält i menyn som söker i yxor, kontakter, tillverkare och transaktioner med grupperade resultat.
    - [x] 25.1 Sökfält i navbar med responsiv design
    - [x] 25.2 Backend-endpoint för global sökning (/api/search/global/)
    - [x] 25.3 Sökning i yxor (tillverkare, modell, kommentar, ID)
    - [x] 25.4 Sökning i kontakter (namn, alias, e-post)
    - [x] 25.5 Sökning i tillverkare (namn, information)
    - [x] 25.6 Sökning i transaktioner (yxa, kontakt, plattform)
    - [x] 25.7 Grupperade resultat med ikoner och antal
    - [x] 25.8 Kortkommando Ctrl+K för att fokusera sökfältet
    - [x] 25.9 Länkar till detaljsidor för varje resultat
    - [x] 25.10 Flaggemoji för kontakter i sökresultaten
    - [x] 24.1 Lägg till country_code fält (ISO 3166-1 alpha-2) i Contact-modellen
    - [x] 24.2 Uppdatera befintliga kontakter med landskod för Sverige och Finland
    - [x] 24.3 Skapa country_flag template filter för att konvertera landskod till flaggemoji
    - [x] 24.4 Uppdatera ContactForm med sökbart select-fält med flagg-emoji och landsnamn
    - [x] 24.5 Lägg till flaggemoji på kontaktdetaljsidan (rubrik)
    - [x] 24.6 Lägg till flaggemoji i transaktionshistoriken på yxdetaljsidan
    - [x] 24.7 Lägg till flaggemoji i transaktioner på tillverkardetaljsidan
    - [x] 24.8 Lägg till flaggemoji i kontakter som handlat med tillverkaren
    - [x] 24.9 Lägg till flaggemoji i mest aktiva kontakter på statistik-sidan
    - [x] 24.10 Visa flaggemoji bredvid kontaktnamn i yxformuläret
    - [x] 24.11 Visa flaggemoji i kontaktlistan
    - [x] 24.12 Visa flaggemoji i transaktionslistan
26. [x] Moderniserad AJAX-sökning för kontakt och plattform i yxformuläret
    - [x] 26.1 Återställt och moderniserat JavaScript för AJAX-sökning
    - [x] 26.2 Lagt till saknade plattformsfält i forms.py (platform_name, platform_url, platform_comment)
    - [x] 26.3 Uppdaterat axe_create i views_axe.py med komplett formulärhantering för kontakt, plattform och transaktion
    - [x] 26.4 Lagt till dropdown-containers för sökresultat i axe_form.html
    - [x] 26.5 Implementerat funktioner för att visa/dölja sektioner för nya kontakter och plattformar
    - [x] 26.6 Lagt till next_id i context för att visa nästa yx-ID
    - [x] 26.7 Förbättrat felhantering och användarupplevelse
27. [x] Sökfunktion för yxor och tillverkare – Snabbt hitta yxor, tillverkare eller transaktioner.
28. [x] Filtrering på t.ex. tillverkare, typ, årtal, mm.
29. [x] Plattformsfilter och visning i yxlistan
    - [x] 29.1 Möjliggör filtrering av yxor på plattform i yxlistan
    - [x] 29.2 Visar alla plattformar för varje yxa direkt i tabellen
    - [x] 29.3 Varje plattform får en unik färg för ökad överskådlighet
    - [x] 29.4 Alla plattformsnamn visas med konsekvent fetstil för tydlighet
    - [x] 29.5 Förbättrar användarupplevelsen vid sortering och översikt av yxor
    - [x] 29.6 Fixat Django ORM-relationer med related_name='transactions'
    - [x] 29.7 Förbättrad CSV-export med hantering av radbrytningar
    - [x] 29.8 Fixat statistikkort som nu visar korrekt data för filtrerade yxor (tidigare visade alltid hela samlingen)
30. [x] Måttkolumn och filtrering i yxlistan
    - [x] 30.1 Lägg till "Mått"-kolumn i yxlistan med linjal-ikon för yxor med registrerade mått
    - [x] 30.2 Visa antalet registrerade mått bredvid linjal-ikonen (t.ex. "📏 3" för 3 mått)
    - [x] 30.3 Tooltip/popup som visar måtten vid hovring över ikonen

## Docker och Deployment

31. [x] Fixa Docker startup-problem
    - [x] 31.1 "exec /app/start.sh: no such file or directory" - fixade line endings och behörigheter
    - [x] 31.2 Nginx visar standard-sida istället för Django - korrekt Nginx-konfiguration inbyggd
    - [x] 31.3 Windows line endings i start.sh - automatisk konvertering i Dockerfile
    - [x] 31.4 Behörigheter för Unraid (nobody:users) - korrekt UID/GID-hantering
    - [x] 31.5 CSRF-fel vid inloggning - dynamisk host-konfiguration via UI och miljövariabler
    - [x] 31.6 Demo-installationer - stöd för flera instanser med olika host-konfigurationer
    - [x] 31.7 Databasbehörigheter på Unraid - automatisk fix av readonly database
    - [x] 31.8 Robust startup-process - automatisk skapande av kataloger och behörigheter

32. [x] Fixa dark mode-konsistens
    - [x] 32.1 Kontaktdetaljsida - vita bakgrunder på kontaktinformation, medlemskap och adress
    - [x] 32.2 Systematisk genomgång av alla sidor för dark mode-konsistens

33. [x] Lägg till footer
    - [x] 33.1 Designa footer med relevant information (version, länkar, kontakt)
    - [x] 33.2 Implementera footer på alla sidor
    - [x] 33.3 Anpassa footer för både light och dark mode

34. [ ] Kommentarsystem (framtida funktion)
    - [ ] 34.1 Möjlighet att kommentera yxor
    - [ ] 34.2 Möjlighet att kommentera tillverkare
    - [ ] 34.3 Moderationssystem för kommentarer
    - [ ] 34.4 Användarhantering för kommentarer

35. [ ] Implementera Django REST Framework och ViewSets
    - [ ] 35.1 Utvärdera nuvarande API-struktur och identifiera förbättringsmöjligheter
    - [ ] 35.2 Skapa serializers för alla modeller (Axe, Contact, Manufacturer, Transaction, etc.)
    - [ ] 35.3 Implementera ViewSets för CRUD-operationer
    - [ ] 35.4 Använda routers för automatisk URL-generering
    - [ ] 35.5 Lägg till browsable API för bättre utvecklarupplevelse
    - [ ] 35.6 Implementera filtrering och sökning via DRF-filter
    - [ ] 35.7 Lägg till pagination för stora datasets
    - [ ] 35.8 Säkerställ att befintlig AJAX-funktionalitet fungerar med nya API:er
    - [ ] 35.9 Dokumentera API:er med DRF:s inbyggda dokumentation

36. [x] Fixa enskilda mått
    - [x] 36.1 Ensamma mått kan inte läggas till, bara via batch-inlägg
    - [x] 36.2 Implementera funktionalitet för att lägga till enskilda mått
    - [x] 36.3 Testa att både enskilda och batch-mått fungerar korrekt

37. [ ] Fixa omorganisering av yxbilder i produktion
    - [ ] 37.1 Omorganisering av yxbilder fungerar inte på Unraid-produktionsservern
    - [ ] 37.2 Undersök skillnader mellan utvecklings- och produktionsmiljö
    - [ ] 37.3 Kontrollera filbehörigheter och sökvägar i produktion
    - [ ] 37.4 Testa drag & drop-funktionalitet i produktionsmiljö

38. [x] Formulär för tillverkarlänkar
    - [x] 38.1 Skapa formulär för att lägga till länkar och resurser på tillverkare
    - [x] 38.2 Implementera i tillverkardetaljsidan (för närvarande bara via Django admin)
    - [x] 38.3 Lägg till funktionalitet för att redigera och ta bort länkar
    - [x] 38.4 Säkerställ att order-fältet fungerar för sortering av länkar
    - [x] 30.4 Filter för att visa endast yxor med/utan mått
    - [x] 30.5 Responsiv design för måttkolumnen på olika skärmstorlekar

## Deployment och miljöhantering

1. [x] Automatisk hantering av sökvägar för olika miljöer
    - [x] 1.1 Skapa script för att fixa bildsökvägar vid deployment (Windows backslashes → Linux forward slashes)
    - [x] 1.2 Automatisk konvertering av `/app/media/` prefix för Docker-miljöer
    - [x] 1.3 Hantera sökvägar för både utvecklingsmiljö (Windows) och produktionsmiljö (Linux)
    - [x] 1.4 Integrera sökvägsfix i deployment-processen
    - [x] 1.5 Testa och verifiera att bilder fungerar i både test- och produktionsmiljö
2. [x] Media-filhantering i produktionsmiljö
    - [x] 2.1 Konfigurera Nginx för att servera media-filer i produktion
    - [x] 2.2 Eller implementera CDN-lösning för media-filer
    - [x] 2.3 Eller konfigurera Django för att servera media-filer i produktion (inte rekommenderat för hög belastning)
    - [x] 2.4 Testa och verifiera att alla bilder fungerar korrekt i produktionsmiljö
    - [x] 2.5 Dokumentera lösningen för framtida deployment

## Yxhantering och inmatning

31. [x] Redigera transaktion, plattform och kontakt för en yxa via detaljvyn
    - [x] 30.1 Visa "Lägg till transaktion"-knapp om ingen transaktion finns
    - [x] 30.2 Visa "Redigera transaktioner"-knapp om en eller flera transaktioner finns
    - [x] 30.3 Bygg formulär för att lägga till/redigera transaktion (pris, frakt, kontakt, plattform, kommentar, datum)
    - [x] 30.4 Implementera AJAX-sökning för kontakt och plattform i formuläret
    - [x] 30.5 Möjlighet att skapa ny kontakt/plattform direkt i formuläret
    - [x] 31.6 Möjlighet att ta bort transaktion
32. [x] UI för att skapa nya yxor i samlingen – Användarvänligt formulär för att lägga till yxor.
33. [x] UI för att redigera befintliga yxor – Möjlighet att uppdatera information efter mottagning.
34. [x] Status-fält och filter – Status "Köpt" vs "Mottagen/Ägd" med filter och snabbåtgärder (markera som mottagen) i yxlistan.
35. [x] Arbetsflöde för inköp: 
    - Skapa/redigera yxa (tillverkare, modell, kommentar) ✅
    - Ladda upp bilder från auktion/annons ✅
    - Skapa/redigera kontakt (försäljare på Tradera etc.) ✅
    - Skapa transaktion (inköp med pris, frakt, datum) ✅
35. [x] Arbetsflöde för mottagning:
    - [x] Lägg till fler bilder av mottagen yxa (via befintlig redigeringsfunktionalitet)
    - [x] Mät och registrera mått (nytt måttinmatningsformulär med mallar)
    - [x] Uppdatera eventuell felaktig information (via befintlig redigeringsfunktionalitet)
    - [x] Dedikerat mottagningsarbetsflöde med steg-för-steg process
    - [x] Måttmallar för olika yxtyper (standard, fällkniv, köksyxa)
    - [x] AJAX-hantering för måttinmatning och borttagning
    - [x] Länkar till mottagningsarbetsflödet från yxlistan och yxdetail
36. [x] Förbättrad mått-UX i redigeringsvyn:
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
    - [x] Bekräfta/ångra-knappar för inline-redigering istället för modaler
    - [x] Fullständig hantering av "Övrigt"-alternativet med textinput för anpassat måttnamn
    - [x] Bootstrap modal för borttagningsbekräftelse istället för alert()
    - [x] Korrekt skickande av data till backend (standardmått vs anpassade mått)
    - [x] Förhindring av dubbla anrop med spärr under uppdatering
    - [x] Automatisk enhetsfyllning när standardmåtttyper väljs
    - [x] Visuell feedback med spinner och inaktiverade knappar under uppdatering
37. [x] Snabbval av tillverkare – Dropdown för att välja tillverkare.
38. [x] Kontakthantering – Skapa nya kontakter direkt från yxformuläret med smart matchning.
39. [x] Transaktionshantering – Koppla yxor till köp/försäljning med pris, frakt och datum.
40. [x] Plattformshantering – Skapa nya plattformar direkt från yxformuläret med smart matchning.
41. [x] Automatisk transaktionstypbestämning – Baserat på pris (negativ = köp, positiv = sälj).
42. [x] Separata formulär för skapande vs redigering – Olika fält visas beroende på om yxa skapas eller redigeras.
43. [ ] Lägg till yxa via auktions-URL – Möjlighet att lägga till yxa genom att ange URL till vunnen Tradera- eller eBay-auktion.
    - [ ] 43.1 Implementera URL-parser för Tradera-auktioner som extraherar titel, beskrivning, bilder och slutpris
    - [ ] 43.2 Implementera URL-parser för eBay-auktioner med motsvarande funktionalitet  
    - [ ] 43.3 Automatisk förfyllning av yxformulär baserat på extraherad auktionsdata
    - [ ] 43.4 Automatisk nedladdning och lagring av auktionsbilder
    - [ ] 43.5 Intelligent kategorisering och tillverkargissning baserat på auktionsbeskrivning
    - [ ] 43.6 Automatisk skapande av transaktion med slutpris som köpvärde
    - [ ] 43.7 Felhantering för ogiltiga URL:er eller auktioner som inte kan parsas
    - [ ] 43.8 Stöd för olika auktionsformat och språk (svenska/engelska)
    - [ ] 43.9 Förhandsvisning av extraherad data innan sparning
    - [ ] 43.10 Möjlighet att redigera och justera automatiskt extraherad information

## Admin och datahantering

44. [x] Förbättrad admin-raderingsvy för yxor – Tydlig lista över vad som tas bort, bockruta för bildradering.
45. [ ] Batchuppladdning av yxor – Möjlighet att ladda upp flera yxor samtidigt. **(Pausad – kräver vidare diskussion och behovsanalys innan implementation)**
46. [x] Export/import av data (CSV, Excel) direkt från admin.
47. [x] Automatiska backuper av databasen.
    - [x] 47.1 Backup-funktionalitet flyttad från admin till systeminställningsvyn
    - [x] 47.2 Integrerad backup-hantering i settings.html med modern UI
    - [x] 47.3 Skapa, ta bort och återställ backuper direkt från inställningssidan
    - [x] 47.4 Statistik-visning för varje backup (antal yxor, kontakter, transaktioner)
    - [x] 47.5 Varningar för återställning med bekräftelsedialoger
    - [x] 47.6 Stöd för komprimerade backuper och media-filer
    - [x] 47.7 Automatisk rensning av gamla backuper (30 dagar)
    - [ ] 47.8 Backup-uppladdning via webbgränssnitt - Lösa problem med stora filer (>100MB) och nginx-konfiguration
        - [ ] 47.8.1 Fixa nginx client_max_body_size för stora backupfiler (2GB+)
        - [ ] 47.8.2 Förbättra JavaScript AJAX-uppladdning för stora filer
        - [ ] 47.8.3 Lägg till progress-indikator för stora filer
        - [ ] 47.8.4 Testa och verifiera att uppladdning fungerar för filer >100MB
        - [ ] 47.8.5 Dokumentera lösningen för framtida deployment
48. [x] Deployment-konfiguration för produktion med SQLite
    - [x] 48.1 Produktionssettings-fil med säkerhetskonfiguration
    - [x] 48.2 Dockerfile med Gunicorn för produktion
    - [x] 48.3 Docker Compose-konfiguration med volymer
    - [x] 48.4 Deployment-guide med steg-för-steg instruktioner
    - [x] 48.5 Backup-script för automatisk säkerhetskopiering
    - [x] 48.6 Miljövariabler och konfigurationsmallar
    - [x] 48.7 Nginx-konfiguration för webbserver
    - [x] 48.8 SSL/HTTPS-konfiguration
    - [x] 48.9 Logging och övervakning
    - [x] 48.10 Säkerhetsinställningar för produktion
    - [x] 48.11 Omorganisation av deployment-filer till deploy/-mapp
    - [x] 48.12 Uppdaterad dokumentation för ny struktur
    - [x] 48.13 Tydlig separation mellan utveckling och deployment
    - [x] 47.1 Backup-funktionalitet flyttad från admin till systeminställningsvyn
    - [x] 47.2 Integrerad backup-hantering i settings.html med modern UI
    - [x] 47.3 Skapa, ta bort och återställ backuper direkt från inställningssidan
    - [x] 47.4 Statistik-visning för varje backup (antal yxor, kontakter, transaktioner)
    - [x] 47.5 Varningar för återställning med bekräftelsedialoger
    - [x] 47.6 Stöd för komprimerade backuper och media-filer
    - [x] 47.7 Automatisk rensning av gamla backuper (30 dagar)
48. [x] Förbättrad navigering på systeminställningssidan.
    - [x] 48.1 Bootstrap navbar för in-page navigering mellan sektioner
    - [x] 48.2 Smooth scrolling med scroll-margin-top för att visa headers
    - [x] 48.3 Aktiv länk-markering baserat på scroll-position
    - [x] 48.4 Responsiv design för navigeringsmenyn
    - [x] 48.5 Korrekt styling med ljus bakgrund och mörk text
48. [x] Eget administratörsgränssnitt för tillverkare
    - [x] 48.1 Redigera tillverkare-knapp kvar på nuvarande plats (endast namnändring)
    - [x] 48.2 Ny redigera-knapp i Informations-gruppen för att redigera information
    - [x] 48.3 Flytta "Lägg till bild"-knapp till Bildgalleri-gruppen
    - [x] 48.4 Flytta "Lägg till länk"-knapp till Länkar-gruppen
    - [x] 48.5 Implementera formulär för redigering av tillverkarnamn
    - [x] 48.6 Implementera formulär för redigering av information
    - [x] 48.7 WYSIWYG markdown-redigerare för informationsfält (EasyMDE)
    - [x] 48.8 AJAX-hantering för snabb redigering utan sidladdning
    - [x] 48.9 Validering och felhantering för alla formulär
    - [x] 48.10 Notifikationer för framgångsrika redigeringar
    - [x] 48.11 Döpa om fält från "comment" till "information"
    - [x] 48.12 Inline-redigering av tillverkarnamn med AJAX
    - [x] 48.13 Markdown-stöd för bildbeskrivningar med EasyMDE
    - [x] 48.14 Lightbox med redigeringsmöjligheter för tillverkarbilder
    - [x] 48.15 Drag & drop-funktionalitet för bildordning
    - [x] 48.16 Navigationsknappar i lightbox för att bläddra mellan bilder i samma grupp
    - [x] 48.17 Semi-bold styling för bildtext för bättre läsbarhet
    - [x] 48.18 Vänsterställd text i lightbox för bättre läsbarhet av längre beskrivningar
    - [x] 48.19 Inline-redigering, borttagning och drag & drop-sortering för tillverkarlänkar
    - [x] 48.20 Klickbara kort för bilder (öppnar lightbox) och aktiva länkar (öppnar i ny flik)
    - [x] 48.21 Visuell hantering för inaktiva länkar (gråtonad styling, URL som text, "Inaktiv"-badge)
    - [x] 48.22 Hover-effekter på bild- och länkkort för bättre användarupplevelse
    - [x] 48.23 Template filter för att visa information i tillverkarlistan (strippa markdown, begränsa längd)
49. [ ] Måttmallshantering i inställningsmenyn – Möjlighet att skapa, redigera och hantera måttmallar direkt från systeminställningarna.
    - [ ] 49.1 Lägg till sektion för måttmallshantering i inställningsmenyn
    - [ ] 49.2 Formulär för att skapa nya måttmallar med namn och beskrivning
    - [ ] 49.3 Drag & drop-gränssnitt för att lägga till/ta bort måtttyper i mallar
    - [ ] 49.4 Redigering av befintliga måttmallar (namn, beskrivning, måtttyper)
    - [ ] 49.5 Borttagning av måttmallar med varning om konsekvenser
    - [ ] 49.6 Förhandsvisning av måttmallar med lista över inkluderade måtttyper
    - [ ] 49.7 Validering för att säkerställa att mallar har minst ett mått
    - [ ] 49.8 AJAX-hantering för snabb uppdatering utan sidladdning
    - [ ] 49.9 Enhethantering - Möjlighet att definiera/ändra måttenheter och välja enhet för måttmallar (gram, mm, grader °)

## Säkerhet och användare

50. [x] Inloggning/behörighet – Privata delar eller flera användare.
    - [x] 50.1 Django Auth-system implementerat med anpassade templates
    - [x] 50.2 Långa sessioner (30 dagar) för bättre användarupplevelse
    - [x] 50.3 Starka lösenord (minst 12 tecken) med Django's validering
    - [x] 50.4 Login/logout-funktionalitet med redirect till rätt sida
    - [x] 50.5 Användardropdown i navigationen med inställningar och logout
    - [x] 50.6 Responsiv login-modal i navigationen för snabb inloggning
    - [x] 50.7 Tydlig visuell feedback för inloggade vs icke-inloggade användare
51. [ ] Loggning av ändringar (audit trail).
52. [x] Inför inloggning/adminvy så att endast inloggade kan redigera, och visa en publik vy där känsliga uppgifter (t.ex. kontaktnamn, personuppgifter och ev. priser) maskeras eller döljs.
    - [x] 51.1 Settings-modell med konfigurerbara publika inställningar
    - [x] 51.2 Context processor som gör publika inställningar tillgängliga i alla templates
    - [x] 51.3 Automatisk filtrering av känslig data för icke-inloggade användare
    - [x] 51.4 Kontroll av användarstatus i alla vyer som visar känslig information
    - [x] 51.5 Fallback-hantering om Settings-modellen inte finns ännu
    - [x] 51.6 Dedikerad inställningssida för administratörer
    - [x] 51.7 Switches för alla publika inställningar med tydliga beskrivningar
    - [x] 51.8 Sajtinställningar för titel och beskrivning
    - [x] 51.9 Endast inloggade användare kan komma åt inställningarna
    - [x] 51.10 Global sökning respekterar publika inställningar
    - [x] 51.11 Kontaktsökning döljs för icke-inloggade användare om inställt
    - [x] 51.12 Plattformssökning kan konfigureras för publik/privat visning
    - [x] 51.13 Intelligent filtrering baserat på användarstatus
    - [x] 51.14 Yxlistan filtreras automatiskt för icke-inloggade användare
    - [x] 51.15 Transaktionsdata döljs eller visas baserat på inställningar
    - [x] 51.16 Kontaktinformation maskeras för publika användare
    - [x] 51.17 Prisinformation kan döljas för publika användare
    - [x] 51.18 Konsekvent navigation som anpassas efter användarstatus
    - [x] 51.19 Snygga ikoner och styling för användargränssnittet
    - [x] 51.20 Fixa yxdetaljsidan: Pris- och fraktkolumner visas fortfarande för publika användare trots att de ska döljas
- [x] 52.21 Fixa ekonomiska statistikkort på /yxor: Kronor-relaterade kort (vinst/förlust, totala värden) visas fortfarande för publika användare, ska döljas helt
53. [x] Vy för okopplade bilder – Rutnätsvy med funktioner för att ta bort och ladda ner bilder som flyttats från borttagna yxor.
    - [x] 53.1 Rutnätsvy med bildkort som visar filnamn, storlek och timestamp
    - [x] 53.2 Gruppering av bilder efter timestamp (när yxan togs bort)
    - [x] 53.3 Soptunne-ikon för att ta bort enskilda bilder
    - [x] 53.4 Ladda ner-ikon för att spara ner enskilda bilder
    - [x] 53.5 Massåtgärder med checkboxar för att välja flera bilder
    - [x] 53.6 "Ladda ner valda"-knapp som skapar ZIP-fil med valda bilder
    - [x] 53.7 Statistik-kort som visar totalt antal bilder, storlek och antal grupper
    - [x] 53.8 Responsiv design som fungerar på mobil och desktop
    - [x] 53.9 AJAX-hantering för borttagning utan sidladdning
    - [x] 53.10 Hover-effekter och animationer för bättre användarupplevelse
    - [x] 53.11 .webp-optimering: visar .webp-versioner för snabbare laddning men laddar ner originalfiler
    - [x] 53.12 Korrekt svenska grammatik med plural-former för "antal bilder" och "antal grupper"
    - [x] 53.13 Lägg till länk till vyn i admin-navigation (kommer att implementeras när inloggning/adminvy införs)
    - [x] 53.14 Implementera motsvarande hantering för borttagning av tillverkare och deras bilder (flytt till okopplade bilder)
        - [x] 53.14.1 Analysera vad som ska hända med yxor som tillhör tillverkaren (behåll som "okänd tillverkare" vs förhindra borttagning)
        - [x] 53.14.2 Utvärdera om funktionen ens behövs eller om tillverkare ska vara permanent

## Prestanda och kodkvalitet

54. [ ] Fler automatiska tester (unit/integration).
55. [ ] CI/CD – Automatiska tester vid push (GitHub Actions).
56. [ ] Kodgranskning – Linting och kodstil (t.ex. black, flake8).
57. [x] Periodvis kodgranskning: Gå igenom och granska koden stegvis för att identifiera behov av övergripande refaktorering, buggfixar och tillsnyggning. Gör detta processvis så att varje steg kan testas innan nästa påbörjas.
    - [x] 57.1 Refaktorera vyer till mindre filer (views_axe.py, views_contact.py, views_manufacturer.py, views_transaction.py)
    - [x] 57.2 Flytta statistik- och ekonomi-beräkning från vyer till model-properties
    - [x] 57.3 Skapa återanvändbara template-includes för statistik-kort (_stat_card.html, _axe_stats_cards.html, _contact_stats_cards.html, _transaction_stats_cards.html)
    - [x] 57.4 Uppdatera templates för att använda nya includes och model-properties
    - [x] 57.5 Förenkla fler templates med includes och templatetags (t.ex. transaktionsrader, status-badges, breadcrumbs)
    - [x] 57.5.1 Förbättrade breadcrumbs och rubrik på detaljsidan: ID - Tillverkare - Modell
    - [x] 57.6 Refaktorera formulär med återanvändbara komponenter
    - [x] Skapat och infört _form_field.html, _form_checkbox.html, _form_input_group.html
    - [x] Använt dessa i axe_form.html för kontakt, plattform, transaktion
    - [x] Förenklat och DRY:at markup för fält, checkboxar och input-grupper
    - [x] Förbättrat frontend-UX för dropdowns och sektioner
    - [x] Fixat buggar kring next_id och TemplateSyntaxError
    - [x] Dokumenterat vanliga fel och lösningar
    - [ ] 57.7 Lägg till tester för vyer, modeller och templatetags
    - [ ] 57.8 Prestandaoptimering (caching, lazy loading, etc.)

## Testdata och demo

73. [x] Skapa fingerad testdata för demo och testning
    - [x] 73.1 Exportera nuvarande databas-struktur för att förstå datamodellen
    - [x] 73.2 Skapa script för att generera realistisk testdata (yxor, tillverkare, kontakter, transaktioner)
    - [x] 73.3 Inkludera olika typer av yxor med varierande mått, bilder och transaktioner
    - [x] 73.4 Skapa tillverkare med olika antal bilder och länkar
    - [x] 73.5 Generera kontakter från olika länder med flaggemoji
    - [x] 73.6 Skapa transaktioner med olika plattformar och priser
    - [x] 73.7 Testa alla funktioner med testdata (sökning, filtrering, statistik, etc.)
    - [ ] 73.8 Förbereda för publik demo-webbplats
    - [x] 73.9 Dokumentera hur man återställer till testdata

74. [ ] Docker demo-läge med miljövariabel
    - [ ] 74.1 Lägg till miljövariabel DEMO_MODE för Docker-containern
    - [ ] 74.2 Implementera logik som kontrollerar DEMO_MODE vid container-start
    - [ ] 74.3 Automatisk körning av `generate_test_data --clear` när DEMO_MODE=true
    - [ ] 74.4 Säkerställ att demo-läget endast körs vid container-start, inte vid reload
    - [ ] 74.5 Dokumentera användning av demo-läge i deployment-guider
    - [ ] 74.6 Testa demo-läge i olika Docker-miljöer (utveckling, produktion)

57. [x] Dokumentation av förbättringar - Uppdatera markdown-filer med genomförda förbättringar och lärdomar

## Design och presentation

58. [x] Bättre visuell presentation av galleriet, t.ex. lightbox för bilder.
59. [x] Förbättrad UI med badges och ikoner – Tydligare visning av transaktionstyper med ikoner.
60. [x] Förbättrad tillverkarsida – ID som badge, kommentar som egen sektion, hela bredden för korten.
61. [x] Visa statistik (t.ex. antal yxor, mest populära tillverkare, dyraste köp).
    - [x] 61.1 Dedikerad statistik-dashboard med samlingsöversikt
    - [x] 61.2 Topplistor för mest aktiva tillverkare, plattformar och kontakter
    - [x] 61.3 Ekonomisk översikt med totala köp- och försäljningsvärden
    - [x] 61.4 Realtidsstatistik som uppdateras baserat på aktiva filter
    - [x] 61.5 Fixat Django ORM-problem med annotate och properties
61.6 [x] Visa antal yxor i samlingen över tid (linje- eller stapeldiagram)
    - [x] 61.6.1 Kombinerad tidslinje med "Yxor köpta (total)" och "Yxor i samlingen"
    - [x] 61.6.2 Grupperad per månad baserat på transaktionsdatum
    - [x] 61.6.3 Visar tydligt skillnaden mellan köpta och kvarvarande yxor
    - [x] 61.6.4 Chart.js-implementation med två färgkodade linjer
61.7 [x] Visa totala inköpskostnader och försäljningsintäkter över tid (diagram)
    - [x] 61.7.1 Stapeldiagram med transaktionsvärden per månad
    - [x] 61.7.2 Röda staplar för köpvärde, gröna för försäljningsvärde
    - [x] 61.7.3 Visar aktivitet över tid istället för kumulativa värden
    - [x] 61.7.4 Svensk formatering av belopp i tooltips och axlar
61.8 [x] Visa dyraste och billigaste köp/sälj i topplistan, med länk till respektive yxa
    - [x] 61.8.1 Länkar till yxorna från alla transaktionslistor
    - [x] 61.8.2 Förbättrad layout med radbrytning för långa yxnamn
    - [x] 61.8.3 Flexbox-layout för bättre "tabb-avstånd" och läsbarhet
    - [x] 61.8.4 Billigaste köp och försäljningar tillagda
61.9 [x] Visa mest aktiva månader (när köps/säljs flest yxor)
    - [x] 61.9.1 Staplat stapeldiagram som visar antal köp/sälj per månad
    - [x] 61.9.2 Färgkodning: röd för köp, blå för sälj
    - [x] 61.9.3 Tooltip med exakt antal transaktioner per typ
    - [x] 61.9.4 Placerat efter ekonomiska diagrammen på statistiksidan
61.10 [x] Visa senaste aktivitet (senaste köp, sälj, tillagd yxa)
    - [x] 61.10.1 Tre kort för senaste köp, försäljningar och tillagda yxor
    - [x] 61.10.2 Visar de 5 senaste aktiviteterna per kategori
    - [x] 61.10.3 Länkar till respektive yxas detaljsida
    - [x] 61.10.4 Färgkodning: grön för köp, röd för sälj, blå för tillagda yxor
    - [x] 61.10.5 Visar datum och pris/tillverkare för varje aktivitet
62. [ ] QR-kod för att snabbt visa en yxa på mobilen. **(Pausad – kräver vidare diskussion och behovsanalys innan implementation)**

## Framtida förbättringar

63. [x] Fixa JavaScript-fel och landsfält-problem
64. [x] Fixa duplicerad "Detaljer"-knapp på /galleri-sidan
    - [x] 62.1 Fixa SyntaxError på yxformuläret (`window.axeId = ;` när axe.pk inte finns)
    - [x] 62.2 Ersätt komplex sökbar select med enkel dropdown för landsfält på kontaktformuläret
    - [x] 62.3 Ta bort all debug-kod (console.log) från båda formulären
    - [x] 62.4 Förbättra felhantering för Django-template-syntax i JavaScript
    - [x] 62.5 Implementera konsekvent landsfält med flagg-emoji och landsnamn
    - [x] 62.6 Stöd för redigering av befintliga kontakter med landskod
    - [x] 62.7 Rensa kod från onödiga CSS-regler och JavaScript-funktioner
    - [x] 63.8 Förbättra användarupplevelse med enkel och pålitlig dropdown-lista
65. [ ] Förbättrad felhantering och validering i formulär.
66. [ ] Snabbare AJAX-sökningar med caching.
67. [ ] Tangentbordsnavigering i lightbox (piltangenter för att bläddra mellan bilder).
68. [ ] Touch-gester för mobil navigering i lightbox (swipe för att bläddra).
69. [ ] Zoom-funktionalitet i lightbox för att se bilder i full storlek.
70. [ ] Automatisk bildrotation baserat på EXIF-data.
71. [ ] Bulk-redigering av bilder (redigera flera bilder samtidigt).
72. [ ] Bildkommentarer med @-mentions för att länka till tillverkare eller yxor.

## Tekniska lärdomar från utveckling

### API och transaktionshantering (2025-07-21)
- **API för borttagning av transaktioner**: Implementerat `/api/transaction/<id>/delete/` endpoint med säkerhet och felhantering
- **Bootstrap-modal istället för alert**: Ersatt `confirm()` och `alert()` med snygga Bootstrap-modaler för bättre användarupplevelse
- **Felhantering**: Separata modaler för bekräftelse och felmeddelanden med tydlig feedback
- **Säkerhet**: `@login_required` decorator för att skydda API-endpoints från oauktoriserad åtkomst
- **JavaScript-struktur**: Globala variabler för modal-instanser och funktioner för återanvändbar felhantering
- **Tekniska lärdomar**:
  - API-design: Använd RESTful endpoints med tydliga URL-mönster (`/api/transaction/<id>/delete/`)
  - Modal-hantering: Bootstrap Modal API ger bättre kontroll än standard browser-dialoger
  - Felhantering: Separera bekräftelse- och felmodaler för tydligare användarupplevelse
  - CSRF-skydd: `@csrf_exempt` för API-endpoints som inte använder Django-forms
  - JavaScript-organisering: Använd globala variabler för modal-instanser och återanvändbara funktioner

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

### Inline-redigering och formulärhantering (2025-01-15)
- **Bekräfta/ångra-knappar**: Ersätter modaler med direkta knappar för bättre användarupplevelse och snabbare arbetsflöde
- **"Övrigt"-alternativhantering**: Kombinerad dropdown + textinput med automatisk visning/dölj-logik för anpassade måttnamn
- **Backend-kompatibilitet**: Separata fält (`name` vs `custom_name`) för standardmått och anpassade mått krävs korrekt hantering i frontend
- **Duplikatsäkerhet**: `data-updating` attribut förhindrar dubbla API-anrop under pågående uppdateringar
- **Användarfeedback**: Kombinera visuell feedback (spinner, inaktiverade knappar) med notifikationer för tydlig status
- **Tekniska lärdomar**:
  - Form-validering: Backend `MeasurementForm` förväntar sig specifika fältnamn - matcha exakt i frontend
  - Event listeners: Använd delegering på document-nivå för dynamiskt skapade element
  - State management: Spara ursprungliga värden i data-attribut för ångra-funktionalitet  
  - DOM-hantering: Rensa och återställ DOM-element korrekt vid avbruten/slutförd redigering
  - Error debugging: Console-loggar hjälper att identifiera backend-valideringsfel

 