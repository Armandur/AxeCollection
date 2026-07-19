# Projektidéer & förbättringsförslag

> **Notera (2026-07-19):** De öppna punkterna har migrerats till backlog-verktyget
> (projekt-alias `axecollection`, se portalens todos-vy). Denna fil behålls som
> historik över genomfört arbete. Lägg nya todos i backlog, inte här.

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
17. [x] Nollställ cachning av bilder när ordning på yxbilder ändras för att undvika extra refresh på yxdetaljsidan
18. [x] Undersök om problemet också är relaterat till optimeringen av .webp-bilder

## 2. Användarupplevelse och interface

19. [x] Förbättrad responsivitet – Testa och förbättra för surfplattor och olika mobilstorlekar.
20. [x] Touchvänliga knappar även på desktop – T.ex. piltangenter för bildbyte.
21. [x] Mörkt läge (dark mode) för hela tjänsten – Respekterar operativsystemets tema automatiskt och har en sol/måne-knapp för manuell växling.
22. [x] Notifikationssystem – Snygga notifikationer för användarfeedback vid alla operationer.
23. [x] Laddningsindikatorer – Spinner och inaktiverade knappar under pågående operationer.
24. [x] AJAX-animationer – Smooth övergångar och animationer för bättre användarupplevelse.
25. [x] Fixa dark mode-konsistens
    - [x] 25.1 Kontaktdetaljsida - vita bakgrunder på kontaktinformation, medlemskap och adress
    - [x] 25.2 Systematisk genomgång av alla sidor för dark mode-konsistens
26. [x] Lägg till footer
    - [x] 26.1 Designa footer med relevant information (version, länkar, kontakt)
    - [x] 26.2 Implementera footer på alla sidor
    - [x] 26.3 Anpassa footer för både light och dark mode
27. [x] I demo-mode ska det visas en hint på logga in med demo/demo123 som användaruppgifter

## 3. Sök och filtrering

28. [x] AJAX-sökning för kontakter – Realtidssökning med dropdown-resultat för befintliga kontakter.
29. [x] AJAX-sökning för plattformar – Realtidssökning med dropdown-resultat för befintliga plattformar.
30. [x] Flaggemoji för kontakter – Visar landskod som flaggemoji bredvid kontaktnamn på alla relevanta ställen.
    - [x] 30.1 Lägg till country_code fält (ISO 3166-1 alpha-2) i Contact-modellen
    - [x] 30.2 Uppdatera befintliga kontakter med landskod för Sverige och Finland
    - [x] 30.3 Skapa country_flag template filter för att konvertera landskod till flaggemoji
    - [x] 30.4 Uppdatera ContactForm med sökbart select-fält med flagg-emoji och landsnamn
    - [x] 30.5 Lägg till flaggemoji på kontaktdetaljsidan (rubrik)
    - [x] 30.6 Lägg till flaggemoji i transaktionshistoriken på yxdetaljsidan
    - [x] 30.7 Lägg till flaggemoji i transaktioner på tillverkardetaljsidan
    - [x] 30.8 Lägg till flaggemoji i kontakter som handlat med tillverkaren
    - [x] 30.9 Lägg till flaggemoji i mest aktiva kontakter på statistik-sidan
    - [x] 30.10 Visa flaggemoji bredvid kontaktnamn i yxformuläret
    - [x] 30.11 Visa flaggemoji i kontaktlistan
    - [x] 30.12 Visa flaggemoji i transaktionslistan
31. [x] Global sökning i navbar – Sökfält i menyn som söker i yxor, kontakter, tillverkare och transaktioner med grupperade resultat.
    - [x] 31.1 Sökfält i navbar med responsiv design
    - [x] 31.2 Backend-endpoint för global sökning (/api/search/global/)
    - [x] 31.3 Sökning i yxor (tillverkare, modell, kommentar, ID)
    - [x] 31.4 Sökning i kontakter (namn, alias, e-post)
    - [x] 31.5 Sökning i tillverkare (namn, information)
    - [x] 31.6 Sökning i transaktioner (yxa, kontakt, plattform)
    - [x] 31.7 Grupperade resultat med ikoner och antal
    - [x] 31.8 Kortkommando Ctrl+K för att fokusera sökfältet
    - [x] 31.9 Länkar till detaljsidor för varje resultat
    - [x] 31.10 Flaggemoji för kontakter i sökresultaten
32. [x] Moderniserad AJAX-sökning för kontakt och plattform i yxformuläret
    - [x] 32.1 Återställt och moderniserat JavaScript för AJAX-sökning
    - [x] 32.2 Lagt till saknade plattformsfält i forms.py (platform_name, platform_url, platform_comment)
    - [x] 32.3 Uppdaterat axe_create i views_axe.py med komplett formulärhantering för kontakt, plattform och transaktion
    - [x] 32.4 Lagt till dropdown-containers för sökresultat i axe_form.html
    - [x] 32.5 Implementerat funktioner för att visa/dölja sektioner för nya kontakter och plattformar
    - [x] 32.6 Lagt till next_id i context för att visa nästa yx-ID
    - [x] 32.7 Förbättrat felhantering och användarupplevelse
