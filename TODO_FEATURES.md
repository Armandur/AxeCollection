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
13. [x] Drag & drop för bildordning i redigeringsläge.
14. [x] Hantera många stämpelbilder på tillverkarsidan (t.ex. paginering, grid, lightbox eller liknande UX-lösning).
15. [x] URL-uppladdning av bilder – Ladda ner bilder från URL:er med förhandsvisning och drag & drop.
16. [x] Fixa rearranging av yxbilder – Implementera drag & drop-funktionalitet för att ändra ordning på yxbilder i galleriet och redigeringsläge.

## 2. Användarupplevelse och interface

17. [x] Förbättrad responsivitet – Testa och förbättra för surfplattor och olika mobilstorlekar.
18. [x] Touchvänliga knappar även på desktop – T.ex. piltangenter för bildbyte.
19. [x] Mörkt läge (dark mode) för hela tjänsten – Respekterar operativsystemets tema automatiskt och har en sol/måne-knapp för manuell växling.
20. [x] Notifikationssystem – Snygga notifikationer för användarfeedback vid alla operationer.
21. [x] Laddningsindikatorer – Spinner och inaktiverade knappar under pågående operationer.
22. [x] AJAX-animationer – Smooth övergångar och animationer för bättre användarupplevelse.
23. [x] Fixa dark mode-konsistens
24. [x] Lägg till footer

## 3. Sök och filtrering

25. [x] AJAX-sökning för kontakter – Realtidssökning med dropdown-resultat för befintliga kontakter.
26. [x] AJAX-sökning för plattformar – Realtidssökning med dropdown-resultat för befintliga plattformar.
27. [x] Flaggemoji för kontakter – Visar landskod som flaggemoji bredvid kontaktnamn på alla relevanta ställen.
28. [x] Global sökning i navbar – Sökfält i menyn som söker i yxor, kontakter, tillverkare och transaktioner med grupperade resultat.
29. [x] Moderniserad AJAX-sökning för kontakt och plattform i yxformuläret
30. [x] Sökfunktion för yxor och tillverkare – Snabbt hitta yxor, tillverkare eller transaktioner.
31. [x] Filtrering på t.ex. tillverkare, typ, årtal, mm.
32. [x] Plattformsfilter och visning i yxlistan
33. [x] Måttkolumn och filtrering i yxlistan

## 4. Deployment och Docker

34. [x] Fixa Docker startup-problem
35. [x] Automatisk hantering av sökvägar för olika miljöer
36. [x] Media-filhantering i produktionsmiljö
37. [x] Deployment-konfiguration för produktion med SQLite
38. [ ] Fixa omorganisering av yxbilder i produktion

## 5. Yxhantering och arbetsflöden

39. [x] Redigera transaktion, plattform och kontakt för en yxa via detaljvyn
40. [x] UI för att skapa nya yxor i samlingen – Användarvänligt formulär för att lägga till yxor.
41. [x] UI för att redigera befintliga yxor – Möjlighet att uppdatera information efter mottagning.
42. [x] Status-fält och filter – Status "Köpt" vs "Mottagen/Ägd" med filter och snabbåtgärder (markera som mottagen) i yxlistan.
43. [x] Arbetsflöde för inköp: 
44. [x] Arbetsflöde för mottagning:
45. [x] Snabbval av tillverkare – Dropdown för att välja tillverkare.
46. [x] Kontakthantering – Skapa nya kontakter direkt från yxformuläret med smart matchning.
47. [x] Plattformshantering – Skapa nya plattformar direkt från yxformuläret med smart matchning.
48. [x] Automatisk transaktionstypbestämning – Baserat på pris (negativ = köp, positiv = sälj).
49. [x] Separata formulär för skapande vs redigering – Olika fält visas beroende på om yxa skapas eller redigeras.
50. [ ] Lägg till yxa via auktions-URL – Möjlighet att lägga till yxa genom att ange URL till vunnen Tradera- eller eBay-auktion.

## 6. Transaktions- och måtthantering

