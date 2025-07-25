# Projektidéer & förbättringsförslag
En checklista för vidareutveckling av AxeCollection. Bocka av med [x] när klart!
## 1. Bildhantering

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

## 2. Användarupplevelse och interface

17. [x] Förbättrad responsivitet – Testa och förbättra för surfplattor och olika mobilstorlekar.
18. [x] Touchvänliga knappar även på desktop – T.ex. piltangenter för bildbyte.
19. [x] Mörkt läge (dark mode) för hela tjänsten – Respekterar operativsystemets tema automatiskt och har en sol/måne-knapp för manuell växling.
20. [x] Notifikationssystem – Snygga notifikationer för användarfeedback vid alla operationer.
21. [x] Laddningsindikatorer – Spinner och inaktiverade knappar under pågående operationer.
22. [x] AJAX-animationer – Smooth övergångar och animationer för bättre användarupplevelse.
23. [x] Fixa dark mode-konsistens
    - [x] 23.1 Kontaktdetaljsida - vita bakgrunder på kontaktinformation, medlemskap och adress
    - [x] 23.2 Systematisk genomgång av alla sidor för dark mode-konsistens
24. [x] Lägg till footer
    - [x] 24.1 Designa footer med relevant information (version, länkar, kontakt)
    - [x] 24.2 Implementera footer på alla sidor
    - [x] 24.3 Anpassa footer för både light och dark mode
25. [ ] I demo-mode ska det visas en hint på logga in med demo/demo123 som användaruppgifter

## 3. Sök och filtrering

26. [x] AJAX-sökning för kontakter – Realtidssökning med dropdown-resultat för befintliga kontakter.
27. [x] AJAX-sökning för plattformar – Realtidssökning med dropdown-resultat för befintliga plattformar.
28. [x] Flaggemoji för kontakter – Visar landskod som flaggemoji bredvid kontaktnamn på alla relevanta ställen.
    - [x] 28.1 Lägg till country_code fält (ISO 3166-1 alpha-2) i Contact-modellen
    - [x] 28.2 Uppdatera befintliga kontakter med landskod för Sverige och Finland
    - [x] 28.3 Skapa country_flag template filter för att konvertera landskod till flaggemoji
    - [x] 28.4 Uppdatera ContactForm med sökbart select-fält med flagg-emoji och landsnamn
    - [x] 28.5 Lägg till flaggemoji på kontaktdetaljsidan (rubrik)
    - [x] 28.6 Lägg till flaggemoji i transaktionshistoriken på yxdetaljsidan
    - [x] 28.7 Lägg till flaggemoji i transaktioner på tillverkardetaljsidan
    - [x] 28.8 Lägg till flaggemoji i kontakter som handlat med tillverkaren
    - [x] 28.9 Lägg till flaggemoji i mest aktiva kontakter på statistik-sidan
    - [x] 28.10 Visa flaggemoji bredvid kontaktnamn i yxformuläret
    - [x] 28.11 Visa flaggemoji i kontaktlistan
    - [x] 28.12 Visa flaggemoji i transaktionslistan
29. [x] Global sökning i navbar – Sökfält i menyn som söker i yxor, kontakter, tillverkare och transaktioner med grupperade resultat.
    - [x] 29.1 Sökfält i navbar med responsiv design
    - [x] 29.2 Backend-endpoint för global sökning (/api/search/global/)
    - [x] 29.3 Sökning i yxor (tillverkare, modell, kommentar, ID)
    - [x] 29.4 Sökning i kontakter (namn, alias, e-post)
    - [x] 29.5 Sökning i tillverkare (namn, information)
    - [x] 29.6 Sökning i transaktioner (yxa, kontakt, plattform)
    - [x] 29.7 Grupperade resultat med ikoner och antal
    - [x] 29.8 Kortkommando Ctrl+K för att fokusera sökfältet
    - [x] 29.9 Länkar till detaljsidor för varje resultat
    - [x] 29.10 Flaggemoji för kontakter i sökresultaten
30. [x] Moderniserad AJAX-sökning för kontakt och plattform i yxformuläret
    - [x] 30.1 Återställt och moderniserat JavaScript för AJAX-sökning
    - [x] 30.2 Lagt till saknade plattformsfält i forms.py (platform_name, platform_url, platform_comment)
    - [x] 30.3 Uppdaterat axe_create i views_axe.py med komplett formulärhantering för kontakt, plattform och transaktion
    - [x] 30.4 Lagt till dropdown-containers för sökresultat i axe_form.html
    - [x] 30.5 Implementerat funktioner för att visa/dölja sektioner för nya kontakter och plattformar
    - [x] 30.6 Lagt till next_id i context för att visa nästa yx-ID
    - [x] 30.7 Förbättrat felhantering och användarupplevelse