33. [x] Sökfunktion för yxor och tillverkare – Snabbt hitta yxor, tillverkare eller transaktioner.
34. [x] Filtrering på t.ex. tillverkare, typ, årtal, mm.
35. [x] Plattformsfilter och visning i yxlistan
    - [x] 35.1 Möjliggör filtrering av yxor på plattform i yxlistan
    - [x] 35.2 Visar alla plattformar för varje yxa direkt i tabellen
    - [x] 35.3 Varje plattform får en unik färg för ökad överskådlighet
    - [x] 35.4 Alla plattformsnamn visas med konsekvent fetstil för tydlighet
    - [x] 35.5 Förbättrar användarupplevelsen vid sortering och översikt av yxor
    - [x] 35.6 Fixat Django ORM-relationer med related_name='transactions'
    - [x] 35.7 Förbättrad CSV-export med hantering av radbrytningar
    - [x] 35.8 Fixat statistikkort som nu visar korrekt data för filtrerade yxor (tidigare visade alltid hela samlingen)
36. [x] Måttkolumn och filtrering i yxlistan
    - [x] 36.1 Lägg till "Mått"-kolumn i yxlistan med linjal-ikon för yxor med registrerade mått
    - [x] 36.2 Visa antalet registrerade mått bredvid linjal-ikonen (t.ex. "📏 3" för 3 mått)
    - [x] 36.3 Tooltip/popup som visar måtten vid hovring över ikonen
37. [x] Filtreringen av Tillverkare på /yxor ska använda hierarkisk indentering med L-tecken som på /tillverkare/ny|redigera och /yxor/ny|redigera

## 4. Deployment och Docker

38. [x] Fixa Docker startup-problem
    - [x] 38.1 "exec /app/start.sh: no such file or directory" - fixade line endings och behörigheter
    - [x] 38.2 Nginx visar standard-sida istället för Django - korrekt Nginx-konfiguration inbyggd
    - [x] 38.3 Windows line endings i start.sh - automatisk konvertering i Dockerfile
    - [x] 38.4 Behörigheter för Unraid (nobody:users) - korrekt UID/GID-hantering
    - [x] 38.5 CSRF-fel vid inloggning - dynamisk host-konfiguration via UI och miljövariabler
    - [x] 38.6 Demo-installationer - stöd för flera instanser med olika host-konfigurationer
    - [x] 38.7 Databasbehörigheter på Unraid - automatisk fix av readonly database
    - [x] 38.8 Robust startup-process - automatisk skapande av kataloger och behörigheter
39. [x] Automatisk hantering av sökvägar för olika miljöer
    - [x] 39.1 Skapa script för att fixa bildsökvägar vid deployment (Windows backslashes → Linux forward slashes)
    - [x] 39.2 Automatisk konvertering av `/app/media/` prefix för Docker-miljöer
    - [x] 39.3 Hantera sökvägar för både utvecklingsmiljö (Windows) och produktionsmiljö (Linux)
    - [x] 39.4 Integrera sökvägsfix i deployment-processen
    - [x] 39.5 Testa och verifiera att bilder fungerar i både test- och produktionsmiljö
40. [x] Media-filhantering i produktionsmiljö
    - [x] 40.1 Konfigurera Nginx för att servera media-filer i produktion
    - [x] 40.2 Eller implementera CDN-lösning för media-filer
    - [x] 40.3 Eller konfigurera Django för att servera media-filer i produktion (inte rekommenderat för hög belastning)
    - [x] 40.4 Testa och verifiera att alla bilder fungerar korrekt i produktionsmiljö
    - [x] 40.5 Dokumentera lösningen för framtida deployment
41. [x] Deployment-konfiguration för produktion med SQLite
    - [x] 41.1 Produktionssettings-fil med säkerhetskonfiguration
    - [x] 41.2 Dockerfile med Gunicorn för produktion
    - [x] 41.3 Docker Compose-konfiguration med volymer
    - [x] 41.4 Deployment-guide med steg-för-steg instruktioner
    - [x] 41.5 Backup-script för automatisk säkerhetskopiering
    - [x] 41.6 Miljövariabler och konfigurationsmallar
    - [x] 41.7 Nginx-konfiguration för webbserver
    - [x] 41.8 SSL/HTTPS-konfiguration
    - [x] 41.9 Logging och övervakning
    - [x] 41.10 Säkerhetsinställningar för produktion
    - [x] 41.11 Omorganisation av deployment-filer till deploy/-mapp
    - [x] 41.12 Uppdaterad dokumentation för ny struktur
    - [x] 41.13 Tydlig separation mellan utveckling och deployment
42. [x] Fixa omorganisering av yxbilder i produktion
    - [x] 42.1 Omorganisering av yxbilder fungerar inte på Unraid-produktionsservern
    - [x] 42.2 Undersök skillnader mellan utvecklings- och produktionsmiljö
    - [x] 42.3 Kontrollera filbehörigheter och sökvägar i produktion
    - [x] 42.4 Testa drag & drop-funktionalitet i produktionsmiljö
