# Todo Manager Changelog

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