# TODO Manager för AxeCollection

Automatisk hantering av TODO_FEATURES.md med korrekt numrering och struktur.

## 📁 Installation och struktur

TODO Manager ligger nu i sin egen mapp: `todo-manager/`

Från projektets rotmapp, navigera till todo-manager mappen:
```bash
cd todo-manager
```

## 🚀 Snabbstart

```bash
# Visa statistik
python todo_manager.py stats

# Lista alla sektioner
python todo_manager.py sections

# Lista uppgifter i en sektion  
python todo_manager.py list "Sektionsnamn"

# Lista bara ofinished uppgifter i en sektion
python todo_manager.py list "Sektionsnamn" --incomplete

# Lista alla oklarade uppgifter från alla sektioner
python todo_manager.py all-incomplete

# Lista alla uppgifter från alla sektioner (klara och oklara)
python todo_manager.py all

# Lägg till ny uppgift
python todo_manager.py add "Min nya uppgift" "Sektionsnamn"

# Lägg till flera uppgifter samtidigt
python todo_manager.py add-multiple "Uppgift 1" "Uppgift 2" "Uppgift 3" "Sektionsnamn"

# Markera uppgift som klar
python todo_manager.py complete 42

# Markera flera uppgifter som klara
python todo_manager.py complete-multiple 42 43 44

# Flytta uppgift till annan sektion
python todo_manager.py move 42 "Ny sektion"
```

**OBS:** Alla kommandon körs från `todo-manager/` mappen och hanterar `../TODO_FEATURES.md` automatiskt.

## 📋 Kommandon

### `add` - Lägg till ny uppgift
```bash
python todo_manager.py add "Uppgiftsbeskrivning" "Sektionsnamn"

# Lägg till som redan klar
python todo_manager.py add "Uppgift" "Sektion" --completed
```

### `complete` / `uncomplete` - Ändra status
```bash
# Markera som klar
python todo_manager.py complete 42

# Markera som ej klar
python todo_manager.py uncomplete 42
```

### `list` - Lista uppgifter i sektion
```bash
# Lista alla uppgifter i en sektion (med underuppgifter)
python todo_manager.py list "Bildhantering"

# Lista bara ofinished uppgifter (men alla underuppgifter visas)
python todo_manager.py list "Prestanda och kodkvalitet" --incomplete
```

### `all-incomplete` - Lista alla oklarade uppgifter
```bash
# Visa alla oklarade uppgifter från alla sektioner på en gång
python todo_manager.py all-incomplete
```
Visar:
```
📋 Alla oklarade uppgifter:

📁 Deployment och Docker:
  38. ⏳ Fixa omorganisering av yxbilder i produktion

📁 Yxhantering och arbetsflöden:
  50. ⏳ Lägg till yxa via auktions-URL

📁 Prestanda och kodkvalitet:
  68. ⏳ Fler automatiska tester (unit/integration)
  69. ⏳ CI/CD – Automatiska tester vid push
  ...

📊 Totalt: 21 oklarade uppgifter
```

### `all` - Lista alla uppgifter
```bash
# Visa alla uppgifter från alla sektioner (både klara och oklara)
python todo_manager.py all
```
Visar:
```
📋 Alla uppgifter:

📁 Bildhantering:
  1. ✅ Bildkomprimering/optimering vid uppladdning
  2. ✅ Stöd för flera bildformat (t.ex. webp)
  3. ⏳ Förbättrad lightbox-funktionalitet
  ...
  📊 16 uppgifter i denna sektion

📁 Användarupplevelse och interface:
  17. ✅ Förbättrad responsivitet
  18. ✅ Touchvänliga knappar även på desktop
  ...
  📊 8 uppgifter i denna sektion

📊 Totalt: 93 uppgifter
```

### `complete-multiple` - Slutför flera uppgifter
```bash
# Markera flera uppgifter som klara på en gång
python todo_manager.py complete-multiple 42 43 44

# Funktionen visar resultat och felaktiga nummer
python todo_manager.py complete-multiple 1 999 3
# ✅ Markerade uppgift 1 som klar
# ❌ Uppgift 999 finns inte!
# ✅ Markerade uppgift 3 som klar
# 📊 Resultat: 2 uppgifter markerade som klara
# ❌ Misslyckades med: 999
```

### `move` - Flytta uppgift
```bash
python todo_manager.py move 42 "Målsektion"
```

### `new-section` - Skapa ny sektion
```bash
python todo_manager.py new-section "Min nya sektion"
```

### `merge` - Slå ihop sektioner
```bash
python todo_manager.py merge "Källsektion" "Målsektion"
```

### `sections` - Lista sektioner
```bash
python todo_manager.py sections
```
Visar:
```
📋 Sektioner:
  1. Bildhantering (16 uppgifter)
  2. Användarupplevelse och interface (8 uppgifter)
  ...
```

### `reorder` - Uppdatera numrering
```bash
python todo_manager.py reorder
```
Räknar om alla nummer automatiskt efter ändringar.

### `stats` - Visa statistik
```bash
python todo_manager.py stats
```
Visar:
```
📊 TODO-statistik:
  📝 Totalt: 91 uppgifter
  ✅ Klara: 71 uppgifter
  ⏳ Kvar: 20 uppgifter
  📁 Sektioner: 13
  📈 Framsteg: 78.0%
```

## ✨ Fördelar

### Automatisk numrering
- **Global numrering**: Alla uppgifter får automatiskt korrekta nummer (1, 2, 3...)
- **Sektionsnumrering**: Sektioner numreras automatiskt (1. Bildhantering, 2. UX...)
- **Deluppgifter**: Stöd för X.Y-numrering (42.1, 42.2, etc.)

### Intelligent hantering
- **Case-insensitive**: "bildhantering" = "Bildhantering"
- **Säker parsing**: Hanterar komplexa TODO-strukturer
- **Backup-säkerhet**: Sparar alltid korrekt format

### Snabb användning
```bash
# Lägg till 3 uppgifter snabbt
python todo_manager.py add "Fixa bug #123" "Prestanda och kodkvalitet"
python todo_manager.py add "Uppdatera README" "Dokumentation"  
python todo_manager.py add "Testa på mobil" "Användarupplevelse och interface"

# Markera första som klar
python todo_manager.py complete 92

# Flytta sista till annan sektion
python todo_manager.py move 94 "Framtida förbättringar"
```

## 🔧 Tekniska detaljer

- **Parser**: Regex-baserad parsing av markdown-struktur
- **Datastruktur**: Dataclasses för typ-säkerhet
- **Encoding**: UTF-8 för svenska tecken
- **Format**: Behåller exakt TODO_FEATURES.md format

## 💡 Användningsexempel

### Daglig användning
```bash
# Morgon - kolla status
python todo_manager.py stats

# Lägg till nya uppgifter som dyker upp
python todo_manager.py add "Fixa CSS-bug i dark mode" "Användarupplevelse och interface"

# Markera klara uppgifter
python todo_manager.py complete 45

# Kväll - se framsteg
python todo_manager.py stats
```

### Stor omstrukturering
```bash
# Skapa ny sektion
python todo_manager.py new-section "API och backend"

# Flytta relevanta uppgifter
python todo_manager.py move 73 "API och backend"
python todo_manager.py move 35 "API och backend"

# Slå ihop gamla sektioner
python todo_manager.py merge "Gamla sektionen" "Ny sektion"

# Uppdatera numrering
python todo_manager.py reorder
```

Detta sparar enormt mycket tid jämfört med manuell redigering! 🎯 