43. [x] Åtgärda nginx-behörigheter i Docker-setup för att förhindra uppladdningsfel. Nginx får 'Permission denied' när den försöker skapa filer i /var/lib/nginx/body/ för uppladdningar. Katalogen ägs av 'nobody:users' men nginx körs som 'www-data'
    - [x] 43.1 Lägg till chown-kommando i Dockerfile eller startup-script för att sätta rätt ägare på /var/lib/nginx/body/ innan nginx startas
    - [x] 43.2 Säkerställ att katalogen alltid ägs av rätt användare (www-data) i Docker-setup för att förhindra framtida behörighetsproblem

## 5. Yxhantering och arbetsflöden

44. [x] Redigera transaktion, plattform och kontakt för en yxa via detaljvyn
    - [x] 44.1 Visa "Lägg till transaktion"-knapp om ingen transaktion finns
    - [x] 44.2 Visa "Redigera transaktioner"-knapp om en eller flera transaktioner finns
    - [x] 44.3 Bygg formulär för att lägga till/redigera transaktion (pris, frakt, kontakt, plattform, kommentar, datum)
    - [x] 44.4 Implementera AJAX-sökning för kontakt och plattform i formuläret
    - [x] 44.5 Möjlighet att skapa ny kontakt/plattform direkt i formuläret
    - [x] 44.6 Möjlighet att ta bort transaktion
45. [x] UI för att skapa nya yxor i samlingen – Användarvänligt formulär för att lägga till yxor.
46. [x] UI för att redigera befintliga yxor – Möjlighet att uppdatera information efter mottagning.
47. [x] Status-fält och filter – Status "Köpt" vs "Mottagen/Ägd" med filter och snabbåtgärder (markera som mottagen) i yxlistan.
48. [x] Arbetsflöde för inköp: 
49. [x] Arbetsflöde för mottagning:
    - [x] 49.1 Lägg till fler bilder av mottagen yxa (via befintlig redigeringsfunktionalitet)
    - [x] 49.2 Mät och registrera mått (nytt måttinmatningsformulär med mallar)
    - [x] 49.3 Uppdatera eventuell felaktig information (via befintlig redigeringsfunktionalitet)
    - [x] 49.4 Dedikerat mottagningsarbetsflöde med steg-för-steg process
    - [x] 49.5 Måttmallar för olika yxtyper (standard, fällkniv, köksyxa)
    - [x] 49.6 AJAX-hantering för måttinmatning och borttagning
    - [x] 49.7 Länkar till mottagningsarbetsflödet från yxlistan och yxdetail
50. [x] Snabbval av tillverkare – Dropdown för att välja tillverkare.
51. [x] Kontakthantering – Skapa nya kontakter direkt från yxformuläret med smart matchning.
52. [x] Plattformshantering – Skapa nya plattformar direkt från yxformuläret med smart matchning.
53. [x] Automatisk transaktionstypbestämning – Baserat på pris (negativ = köp, positiv = sälj).
54. [x] Separata formulär för skapande vs redigering – Olika fält visas beroende på om yxa skapas eller redigeras.
55. [x] Lägg till yxa via auktions-URL – Möjlighet att lägga till yxa genom att ange URL till vunnen Tradera- eller eBay-auktion.
    - [x] 55.1 Implementera URL-parser för Tradera-auktioner som extraherar titel, beskrivning, bilder och slutpris
    - [x] 55.2 Implementera URL-parser för eBay-auktioner med motsvarande funktionalitet
    - [x] 55.3 Automatisk förfyllning av yxformulär baserat på extraherad auktionsdata
    - [x] 55.4 Automatisk nedladdning och lagring av auktionsbilder
    - [x] 55.5 Intelligent kategorisering och tillverkargissning baserat på auktionsbeskrivning
    - [x] 55.6 Automatisk skapande av transaktion med slutpris som köpvärde
    - [x] 55.7 Felhantering för ogiltiga URL:er eller auktioner som inte kan parsas
    - [x] 55.8 Stöd för olika auktionsformat och språk (svenska/engelska)
    - [x] 55.9 Förhandsvisning av extraherad data innan sparning
    - [x] 55.10 Möjlighet att redigera och justera automatiskt extraherad information
    - [x] 55.11 Förbättrad eBay-parser: använd titeln som beskrivning om ingen beskrivning hittas
    - [x] 55.12 Automatisk skapande av Tradera och eBay som standardplattformar
    - [x] 55.13 Lagt till url och comment fält till Platform-modellen för bättre metadata
    - [x] 55.14 Valutahantering för auktionsparsers - identifiera och visa valuta från eBay-auktioner
    - [x] 55.15 Stöd för flera valutor (USD, EUR, GBP, SEK) i eBay-parsern
    - [x] 55.16 Valutavarningar i UI när priset inte är i SEK
    - [x] 55.17 Live valutakonvertering med exchangerate-api.com och caching
    - [x] 55.18 Konverteringsknapp i UI för att konvertera priser till SEK
    - [x] 55.19 Management command för att testa valutakonvertering
    - [x] 55.20 Omfattande tester för valutakonvertering och integration
56. [x] Fixa problem med att ändra tillverkare på en yxa - formuläret fungerar inte korrekt

## 6. Transaktions- och måtthantering