51. [x] Transaktionshantering – Koppla yxor till köp/försäljning med pris, frakt och datum.
52. [x] Förbättrad mått-UX i redigeringsvyn:
53. [x] Fixa enskilda mått
54. [x] Måttfiltrering i yxlistan – Filter för att visa endast yxor med eller utan mått
55. [x] Måttmallshantering i inställningsmenyn – Möjlighet att skapa, redigera och hantera måttmallar direkt från systeminställningarna.

## 7. Tillverkarhantering

56. [x] Formulär för tillverkarlänkar
57. [x] Eget administratörsgränssnitt för tillverkare
58. [ ] Hierarkiskt tillverkarsystem med undertillverkare/smeder

## 8. Admin och datahantering

59. [x] Förbättrad admin-raderingsvy för yxor – Tydlig lista över vad som tas bort, bockruta för bildradering.
60. [ ] Batchuppladdning av yxor – Möjlighet att ladda upp flera yxor samtidigt. **(Pausad – kräver vidare diskussion och behovsanalys innan implementation)**
61. [x] Export/import av data (CSV, Excel) direkt från admin.
62. [x] Automatiska backuper av databasen.
63. [x] Förbättrad navigering på systeminställningssidan.
64. [x] Vy för okopplade bilder – Rutnätsvy med funktioner för att ta bort och ladda ner bilder som flyttats från borttagna yxor.

## 9. Säkerhet och användare

65. [x] Inloggning/behörighet – Privata delar eller flera användare.
66. [ ] Loggning av ändringar (audit trail).
67. [x] Inför inloggning/adminvy så att endast inloggade kan redigera, och visa en publik vy där känsliga uppgifter (t.ex. kontaktnamn, personuppgifter och ev. priser) maskeras eller döljs.

## 10. Prestanda och kodkvalitet

68. [ ] Fler automatiska tester (unit/integration).
69. [ ] CI/CD – Automatiska tester vid push (GitHub Actions).
70. [ ] Kodgranskning – Linting och kodstil (t.ex. black, flake8).
71. [ ] Periodvis kodgranskning: Gå igenom och granska koden stegvis för att identifiera behov av övergripande refaktorering, buggfixar och tillsnyggning. Gör detta processvis så att varje steg kan testas innan nästa påbörjas.
72. [x] Dokumentation av förbättringar - Uppdatera markdown-filer med genomförda förbättringar och lärdomar
73. [ ] Implementera Django REST Framework och ViewSets
74. [x] Testa ny TODO-hantering
75. [x] Test av förbättrat verktyg

## 11. Testdata och demo

76. [x] Skapa fingerad testdata för demo och testning
77. [ ] Docker demo-läge med miljövariabel

## 12. Design och presentation

78. [x] Bättre visuell presentation av galleriet, t.ex. lightbox för bilder.
79. [x] Förbättrad UI med badges och ikoner – Tydligare visning av transaktionstyper med ikoner.
80. [x] Förbättrad tillverkarsida – ID som badge, kommentar som egen sektion, hela bredden för korten.
81. [x] Visa statistik (t.ex. antal yxor, mest populära tillverkare, dyraste köp).
82. [ ] QR-kod för att snabbt visa en yxa på mobilen. **(Pausad – kräver vidare diskussion och behovsanalys innan implementation)**

## 13. Framtida förbättringar

83. [x] Fixa JavaScript-fel och landsfält-problem
84. [x] Fixa duplicerad "Detaljer"-knapp på /galleri-sidan
85. [ ] Kommentarsystem (framtida funktion)
86. [ ] Förbättrad felhantering och validering i formulär.
87. [ ] Snabbare AJAX-sökningar med caching.
88. [ ] Tangentbordsnavigering i lightbox (piltangenter för att bläddra mellan bilder).
89. [ ] Touch-gester för mobil navigering i lightbox (swipe för att bläddra).
90. [ ] Zoom-funktionalitet i lightbox för att se bilder i full storlek.
91. [ ] Automatisk bildrotation baserat på EXIF-data.
92. [ ] Bulk-redigering av bilder (redigera flera bilder samtidigt).
93. [ ] Bildkommentarer med @-mentions för att länka till tillverkare eller yxor.