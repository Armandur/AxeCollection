# Backlog Export

## [P2][todo] [axecollection] Backup-uppladdning via webbgränssnitt - lösa stora filer (>100MB, upp till 2GB)

Uppladdning av backupfiler via webbgränssnittet fungerar inte för stora filer. Kräver fix av nginx-konfig och förbättrat AJAX-flöde. Berör produktion (yxor.pettersson-vik.se).

- ID: `01KXX7K2JE2XAFSVX4MYDHV27T`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P3][todo] [axecollection] Behåll senaste X backuper oavsett ålder (keep-last-N)

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

## [P3][todo] [axecollection] Förbättrad felhantering och validering i formulär

- ID: `01KXX7K2MVSS0593YYJ3XE21C6`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P3][todo] [axecollection] Prestandaoptimering (caching, lazy loading, etc.)

- ID: `01KXX7K2MDRSX13KZ2957G8K9T`
- Type: improvement
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

## [P4][todo] [axecollection] Backup-uppladdning: 'Ladda upp'-knappen linjerar inte med filfältet

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

## [P4][todo] [axecollection] Automatisk bildrotation baserat på EXIF-data

- ID: `01KXX7K2N582QQ0TQT7YWMB1Q3`
- Type: feature
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Zoom-funktionalitet i lightbox för att se bilder i full storlek

- ID: `01KXX7K2N3NM33F2NVCS9TYVKD`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Touch-gester för mobil navigering i lightbox (swipe)

- ID: `01KXX7K2N1C0710WFTWPY6HN21`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Tangentbordsnavigering i lightbox (piltangenter mellan bilder)

- ID: `01KXX7K2MZFMR1VRZ7MATVXMHA`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Snabbare AJAX-sökningar med caching

- ID: `01KXX7K2MX507BWX56H389K8VB`
- Type: improvement
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Kommentarsystem för yxor och tillverkare

Framtida funktion.

- ID: `01KXX7K2MQAFSNYPXFCX62BM1X`
- Type: feature
- Actor: ai:claude-opus-4-8

---

## [P4][todo] [axecollection] Implementera Django REST Framework och ViewSets

- ID: `01KXX7K2MMB13XV325X6C4PFSM`
- Type: feature
- Actor: ai:claude-opus-4-8

---

## [P5][todo] [axecollection] QR-kod för att snabbt visa en yxa på mobilen

PAUSAD - kräver vidare diskussion och behovsanalys innan implementation.

- ID: `01KXX7K2MN245BFY6ZSTXCXB3X`
- Type: feature
- Actor: ai:claude-opus-4-8

---

## [P5][todo] [axecollection] Batchuppladdning av yxor - ladda upp flera yxor samtidigt

PAUSAD - kräver vidare diskussion och behovsanalys innan implementation.

- ID: `01KXX7K2JZYVGC9VKRYKFKTP6J`
- Type: feature
- Actor: ai:claude-opus-4-8

---