57. [x] Transaktionshantering – Koppla yxor till köp/försäljning med pris, frakt och datum.
58. [x] Förbättrad mått-UX i redigeringsvyn:
    - [x] 58.1 Batch-läggning av mått med tydlig info och notifikation
    - [x] 58.2 Inline-redigering av mått (värde och enhet) via AJAX
    - [x] 58.3 Borttagning av mått med snygg animation (utan sidladdning)
    - [x] 58.4 Visuell feedback vid alla måttoperationer (notifikationer, laddningsindikatorer)
    - [x] 58.5 Förbättrad felhantering och återställning av UI
    - [x] 58.6 Fördröjd sidladdning för att visa notifikationer
    - [x] 58.7 Möjlighet att ta bort enskilda rader från batch-måttformuläret (soptunne-ikon per rad)
    - [x] 58.8 Förbättrad DRY-princip med återanvändbar JavaScript-kod
    - [x] 58.9 Automatisk UI-uppdatering vid borttagning av mått (tomt tillstånd, räknare)
    - [x] 58.10 Event listener-baserad hantering istället för inline onclick
    - [x] 58.11 Korrekt omindexering av batch-formulärrader vid borttagning
    - [x] 58.12 Bekräfta/ångra-knappar för inline-redigering istället för modaler
    - [x] 58.13 Fullständig hantering av "Övrigt"-alternativet med textinput för anpassat måttnamn
    - [x] 58.14 Bootstrap modal för borttagningsbekräftelse istället för alert()
    - [x] 58.15 Korrekt skickande av data till backend (standardmått vs anpassade mått)
    - [x] 58.16 Förhindring av dubbla anrop med spärr under uppdatering
    - [x] 58.17 Automatisk enhetsfyllning när standardmåtttyper väljs
    - [x] 58.18 Visuell feedback med spinner och inaktiverade knappar under uppdatering
59. [x] Fixa enskilda mått
    - [x] 59.1 Ensamma mått kan inte läggas till, bara via batch-inlägg
    - [x] 59.2 Implementera funktionalitet för att lägga till enskilda mått
    - [x] 59.3 Testa att både enskilda och batch-mått fungerar korrekt
60. [x] Måttfiltrering i yxlistan – Filter för att visa endast yxor med eller utan mått
    - [x] 60.1 Filter för att visa endast yxor med/utan mått
    - [x] 60.2 Responsiv design för måttkolumnen på olika skärmstorlekar
61. [x] Måttmallshantering i inställningsmenyn – Möjlighet att skapa, redigera och hantera måttmallar direkt från systeminställningarna.
    - [x] 61.1 Lägg till sektion för måttmallshantering i inställningsmenyn
    - [x] 61.2 Formulär för att skapa nya måttmallar med namn och beskrivning
    - [x] 61.3 Drag & drop-gränssnitt för att lägga till/ta bort måtttyper i mallar
    - [x] 61.4 Redigering av befintliga måttmallar (namn, beskrivning, måtttyper)
    - [x] 61.5 Borttagning av måttmallar med varning om konsekvenser
    - [x] 61.6 Förhandsvisning av måttmallar med lista över inkluderade måtttyper
    - [x] 61.7 Validering för att säkerställa att mallar har minst ett mått
    - [x] 61.8 AJAX-hantering för snabb uppdatering utan sidladdning
    - [x] 61.9 Enhethantering - Möjlighet att definiera/ändra måttenheter och välja enhet för måttmallar (gram, mm, grader °)

## 7. Tillverkarhantering

62. [x] Formulär för tillverkarlänkar
    - [x] 62.1 Skapa formulär för att lägga till länkar och resurser på tillverkare
    - [x] 62.2 Implementera i tillverkardetaljsidan (för närvarande bara via Django admin)
    - [x] 62.3 Lägg till funktionalitet för att redigera och ta bort länkar
    - [x] 62.4 Säkerställ att order-fältet fungerar för sortering av länkar
63. [x] Eget administratörsgränssnitt för tillverkare
    - [x] 63.1 Redigera tillverkare-knapp kvar på nuvarande plats (endast namnändring)
    - [x] 63.2 Ny redigera-knapp i Informations-gruppen för att redigera information
    - [x] 63.3 Flytta "Lägg till bild"-knapp till Bildgalleri-gruppen
    - [x] 63.4 Flytta "Lägg till länk"-knapp till Länkar-gruppen
    - [x] 63.5 Implementera formulär för redigering av tillverkarnamn
    - [x] 63.6 Implementera formulär för redigering av information
    - [x] 63.7 WYSIWYG markdown-redigerare för informationsfält (EasyMDE)
    - [x] 63.8 AJAX-hantering för snabb redigering utan sidladdning
    - [x] 63.9 Validering och felhantering för alla formulär
    - [x] 63.10 Notifikationer för framgångsrika redigeringar
    - [x] 63.11 Döpa om fält från "comment" till "information"
    - [x] 63.12 Inline-redigering av tillverkarnamn med AJAX
    - [x] 63.13 Markdown-stöd för bildbeskrivningar med EasyMDE
    - [x] 63.14 Lightbox med redigeringsmöjligheter för tillverkarbilder
    - [x] 63.15 Drag & drop-funktionalitet för bildordning
    - [x] 63.16 Navigationsknappar i lightbox för att bläddra mellan bilder i samma grupp
    - [x] 63.17 Semi-bold styling för bildtext för bättre läsbarhet
    - [x] 63.18 Vänsterställd text i lightbox för bättre läsbarhet av längre beskrivningar
    - [x] 63.19 Inline-redigering, borttagning och drag & drop-sortering för tillverkarlänkar
    - [x] 63.20 Klickbara kort för bilder (öppnar lightbox) och aktiva länkar (öppnar i ny flik)
    - [x] 63.21 Visuell hantering för inaktiva länkar (gråtonad styling, URL som text, "Inaktiv"-badge)
    - [x] 63.22 Hover-effekter på bild- och länkkort för bättre användarupplevelse
    - [x] 63.23 Template filter för att visa information i tillverkarlistan (strippa markdown, begränsa längd)