31. [x] Sökfunktion för yxor och tillverkare – Snabbt hitta yxor, tillverkare eller transaktioner.
32. [x] Filtrering på t.ex. tillverkare, typ, årtal, mm.
33. [x] Plattformsfilter och visning i yxlistan
    - [x] 33.1 Möjliggör filtrering av yxor på plattform i yxlistan
    - [x] 33.2 Visar alla plattformar för varje yxa direkt i tabellen
    - [x] 33.3 Varje plattform får en unik färg för ökad överskådlighet
    - [x] 33.4 Alla plattformsnamn visas med konsekvent fetstil för tydlighet
    - [x] 33.5 Förbättrar användarupplevelsen vid sortering och översikt av yxor
    - [x] 33.6 Fixat Django ORM-relationer med related_name='transactions'
    - [x] 33.7 Förbättrad CSV-export med hantering av radbrytningar
    - [x] 33.8 Fixat statistikkort som nu visar korrekt data för filtrerade yxor (tidigare visade alltid hela samlingen)
34. [x] Måttkolumn och filtrering i yxlistan
    - [x] 34.1 Lägg till "Mått"-kolumn i yxlistan med linjal-ikon för yxor med registrerade mått
    - [x] 34.2 Visa antalet registrerade mått bredvid linjal-ikonen (t.ex. "📏 3" för 3 mått)
    - [x] 34.3 Tooltip/popup som visar måtten vid hovring över ikonen
35. [ ] Filtreringen av Tillverkare på /yxor ska använda hierarkisk indentering med L-tecken som på /tillverkare/ny|redigera och /yxor/ny|redigera

## 4. Deployment och Docker

36. [x] Fixa Docker startup-problem
    - [x] 36.1 "exec /app/start.sh: no such file or directory" - fixade line endings och behörigheter
    - [x] 36.2 Nginx visar standard-sida istället för Django - korrekt Nginx-konfiguration inbyggd
    - [x] 36.3 Windows line endings i start.sh - automatisk konvertering i Dockerfile
    - [x] 36.4 Behörigheter för Unraid (nobody:users) - korrekt UID/GID-hantering
    - [x] 36.5 CSRF-fel vid inloggning - dynamisk host-konfiguration via UI och miljövariabler
    - [x] 36.6 Demo-installationer - stöd för flera instanser med olika host-konfigurationer
    - [x] 36.7 Databasbehörigheter på Unraid - automatisk fix av readonly database
    - [x] 36.8 Robust startup-process - automatisk skapande av kataloger och behörigheter
37. [x] Automatisk hantering av sökvägar för olika miljöer
    - [x] 37.1 Skapa script för att fixa bildsökvägar vid deployment (Windows backslashes → Linux forward slashes)
    - [x] 37.2 Automatisk konvertering av `/app/media/` prefix för Docker-miljöer
    - [x] 37.3 Hantera sökvägar för både utvecklingsmiljö (Windows) och produktionsmiljö (Linux)
    - [x] 37.4 Integrera sökvägsfix i deployment-processen
    - [x] 37.5 Testa och verifiera att bilder fungerar i både test- och produktionsmiljö
38. [x] Media-filhantering i produktionsmiljö
    - [x] 38.1 Konfigurera Nginx för att servera media-filer i produktion
    - [x] 38.2 Eller implementera CDN-lösning för media-filer
    - [x] 38.3 Eller konfigurera Django för att servera media-filer i produktion (inte rekommenderat för hög belastning)
    - [x] 38.4 Testa och verifiera att alla bilder fungerar korrekt i produktionsmiljö
    - [x] 38.5 Dokumentera lösningen för framtida deployment
39. [x] Deployment-konfiguration för produktion med SQLite
    - [x] 39.1 Produktionssettings-fil med säkerhetskonfiguration
    - [x] 39.2 Dockerfile med Gunicorn för produktion
    - [x] 39.3 Docker Compose-konfiguration med volymer
    - [x] 39.4 Deployment-guide med steg-för-steg instruktioner
    - [x] 39.5 Backup-script för automatisk säkerhetskopiering
    - [x] 39.6 Miljövariabler och konfigurationsmallar
    - [x] 39.7 Nginx-konfiguration för webbserver
    - [x] 39.8 SSL/HTTPS-konfiguration
    - [x] 39.9 Logging och övervakning
    - [x] 39.10 Säkerhetsinställningar för produktion
    - [x] 39.11 Omorganisation av deployment-filer till deploy/-mapp
    - [x] 39.12 Uppdaterad dokumentation för ny struktur
    - [x] 39.13 Tydlig separation mellan utveckling och deployment
