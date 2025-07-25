# 🧪 Todo Manager Testing README

Detta dokument beskriver hur du kör testerna för den hierarkiska funktionaliteten i TODO Manager.

## 📋 Vad testas?

De hierarkiska testerna validerar följande ny funktionalitet:

### ✅ **Grundläggande hierarkisk hantering:**
- ✅ Ladda och parsa hierarkiska strukturer (5 nivåer djupt)
- ✅ Hitta underuppgifter på alla nivåer
- ✅ Korrekt nivå-spårning (level 2-5)

### 🔄 **Flytta underuppgifter:**
- ✅ `move_sub_item()` - Flytta underuppgift till ny förälder
- ✅ Flytta mellan huvuduppgifter (42.1 → 43.2)
- ✅ Flytta mellan underuppgifter (42.1.2 → 42.2.1)
- ✅ Rekursiv uppdatering av hela hierarkier

### 🔁 **Byta plats på underuppgifter:**
- ✅ `swap_sub_items()` - Byt plats på två underuppgifter
- ✅ Swap inom samma förälder
- ✅ Swap mellan olika föräldrar

### ⬆️⬇️ **Nivåändringar:**
- ✅ `promote_sub_item()` - Flytta upp en nivå
- ✅ `demote_sub_item()` - Flytta ner en nivå
- ✅ Automatisk nivåkontroll och gränser

### 🛡️ **Felhantering:**
- ✅ Respektera 5-nivågräns
- ✅ Hantera icke-existerande uppgifter
- ✅ Validera ogiltiga operationer

## 🚀 Köra testerna

### **Alternativ 1: Med pytest (rekommenderat)**

Om du har pytest installerat:

```bash
# Installera pytest om det behövs
pip install pytest

# Kör alla hierarkiska tester
pytest test_todo_manager_hierarki.py -v

# Kör specifikt test
pytest test_todo_manager_hierarki.py::TestTodoManagerHierarki::test_move_sub_item_between_main_tasks -v
```

### **Alternativ 2: Standalone test runner**

Utan att installera pytest:

```bash
# Kör den inbyggda test runnern
python run_tests.py
```

### **Alternativ 3: Manuell unittest**

```bash
python -m unittest test_todo_manager_hierarki.TestTodoManagerHierarki -v
```

## 📊 Testresultat

Framgångsrika tester visar:

```
🚀 Startar hierarkiska tester för TODO Manager...
============================================================

🧪 Testar move_sub_item mellan huvuduppgifter...
✅ Move mellan huvuduppgifter fungerar!

🧪 Testar swap_sub_items med samma förälder...
✅ Swap med samma förälder fungerar!

🧪 Testar promote_sub_item...
✅ Promote fungerar!

🧪 Testar demote_sub_item...
✅ Demote fungerar!

🧪 Testar nivågränser...
✅ Nivågränser respekteras!

🧪 Testar felhantering...
✅ Felhantering fungerar!

🧪 Testar komplex omorganisering...
✅ Komplex omorganisering fungerar!

============================================================
🎉 Alla tester lyckades! Hierarkisk funktionalitet verifierad.
✅ 7 tester körda utan fel
```

## 🔍 Testdata

Testerna använder en temporär TODO-fil med följande struktur:

```markdown
## 1. Test Sektion Alpha

42. [ ] Huvuduppgift Alpha
    - [ ] 42.1 Underuppgift Alpha 1
        - [ ] 42.1.1 Djup nivå 3
            - [ ] 42.1.1.1 Djup nivå 4
                - [ ] 42.1.1.1.1 Djup nivå 5 (max)
        - [ ] 42.1.2 Ytterligare nivå 3
    - [ ] 42.2 Underuppgift Alpha 2
        - [ ] 42.2.1 Nivå 3 under Alpha 2

43. [ ] Huvuduppgift Beta
    - [ ] 43.1 Underuppgift Beta 1
    - [ ] 43.2 Underuppgift Beta 2

## 2. Test Sektion Beta

44. [ ] Huvuduppgift Gamma
    - [ ] 44.1 Underuppgift Gamma 1

45. [ ] Huvuduppgift Delta (tom)
```

## 🛠️ Felsökning

### **ImportError: No module named 'todo_manager'**
Se till att du kör testerna från `todo-manager/` mappen där `todo_manager.py` finns.

### **Permission errors på Windows**
Kör kommandoprompten som administratör eller använd PowerShell.

### **Testfel**
Om tester misslyckas, kontrollera:
1. Att `todo_manager.py` är uppdaterad med hierarkisk funktionalitet
2. Att alla nya metoder implementerats korrekt
3. Att import-path stämmer

## 📚 Testdriven utveckling

Dessa tester följer TDD-principen:

1. **🔴 Red:** Skriv test som misslyckas
2. **🟢 Green:** Implementera minsta kod som klarar testet
3. **🔄 Refactor:** Förbättra koden utan att bryta tester

Testerna validerar både:
- **Happy path:** Normal användning fungerar
- **Edge cases:** Gränser och felhantering
- **Integration:** Komplexa sekvenser av operationer

## 🎯 Nästa steg

För att lägga till fler tester:

1. Lägg till nya testmetoder i `TestTodoManagerHierarki`
2. Använd `setUp()` och `tearDown()` för datainställning
3. Namnge tester tydligt: `test_what_when_expected()`
4. Inkludera både positiva och negativa testfall

Happy testing! 🚀 