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

12. [ ] Förbättrad responsivitet – Testa och förbättra för surfplattor och olika mobilstorlekar.
13. [ ] Touchvänliga knappar även på desktop – T.ex. piltangenter för bildbyte.
14. [x] Mörkt läge (dark mode) för hela tjänsten – Respekterar operativsystemets tema automatiskt och har en sol/måne-knapp för manuell växling.

## Sök och filtrering

15. [ ] Sökfunktion – Snabbt hitta yxor, tillverkare eller transaktioner.
16. [ ] Filtrering på t.ex. tillverkare, typ, årtal, mm.

## Yxhantering och inmatning

17. [x] UI för att skapa nya yxor i samlingen – Användarvänligt formulär för att lägga till yxor.
18. [x] UI för att redigera befintliga yxor – Möjlighet att uppdatera information efter mottagning.
19. [x] Status-fält och filter – Status "Köpt" vs "Mottagen/Ägd" med filter och snabbåtgärder (markera som mottagen) i yxlistan.
20. [ ] Arbetsflöde för inköp: 
    - Skapa/redigera yxa (tillverkare, modell, kommentar) ✅
    - Ladda upp bilder från auktion/annons ✅
    - Skapa/redigera kontakt (försäljare på Tradera etc.)
    - Skapa transaktion (inköp med pris, frakt, datum)
21. [ ] Arbetsflöde för mottagning:
    - Lägg till fler bilder av mottagen yxa ✅
    - Mät och registrera mått
    - Uppdatera eventuell felaktig information
22. [x] Snabbval av tillverkare – Dropdown för att välja tillverkare.
23. [ ] Kontakthantering – Skapa nya kontakter direkt från yxformuläret.
24. [ ] Transaktionshantering – Koppla yxor till köp/försäljning med pris, frakt och datum.

## Admin och datahantering

24. [ ] Batchuppladdning av bilder och yxor.
25. [ ] Export/import av data (CSV, Excel) direkt från admin.
26. [ ] Automatiska backuper av databasen.

## Säkerhet och användare

27. [ ] Inloggning/behörighet – Privata delar eller flera användare.
28. [ ] Loggning av ändringar (audit trail).

## Prestanda och kodkvalitet

29. [ ] Fler automatiska tester (unit/integration).
30. [ ] CI/CD – Automatiska tester vid push (GitHub Actions).
31. [ ] Kodgranskning – Linting och kodstil (t.ex. black, flake8).

## Design och presentation

32. [x] Bättre visuell presentation av galleriet, t.ex. lightbox för bilder.
33. [ ] Visa statistik (t.ex. antal yxor, mest populära tillverkare, dyraste köp).
34. [ ] QR-kod för att snabbt visa en yxa på mobilen.
35. [ ] Hantera många stämpelbilder på tillverkarsidan (t.ex. paginering, grid, lightbox eller liknande UX-lösning). 