40. [ ] Fixa omorganisering av yxbilder i produktion
    - [ ] 40.1 Omorganisering av yxbilder fungerar inte på Unraid-produktionsservern
    - [ ] 40.2 Undersök skillnader mellan utvecklings- och produktionsmiljö
    - [ ] 40.3 Kontrollera filbehörigheter och sökvägar i produktion
    - [ ] 40.4 Testa drag & drop-funktionalitet i produktionsmiljö

## 5. Yxhantering och arbetsflöden

41. [x] Redigera transaktion, plattform och kontakt för en yxa via detaljvyn
    - [x] 41.1 Visa "Lägg till transaktion"-knapp om ingen transaktion finns
    - [x] 41.2 Visa "Redigera transaktioner"-knapp om en eller flera transaktioner finns
    - [x] 41.3 Bygg formulär för att lägga till/redigera transaktion (pris, frakt, kontakt, plattform, kommentar, datum)
    - [x] 41.4 Implementera AJAX-sökning för kontakt och plattform i formuläret
    - [x] 41.5 Möjlighet att skapa ny kontakt/plattform direkt i formuläret
    - [x] 41.6 Möjlighet att ta bort transaktion
42. [x] UI för att skapa nya yxor i samlingen – Användarvänligt formulär för att lägga till yxor.
43. [x] UI för att redigera befintliga yxor – Möjlighet att uppdatera information efter mottagning.
44. [x] Status-fält och filter – Status "Köpt" vs "Mottagen/Ägd" med filter och snabbåtgärder (markera som mottagen) i yxlistan.
45. [x] Arbetsflöde för inköp: 
46. [x] Arbetsflöde för mottagning:
    - [x] 46.1 Lägg till fler bilder av mottagen yxa (via befintlig redigeringsfunktionalitet)
    - [x] 46.2 Mät och registrera mått (nytt måttinmatningsformulär med mallar)
    - [x] 46.3 Uppdatera eventuell felaktig information (via befintlig redigeringsfunktionalitet)
    - [x] 46.4 Dedikerat mottagningsarbetsflöde med steg-för-steg process
    - [x] 46.5 Måttmallar för olika yxtyper (standard, fällkniv, köksyxa)
    - [x] 46.6 AJAX-hantering för måttinmatning och borttagning
    - [x] 46.7 Länkar till mottagningsarbetsflödet från yxlistan och yxdetail
47. [x] Snabbval av tillverkare – Dropdown för att välja tillverkare.
48. [x] Kontakthantering – Skapa nya kontakter direkt från yxformuläret med smart matchning.
49. [x] Plattformshantering – Skapa nya plattformar direkt från yxformuläret med smart matchning.
50. [x] Automatisk transaktionstypbestämning – Baserat på pris (negativ = köp, positiv = sälj).
51. [x] Separata formulär för skapande vs redigering – Olika fält visas beroende på om yxa skapas eller redigeras.
52. [ ] Lägg till yxa via auktions-URL – Möjlighet att lägga till yxa genom att ange URL till vunnen Tradera- eller eBay-auktion.
    - [ ] 52.1 Implementera URL-parser för Tradera-auktioner som extraherar titel, beskrivning, bilder och slutpris
    - [ ] 52.2 Implementera URL-parser för eBay-auktioner med motsvarande funktionalitet
    - [ ] 52.3 Automatisk förfyllning av yxformulär baserat på extraherad auktionsdata
    - [ ] 52.4 Automatisk nedladdning och lagring av auktionsbilder
    - [ ] 52.5 Intelligent kategorisering och tillverkargissning baserat på auktionsbeskrivning
    - [ ] 52.6 Automatisk skapande av transaktion med slutpris som köpvärde
    - [ ] 52.7 Felhantering för ogiltiga URL:er eller auktioner som inte kan parsas
    - [ ] 52.8 Stöd för olika auktionsformat och språk (svenska/engelska)
    - [ ] 52.9 Förhandsvisning av extraherad data innan sparning
    - [ ] 52.10 Möjlighet att redigera och justera automatiskt extraherad information
53. [ ] Fixa problem med att ändra tillverkare på en yxa - formuläret fungerar inte korrekt

## 6. Transaktions- och måtthantering

