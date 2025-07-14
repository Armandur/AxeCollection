# Projektidéer & förbättringsförslag

En checklista för vidareutveckling av AxeCollection. Bocka av med [x] när klart!

## Bildhantering

1. [ ] Bildkomprimering/optimering vid uppladdning – Gör bilder snabbare att ladda på mobil.
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

## Användarupplevelse

15. [ ] Förbättrad responsivitet – Testa och förbättra för surfplattor och olika mobilstorlekar.
16. [ ] Touchvänliga knappar även på desktop – T.ex. piltangenter för bildbyte.
17. [x] Mörkt läge (dark mode) för hela tjänsten – Respekterar operativsystemets tema automatiskt och har en sol/måne-knapp för manuell växling.
18. [x] Notifikationssystem – Snygga notifikationer för användarfeedback vid alla operationer.
19. [x] Laddningsindikatorer – Spinner och inaktiverade knappar under pågående operationer.
20. [x] AJAX-animationer – Smooth övergångar och animationer för bättre användarupplevelse.

## Sök och filtrering

18. [x] AJAX-sökning för kontakter – Realtidssökning med dropdown-resultat för befintliga kontakter.
19. [x] AJAX-sökning för plattformar – Realtidssökning med dropdown-resultat för befintliga plattformar.
20. [x] Moderniserad AJAX-sökning för kontakt och plattform i yxformuläret
    - [x] 20.1 Återställt och moderniserat JavaScript för AJAX-sökning
    - [x] 20.2 Lagt till saknade plattformsfält i forms.py (platform_name, platform_url, platform_comment)
    - [x] 20.3 Uppdaterat axe_create i views_axe.py med komplett formulärhantering för kontakt, plattform och transaktion
    - [x] 20.4 Lagt till dropdown-containers för sökresultat i axe_form.html
    - [x] 20.5 Implementerat funktioner för att visa/dölja sektioner för nya kontakter och plattformar
    - [x] 20.6 Lagt till next_id i context för att visa nästa yx-ID
    - [x] 20.7 Förbättrat felhantering och användarupplevelse
21. [ ] Sökfunktion för yxor och tillverkare – Snabbt hitta yxor, tillverkare eller transaktioner.
22. [ ] Filtrering på t.ex. tillverkare, typ, årtal, mm.

## Yxhantering och inmatning

23. [x] Redigera transaktion, plattform och kontakt för en yxa via detaljvyn
    - [x] 23.1 Visa "Lägg till transaktion"-knapp om ingen transaktion finns
    - [x] 23.2 Visa "Redigera transaktioner"-knapp om en eller flera transaktioner finns
    - [x] 23.3 Bygg formulär för att lägga till/redigera transaktion (pris, frakt, kontakt, plattform, kommentar, datum)
    - [x] 23.4 Implementera AJAX-sökning för kontakt och plattform i formuläret
    - [x] 23.5 Möjlighet att skapa ny kontakt/plattform direkt i formuläret
    - [x] 23.6 Möjlighet att ta bort transaktion
24. [x] UI för att skapa nya yxor i samlingen – Användarvänligt formulär för att lägga till yxor.
25. [x] UI för att redigera befintliga yxor – Möjlighet att uppdatera information efter mottagning.
26. [x] Status-fält och filter – Status "Köpt" vs "Mottagen/Ägd" med filter och snabbåtgärder (markera som mottagen) i yxlistan.
27. [x] Arbetsflöde för inköp: 
    - Skapa/redigera yxa (tillverkare, modell, kommentar) ✅
    - Ladda upp bilder från auktion/annons ✅
    - Skapa/redigera kontakt (försäljare på Tradera etc.) ✅
    - Skapa transaktion (inköp med pris, frakt, datum) ✅
