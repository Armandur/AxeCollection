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
12. [ ] Motsvarande bildhantering för tillverkare – Implementera samma avancerade bildhantering (drag & drop, ordning, .webp-stöd) för tillverkarbilder som redan finns för yxbilder.

## Användarupplevelse

13. [ ] Förbättrad responsivitet – Testa och förbättra för surfplattor och olika mobilstorlekar.
14. [ ] Touchvänliga knappar även på desktop – T.ex. piltangenter för bildbyte.
15. [x] Mörkt läge (dark mode) för hela tjänsten – Respekterar operativsystemets tema automatiskt och har en sol/måne-knapp för manuell växling.

## Sök och filtrering

16. [x] AJAX-sökning för kontakter – Realtidssökning med dropdown-resultat för befintliga kontakter.
17. [x] AJAX-sökning för plattformar – Realtidssökning med dropdown-resultat för befintliga plattformar.
18. [ ] Sökfunktion för yxor och tillverkare – Snabbt hitta yxor, tillverkare eller transaktioner.
19. [ ] Filtrering på t.ex. tillverkare, typ, årtal, mm.
19. [ ] Redigera transaktion, plattform och kontakt för en yxa via detaljvyn
    - [ ] 19.1 Visa "Lägg till transaktion"-knapp om ingen transaktion finns
    - [ ] 19.2 Visa "Redigera transaktioner"-knapp om en eller flera transaktioner finns
    - [ ] 19.3 Bygg formulär för att lägga till/redigera transaktion (pris, frakt, kontakt, plattform, kommentar, datum)
    - [ ] 19.4 Implementera AJAX-sökning för kontakt och plattform i formuläret
    - [ ] 19.5 Möjlighet att skapa ny kontakt/plattform direkt i formuläret
    - [ ] 19.6 (Ev.) Möjlighet att ta bort transaktion

## Yxhantering och inmatning

20. [x] UI för att skapa nya yxor i samlingen – Användarvänligt formulär för att lägga till yxor.
21. [x] UI för att redigera befintliga yxor – Möjlighet att uppdatera information efter mottagning.
22. [x] Status-fält och filter – Status "Köpt" vs "Mottagen/Ägd" med filter och snabbåtgärder (markera som mottagen) i yxlistan.
23. [x] Arbetsflöde för inköp: 
    - Skapa/redigera yxa (tillverkare, modell, kommentar) ✅
    - Ladda upp bilder från auktion/annons ✅
    - Skapa/redigera kontakt (försäljare på Tradera etc.) ✅
    - Skapa transaktion (inköp med pris, frakt, datum) ✅
24. [ ] Arbetsflöde för mottagning:
    - Lägg till fler bilder av mottagen yxa ✅
    - Mät och registrera mått
    - Uppdatera eventuell felaktig information
25. [x] Snabbval av tillverkare – Dropdown för att välja tillverkare.
26. [x] Kontakthantering – Skapa nya kontakter direkt från yxformuläret med smart matchning.
27. [x] Transaktionshantering – Koppla yxor till köp/försäljning med pris, frakt och datum.
28. [x] Plattformshantering – Skapa nya plattformar direkt från yxformuläret med smart matchning.
29. [x] Automatisk transaktionstypbestämning – Baserat på pris (negativ = köp, positiv = sälj).
30. [x] Separata formulär för skapande vs redigering – Olika fält visas beroende på om yxa skapas eller redigeras.

## Admin och datahantering

31. [x] Förbättrad admin-raderingsvy för yxor – Tydlig lista över vad som tas bort, bockruta för bildradering.
32. [ ] Batchuppladdning av bilder och yxor.
33. [ ] Export/import av data (CSV, Excel) direkt från admin.
34. [ ] Automatiska backuper av databasen.

## Säkerhet och användare

35. [ ] Inloggning/behörighet – Privata delar eller flera användare.
36. [ ] Loggning av ändringar (audit trail).

## Prestanda och kodkvalitet

37. [ ] Fler automatiska tester (unit/integration).
38. [ ] CI/CD – Automatiska tester vid push (GitHub Actions).
39. [ ] Kodgranskning – Linting och kodstil (t.ex. black, flake8).

## Design och presentation

40. [x] Bättre visuell presentation av galleriet, t.ex. lightbox för bilder.
41. [x] Förbättrad UI med badges och ikoner – Tydligare visning av transaktionstyper med ikoner.
42. [ ] Visa statistik (t.ex. antal yxor, mest populära tillverkare, dyraste köp).
43. [ ] QR-kod för att snabbt visa en yxa på mobilen.
44. [ ] Hantera många stämpelbilder på tillverkarsidan (t.ex. paginering, grid, lightbox eller liknande UX-lösning).

## Framtida förbättringar

45. [ ] Möjlighet att redigera transaktion, plattform och kontakt för en yxa via detaljvyn (t.ex. klicka på en transaktion och få upp ett redigeringsformulär).
46. [ ] Förbättrad felhantering och validering i formulär.
47. [ ] Snabbare AJAX-sökningar med caching.
48. [ ] Drag & drop för bildordning i redigeringsläge. 