54. [x] Transaktionshantering – Koppla yxor till köp/försäljning med pris, frakt och datum.
55. [x] Förbättrad mått-UX i redigeringsvyn:
    - [x] 55.1 Batch-läggning av mått med tydlig info och notifikation
    - [x] 55.2 Inline-redigering av mått (värde och enhet) via AJAX
    - [x] 55.3 Borttagning av mått med snygg animation (utan sidladdning)
    - [x] 55.4 Visuell feedback vid alla måttoperationer (notifikationer, laddningsindikatorer)
    - [x] 55.5 Förbättrad felhantering och återställning av UI
    - [x] 55.6 Fördröjd sidladdning för att visa notifikationer
    - [x] 55.7 Möjlighet att ta bort enskilda rader från batch-måttformuläret (soptunne-ikon per rad)
    - [x] 55.8 Förbättrad DRY-princip med återanvändbar JavaScript-kod
    - [x] 55.9 Automatisk UI-uppdatering vid borttagning av mått (tomt tillstånd, räknare)
    - [x] 55.10 Event listener-baserad hantering istället för inline onclick
    - [x] 55.11 Korrekt omindexering av batch-formulärrader vid borttagning
    - [x] 55.12 Bekräfta/ångra-knappar för inline-redigering istället för modaler
    - [x] 55.13 Fullständig hantering av "Övrigt"-alternativet med textinput för anpassat måttnamn
    - [x] 55.14 Bootstrap modal för borttagningsbekräftelse istället för alert()
    - [x] 55.15 Korrekt skickande av data till backend (standardmått vs anpassade mått)
    - [x] 55.16 Förhindring av dubbla anrop med spärr under uppdatering
    - [x] 55.17 Automatisk enhetsfyllning när standardmåtttyper väljs
    - [x] 55.18 Visuell feedback med spinner och inaktiverade knappar under uppdatering
56. [x] Fixa enskilda mått
    - [x] 56.1 Ensamma mått kan inte läggas till, bara via batch-inlägg
    - [x] 56.2 Implementera funktionalitet för att lägga till enskilda mått
    - [x] 56.3 Testa att både enskilda och batch-mått fungerar korrekt
57. [x] Måttfiltrering i yxlistan – Filter för att visa endast yxor med eller utan mått
    - [x] 57.1 Filter för att visa endast yxor med/utan mått
    - [x] 57.2 Responsiv design för måttkolumnen på olika skärmstorlekar
58. [x] Måttmallshantering i inställningsmenyn – Möjlighet att skapa, redigera och hantera måttmallar direkt från systeminställningarna.
    - [x] 58.1 Lägg till sektion för måttmallshantering i inställningsmenyn
    - [x] 58.2 Formulär för att skapa nya måttmallar med namn och beskrivning
    - [x] 58.3 Drag & drop-gränssnitt för att lägga till/ta bort måtttyper i mallar
    - [x] 58.4 Redigering av befintliga måttmallar (namn, beskrivning, måtttyper)
    - [x] 58.5 Borttagning av måttmallar med varning om konsekvenser
    - [x] 58.6 Förhandsvisning av måttmallar med lista över inkluderade måtttyper
    - [x] 58.7 Validering för att säkerställa att mallar har minst ett mått
    - [x] 58.8 AJAX-hantering för snabb uppdatering utan sidladdning
    - [x] 58.9 Enhethantering - Möjlighet att definiera/ändra måttenheter och välja enhet för måttmallar (gram, mm, grader °)

## 7. Tillverkarhantering

59. [x] Formulär för tillverkarlänkar
    - [x] 59.1 Skapa formulär för att lägga till länkar och resurser på tillverkare
    - [x] 59.2 Implementera i tillverkardetaljsidan (för närvarande bara via Django admin)
    - [x] 59.3 Lägg till funktionalitet för att redigera och ta bort länkar
    - [x] 59.4 Säkerställ att order-fältet fungerar för sortering av länkar
60. [x] Eget administratörsgränssnitt för tillverkare
    - [x] 60.1 Redigera tillverkare-knapp kvar på nuvarande plats (endast namnändring)
    - [x] 60.2 Ny redigera-knapp i Informations-gruppen för att redigera information
    - [x] 60.3 Flytta "Lägg till bild"-knapp till Bildgalleri-gruppen
    - [x] 60.4 Flytta "Lägg till länk"-knapp till Länkar-gruppen
    - [x] 60.5 Implementera formulär för redigering av tillverkarnamn
    - [x] 60.6 Implementera formulär för redigering av information
    - [x] 60.7 WYSIWYG markdown-redigerare för informationsfält (EasyMDE)
    - [x] 60.8 AJAX-hantering för snabb redigering utan sidladdning
    - [x] 60.9 Validering och felhantering för alla formulär
    - [x] 60.10 Notifikationer för framgångsrika redigeringar
    - [x] 60.11 Döpa om fält från "comment" till "information"
    - [x] 60.12 Inline-redigering av tillverkarnamn med AJAX
    - [x] 60.13 Markdown-stöd för bildbeskrivningar med EasyMDE
    - [x] 60.14 Lightbox med redigeringsmöjligheter för tillverkarbilder
    - [x] 60.15 Drag & drop-funktionalitet för bildordning
    - [x] 60.16 Navigationsknappar i lightbox för att bläddra mellan bilder i samma grupp
    - [x] 60.17 Semi-bold styling för bildtext för bättre läsbarhet
    - [x] 60.18 Vänsterställd text i lightbox för bättre läsbarhet av längre beskrivningar
    - [x] 60.19 Inline-redigering, borttagning och drag & drop-sortering för tillverkarlänkar
    - [x] 60.20 Klickbara kort för bilder (öppnar lightbox) och aktiva länkar (öppnar i ny flik)
    - [x] 60.21 Visuell hantering för inaktiva länkar (gråtonad styling, URL som text, "Inaktiv"-badge)
    - [x] 60.22 Hover-effekter på bild- och länkkort för bättre användarupplevelse
    - [x] 60.23 Template filter för att visa information i tillverkarlistan (strippa markdown, begränsa längd)