64. [x] Hierarkiskt tillverkarsystem med undertillverkare/smeder
    - [x] 64.1 Lägg till parent_manufacturer ForeignKey-fält i Manufacturer-modellen
    - [x] 64.2 Uppdatera tillverkarformuläret med dropdown för överordnad tillverkare
    - [x] 64.3 Visa undertillverkare/smeder som underavdelning på tillverkardetaljsidan (t.ex. "Smeder på Gränsfors Bruk")
    - [x] 64.4 Implementera träd-visning i tillverkarlistan med indenterade undertillverkare
    - [x] 64.5 Möjlighet att filtrera yxor på både huvud- och undertillverkare
    - [x] 64.6 Statistik för undertillverkare som summeras till huvudtillverkaren
    - [x] 64.7 Breadcrumbs som visar hierarki
    - [x] 64.8 Validering för att förhindra cirkulära referenser
    - [x] 64.9 Migration för att hantera befintliga tillverkare
    - [x] 64.10 Admin-gränssnitt med träd-struktur för enkel hantering
65. [x] Ekonomikolumnen för tillverkare ska summera de eventuella underliggande tillverkarna - både i tillverkarlistan och på tillverkaredetaljsidan. På detaljsidan ska det delas upp mellan yxor kopplade direkt till tillverkaren och yxor från underliggande tillverkare/smeder
66. [x] Indentering av tillverkare och underordnade smeder ska fungera även på skapa/redigera yxformuläret
67. [x] Organisationssektionen på tillverkarsidan ska visas för inloggade användare även när det inte finns undertillverkare, med "Lägg till undertillverkare"-knapp
68. [x] Breadcrumbs för tillverkare verkar inte hantera alla nivåer korrekt
69. [x] Behöver tänka på hur vi ska hantera borttag av tillverkare som har underliggande tillverkare/smeder
70. [x] Lägg till land på tillverkare och visa flaggemoji vid tillverkarnamnet/smednamnet precis som för kontakter
71. [x] Implementera förbättrad hantering av borttag av tillverkare med undertillverkare/smeder
    - [x] 71.1 Uppdatera delete-funktionen i views_manufacturer.py att hantera undertillverkare
    - [x] 71.2 Lägg till validering för undertillverkare i delete-funktionen
    - [x] 71.3 Uppdatera manufacturer_detail.html modal att visa undertillverkare
    - [x] 71.4 Lägg till alternativ för hantering av undertillverkare (ta bort/flytta/gör till huvudtillverkare)
    - [x] 71.5 Uppdatera JavaScript för att hantera nya val för undertillverkare
    - [x] 71.6 Lägg till varningar och bekräftelse för destruktiva operationer
    - [x] 71.7 Uppdatera AJAX-anrop att skicka data för undertillverkare-hantering
    - [x] 71.8 Testa funktionaliteten med hierarkiska tillverkare
    - [x] 71.9 Dokumentera den nya funktionaliteten
72. [x] Fixat Python-fel i delete_manufacturer - target_manufacturer_name variabeln var inte alltid definierad

## 8. Admin och datahantering

73. [x] Förbättrad admin-raderingsvy för yxor – Tydlig lista över vad som tas bort, bockruta för bildradering.
74. [ ] Batchuppladdning av yxor – Möjlighet att ladda upp flera yxor samtidigt. **(Pausad – kräver vidare diskussion och behovsanalys innan implementation)**
75. [x] Export/import av data (CSV, Excel) direkt från admin.
76. [x] Automatiska backuper av databasen.
    - [x] 76.1 Backup-funktionalitet flyttad från admin till systeminställningsvyn
    - [x] 76.2 Integrerad backup-hantering i settings.html med modern UI
    - [x] 76.3 Skapa, ta bort och återställ backuper direkt från inställningssidan
    - [x] 76.4 Statistik-visning för varje backup (antal yxor, kontakter, transaktioner)
    - [x] 76.5 Varningar för återställning med bekräftelsedialoger
    - [x] 76.6 Stöd för komprimerade backuper och media-filer
    - [x] 76.7 Automatisk rensning av gamla backuper (30 dagar)
    - [ ] 76.8 Backup-uppladdning via webbgränssnitt - Lösa problem med stora filer (>100MB) och nginx-konfiguration
        - [ ] 76.8.1 Fixa nginx client_max_body_size för stora backupfiler (2GB+)
        - [ ] 76.8.2 Förbättra JavaScript AJAX-uppladdning för stora filer
        - [ ] 76.8.3 Lägg till progress-indikator för stora filer
        - [ ] 76.8.4 Testa och verifiera att uppladdning fungerar för filer >100MB
        - [ ] 76.8.5 Dokumentera lösningen för framtida deployment
