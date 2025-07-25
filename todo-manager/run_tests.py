#!/usr/bin/env python3
"""
Enkel test runner för TODO Manager hierarkiska tester
Kör testerna utan att kräva pytest installation
"""

import sys
import unittest
import tempfile
import os
from todo_manager import TodoManager


class TestTodoManagerHierarkiStandalone(unittest.TestCase):
    """Standalone version av hierarkiska tester"""
    
    def setUp(self):
        """Sätter upp testdata före varje test"""
        content = """# TODO Features för AxeCollection

Detta är test TODO-filen för hierarkiska tester.

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
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            self.temp_path = f.name
            
        self.manager = TodoManager(self.temp_path)
        self.manager.load()
    
    def tearDown(self):
        """Städar upp efter varje test"""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)
    
    def test_move_sub_item_between_main_tasks(self):
        """Testar flyttning av underuppgift mellan huvuduppgifter"""
        print("🧪 Testar move_sub_item mellan huvuduppgifter...")
        
        # Flytta 42.2 till huvuduppgift 43
        result = self.manager.move_sub_item("42.2", "43")
        self.assertTrue(result)
        
        # Verifiera att den nu finns under 43 som 43.3
        moved_sub = self.manager.find_sub_item("43.3")
        self.assertIsNotNone(moved_sub)
        self.assertEqual(moved_sub.text, "Underuppgift Alpha 2")
        
        # Verifiera att barn följde med
        child = self.manager.find_sub_item("43.3.1")
        self.assertIsNotNone(child)
        self.assertEqual(child.text, "Nivå 3 under Alpha 2")
        
        print("✅ Move mellan huvuduppgifter fungerar!")
    
    def test_swap_sub_items_same_parent(self):
        """Testar att byta plats på underuppgifter med samma förälder"""
        print("🧪 Testar swap_sub_items med samma förälder...")
        
        # Byt plats på 42.1 och 42.2
        result = self.manager.swap_sub_items("42.1", "42.2")
        self.assertTrue(result)
        
        # Verifiera att texterna stämmer
        item_42 = self.manager.find_item(42)
        self.assertEqual(item_42.sub_items[0].text, "Underuppgift Alpha 2")
        self.assertEqual(item_42.sub_items[1].text, "Underuppgift Alpha 1")
        
        print("✅ Swap med samma förälder fungerar!")
    
    def test_promote_sub_item(self):
        """Testar att flytta underuppgift upp en nivå"""
        print("🧪 Testar promote_sub_item...")
        
        # Flytta 42.1.2 upp en nivå (från 42.1 till 42)
        result = self.manager.promote_sub_item("42.1.2")
        self.assertTrue(result)
        
        # Verifiera att den nu finns som 42.3
        promoted = self.manager.find_sub_item("42.3")
        self.assertIsNotNone(promoted)
        self.assertEqual(promoted.text, "Ytterligare nivå 3")
        self.assertEqual(promoted.level, 2)
        
        print("✅ Promote fungerar!")
    
    def test_demote_sub_item(self):
        """Testar att flytta underuppgift ner en nivå"""
        print("🧪 Testar demote_sub_item...")
        
        # Flytta 42.2 ner under 42.1
        result = self.manager.demote_sub_item("42.2", "42.1")
        self.assertTrue(result)
        
        # Verifiera att den nu finns som 42.1.3
        demoted = self.manager.find_sub_item("42.1.3")
        self.assertIsNotNone(demoted)
        self.assertEqual(demoted.text, "Underuppgift Alpha 2")
        self.assertEqual(demoted.level, 3)
        
        print("✅ Demote fungerar!")
    
    def test_level_limits(self):
        """Testar att nivågränser respekteras"""
        print("🧪 Testar nivågränser...")
        
        # Försök flytta något under redan max nivå
        result = self.manager.move_sub_item("42.2", "42.1.1.1.1")
        self.assertFalse(result)  # Borde misslyckas
        
        # Försök promote från nivå 2
        result = self.manager.promote_sub_item("42.1")
        self.assertFalse(result)  # Borde misslyckas
        
        print("✅ Nivågränser respekteras!")
    
    def test_error_handling(self):
        """Testar felhantering för ogiltiga operationer"""
        print("🧪 Testar felhantering...")
        
        # Icke-existerande underuppgifter
        result = self.manager.move_sub_item("99.99", "42")
        self.assertFalse(result)
        
        result = self.manager.swap_sub_items("99.99", "42.1")
        self.assertFalse(result)
        
        # Icke-existerande föräldrar
        result = self.manager.move_sub_item("42.1", "99")
        self.assertFalse(result)
        
        print("✅ Felhantering fungerar!")
    
    def test_complex_reorganization(self):
        """Testar komplex omorganisering med flera operationer"""
        print("🧪 Testar komplex omorganisering...")
        
        # Utför flera operationer i sekvens
        self.manager.move_sub_item("42.2", "43")  # 42.2 → 43.3
        self.manager.promote_sub_item("42.1.1")   # 42.1.1 → 42.2
        self.manager.swap_sub_items("43.1", "43.2")  # Byt plats
        
        # Verifiera att alla operationer fungerade
        moved_sub = self.manager.find_sub_item("43.3")
        self.assertIsNotNone(moved_sub)
        
        promoted_sub = self.manager.find_sub_item("42.2")
        self.assertIsNotNone(promoted_sub)
        self.assertEqual(promoted_sub.text, "Djup nivå 3")
        
        # Testa save/load persistence
        self.manager.save()
        self.manager.load()
        
        # Verifiera att allt fortfarande stämmer efter save/load
        # Efter save/load renumreras: 43.3 blir 2.3 (tredje underuppgift till uppgift 2)
        moved_sub_reloaded = self.manager.find_sub_item("2.3")
        self.assertIsNotNone(moved_sub_reloaded)
        self.assertEqual(moved_sub_reloaded.text, "Underuppgift Alpha 2")
        
        print("✅ Komplex omorganisering fungerar!")


def run_tests():
    """Kör alla tester och visar resultat"""
    print("🚀 Startar hierarkiska tester för TODO Manager...")
    print("=" * 60)
    
    # Kör unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTodoManagerHierarkiStandalone)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 Alla tester lyckades! Hierarkisk funktionalitet verifierad.")
        print(f"✅ {result.testsRun} tester körda utan fel")
    else:
        print("❌ Några tester misslyckades:")
        print(f"💥 {len(result.failures)} fel, {len(result.errors)} exceptions")
        for test, error in result.failures + result.errors:
            print(f"   - {test}: {error}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("📋 TODO Manager - Hierarkiska Tester")
    print("Testar all ny funktionalitet för underuppgiftshantering\n")
    
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except ImportError as e:
        print(f"❌ Kunde inte importera todo_manager: {e}")
        print("💡 Se till att todo_manager.py finns i samma mapp")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Oväntat fel: {e}")
        sys.exit(1) 