61. [x] Hierarkiskt tillverkarsystem med undertillverkare/smeder
    - [x] 61.1 Lägg till parent_manufacturer ForeignKey-fält i Manufacturer-modellen
    - [x] 61.2 Uppdatera tillverkarformuläret med dropdown för överordnad tillverkare
    - [x] 61.3 Visa undertillverkare/smeder som underavdelning på tillverkardetaljsidan (t.ex. "Smeder på Gränsfors Bruk")
    - [x] 61.4 Implementera träd-visning i tillverkarlistan med indenterade undertillverkare
    - [x] 61.5 Möjlighet att filtrera yxor på både huvud- och undertillverkare
    - [x] 61.6 Statistik för undertillverkare som summeras till huvudtillverkaren
    - [x] 61.7 Breadcrumbs som visar hierarki
    - [x] 61.8 Validering för att förhindra cirkulära referenser
    - [x] 61.9 Migration för att hantera befintliga tillverkare
    - [x] 61.10 Admin-gränssnitt med träd-struktur för enkel hantering
62. [x] Ekonomikolumnen för tillverkare ska summera de eventuella underliggande tillverkarna - både i tillverkarlistan och på tillverkaredetaljsidan. På detaljsidan ska det delas upp mellan yxor kopplade direkt till tillverkaren och yxor från underliggande tillverkare/smeder
63. [x] Indentering av tillverkare och underordnade smeder ska fungera även på skapa/redigera yxformuläret
64. [x] Organisationssektionen på tillverkarsidan ska visas för inloggade användare även när det inte finns undertillverkare, med "Lägg till undertillverkare"-knapp
65. [x] Breadcrumbs för tillverkare verkar inte hantera alla nivåer korrekt

## 8. Admin och datahantering

66. [x] Förbättrad admin-raderingsvy för yxor – Tydlig lista över vad som tas bort, bockruta för bildradering.
67. [ ] Batchuppladdning av yxor – Möjlighet att ladda upp flera yxor samtidigt. **(Pausad – kräver vidare diskussion och behovsanalys innan implementation)**
68. [x] Export/import av data (CSV, Excel) direkt från admin.
69. [x] Automatiska backuper av databasen.
    - [x] 69.1 Backup-funktionalitet flyttad från admin till systeminställningsvyn
    - [x] 69.2 Integrerad backup-hantering i settings.html med modern UI
    - [x] 69.3 Skapa, ta bort och återställ backuper direkt från inställningssidan
    - [x] 69.4 Statistik-visning för varje backup (antal yxor, kontakter, transaktioner)
    - [x] 69.5 Varningar för återställning med bekräftelsedialoger
    - [x] 69.6 Stöd för komprimerade backuper och media-filer
    - [x] 69.7 Automatisk rensning av gamla backuper (30 dagar)
    - [ ] 69.8 Backup-uppladdning via webbgränssnitt - Lösa problem med stora filer (>100MB) och nginx-konfiguration
        - [ ] 69.8.1 Fixa nginx client_max_body_size för stora backupfiler (2GB+)
        - [ ] 69.8.2 Förbättra JavaScript AJAX-uppladdning för stora filer
        - [ ] 69.8.3 Lägg till progress-indikator för stora filer
        - [ ] 69.8.4 Testa och verifiera att uppladdning fungerar för filer >100MB
        - [ ] 69.8.5 Dokumentera lösningen för framtida deployment
70. [x] Förbättrad navigering på systeminställningssidan.
    - [x] 70.1 Bootstrap navbar för in-page navigering mellan sektioner
    - [x] 70.2 Smooth scrolling med scroll-margin-top för att visa headers
    - [x] 70.3 Aktiv länk-markering baserat på scroll-position
    - [x] 70.4 Responsiv design för navigeringsmenyn
    - [x] 70.5 Korrekt styling med ljus bakgrund och mörk text