28. [x] Arbetsflöde för mottagning:
    - [x] Lägg till fler bilder av mottagen yxa (via befintlig redigeringsfunktionalitet)
    - [x] Mät och registrera mått (nytt måttinmatningsformulär med mallar)
    - [x] Uppdatera eventuell felaktig information (via befintlig redigeringsfunktionalitet)
    - [x] Dedikerat mottagningsarbetsflöde med steg-för-steg process
    - [x] Måttmallar för olika yxtyper (standard, fällkniv, köksyxa)
    - [x] AJAX-hantering för måttinmatning och borttagning
    - [x] Länkar till mottagningsarbetsflödet från yxlistan och yxdetail
29. [x] Förbättrad mått-UX i redigeringsvyn:
    - [x] Batch-läggning av mått med tydlig info och notifikation
    - [x] Inline-redigering av mått (värde och enhet) via AJAX
    - [x] Borttagning av mått med snygg animation (utan sidladdning)
    - [x] Visuell feedback vid alla måttoperationer (notifikationer, laddningsindikatorer)
    - [x] Förbättrad felhantering och återställning av UI
    - [x] Fördröjd sidladdning för att visa notifikationer
30. [x] Snabbval av tillverkare – Dropdown för att välja tillverkare.
31. [x] Kontakthantering – Skapa nya kontakter direkt från yxformuläret med smart matchning.
32. [x] Transaktionshantering – Koppla yxor till köp/försäljning med pris, frakt och datum.
33. [x] Plattformshantering – Skapa nya plattformar direkt från yxformuläret med smart matchning.
34. [x] Automatisk transaktionstypbestämning – Baserat på pris (negativ = köp, positiv = sälj).
35. [x] Separata formulär för skapande vs redigering – Olika fält visas beroende på om yxa skapas eller redigeras.

## Admin och datahantering

34. [x] Förbättrad admin-raderingsvy för yxor – Tydlig lista över vad som tas bort, bockruta för bildradering.
35. [ ] Batchuppladdning av bilder och yxor.
36. [ ] Export/import av data (CSV, Excel) direkt från admin.
37. [ ] Automatiska backuper av databasen.
38. [ ] Eget administratörsgränssnitt för tillverkare
    - [x] 38.1 Redigera tillverkare-knapp kvar på nuvarande plats (endast namnändring)
    - [x] 38.2 Ny redigera-knapp i Informations-gruppen för att redigera information
    - [ ] 38.3 Flytta "Lägg till bild"-knapp till Bildgalleri-gruppen
    - [ ] 38.4 Flytta "Lägg till länk"-knapp till Länkar-gruppen
    - [ ] 38.5 Implementera formulär för redigering av tillverkarnamn
    - [x] 38.6 Implementera formulär för redigering av information
    - [x] 38.7 WYSIWYG markdown-redigerare för informationsfält (EasyMDE)
    - [x] 38.8 AJAX-hantering för snabb redigering utan sidladdning
    - [x] 38.9 Validering och felhantering för alla formulär
    - [x] 38.10 Notifikationer för framgångsrika redigeringar
    - [x] 38.11 Döpa om fält från "comment" till "information"
    - [x] 38.12 Inline-redigering av tillverkarnamn med AJAX
    - [x] 38.13 Markdown-stöd för bildbeskrivningar med EasyMDE
    - [x] 38.14 Lightbox med redigeringsmöjligheter för tillverkarbilder
    - [x] 38.15 Drag & drop-funktionalitet för bildordning
    - [x] 38.16 Navigationsknappar i lightbox för att bläddra mellan bilder i samma grupp
    - [x] 38.17 Semi-bold styling för bildtext för bättre läsbarhet
    - [x] 38.18 Vänsterställd text i lightbox för bättre läsbarhet av längre beskrivningar
    - [x] 38.19 Inline-redigering, borttagning och drag & drop-sortering för tillverkarlänkar
    - [x] 38.20 Klickbara kort för bilder (öppnar lightbox) och aktiva länkar (öppnar i ny flik)
    - [x] 38.21 Visuell hantering för inaktiva länkar (gråtonad styling, URL som text, "Inaktiv"-badge)
    - [x] 38.22 Hover-effekter på bild- och länkkort för bättre användarupplevelse
    - [x] 38.23 Template filter för att visa information i tillverkarlistan (strippa markdown, begränsa längd)

