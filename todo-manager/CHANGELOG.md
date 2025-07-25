# Todo Manager Changelog

## v2.1.0 - 2025-01-22

### 🆕 Ny funktionalitet
- ✅ **Show-kommando**: Nytt `show`-kommando för att visa detaljerad information om uppgifter
  - `python todo_manager.py show 42` - Visa huvuduppgift med alla underuppgifter
  - `python todo_manager.py show 42.1` - Visa underuppgift med nivåinformation
  - Visar sektion, status, underuppgifter och hierarkisk struktur
  - Stöd för upp till 5 nivåer av underuppgifter
  - Felhantering för icke-existerande uppgifter och ogiltiga nummer

### 🧪 Tester
- ✅ **Show-funktion tester**: Omfattande tester för show-funktionaliteten
  - Test för huvuduppgifter, underuppgifter och djupa hierarkier
  - Test för felhantering och edge cases
  - Integrerade i `run_tests.py` för enhetlig testning med hierarkiska tester
  - Alla 14 tester (7 hierarkiska + 7 show) passerar framgångsrikt

### 📚 Dokumentation
- ✅ **README uppdaterad**: Dokumentation för show-kommandot tillagd
- ✅ **Exempel och användning**: Tydliga exempel på utdata från show-kommandot
- ✅ **Snabbstart**: Show-kommando tillagt i snabbstart-sektionen

## v2.0.0 - 2025-01-22

### 📁 Strukturförändringar
- ✅ **Flyttad till egen mapp**: Todo Manager ligger nu i `todo-manager/` mapp
- ✅ **Organiserad dokumentation**: 
  - `README.md` - Huvuddokumentation
  - `TODO_MANAGER_TESTING_README.md` - Testdokumentation
  - `CHANGELOG.md` - Versionshistorik
- ✅ **Uppdaterade sökvägar**: Dokumentation uppdaterad för den nya mappstrukturen
- ✅ **Städat projekt**: Borttagen duplicerad fil från `tools/` mappen

### 🚀 Användning
Från projektets rotmapp:
```bash
cd todo-manager
python todo_manager.py stats
```

### 📋 Filer i todo-manager/
- `todo_manager.py` - Huvudverktyget (1059 rader)
- `test_todo_manager_hierarki.py` - Hierarkiska tester (337 rader)  
- `run_tests.py` - Test runner (222 rader)
- `README.md` - Dokumentation (202 rader)
- `TODO_MANAGER_TESTING_README.md` - Testdokumentation (165 rader)
- `CHANGELOG.md` - Denna fil

### 🛠️ Teknisk information
- Verktyget hanterar fortfarande `../TODO_FEATURES.md` automatiskt
- Alla befintliga kommandon fungerar som tidigare
- Inga funktionella förändringar i verktyget självt 