71. [x] Vy för okopplade bilder – Rutnätsvy med funktioner för att ta bort och ladda ner bilder som flyttats från borttagna yxor.
    - [x] 71.1 Rutnätsvy med bildkort som visar filnamn, storlek och timestamp
    - [x] 71.2 Gruppering av bilder efter timestamp (när yxan togs bort)
    - [x] 71.3 Soptunne-ikon för att ta bort enskilda bilder
    - [x] 71.4 Ladda ner-ikon för att spara ner enskilda bilder
    - [x] 71.5 Massåtgärder med checkboxar för att välja flera bilder
    - [x] 71.6 "Ladda ner valda"-knapp som skapar ZIP-fil med valda bilder
    - [x] 71.7 Statistik-kort som visar totalt antal bilder, storlek och antal grupper
    - [x] 71.8 Responsiv design som fungerar på mobil och desktop
    - [x] 71.9 AJAX-hantering för borttagning utan sidladdning
    - [x] 71.10 Hover-effekter och animationer för bättre användarupplevelse
    - [x] 71.11 .webp-optimering: visar .webp-versioner för snabbare laddning men laddar ner originalfiler
    - [x] 71.12 Korrekt svenska grammatik med plural-former för "antal bilder" och "antal grupper"
    - [x] 71.13 Lägg till länk till vyn i admin-navigation (kommer att implementeras när inloggning/adminvy införs)
    - [x] 71.14 Implementera motsvarande hantering för borttagning av tillverkare och deras bilder (flytt till okopplade bilder)
        - [x] 71.14.1 Analysera vad som ska hända med yxor som tillhör tillverkaren (behåll som "okänd tillverkare" vs förhindra borttagning)
        - [x] 71.14.2 Utvärdera om funktionen ens behövs eller om tillverkare ska vara permanent

## 9. Säkerhet och användare

72. [x] Inloggning/behörighet – Privata delar eller flera användare.
    - [x] 72.1 Django Auth-system implementerat med anpassade templates
    - [x] 72.2 Långa sessioner (30 dagar) för bättre användarupplevelse
    - [x] 72.3 Starka lösenord (minst 12 tecken) med Django's validering
    - [x] 72.4 Login/logout-funktionalitet med redirect till rätt sida
    - [x] 72.5 Användardropdown i navigationen med inställningar och logout
    - [x] 72.6 Responsiv login-modal i navigationen för snabb inloggning
    - [x] 72.7 Tydlig visuell feedback för inloggade vs icke-inloggade användare
73. [ ] Loggning av ändringar (audit trail).
74. [x] Inför inloggning/adminvy så att endast inloggade kan redigera, och visa en publik vy där känsliga uppgifter (t.ex. kontaktnamn, personuppgifter och ev. priser) maskeras eller döljs.
    - [x] 74.1 Settings-modell med konfigurerbara publika inställningar
    - [x] 74.2 Context processor som gör publika inställningar tillgängliga i alla templates
    - [x] 74.3 Automatisk filtrering av känslig data för icke-inloggade användare
    - [x] 74.4 Kontroll av användarstatus i alla vyer som visar känslig information
    - [x] 74.5 Fallback-hantering om Settings-modellen inte finns ännu
    - [x] 74.6 Dedikerad inställningssida för administratörer
    - [x] 74.7 Switches för alla publika inställningar med tydliga beskrivningar
    - [x] 74.8 Sajtinställningar för titel och beskrivning
    - [x] 74.9 Endast inloggade användare kan komma åt inställningarna
    - [x] 74.10 Global sökning respekterar publika inställningar
    - [x] 74.11 Kontaktsökning döljs för icke-inloggade användare om inställt
    - [x] 74.12 Plattformssökning kan konfigureras för publik/privat visning
    - [x] 74.13 Intelligent filtrering baserat på användarstatus
    - [x] 74.14 Yxlistan filtreras automatiskt för icke-inloggade användare
    - [x] 74.15 Transaktionsdata döljs eller visas baserat på inställningar
    - [x] 74.16 Kontaktinformation maskeras för publika användare
    - [x] 74.17 Prisinformation kan döljas för publika användare
    - [x] 74.18 Konsekvent navigation som anpassas efter användarstatus
    - [x] 74.19 Snygga ikoner och styling för användargränssnittet
    - [x] 74.20 Fixa yxdetaljsidan: Pris- och fraktkolumner visas fortfarande för publika användare trots att de ska döljas
    - [x] 74.21 Fixa ekonomiska statistikkort på /yxor: Kronor-relaterade kort (vinst/förlust, totala värden) visas fortfarande för publika användare, ska döljas helt

## 10. Prestanda och kodkvalitet

