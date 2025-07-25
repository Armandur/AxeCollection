#!/usr/bin/env python3
"""
Tester för hierarkisk funktionalitet i TODO Manager
Testar flyttning, swapping och nivåändringar av underuppgifter
"""

import pytest
import tempfile
import os
from todo_manager import TodoManager, TodoItem, TodoSubItem, Section


class TestTodoManagerHierarki:
    """Test suite för hierarkiska operationer på underuppgifter"""
    
    @pytest.fixture
    def temp_todo_file(self):
        """Skapar en temporär TODO-fil för tester"""
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
            temp_path = f.name
            
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def manager(self, temp_todo_file):
        """Skapar en TodoManager instans med testdata"""
        manager = TodoManager(temp_todo_file)
        manager.load()
        return manager
    
    def test_load_hierarchical_structure(self, manager):
        """Testar att hierarkisk struktur laddas korrekt"""
        # Kontrollera att huvuduppgifter laddats
        assert len(manager.sections) == 2
        assert manager.sections[0].name == "Test Sektion Alpha"
        assert len(manager.sections[0].items) == 2
        
        # Kontrollera hierarkisk struktur för uppgift 42
        item_42 = manager.find_item(42)
        assert item_42 is not None
        assert len(item_42.sub_items) == 2
        
        # Kontrollera djup struktur 42.1.1.1.1 (5 nivåer)
        sub_42_1 = manager.find_sub_item("42.1")
        assert sub_42_1 is not None
        assert sub_42_1.level == 2
        
        sub_42_1_1_1_1_1 = manager.find_sub_item("42.1.1.1.1")
        assert sub_42_1_1_1_1_1 is not None
        assert sub_42_1_1_1_1_1.level == 5
    
    def test_move_sub_item_between_main_tasks(self, manager):
        """Testar flyttning av underuppgift mellan huvuduppgifter"""
        # Flytta 42.2 till huvuduppgift 43
        result = manager.move_sub_item("42.2", "43")
        assert result is True
        
        # Verifiera att 42.2 nu är borta från 42
        item_42 = manager.find_item(42)
        sub_numbers = [sub.number for sub in item_42.sub_items]
        assert "42.2" not in sub_numbers
        
        # Verifiera att den nu finns under 43 som 43.3
        item_43 = manager.find_item(43)
        moved_sub = manager.find_sub_item("43.3")
        assert moved_sub is not None
        assert moved_sub.text == "Underuppgift Alpha 2"
        assert moved_sub.level == 2
        
        # Verifiera att barn följde med (42.2.1 → 43.3.1)
        child = manager.find_sub_item("43.3.1")
        assert child is not None
        assert child.text == "Nivå 3 under Alpha 2"
    
    def test_move_sub_item_between_sub_items(self, manager):
        """Testar flyttning av underuppgift mellan andra underuppgifter"""
        # Flytta 42.1.2 under 42.2
        result = manager.move_sub_item("42.1.2", "42.2")
        assert result is True
        
        # Verifiera att 42.1.2 nu är borta från 42.1
        sub_42_1 = manager.find_sub_item("42.1")
        child_numbers = [child.number for child in sub_42_1.sub_items]
        assert "42.1.2" not in child_numbers
        
        # Verifiera att den nu finns under 42.2 som 42.2.2
        moved_sub = manager.find_sub_item("42.2.2")
        assert moved_sub is not None
        assert moved_sub.text == "Ytterligare nivå 3"
        assert moved_sub.level == 3
    
    def test_move_sub_item_level_limit(self, manager):
        """Testar att nivågräns (5 nivåer) respekteras"""
        # Försök flytta något under den redan maximala nivån 42.1.1.1.1
        result = manager.move_sub_item("42.2", "42.1.1.1.1")
        assert result is False  # Borde misslyckas pga nivågräns
    
    def test_move_nonexistent_sub_item(self, manager):
        """Testar flyttning av icke-existerande underuppgift"""
        result = manager.move_sub_item("99.99", "42")
        assert result is False
    
    def test_move_to_nonexistent_parent(self, manager):
        """Testar flyttning till icke-existerande förälder"""
        result = manager.move_sub_item("42.1", "99")
        assert result is False
        
        result = manager.move_sub_item("42.1", "99.99")
        assert result is False
    
    def test_swap_sub_items_same_parent(self, manager):
        """Testar att byta plats på underuppgifter med samma förälder"""
        # Byt plats på 42.1 och 42.2
        result = manager.swap_sub_items("42.1", "42.2")
        assert result is True
        
        # Verifiera att de bytt plats i listan
        item_42 = manager.find_item(42)
        assert item_42.sub_items[0].number == "42.1"  # Var ursprungligen 42.2
        assert item_42.sub_items[1].number == "42.2"  # Var ursprungligen 42.1
        
        # Verifiera att texterna stämmer
        assert item_42.sub_items[0].text == "Underuppgift Alpha 2"
        assert item_42.sub_items[1].text == "Underuppgift Alpha 1"
    
    def test_swap_sub_items_different_parents(self, manager):
        """Testar att byta plats på underuppgifter med olika föräldrar"""
        # Byt plats på 42.1 och 43.1
        result = manager.swap_sub_items("42.1", "43.1")
        assert result is True
        
        # Verifiera att 43.1 nu finns under 42
        item_42 = manager.find_item(42)
        first_sub_42 = item_42.sub_items[0]
        assert first_sub_42.text == "Underuppgift Beta 1"
        
        # Verifiera att 42.1 nu finns under 43
        item_43 = manager.find_item(43)
        first_sub_43 = item_43.sub_items[0]
        assert first_sub_43.text == "Underuppgift Alpha 1"
    
    def test_swap_nonexistent_sub_items(self, manager):
        """Testar swap med icke-existerande underuppgifter"""
        result = manager.swap_sub_items("99.99", "42.1")
        assert result is False
        
        result = manager.swap_sub_items("42.1", "99.99")
        assert result is False
    
    def test_promote_sub_item(self, manager):
        """Testar att flytta underuppgift upp en nivå"""
        # Flytta 42.1.2 upp en nivå (från 42.1 till 42)
        result = manager.promote_sub_item("42.1.2")
        assert result is True
        
        # Verifiera att den nu finns som 42.3
        promoted = manager.find_sub_item("42.3")
        assert promoted is not None
        assert promoted.text == "Ytterligare nivå 3"
        assert promoted.level == 2
        
        # Verifiera att den inte längre finns under 42.1
        sub_42_1 = manager.find_sub_item("42.1")
        child_numbers = [child.number for child in sub_42_1.sub_items]
        assert "42.1.2" not in child_numbers
    
    def test_promote_sub_item_already_level_2(self, manager):
        """Testar promote på underuppgift som redan är på nivå 2"""
        result = manager.promote_sub_item("42.1")
        assert result is False  # Kan inte flytta upp från nivå 2
    
    def test_demote_sub_item(self, manager):
        """Testar att flytta underuppgift ner en nivå"""
        # Flytta 42.2 ner under 42.1
        result = manager.demote_sub_item("42.2", "42.1")
        assert result is True
        
        # Verifiera att den nu finns som 42.1.3
        demoted = manager.find_sub_item("42.1.3")
        assert demoted is not None
        assert demoted.text == "Underuppgift Alpha 2"
        assert demoted.level == 3
        
        # Verifiera att barn följde med
        child = manager.find_sub_item("42.1.3.1")
        assert child is not None
        assert child.text == "Nivå 3 under Alpha 2"
    
    def test_demote_sub_item_wrong_level(self, manager):
        """Testar demote med målsyskon på fel nivå"""
        # Försök flytta 42.1 (nivå 2) under 42.1.1 (nivå 3) - olika nivåer
        result = manager.demote_sub_item("42.1", "42.1.1")
        assert result is False
    
    def test_demote_sub_item_max_level(self, manager):
        """Testar demote på underuppgift som redan är på max nivå"""
        result = manager.demote_sub_item("42.1.1.1.1", "42.1.1.1")
        assert result is False  # Redan på nivå 5
    
    def test_demote_nonexistent_target(self, manager):
        """Testar demote med icke-existerande målsyskon"""
        result = manager.demote_sub_item("42.1", "99.99")
        assert result is False
    
    def test_hierarchy_updates_recursively(self, manager):
        """Testar att hela hierarkier uppdateras rekursivt"""
        # Flytta 42.1 (som har djup hierarki) till 44
        result = manager.move_sub_item("42.1", "44")
        assert result is True
        
        # Kontrollera att hela hierarkin följde med och numrerades om
        moved_root = manager.find_sub_item("44.2")
        assert moved_root is not None
        assert moved_root.text == "Underuppgift Alpha 1"
        
        # Kontrollera djupa nivåer
        deep_child = manager.find_sub_item("44.2.1.1.1")
        assert deep_child is not None
        assert deep_child.text == "Djup nivå 5 (max)"
        assert deep_child.level == 5
    
    def test_find_parent_container(self, manager):
        """Testar _find_parent_container hjälpfunktion"""
        # Test nivå 2 (direkt under huvuduppgift)
        container = manager._find_parent_container("42.1")
        assert container is not None
        assert len(container) == 2  # 42.1 och 42.2
        
        # Test djupare nivå
        container = manager._find_parent_container("42.1.1.1")
        assert container is not None
        # Borde vara under 42.1.1
        parent_42_1_1 = manager.find_sub_item("42.1.1")
        assert container is parent_42_1_1.sub_items
    
    def test_update_sub_item_hierarchy(self, manager):
        """Testar _update_sub_item_hierarchy hjälpfunktion"""
        # Hämta en underuppgift med barn
        sub_42_1 = manager.find_sub_item("42.1")
        assert sub_42_1 is not None
        
        # Uppdatera hierarkin till nytt nummer
        manager._update_sub_item_hierarchy(sub_42_1, "99.5", 2)
        
        # Kontrollera att numret uppdaterades
        assert sub_42_1.number == "99.5"
        assert sub_42_1.level == 2
        
        # Kontrollera att alla barn uppdaterades rekursivt
        first_child = sub_42_1.sub_items[0]
        assert first_child.number == "99.5.1"
        assert first_child.level == 3
    
    def test_remove_sub_item_from_parent(self, manager):
        """Testar _remove_sub_item_from_parent hjälpfunktion"""
        # Kontrollera att underuppgiften finns först
        assert manager.find_sub_item("42.1.2") is not None
        
        # Ta bort den
        result = manager._remove_sub_item_from_parent("42.1.2")
        assert result is True
        
        # Kontrollera att den är borta
        assert manager.find_sub_item("42.1.2") is None
        
        # Kontrollera att föräldern förlorade barnet
        sub_42_1 = manager.find_sub_item("42.1")
        child_numbers = [child.number for child in sub_42_1.sub_items]
        assert "42.1.2" not in child_numbers
    
    def test_complete_workflow_complex_reorganization(self, manager):
        """Testar komplex omorganisering med flera operationer"""
        # 1. Flytta 42.2 till att bli 43.3
        manager.move_sub_item("42.2", "43")
        
        # 2. Promote 42.1.1 till att bli 42.2
        manager.promote_sub_item("42.1.1")
        
        # 3. Swap 43.1 och 43.2
        manager.swap_sub_items("43.1", "43.2")
        
        # 4. Demote 42.2 under 42.1 (blir 42.1.2)
        manager.demote_sub_item("42.2", "42.1")
        
        # Verifiera slutresultat
        # 42.1 borde nu ha både original 42.1.2 och den flyttade/promoverade
        sub_42_1 = manager.find_sub_item("42.1")
        assert len(sub_42_1.sub_items) >= 2
        
        # 43 borde ha 3 underuppgifter (original 2 + flyttad 42.2)
        item_43 = manager.find_item(43)
        assert len(item_43.sub_items) == 3
        
        # Spara och ladda för att testa persistence
        manager.save()
        manager.load()
        
        # Verifiera att allt fortfarande stämmer efter save/load
        item_43_reloaded = manager.find_item(43)
        assert len(item_43_reloaded.sub_items) == 3


if __name__ == "__main__":
    # Kör testerna med pytest
    pytest.main([__file__, "-v"]) 