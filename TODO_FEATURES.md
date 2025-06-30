# Projektidéer & förbättringsförslag

En checklista för vidareutveckling av AxeCollection. Bocka av med [x] när klart!

## Bildhantering

1. [ ] Bildkomprimering/optimering vid uppladdning – Gör bilder snabbare att ladda på mobil.
2. [x] Stöd för flera bildformat (t.ex. webp) – För bättre prestanda och kompatibilitet.
3. [x] Lazy loading av bilder i galleriet – Ladda bara bilder som syns.

## Användarupplevelse

4. [ ] Förbättrad responsivitet – Testa och förbättra för surfplattor och olika mobilstorlekar.
5. [ ] Touchvänliga knappar även på desktop – T.ex. piltangenter för bildbyte.
6. [x] Mörkt läge (dark mode) för hela tjänsten – Respekterar operativsystemets tema automatiskt och har en sol/måne-knapp för manuell växling.

## Sök och filtrering

7. [ ] Sökfunktion – Snabbt hitta yxor, tillverkare eller transaktioner.
8. [ ] Filtrering på t.ex. tillverkare, typ, årtal, mm.

## Yxhantering och inmatning

21. [ ] UI för att skapa nya yxor i samlingen – Användarvänligt formulär för att lägga till yxor.
22. [ ] UI för att redigera befintliga yxor – Möjlighet att uppdatera information efter mottagning.
23. [ ] Arbetsflöde för inköp: 
    - Skapa/redigera yxa (tillverkare, modell, kommentar)
    - Ladda upp bilder från auktion/annons
    - Skapa/redigera kontakt (försäljare på Tradera etc.)
    - Skapa transaktion (inköp med pris, frakt, datum)
24. [ ] Arbetsflöde för mottagning:
    - Lägg till fler bilder av mottagen yxa
    - Mät och registrera mått
    - Uppdatera eventuell felaktig information
25. [ ] Snabbval av tillverkare – Dropdown eller sökfunktion för att välja tillverkare.
26. [ ] Kontakthantering – Skapa nya kontakter direkt från yxformuläret.
27. [ ] Transaktionshantering – Koppla yxor till köp/försäljning med pris, frakt och datum.

## Admin och datahantering

9. [ ] Batchuppladdning av bilder och yxor.
10. [ ] Export/import av data (CSV, Excel) direkt från admin.
11. [ ] Automatiska backuper av databasen.

## Säkerhet och användare

12. [ ] Inloggning/behörighet – Privata delar eller flera användare.
13. [ ] Loggning av ändringar (audit trail).

## Prestanda och kodkvalitet

14. [ ] Fler automatiska tester (unit/integration).
15. [ ] CI/CD – Automatiska tester vid push (GitHub Actions).
16. [ ] Kodgranskning – Linting och kodstil (t.ex. black, flake8).

## Design och presentation

17. [x] Bättre visuell presentation av galleriet, t.ex. lightbox för bilder.
18. [ ] Visa statistik (t.ex. antal yxor, mest populära tillverkare, dyraste köp).
19. [ ] QR-kod för att snabbt visa en yxa på mobilen.
20. [ ] Hantera många stämpelbilder på tillverkarsidan (t.ex. paginering, grid, lightbox eller liknande UX-lösning). 