77. [x] Förbättrad navigering på systeminställningssidan.
    - [x] 77.1 Bootstrap navbar för in-page navigering mellan sektioner
    - [x] 77.2 Smooth scrolling med scroll-margin-top för att visa headers
    - [x] 77.3 Aktiv länk-markering baserat på scroll-position
    - [x] 77.4 Responsiv design för navigeringsmenyn
    - [x] 77.5 Korrekt styling med ljus bakgrund och mörk text
78. [x] Vy för okopplade bilder – Rutnätsvy med funktioner för att ta bort och ladda ner bilder som flyttats från borttagna yxor.
    - [x] 78.1 Rutnätsvy med bildkort som visar filnamn, storlek och timestamp
    - [x] 78.2 Gruppering av bilder efter timestamp (när yxan togs bort)
    - [x] 78.3 Soptunne-ikon för att ta bort enskilda bilder
    - [x] 78.4 Ladda ner-ikon för att spara ner enskilda bilder
    - [x] 78.5 Massåtgärder med checkboxar för att välja flera bilder
    - [x] 78.6 "Ladda ner valda"-knapp som skapar ZIP-fil med valda bilder
    - [x] 78.7 Statistik-kort som visar totalt antal bilder, storlek och antal grupper
    - [x] 78.8 Responsiv design som fungerar på mobil och desktop
    - [x] 78.9 AJAX-hantering för borttagning utan sidladdning
    - [x] 78.10 Hover-effekter och animationer för bättre användarupplevelse
    - [x] 78.11 .webp-optimering: visar .webp-versioner för snabbare laddning men laddar ner originalfiler
    - [x] 78.12 Korrekt svenska grammatik med plural-former för "antal bilder" och "antal grupper"
    - [x] 78.13 Lägg till länk till vyn i admin-navigation (kommer att implementeras när inloggning/adminvy införs)
    - [x] 78.14 Implementera motsvarande hantering för borttagning av tillverkare och deras bilder (flytt till okopplade bilder)
        - [x] 78.14.1 Analysera vad som ska hända med yxor som tillhör tillverkaren (behåll som "okänd tillverkare" vs förhindra borttagning)
        - [x] 78.14.2 Utvärdera om funktionen ens behövs eller om tillverkare ska vara permanent

## 9. Säkerhet och användare

79. [x] Inloggning/behörighet – Privata delar eller flera användare.
    - [x] 79.1 Django Auth-system implementerat med anpassade templates
    - [x] 79.2 Långa sessioner (30 dagar) för bättre användarupplevelse
    - [x] 79.3 Starka lösenord (minst 12 tecken) med Django's validering
    - [x] 79.4 Login/logout-funktionalitet med redirect till rätt sida
    - [x] 79.5 Användardropdown i navigationen med inställningar och logout
    - [x] 79.6 Responsiv login-modal i navigationen för snabb inloggning
    - [x] 79.7 Tydlig visuell feedback för inloggade vs icke-inloggade användare
80. [ ] Loggning av ändringar (audit trail).
81. [x] Inför inloggning/adminvy så att endast inloggade kan redigera, och visa en publik vy där känsliga uppgifter (t.ex. kontaktnamn, personuppgifter och ev. priser) maskeras eller döljs.
    - [x] 81.1 Settings-modell med konfigurerbara publika inställningar
    - [x] 81.2 Context processor som gör publika inställningar tillgängliga i alla templates
    - [x] 81.3 Automatisk filtrering av känslig data för icke-inloggade användare
    - [x] 81.4 Kontroll av användarstatus i alla vyer som visar känslig information
    - [x] 81.5 Fallback-hantering om Settings-modellen inte finns ännu
    - [x] 81.6 Dedikerad inställningssida för administratörer
    - [x] 81.7 Switches för alla publika inställningar med tydliga beskrivningar
    - [x] 81.8 Sajtinställningar för titel och beskrivning
    - [x] 81.9 Endast inloggade användare kan komma åt inställningarna
    - [x] 81.10 Global sökning respekterar publika inställningar
    - [x] 81.11 Kontaktsökning döljs för icke-inloggade användare om inställt
    - [x] 81.12 Plattformssökning kan konfigureras för publik/privat visning
    - [x] 81.13 Intelligent filtrering baserat på användarstatus
    - [x] 81.14 Yxlistan filtreras automatiskt för icke-inloggade användare
    - [x] 81.15 Transaktionsdata döljs eller visas baserat på inställningar
    - [x] 81.16 Kontaktinformation maskeras för publika användare
    - [x] 81.17 Prisinformation kan döljas för publika användare
    - [x] 81.18 Konsekvent navigation som anpassas efter användarstatus
    - [x] 81.19 Snygga ikoner och styling för användargränssnittet
    - [x] 81.20 Fixa yxdetaljsidan: Pris- och fraktkolumner visas fortfarande för publika användare trots att de ska döljas
    - [x] 81.21 Fixa ekonomiska statistikkort på /yxor: Kronor-relaterade kort (vinst/förlust, totala värden) visas fortfarande för publika användare, ska döljas helt

