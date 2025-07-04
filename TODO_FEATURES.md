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
13. [x] Drag & drop för bildordning i redigeringsläge.
14. [ ] Hantera många stämpelbilder på tillverkarsidan (t.ex. paginering, grid, lightbox eller liknande UX-lösning).

## Användarupplevelse

15. [ ] Förbättrad responsivitet – Testa och förbättra för surfplattor och olika mobilstorlekar.
16. [ ] Touchvänliga knappar även på desktop – T.ex. piltangenter för bildbyte.
17. [x] Mörkt läge (dark mode) för hela tjänsten – Respekterar operativsystemets tema automatiskt och har en sol/måne-knapp för manuell växling.

## Sök och filtrering

18. [x] AJAX-sökning för kontakter – Realtidssökning med dropdown-resultat för befintliga kontakter.
19. [x] AJAX-sökning för plattformar – Realtidssökning med dropdown-resultat för befintliga plattformar.
20. [ ] Sökfunktion för yxor och tillverkare – Snabbt hitta yxor, tillverkare eller transaktioner.
21. [ ] Filtrering på t.ex. tillverkare, typ, årtal, mm.

## Yxhantering och inmatning

22. [x] Redigera transaktion, plattform och kontakt för en yxa via detaljvyn
    - [x] 22.1 Visa "Lägg till transaktion"-knapp om ingen transaktion finns
    - [x] 22.2 Visa "Redigera transaktioner"-knapp om en eller flera transaktioner finns
    - [x] 22.3 Bygg formulär för att lägga till/redigera transaktion (pris, frakt, kontakt, plattform, kommentar, datum)
    - [x] 22.4 Implementera AJAX-sökning för kontakt och plattform i formuläret
    - [x] 22.5 Möjlighet att skapa ny kontakt/plattform direkt i formuläret
    - [x] 22.6 Möjlighet att ta bort transaktion
23. [x] UI för att skapa nya yxor i samlingen – Användarvänligt formulär för att lägga till yxor.
24. [x] UI för att redigera befintliga yxor – Möjlighet att uppdatera information efter mottagning.
25. [x] Status-fält och filter – Status "Köpt" vs "Mottagen/Ägd" med filter och snabbåtgärder (markera som mottagen) i yxlistan.
26. [x] Arbetsflöde för inköp: 
    - Skapa/redigera yxa (tillverkare, modell, kommentar) ✅
    - Ladda upp bilder från auktion/annons ✅
    - Skapa/redigera kontakt (försäljare på Tradera etc.) ✅
    - Skapa transaktion (inköp med pris, frakt, datum) ✅
27. [ ] Arbetsflöde för mottagning:
    - Lägg till fler bilder av mottagen yxa
    - Mät och registrera mått
    - Uppdatera eventuell felaktig information
28. [x] Snabbval av tillverkare – Dropdown för att välja tillverkare.
29. [x] Kontakthantering – Skapa nya kontakter direkt från yxformuläret med smart matchning.
30. [x] Transaktionshantering – Koppla yxor till köp/försäljning med pris, frakt och datum.
31. [x] Plattformshantering – Skapa nya plattformar direkt från yxformuläret med smart matchning.
32. [x] Automatisk transaktionstypbestämning – Baserat på pris (negativ = köp, positiv = sälj).
33. [x] Separata formulär för skapande vs redigering – Olika fält visas beroende på om yxa skapas eller redigeras.

## Admin och datahantering

34. [x] Förbättrad admin-raderingsvy för yxor – Tydlig lista över vad som tas bort, bockruta för bildradering.
35. [ ] Batchuppladdning av bilder och yxor.
36. [ ] Export/import av data (CSV, Excel) direkt från admin.
37. [ ] Automatiska backuper av databasen.

## Säkerhet och användare

38. [ ] Inloggning/behörighet – Privata delar eller flera användare.
39. [ ] Loggning av ändringar (audit trail).
40. [ ] Inför inloggning/adminvy så att endast inloggade kan redigera, och visa en publik vy där känsliga uppgifter (t.ex. kontaktnamn, personuppgifter och ev. priser) maskeras eller döljs.

## Prestanda och kodkvalitet

41. [ ] Fler automatiska tester (unit/integration).
42. [ ] CI/CD – Automatiska tester vid push (GitHub Actions).
43. [ ] Kodgranskning – Linting och kodstil (t.ex. black, flake8).
44. [ ] Periodvis kodgranskning: Gå igenom och granska koden stegvis för att identifiera behov av övergripande refaktorisering, buggfixar och tillsnyggning. Gör detta processvis så att varje steg kan testas innan nästa påbörjas.

## Design och presentation

45. [x] Bättre visuell presentation av galleriet, t.ex. lightbox för bilder.
46. [x] Förbättrad UI med badges och ikoner – Tydligare visning av transaktionstyper med ikoner.
47. [ ] Visa statistik (t.ex. antal yxor, mest populära tillverkare, dyraste köp).
48. [ ] QR-kod för att snabbt visa en yxa på mobilen.

## Framtida förbättringar

49. [ ] Förbättrad felhantering och validering i formulär.
50. [ ] Snabbare AJAX-sökningar med caching. 