75. [ ] Fler automatiska tester (unit/integration).
76. [ ] CI/CD – Automatiska tester vid push (GitHub Actions).
77. [ ] Kodgranskning – Linting och kodstil (t.ex. black, flake8).
78. [x] Periodvis kodgranskning: Gå igenom och granska koden stegvis för att identifiera behov av övergripande refaktorering, buggfixar och tillsnyggning. Gör detta processvis så att varje steg kan testas innan nästa påbörjas.
    - [x] 78.1 Refaktorera vyer till mindre filer (views_axe.py, views_contact.py, views_manufacturer.py, views_transaction.py)
    - [x] 78.2 Flytta statistik- och ekonomi-beräkning från vyer till model-properties
    - [x] 78.3 Skapa återanvändbara template-includes för statistik-kort (_stat_card.html, _axe_stats_cards.html, _contact_stats_cards.html, _transaction_stats_cards.html)
    - [x] 78.4 Uppdatera templates för att använda nya includes och model-properties
    - [x] 78.5 Förenkla fler templates med includes och templatetags (t.ex. transaktionsrader, status-badges, breadcrumbs)
    - [x] 78.6 Refaktorera formulär med återanvändbara komponenter
    - [ ] 78.7 Lägg till tester för vyer, modeller och templatetags
    - [ ] 78.8 Prestandaoptimering (caching, lazy loading, etc.)
79. [x] Dokumentation av förbättringar - Uppdatera markdown-filer med genomförda förbättringar och lärdomar
80. [ ] Implementera Django REST Framework och ViewSets
81. [x] Skapa fingerad testdata för demo och testning
    - [x] 81.1 Exportera nuvarande databas-struktur för att förstå datamodellen
    - [x] 81.2 Skapa script för att generera realistisk testdata (yxor, tillverkare, kontakter, transaktioner)
    - [x] 81.3 Inkludera olika typer av yxor med varierande mått, bilder och transaktioner
    - [x] 81.4 Skapa tillverkare med olika antal bilder och länkar
    - [x] 81.5 Generera kontakter från olika länder med flaggemoji
    - [x] 81.6 Skapa transaktioner med olika plattformar och priser
    - [x] 81.7 Testa alla funktioner med testdata (sökning, filtrering, statistik, etc.)
    - [x] 81.8 Förbereda för publik demo-webbplats
    - [x] 81.9 Dokumentera hur man återställer till testdata
82. [x] todo_manager behöver kunna hantera underuppgifter som 58.4 (slutföra underuppgifter)

## 11. Testdata och demo

83. [x] Skapa fingerad testdata för demo och testning
84. [x] Docker demo-läge med miljövariabel
    - [x] 84.1 Lägg till miljövariabel DEMO_MODE för Docker-containern
    - [x] 84.2 Implementera logik som kontrollerar DEMO_MODE vid container-start
    - [x] 84.3 Automatisk körning av `generate_test_data --clear` när DEMO_MODE=true
    - [x] 84.4 Säkerställ att demo-läget endast körs vid container-start, inte vid reload
    - [x] 84.5 Dokumentera användning av demo-läge i deployment-guider
    - [x] 84.6 Testa demo-läge i olika Docker-miljöer (utveckling, produktion)
85. [x] Ordna demodata med hierarkiska tillverkare - Till exempel är smederna Johan Jonsson, Johan Skog och Willy Persson alla tre smeder hos Hjärtumssmedjan

## 12. Design och presentation