## 10. Prestanda och kodkvalitet

82. [x] Fler automatiska tester (unit/integration).
83. [x] CI/CD – Automatiska tester vid push (GitHub Actions).
    - [x] 83.1 Skapa GitHub Actions workflow för automatisk testning
    - [x] 83.2 Konfigurera Docker build och push i CI/CD
    - [x] 83.3 Lägg till test coverage reporting i CI/CD
    - [ ] 83.4 Konfigurera automatisk deployment till testmiljö
84. [x] Kodgranskning – Linting och kodstil (t.ex. black, flake8).
85. [x] Periodvis kodgranskning: Gå igenom och granska koden stegvis för att identifiera behov av övergripande refaktorering, buggfixar och tillsnyggning. Gör detta processvis så att varje steg kan testas innan nästa påbörjas.
    - [x] 85.1 Refaktorera vyer till mindre filer (views_axe.py, views_contact.py, views_manufacturer.py, views_transaction.py)
    - [x] 85.2 Flytta statistik- och ekonomi-beräkning från vyer till model-properties
    - [x] 85.3 Skapa återanvändbara template-includes för statistik-kort (_stat_card.html, _axe_stats_cards.html, _contact_stats_cards.html, _transaction_stats_cards.html)
    - [x] 85.4 Uppdatera templates för att använda nya includes och model-properties
    - [x] 85.5 Förenkla fler templates med includes och templatetags (t.ex. transaktionsrader, status-badges, breadcrumbs)
    - [x] 85.6 Refaktorera formulär med återanvändbara komponenter
    - [x] 85.7 Lägg till tester för vyer, modeller och templatetags
    - [ ] 85.8 Prestandaoptimering (caching, lazy loading, etc.)
86. [x] Dokumentation av förbättringar - Uppdatera markdown-filer med genomförda förbättringar och lärdomar
87. [ ] Implementera Django REST Framework och ViewSets
88. [x] Skapa fingerad testdata för demo och testning
    - [x] 88.1 Exportera nuvarande databas-struktur för att förstå datamodellen
    - [x] 88.2 Skapa script för att generera realistisk testdata (yxor, tillverkare, kontakter, transaktioner)
    - [x] 88.3 Inkludera olika typer av yxor med varierande mått, bilder och transaktioner
    - [x] 88.4 Skapa tillverkare med olika antal bilder och länkar
    - [x] 88.5 Generera kontakter från olika länder med flaggemoji
    - [x] 88.6 Skapa transaktioner med olika plattformar och priser
    - [x] 88.7 Testa alla funktioner med testdata (sökning, filtrering, statistik, etc.)
    - [x] 88.8 Förbereda för publik demo-webbplats
    - [x] 88.9 Dokumentera hur man återställer till testdata
89. [x] todo_manager behöver kunna hantera underuppgifter som 58.4 (slutföra underuppgifter)

## 11. Testdata och demo

90. [x] Skapa fingerad testdata för demo och testning
91. [x] Docker demo-läge med miljövariabel
    - [x] 91.1 Lägg till miljövariabel DEMO_MODE för Docker-containern
    - [x] 91.2 Implementera logik som kontrollerar DEMO_MODE vid container-start
    - [x] 91.3 Automatisk körning av `generate_test_data --clear` när DEMO_MODE=true
    - [x] 91.4 Säkerställ att demo-läget endast körs vid container-start, inte vid reload
    - [x] 91.5 Dokumentera användning av demo-läge i deployment-guider
    - [x] 91.6 Testa demo-läge i olika Docker-miljöer (utveckling, produktion)
92. [x] Ordna demodata med hierarkiska tillverkare - Till exempel är smederna Johan Jonsson, Johan Skog och Willy Persson alla tre smeder hos Hjärtumssmedjan

## 12. Design och presentation