## Säkerhet och användare

38. [ ] Inloggning/behörighet – Privata delar eller flera användare.
39. [ ] Loggning av ändringar (audit trail).
40. [ ] Inför inloggning/adminvy så att endast inloggade kan redigera, och visa en publik vy där känsliga uppgifter (t.ex. kontaktnamn, personuppgifter och ev. priser) maskeras eller döljs.

## Prestanda och kodkvalitet

41. [ ] Fler automatiska tester (unit/integration).
42. [ ] CI/CD – Automatiska tester vid push (GitHub Actions).
43. [ ] Kodgranskning – Linting och kodstil (t.ex. black, flake8).
44. [x] Periodvis kodgranskning: Gå igenom och granska koden stegvis för att identifiera behov av övergripande refaktorisering, buggfixar och tillsnyggning. Gör detta processvis så att varje steg kan testas innan nästa påbörjas.
    - [x] 44.1 Refaktorera vyer till mindre filer (views_axe.py, views_contact.py, views_manufacturer.py, views_transaction.py)
    - [x] 44.2 Flytta statistik- och ekonomi-beräkning från vyer till model-properties
    - [x] 44.3 Skapa återanvändbara template-includes för statistik-kort (_stat_card.html, _axe_stats_cards.html, _contact_stats_cards.html, _transaction_stats_cards.html)
    - [x] 44.4 Uppdatera templates för att använda nya includes och model-properties
    - [x] 44.5 Förenkla fler templates med includes och templatetags (t.ex. transaktionsrader, status-badges, breadcrumbs)
    - [x] 44.5.1 Förbättrade breadcrumbs och rubrik på detaljsidan: ID - Tillverkare - Modell
    - [x] 44.6 Refaktorera formulär med återanvändbara komponenter
    - [x] Skapat och infört _form_field.html, _form_checkbox.html, _form_input_group.html
    - [x] Använt dessa i axe_form.html för kontakt, plattform, transaktion
    - [x] Förenklat och DRY:at markup för fält, checkboxar och input-grupper
    - [x] Förbättrat frontend-UX för dropdowns och sektioner
    - [x] Fixat buggar kring next_id och TemplateSyntaxError
    - [x] Dokumenterat vanliga fel och lösningar
    - [ ] 44.7 Lägg till tester för vyer, modeller och templatetags
    - [ ] 44.8 Prestandaoptimering (caching, lazy loading, etc.)
45. [x] Dokumentation av förbättringar - Uppdatera markdown-filer med genomförda förbättringar och lärdomar

## Design och presentation

45. [x] Bättre visuell presentation av galleriet, t.ex. lightbox för bilder.
46. [x] Förbättrad UI med badges och ikoner – Tydligare visning av transaktionstyper med ikoner.
47. [x] Förbättrad tillverkarsida – ID som badge, kommentar som egen sektion, hela bredden för korten.
48. [ ] Visa statistik (t.ex. antal yxor, mest populära tillverkare, dyraste köp).
49. [ ] QR-kod för att snabbt visa en yxa på mobilen.

## Framtida förbättringar

49. [ ] Förbättrad felhantering och validering i formulär.
50. [ ] Snabbare AJAX-sökningar med caching.
51. [ ] Tangentbordsnavigering i lightbox (piltangenter för att bläddra mellan bilder).
52. [ ] Touch-gester för mobil navigering i lightbox (swipe för att bläddra).
53. [ ] Zoom-funktionalitet i lightbox för att se bilder i full storlek.
54. [ ] Automatisk bildrotation baserat på EXIF-data.
55. [ ] Bulk-redigering av bilder (redigera flera bilder samtidigt).
56. [ ] Bildkommentarer med @-mentions för att länka till tillverkare eller yxor.

 