86. [x] Bättre visuell presentation av galleriet, t.ex. lightbox för bilder.
87. [x] Förbättrad UI med badges och ikoner – Tydligare visning av transaktionstyper med ikoner.
88. [x] Förbättrad tillverkarsida – ID som badge, kommentar som egen sektion, hela bredden för korten.
89. [x] Visa statistik (t.ex. antal yxor, mest populära tillverkare, dyraste köp).
    - [x] 89.1 Dedikerad statistik-dashboard med samlingsöversikt
    - [x] 89.2 Topplistor för mest aktiva tillverkare, plattformar och kontakter
    - [x] 89.3 Ekonomisk översikt med totala köp- och försäljningsvärden
    - [x] 89.4 Realtidsstatistik som uppdateras baserat på aktiva filter
    - [x] 89.5 Fixat Django ORM-problem med annotate och properties
    - [x] 89.6 Visa antal yxor i samlingen över tid (linje- eller stapeldiagram)
        - [x] 89.6.1 Kombinerad tidslinje med "Yxor köpta (total)" och "Yxor i samlingen"
        - [x] 89.6.2 Grupperad per månad baserat på transaktionsdatum
        - [x] 89.6.3 Visar tydligt skillnaden mellan köpta och kvarvarande yxor
        - [x] 89.6.4 Chart.js-implementation med två färgkodade linjer
    - [x] 89.7 Visa totala inköpskostnader och försäljningsintäkter över tid (diagram)
        - [x] 89.7.1 Stapeldiagram med transaktionsvärden per månad
        - [x] 89.7.2 Röda staplar för köpvärde, gröna för försäljningsvärde
        - [x] 89.7.3 Visar aktivitet över tid istället för kumulativa värden
        - [x] 89.7.4 Svensk formatering av belopp i tooltips och axlar
    - [x] 89.8 Visa dyraste och billigaste köp/sälj i topplistan, med länk till respektive yxa
        - [x] 89.8.1 Länkar till yxorna från alla transaktionslistor
        - [x] 89.8.2 Förbättrad layout med radbrytning för långa yxnamn
        - [x] 89.8.3 Flexbox-layout för bättre "tabb-avstånd" och läsbarhet
        - [x] 89.8.4 Billigaste köp och försäljningar tillagda
    - [x] 89.9 Visa mest aktiva månader (när köps/säljs flest yxor)
        - [x] 89.9.1 Staplat stapeldiagram som visar antal köp/sälj per månad
        - [x] 89.9.2 Färgkodning: röd för köp, blå för sälj
        - [x] 89.9.3 Tooltip med exakt antal transaktioner per typ
        - [x] 89.9.4 Placerat efter ekonomiska diagrammen på statistiksidan
    - [x] 89.10 Visa senaste aktivitet (senaste köp, sälj, tillagd yxa)
        - [x] 89.10.1 Tre kort för senaste köp, försäljningar och tillagda yxor
        - [x] 89.10.2 Visar de 5 senaste aktiviteterna per kategori
        - [x] 89.10.3 Länkar till respektive yxas detaljsida
        - [x] 89.10.4 Färgkodning: grön för köp, röd för sälj, blå för tillagda yxor
        - [x] 89.10.5 Visar datum och pris/tillverkare för varje aktivitet
90. [ ] QR-kod för att snabbt visa en yxa på mobilen. **(Pausad – kräver vidare diskussion och behovsanalys innan implementation)**

## 13. Framtida förbättringar

91. [x] Fixa JavaScript-fel och landsfält-problem
    - [x] 91.1 Fixa SyntaxError på yxformuläret (`window.axeId = ;` när axe.pk inte finns)
    - [x] 91.2 Ersätt komplex sökbar select med enkel dropdown för landsfält på kontaktformuläret
    - [x] 91.3 Ta bort all debug-kod (console.log) från båda formulären
    - [x] 91.4 Förbättra felhantering för Django-template-syntax i JavaScript
    - [x] 91.5 Implementera konsekvent landsfält med flagg-emoji och landsnamn
    - [x] 91.6 Stöd för redigering av befintliga kontakter med landskod
    - [x] 91.7 Rensa kod från onödiga CSS-regler och JavaScript-funktioner
    - [x] 91.8 Förbättra användarupplevelse med enkel och pålitlig dropdown-lista
92. [x] Fixa duplicerad "Detaljer"-knapp på /galleri-sidan
    - [x] 92.1 Fixa SyntaxError på yxformuläret (`window.axeId = ;` när axe.pk inte finns)
    - [x] 92.2 Ersätt komplex sökbar select med enkel dropdown för landsfält på kontaktformuläret
    - [x] 92.3 Ta bort all debug-kod (console.log) från båda formulären
    - [x] 92.4 Förbättra felhantering för Django-template-syntax i JavaScript
    - [x] 92.5 Implementera konsekvent landsfält med flagg-emoji och landsnamn
    - [x] 92.6 Stöd för redigering av befintliga kontakter med landskod
    - [x] 92.7 Rensa kod från onödiga CSS-regler och JavaScript-funktioner
    - [x] 92.8 Förbättra användarupplevelse med enkel och pålitlig dropdown-lista
93. [ ] Kommentarsystem (framtida funktion)
    - [ ] 93.1 Möjlighet att kommentera yxor
    - [ ] 93.2 Möjlighet att kommentera tillverkare
    - [ ] 93.3 Moderationssystem för kommentarer
    - [ ] 93.4 Användarhantering för kommentarer
94. [ ] Förbättrad felhantering och validering i formulär.
95. [ ] Snabbare AJAX-sökningar med caching.
96. [ ] Tangentbordsnavigering i lightbox (piltangenter för att bläddra mellan bilder).
97. [ ] Touch-gester för mobil navigering i lightbox (swipe för att bläddra).
98. [ ] Zoom-funktionalitet i lightbox för att se bilder i full storlek.
99. [ ] Automatisk bildrotation baserat på EXIF-data.
100. [ ] Bulk-redigering av bilder (redigera flera bilder samtidigt).
101. [ ] Bildkommentarer med @-mentions för att länka till tillverkare eller yxor.