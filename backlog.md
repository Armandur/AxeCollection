# Backlog Export

## [P2][todo] [axecollection] Sänk FILE_UPLOAD_MAX_MEMORY_SIZE så stora uppladdningar streamas till disk

FILE_UPLOAD_MAX_MEMORY_SIZE=2GB gör att hela uppladdade filen hålls i RAM innan den spills till disk - kan spränga minnet i containern vid stora backup-uppladdningar. Sänk till Django-default (~2.5MB) så filer streamas till FILE_UPLOAD_TEMP_DIR. FÖRUTSÄTTNING: i prod är TEMP_DIR /app/tmp - verifiera att den finns och är skrivbar för nobody:users (deploy-setup skapar data/media/logs/staticfiles/backups men INTE tmp), annars blir det FileNotFoundError vid varje stor uppladdning. Gäller settings_production.py + settings_production_http.py. Deploy-gated.

- ID: `01KXXJCGQKX83PTCEWTH3Y2JJD`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P2][done] [axecollection] Backup-uppladdning via webbgränssnitt - lösa stora filer (>100MB, upp till 2GB)

Uppladdning av backupfiler via webbgränssnittet fungerar inte för stora filer. Kräver fix av nginx-konfig och förbättrat AJAX-flöde. Berör produktion (yxor.pettersson-vik.se).

- ID: `01KXX7K2JE2XAFSVX4MYDHV27T`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P3][todo] [axecollection] Verifiera att eBay- och Tradera-parsern fungerar (live + edge-cases)

Todo från Rasmus 2026-07-19: kontrollera att båda auktionsparsrarna fungerar.

Redan hittat under CI-felsökning:
1. FIXAT (commit cada52d): test_extract_auction_end_date var väggklocksberoende och sprack i juli - frös nu-datum. Blockerade CI.
2. VERKLIG SVAGHET (ej åtgärdad): ebay_parser._extract_auction_end_date tappar explicit årtal. HTML 'Ended Jan 27, 2025' fångas av regex (\w+ \d+) som 'Jan 27' FÖRE den år-bärande grenen, så 2025 ignoreras och aktuellt år sätts i stället. Bör fånga 'Mon DD, YYYY' först.
3. Testsviterna för båda parsrarna passerar annars (tradera-testerna gick igenom i CI).

Kvar att göra: live-verifiera mot riktiga eBay/Tradera-annonser (CI mockar nätverk; eBay ger 403 utan riktig session - ev. via pia-proxy). Kolla att titel/pris/datum/bilder extraheras korrekt på nuvarande sidlayouter.

- ID: `01KXXQ13YQHCQFYDV7665P5YTR`
- Type: task
- Actor: ai:claude-opus-4-8

---

## [P3][done] [axecollection] Behåll senaste X backuper oavsett ålder (keep-last-N)

cleanup_old_backups() raderar idag allt äldre än keep_days (30). Risk: har ingen ny backup skapats på 30 dagar rensas allt bort. Lägg till en keep-last-N-retention (t.ex. --keep-last N) som alltid sparar de N senaste oavsett ålder, som komplement till ålderregeln.

- ID: `01KXX9PMQKD5NESX6CAFETGDZC`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P3][todo] [axecollection] Bulk-redigering av bilder (redigera flera bilder samtidigt)

- ID: `01KXX7K2N8NNTVYC1F343Y2ZS8`
- Type: feature
- Actor: ai:claude-opus-4-8

---

## [P3][done] [axecollection] Automatisk bildrotation baserat på EXIF-data

- ID: `01KXX7K2N582QQ0TQT7YWMB1Q3`
- Type: feature
- Actor: ai:claude-opus-4-8

---

## [P3][todo] [axecollection] Konfigurera automatisk deployment till testmiljö

Utöka CI/CD (GitHub Actions) med automatisk deployment till en testmiljö.

- ID: `01KXX7K2K7G9T2N6HGRBEXTA51`
- Type: chore
- Actor: ai:claude-opus-4-8

---

## [P3][todo] [axecollection] Loggning av ändringar (audit trail)

- ID: `01KXX7K2K2HTVBJWE5B4891HYP`
- Type: feature
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Regenerera webp för befintliga bilder (applicera EXIF-rotation retroaktivt)

TASK-136 roterar bilder enligt EXIF vid webp-generering, men bara för nya/omsparade bilder. Befintliga (redan genererade) webp:ar i prod/demo är oförändrade - telefonbilder som var felvända förblir felvända tills de sparas om. Lägg ett management-kommando som itererar AxeImage + ManufacturerImage och regenererar webp (Image.open -> exif_transpose -> spara webp). Kör sen gång i prod efter deploy av 5d2fabd.

- ID: `01KXXTPM02D3WKYJ29590V9HCZ`
- Type: chore
- Actor: ai:claude-opus-4-8

---

## [P4][done] [axecollection] Backup-uppladdning: 'Ladda upp'-knappen linjerar inte med filfältet

På inställningssidan (backup-upload) ligger 'Ladda upp backup'-knappen snett mot filinput-fältet. Orsak: knappkolumnen har 'd-flex align-items-end' och bottenlinjerar mot en högre grannkolumn (filinput + hjälptext + dold progress-bar), så knappen hamnar i fel höjd. Fix: linjera knappen mot själva input-raden, inte kolumnbotten.

- ID: `01KXX9Y3GN2GR5GFSFR5BHMEWX`
- Type: bug
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Bildkommentarer med @-mentions (länka till tillverkare eller yxor)

- ID: `01KXX7K2N94Y53WJK9HSX36Z6D`
- Type: feature
- Actor: ai:claude-opus-4-8

---

## [P4][done] [axecollection] Zoom-funktionalitet i lightbox för att se bilder i full storlek

- ID: `01KXX7K2N3NM33F2NVCS9TYVKD`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P4][done] [axecollection] Touch-gester för mobil navigering i lightbox (swipe)

- ID: `01KXX7K2N1C0710WFTWPY6HN21`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P4][done] [axecollection] Tangentbordsnavigering i lightbox (piltangenter mellan bilder)

- ID: `01KXX7K2MZFMR1VRZ7MATVXMHA`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Snabbare AJAX-sökningar med caching

- ID: `01KXX7K2MX507BWX56H389K8VB`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Förbättrad felhantering och validering i formulär

- ID: `01KXX7K2MVSS0593YYJ3XE21C6`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Kommentarsystem för yxor och tillverkare

Framtida funktion.

- ID: `01KXX7K2MQAFSNYPXFCX62BM1X`
- Type: feature
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Prestandaoptimering (caching, lazy loading, etc.)

- ID: `01KXX7K2MDRSX13KZ2957G8K9T`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P5][todo] [axecollection] QR-kod för att snabbt visa en yxa på mobilen

PAUSAD - kräver vidare diskussion och behovsanalys innan implementation.

- ID: `01KXX7K2MN245BFY6ZSTXCXB3X`
- Type: feature
- Actor: ai:claude-opus-4-8

---

## [P5][todo] [axecollection] Implementera Django REST Framework och ViewSets

- ID: `01KXX7K2MMB13XV325X6C4PFSM`
- Type: feature
- Actor: ai:claude-opus-4-8

---

## [P5][todo] [axecollection] Batchuppladdning av yxor - ladda upp flera yxor samtidigt

PAUSAD - kräver vidare diskussion och behovsanalys innan implementation.

- ID: `01KXX7K2JZYVGC9VKRYKFKTP6J`
- Type: feature
- Actor: ai:claude-opus-4-8

---