93. [x] Bättre visuell presentation av galleriet, t.ex. lightbox för bilder.
94. [x] Förbättrad UI med badges och ikoner – Tydligare visning av transaktionstyper med ikoner.
95. [x] Förbättrad tillverkarsida – ID som badge, kommentar som egen sektion, hela bredden för korten.
96. [x] Visa statistik (t.ex. antal yxor, mest populära tillverkare, dyraste köp).
    - [x] 96.1 Dedikerad statistik-dashboard med samlingsöversikt
    - [x] 96.2 Topplistor för mest aktiva tillverkare, plattformar och kontakter
    - [x] 96.3 Ekonomisk översikt med totala köp- och försäljningsvärden
    - [x] 96.4 Realtidsstatistik som uppdateras baserat på aktiva filter
    - [x] 96.5 Fixat Django ORM-problem med annotate och properties
    - [x] 96.6 Visa antal yxor i samlingen över tid (linje- eller stapeldiagram)
        - [x] 96.6.1 Kombinerad tidslinje med "Yxor köpta (total)" och "Yxor i samlingen"
        - [x] 96.6.2 Grupperad per månad baserat på transaktionsdatum
        - [x] 96.6.3 Visar tydligt skillnaden mellan köpta och kvarvarande yxor
        - [x] 96.6.4 Chart.js-implementation med två färgkodade linjer
    - [x] 96.7 Visa totala inköpskostnader och försäljningsintäkter över tid (diagram)
        - [x] 96.7.1 Stapeldiagram med transaktionsvärden per månad
        - [x] 96.7.2 Röda staplar för köpvärde, gröna för försäljningsvärde
        - [x] 96.7.3 Visar aktivitet över tid istället för kumulativa värden
        - [x] 96.7.4 Svensk formatering av belopp i tooltips och axlar
    - [x] 96.8 Visa dyraste och billigaste köp/sälj i topplistan, med länk till respektive yxa
        - [x] 96.8.1 Länkar till yxorna från alla transaktionslistor
        - [x] 96.8.2 Förbättrad layout med radbrytning för långa yxnamn
        - [x] 96.8.3 Flexbox-layout för bättre "tabb-avstånd" och läsbarhet
        - [x] 96.8.4 Billigaste köp och försäljningar tillagda
    - [x] 96.9 Visa mest aktiva månader (när köps/säljs flest yxor)
        - [x] 96.9.1 Staplat stapeldiagram som visar antal köp/sälj per månad
        - [x] 96.9.2 Färgkodning: röd för köp, blå för sälj
        - [x] 96.9.3 Tooltip med exakt antal transaktioner per typ
        - [x] 96.9.4 Placerat efter ekonomiska diagrammen på statistiksidan
    - [x] 96.10 Visa senaste aktivitet (senaste köp, sälj, tillagd yxa)
        - [x] 96.10.1 Tre kort för senaste köp, försäljningar och tillagda yxor
        - [x] 96.10.2 Visar de 5 senaste aktiviteterna per kategori
        - [x] 96.10.3 Länkar till respektive yxas detaljsida
        - [x] 96.10.4 Färgkodning: grön för köp, röd för sälj, blå för tillagda yxor
        - [x] 96.10.5 Visar datum och pris/tillverkare för varje aktivitet
97. [ ] QR-kod för att snabbt visa en yxa på mobilen. **(Pausad – kräver vidare diskussion och behovsanalys innan implementation)**

## 13. Framtida förbättringar

98. [x] Fixa JavaScript-fel och landsfält-problem
    - [x] 98.1 Fixa SyntaxError på yxformuläret (`window.axeId = ;` när axe.pk inte finns)
    - [x] 98.2 Ersätt komplex sökbar select med enkel dropdown för landsfält på kontaktformuläret
    - [x] 98.3 Ta bort all debug-kod (console.log) från båda formulären
    - [x] 98.4 Förbättra felhantering för Django-template-syntax i JavaScript
    - [x] 98.5 Implementera konsekvent landsfält med flagg-emoji och landsnamn
    - [x] 98.6 Stöd för redigering av befintliga kontakter med landskod
    - [x] 98.7 Rensa kod från onödiga CSS-regler och JavaScript-funktioner
    - [x] 98.8 Förbättra användarupplevelse med enkel och pålitlig dropdown-lista
99. [x] Fixa duplicerad "Detaljer"-knapp på /galleri-sidan
    - [x] 99.1 Fixa SyntaxError på yxformuläret (`window.axeId = ;` när axe.pk inte finns)
    - [x] 99.2 Ersätt komplex sökbar select med enkel dropdown för landsfält på kontaktformuläret
    - [x] 99.3 Ta bort all debug-kod (console.log) från båda formulären
    - [x] 99.4 Förbättra felhantering för Django-template-syntax i JavaScript
    - [x] 99.5 Implementera konsekvent landsfält med flagg-emoji och landsnamn
    - [x] 99.6 Stöd för redigering av befintliga kontakter med landskod
    - [x] 99.7 Rensa kod från onödiga CSS-regler och JavaScript-funktioner
    - [x] 99.8 Förbättra användarupplevelse med enkel och pålitlig dropdown-lista
100. [ ] Kommentarsystem (framtida funktion)
    - [ ] 100.1 Möjlighet att kommentera yxor
    - [ ] 100.2 Möjlighet att kommentera tillverkare
    - [ ] 100.3 Moderationssystem för kommentarer
    - [ ] 100.4 Användarhantering för kommentarer
101. [ ] Förbättrad felhantering och validering i formulär.
102. [ ] Snabbare AJAX-sökningar med caching.
103. [ ] Tangentbordsnavigering i lightbox (piltangenter för att bläddra mellan bilder).
104. [ ] Touch-gester för mobil navigering i lightbox (swipe för att bläddra).
105. [ ] Zoom-funktionalitet i lightbox för att se bilder i full storlek.
106. [ ] Automatisk bildrotation baserat på EXIF-data.
107. [ ] Bulk-redigering av bilder (redigera flera bilder samtidigt).
108. [ ] Bildkommentarer med @-mentions för att länka till tillverkare eller yxor.
109. [ ] **📋 Detaljerad dokumentation:** Se [STAMP_REGISTER_FEATURE.md](STAMP_REGISTER_FEATURE.md) för fullständig beskrivning av funktionen, datamodeller, API-endpoints och implementation.