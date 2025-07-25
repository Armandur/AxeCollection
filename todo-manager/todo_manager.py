#!/usr/bin/env python3
"""
TODO Manager för AxeCollection
Automatisk hantering av TODO_FEATURES.md med korrekt numrering och struktur.

Usage:
    # Grundläggande kommandon
    python todo_manager.py add "Ny uppgift" "Sektionsnamn"
    python todo_manager.py complete 42
    python todo_manager.py remove 42
    
    # Visa uppgifter
    python todo_manager.py list "Sektionsnamn" --incomplete
    python todo_manager.py all-incomplete  # Alla oklarade från alla sektioner
    
    # Hierarkiska underuppgifter (5 nivåer: 1 huvud + 4 under)
    python todo_manager.py add-sub 42 "Ny underuppgift"
    python todo_manager.py add-sub 42.1 "Underuppgift till 42.1"
    python todo_manager.py complete-sub 42.1.2
    
    # Flytta och organisera
    python todo_manager.py move 42 "Ny sektion"
    python todo_manager.py swap 42 43
    python todo_manager.py move-sub 42.1.2 43
    python todo_manager.py promote-sub 42.1.2
    python todo_manager.py demote-sub 42.1 42.2
    
    # Sektionshantering
    python todo_manager.py new_section "Ny sektion"
    python todo_manager.py merge_sections "Sektion 1" "Sektion 2"
"""

import re
import argparse
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TodoSubItem:
    """Hierarkisk underuppgift som kan ha egna underuppgifter (totalt 5 nivåer: 1 huvud + 4 under)"""
    number: str  # e.g., "42.1" eller "42.1.1.1"
    completed: bool
    text: str
    sub_items: List['TodoSubItem']  # Rekursiv struktur
    level: int  # 2-5, vilken nivå detta är (nivå 1 är huvuduppgift)

@dataclass 
class TodoItem:
    """Huvuduppgift med möjliga underuppgifter"""
    number: int
    completed: bool
    text: str
    sub_items: List[TodoSubItem]
    section: str

@dataclass
class Section:
    name: str
    number: int
    items: List[TodoItem]

class TodoManager:
    def __init__(self, filename: str = "../TODO_FEATURES.md"):
        self.filename = filename
        self.sections: List[Section] = []
        self.header_lines: List[str] = []
        
    def load(self):
        """Laddar och parsar TODO_FEATURES.md"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Filen {self.filename} finns inte!")
            return False
            
        # Rensa befintliga data före laddning
        self.sections = []
        self.header_lines = []
        
        lines = content.split('\n')
        current_section = None
        current_item = None
        
        for line in lines:
            # Header lines (innan första sektionen)
            if not line.startswith('##') and current_section is None:
                # Lägg bara till icke-tomma rader i header_lines
                if line.strip():
                    self.header_lines.append(line)
                continue
                
            # Sektion (## X. Sektionsnamn)
            section_match = re.match(r'^## (\d+)\. (.+)$', line)
            if section_match:
                section_num = int(section_match.group(1))
                section_name = section_match.group(2)
                current_section = Section(section_name, section_num, [])
                self.sections.append(current_section)
                current_item = None
                continue
                
            # Huvuduppgift (X. [x] eller [ ] Uppgift)
            main_item_match = re.match(r'^(\d+)\. \[([ x])\] (.+)$', line)
            if main_item_match and current_section:
                item_num = int(main_item_match.group(1))
                completed = main_item_match.group(2) == 'x'
                text = main_item_match.group(3)
                current_item = TodoItem(item_num, completed, text, [], current_section.name)
                current_section.items.append(current_item)
                continue
                
            # Hierarkiska underuppgifter (nivå 2-5: 4, 8, 12, 16 spaces)
            if current_item and self._parse_sub_item(line, current_item):
                continue
                
        return True
        
    def _parse_sub_item(self, line: str, parent_item: TodoItem) -> bool:
        """Parsar hierarkiska underuppgifter på alla nivåer (2-5)"""
        # Kontrollera för nivå 2-5 (4, 8, 12, 16 spaces + "- [x] nummer text")
        for level in range(2, 6):  # Nivå 2-5
            indent = "    " * (level - 1)  # 4 spaces per nivå (minus 1 eftersom level börjar på 2)
            pattern = f"^{indent}- \\[([ x])\\] ([\\d.]+) (.+)$"
            match = re.match(pattern, line)
            
            if match:
                completed = match.group(1) == 'x'
                number = match.group(2)
                text = match.group(3)
                
                # Kontrollera att numreringen stämmer för denna nivå
                expected_parts = level  # Nivå 2 = X.Y (2 delar), Nivå 3 = X.Y.Z (3 delar), etc.
                if len(number.split('.')) != expected_parts:
                    continue  # Fel nivå för detta nummer
                
                # Hitta rätt föräldrauppgift att lägga till denna underuppgift i
                parent_container = self._find_parent_for_level(parent_item, number, level)
                if parent_container is not None:
                    sub_item = TodoSubItem(number, completed, text, [], level)
                    parent_container.append(sub_item)
                    return True
                    
        return False
        
    def _find_parent_for_level(self, root_item: TodoItem, number: str, level: int) -> Optional[List[TodoSubItem]]:
        """Hittar rätt lista att lägga till underuppgiften i baserat på numrering och nivå"""
        parts = number.split('.')
        
        if level == 2:
            # Nivå 2: Lägg direkt under huvuduppgiften
            return root_item.sub_items
        
        # Nivå 3-5: Rekursivt hitta rätt förälder
        current_container = root_item.sub_items
        
        # Gå igenom varje nivå för att hitta rätt förälder
        for depth in range(2, level):
            # Bygga upp förväntad föräldranummer
            parent_number = '.'.join(parts[:depth])
            
            # Hitta föräldrauppgiften på denna nivå
            found_parent = None
            for sub_item in current_container:
                if sub_item.number == parent_number:
                    found_parent = sub_item
                    break
                    
            if found_parent is None:
                return None  # Kunde inte hitta förälder
                
            current_container = found_parent.sub_items
            
        return current_container
        
    def save(self):
        """Sparar TODO-listan med korrekt numrering"""
        content = []
        
        # Header
        content.extend(self.header_lines)
        
        # Sections med automatisk numrering
        for section_idx, section in enumerate(self.sections, 1):
            section.number = section_idx
            content.append(f"## {section_idx}. {section.name}")
            content.append("")
            
            # Items med automatisk numrering
            for item_idx, item in enumerate(section.items, 1):
                # Beräkna globalt nummer
                global_num = sum(len(s.items) for s in self.sections[:section_idx-1]) + item_idx
                item.number = global_num
                
                # Huvuduppgift
                status = "x" if item.completed else " "
                content.append(f"{global_num}. [{status}] {item.text}")
                
                # Hierarkiska underuppgifter (alla 5 nivåer)
                self._save_sub_items(content, item.sub_items, global_num, 2)
                    
            content.append("")
            
        # Ta bort extra tomma rader i slutet
        while content and content[-1] == "":
            content.pop()
            
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
            
        print(f"✅ TODO-lista sparad till {self.filename}")
         
    def _save_sub_items(self, content: List[str], sub_items: List[TodoSubItem], parent_number, level: int):
         """Rekursivt sparar underuppgifter på alla nivåer (2-5)"""
         if level > 5:  # Max 5 nivåer totalt
             return
             
         for sub_idx, sub_item in enumerate(sub_items, 1):
             # Beräkna korrekt numrering baserat på nivå och förälder
             if level == 2:
                 # Nivå 2: parent är ett int (huvuduppgiftsnummer)
                 number = f"{parent_number}.{sub_idx}"
             else:
                 # Nivå 3-5: parent är en sträng, lägg till index
                 number = f"{parent_number}.{sub_idx}"
                 
             # Indentering: 4 spaces per nivå efter huvudnivån
             indent = "    " * (level - 1)  # Minus 1 eftersom level börjar på 2
             status = "x" if sub_item.completed else " "
             content.append(f"{indent}- [{status}] {number} {sub_item.text}")
             
             # Rekursivt hantera underuppgifter på nästa nivå
             if sub_item.sub_items and level < 5:
                 self._save_sub_items(content, sub_item.sub_items, number, level + 1)
        
    def add_item(self, text: str, section_name: str, completed: bool = False):
        """Lägger till en ny uppgift i angiven sektion"""
        section = self.find_section(section_name)
        if not section:
            print(f"❌ Sektion '{section_name}' finns inte!")
            return False
            
        new_item = TodoItem(0, completed, text, [], section_name)  # Nummer sätts vid save()
        section.items.append(new_item)
        
        # Beräkna vilket nummer uppgiften kommer att få
        section_idx = self.sections.index(section) + 1
        global_num = sum(len(s.items) for s in self.sections[:section_idx-1]) + len(section.items)
        
        print(f"✅ Lade till '{text}' i sektion '{section_name}' som uppgift #{global_num}")
        return global_num
        
    def add_sub_item(self, parent_number: str, text: str, completed: bool = False):
        """Lägger till en underuppgift till en befintlig uppgift eller underuppgift"""
        parent_parts = parent_number.split('.')
        
        if len(parent_parts) >= 5:
            print(f"❌ Kan inte lägga till fler undernivåer! Max 5 nivåer totalt.")
            return False
            
        # Hitta föräldrauppgiften
        parent_item = None
        parent_container = None
        
        if len(parent_parts) == 1:
            # Förälder är en huvuduppgift
            parent_item = self.find_item(int(parent_number))
            if parent_item:
                parent_container = parent_item.sub_items
        else:
            # Förälder är en underuppgift - hitta den rekursivt
            root_number = int(parent_parts[0])
            root_item = self.find_item(root_number)
            if root_item:
                parent_container = self._find_sub_item_container(root_item, parent_number)
                
        if parent_container is None:
            print(f"❌ Uppgift {parent_number} finns inte!")
            return False
            
        # Beräkna nästa nummer på denna nivå
        next_index = len(parent_container) + 1
        new_number = f"{parent_number}.{next_index}"
        new_level = len(parent_parts) + 1
        
        # Skapa ny underuppgift
        new_sub_item = TodoSubItem(new_number, completed, text, [], new_level)
        parent_container.append(new_sub_item)
        
        print(f"✅ Lade till underuppgift '{text}' som {new_number}")
        return new_number
        
    def _find_sub_item_container(self, root_item: TodoItem, target_number: str) -> Optional[List[TodoSubItem]]:
        """Hittar containern för underuppgifter för en given underuppgift"""
        def search_recursive(items: List[TodoSubItem]) -> Optional[List[TodoSubItem]]:
            for item in items:
                if item.number == target_number:
                    return item.sub_items
                # Sök rekursivt i underuppgifter
                result = search_recursive(item.sub_items)
                if result is not None:
                    return result
            return None
            
        return search_recursive(root_item.sub_items)
        
    def complete_item(self, item_number: int):
        """Markerar en uppgift som klar"""
        item = self.find_item(item_number)
        if not item:
            print(f"❌ Uppgift {item_number} finns inte!")
            return False
            
        item.completed = True
        print(f"✅ Markerade uppgift {item_number} som klar")
        return True
        
    def complete_sub_item(self, sub_number: str):
        """Markerar en underuppgift som klar"""
        sub_item = self.find_sub_item(sub_number)
        if not sub_item:
            print(f"❌ Underuppgift {sub_number} finns inte!")
            return False
            
        sub_item.completed = True
        print(f"✅ Markerade underuppgift {sub_number} som klar")
        return True
        
    def uncomplete_sub_item(self, sub_number: str):
        """Markerar en underuppgift som ej klar"""
        sub_item = self.find_sub_item(sub_number)
        if not sub_item:
            print(f"❌ Underuppgift {sub_number} finns inte!")
            return False
            
        sub_item.completed = False
        print(f"✅ Markerade underuppgift {sub_number} som ej klar")
        return True
        
    def uncomplete_item(self, item_number: int):
        """Markerar en uppgift som ej klar"""
        item = self.find_item(item_number)
        if not item:
            print(f"❌ Uppgift {item_number} finns inte!")
            return False
            
        item.completed = False
        print(f"✅ Markerade uppgift {item_number} som ej klar")
        return True
        
    def move_item(self, item_number: int, target_section: str):
        """Flyttar en uppgift till en annan sektion"""
        item = self.find_item(item_number)
        if not item:
            print(f"❌ Uppgift {item_number} finns inte!")
            return False
            
        target = self.find_section(target_section)
        if not target:
            print(f"❌ Sektion '{target_section}' finns inte!")
            return False
            
        # Ta bort från nuvarande sektion
        current_section = self.find_section(item.section)
        current_section.items.remove(item)
        
        # Lägg till i ny sektion
        item.section = target_section
        target.items.append(item)
        
        print(f"✅ Flyttade uppgift {item_number} till sektion '{target_section}'")
        return True
        
    def swap_items(self, item1_number: int, item2_number: int):
        """Byter plats på två uppgifter"""
        item1 = self.find_item(item1_number)
        item2 = self.find_item(item2_number)
        
        if not item1:
            print(f"❌ Uppgift {item1_number} finns inte!")
            return False
        if not item2:
            print(f"❌ Uppgift {item2_number} finns inte!")
            return False
            
        # Hitta sektioner
        section1 = self.find_section(item1.section)
        section2 = self.find_section(item2.section)
        
        # Hitta positioner i sina respektive sektioner
        pos1 = section1.items.index(item1)
        pos2 = section2.items.index(item2)
        
        # Byt plats
        if section1 == section2:
            # Samma sektion - enkelt byte
            section1.items[pos1], section1.items[pos2] = section1.items[pos2], section1.items[pos1]
        else:
            # Olika sektioner - byt sektion-tillhörighet också
            section1.items[pos1] = item2
            section2.items[pos2] = item1
            item1.section = section2.name
            item2.section = section1.name
            
        print(f"✅ Bytte plats på uppgift {item1_number} och {item2_number}")
        return True
        
    def move_to_position(self, item_number: int, target_position: int):
        """Flyttar en uppgift till en specifik global position"""
        item = self.find_item(item_number)
        if not item:
            print(f"❌ Uppgift {item_number} finns inte!")
            return False
            
        # Räkna totalt antal uppgifter
        total_items = sum(len(section.items) for section in self.sections)
        if target_position < 1 or target_position > total_items:
            print(f"❌ Position {target_position} är ogiltig! Måste vara mellan 1 och {total_items}")
            return False
            
        # Ta bort från nuvarande position
        current_section = self.find_section(item.section)
        current_section.items.remove(item)
        
        # Hitta målsektion och position inom den sektionen
        current_pos = 1
        for section in self.sections:
            section_start = current_pos
            section_end = current_pos + len(section.items)
            
            if target_position >= section_start and target_position < section_end:
                # Målet är i denna sektion
                position_in_section = target_position - section_start
                item.section = section.name
                section.items.insert(position_in_section, item)
                break
            elif target_position == section_end:
                # Lägg till i slutet av denna sektion
                item.section = section.name
                section.items.append(item)
                break
                
            current_pos = section_end
            
        print(f"✅ Flyttade uppgift {item_number} till position {target_position}")
        return True
        
    def move_sub_item(self, sub_number: str, new_parent_number: str):
        """Flyttar en underuppgift till en ny förälder"""
        # Hitta underuppgiften som ska flyttas
        sub_item = self.find_sub_item(sub_number)
        if not sub_item:
            print(f"❌ Underuppgift {sub_number} finns inte!")
            return False
            
        # Kontrollera att ny förälder finns och kan ta emot fler nivåer
        new_parent_parts = new_parent_number.split('.')
        if len(new_parent_parts) >= 5:
            print(f"❌ Kan inte flytta till {new_parent_number}! Max 5 nivåer totalt.")
            return False
            
        # Hitta ny förälder
        if len(new_parent_parts) == 1:
            # Ny förälder är huvuduppgift
            new_parent_item = self.find_item(int(new_parent_number))
            if not new_parent_item:
                print(f"❌ Huvuduppgift {new_parent_number} finns inte!")
                return False
            new_parent_container = new_parent_item.sub_items
        else:
            # Ny förälder är underuppgift
            root_number = int(new_parent_parts[0])
            root_item = self.find_item(root_number)
            if not root_item:
                print(f"❌ Huvuduppgift {root_number} finns inte!")
                return False
            new_parent_container = self._find_sub_item_container(root_item, new_parent_number)
            if new_parent_container is None:
                print(f"❌ Underuppgift {new_parent_number} finns inte!")
                return False
                
        # Ta bort från nuvarande position
        if not self._remove_sub_item_from_parent(sub_number):
            return False
            
        # Beräkna nytt nummer och nivå
        next_index = len(new_parent_container) + 1
        new_number = f"{new_parent_number}.{next_index}"
        new_level = len(new_parent_parts) + 1
        
        # Uppdatera nummer och nivå rekursivt
        self._update_sub_item_hierarchy(sub_item, new_number, new_level)
        
        # Lägg till i ny position
        new_parent_container.append(sub_item)
        
        print(f"✅ Flyttade underuppgift från {sub_number} till {new_number}")
        return True
        
    def _remove_sub_item_from_parent(self, sub_number: str) -> bool:
        """Tar bort underuppgift från dess nuvarande förälder"""
        parts = sub_number.split('.')
        root_number = int(parts[0])
        root_item = self.find_item(root_number)
        
        if not root_item:
            return False
            
        def remove_recursive(items: List[TodoSubItem], target_number: str) -> bool:
            for i, item in enumerate(items):
                if item.number == target_number:
                    items.pop(i)
                    return True
                if remove_recursive(item.sub_items, target_number):
                    return True
            return False
            
        return remove_recursive(root_item.sub_items, sub_number)
        
    def _update_sub_item_hierarchy(self, sub_item: TodoSubItem, new_number: str, new_level: int):
        """Uppdaterar numrering och nivå för underuppgift och alla dess barn"""
        old_number = sub_item.number
        sub_item.number = new_number
        sub_item.level = new_level
        
        # Uppdatera alla underuppgifter rekursivt
        for i, child in enumerate(sub_item.sub_items, 1):
            child_new_number = f"{new_number}.{i}"
            self._update_sub_item_hierarchy(child, child_new_number, new_level + 1)
            
    def swap_sub_items(self, sub1_number: str, sub2_number: str):
        """Byter plats på två underuppgifter"""
        sub1 = self.find_sub_item(sub1_number)
        sub2 = self.find_sub_item(sub2_number)
        
        if not sub1:
            print(f"❌ Underuppgift {sub1_number} finns inte!")
            return False
        if not sub2:
            print(f"❌ Underuppgift {sub2_number} finns inte!")
            return False
            
        # Hitta föräldrar
        parent1_container = self._find_parent_container(sub1_number)
        parent2_container = self._find_parent_container(sub2_number)
        
        if not parent1_container or not parent2_container:
            print(f"❌ Kunde inte hitta föräldracontainers!")
            return False
            
        # Hitta positioner
        pos1 = next((i for i, item in enumerate(parent1_container) if item.number == sub1_number), None)
        pos2 = next((i for i, item in enumerate(parent2_container) if item.number == sub2_number), None)
        
        if pos1 is None or pos2 is None:
            print(f"❌ Kunde inte hitta positioner för underuppgifterna!")
            return False
        
        # Byt plats
        if parent1_container is parent2_container:
            # Samma förälder
            parent1_container[pos1], parent1_container[pos2] = parent1_container[pos2], parent1_container[pos1]
        else:
            # Olika föräldrar
            parent1_container[pos1] = sub2
            parent2_container[pos2] = sub1
            
        print(f"✅ Bytte plats på underuppgift {sub1_number} och {sub2_number}")
        return True
        
    def _find_parent_container(self, sub_number: str) -> Optional[List[TodoSubItem]]:
        """Hittar föräldracontainern för en underuppgift"""
        parts = sub_number.split('.')
        root_number = int(parts[0])
        root_item = self.find_item(root_number)
        
        if not root_item:
            return None
            
        if len(parts) == 2:
            # Direktbarn till huvuduppgift
            return root_item.sub_items
            
        # Hitta föräldracontainern rekursivt
        parent_number = '.'.join(parts[:-1])
        
        def search_recursive(items: List[TodoSubItem]) -> Optional[List[TodoSubItem]]:
            for item in items:
                if item.number == parent_number:
                    return item.sub_items
                result = search_recursive(item.sub_items)
                if result is not None:
                    return result
            return None
            
        return search_recursive(root_item.sub_items)
        
    def promote_sub_item(self, sub_number: str):
        """Flyttar underuppgift upp en nivå (t.ex. 42.1.2 → 42.2)"""
        parts = sub_number.split('.')
        if len(parts) <= 2:
            print(f"❌ Underuppgift {sub_number} kan inte flyttas upp! Redan på nivå 2.")
            return False
            
        # Beräkna ny förälders nummer (ta bort sista nivån)
        new_parent_number = '.'.join(parts[:-2])
        if not new_parent_number:
            new_parent_number = parts[0]  # Flytta till huvuduppgift
            
        return self.move_sub_item(sub_number, new_parent_number)
        
    def demote_sub_item(self, sub_number: str, target_sibling: str):
        """Flyttar underuppgift ner en nivå under en av dess syskon"""
        parts = sub_number.split('.')
        if len(parts) >= 5:
            print(f"❌ Underuppgift {sub_number} kan inte flyttas ner! Redan på nivå 5.")
            return False
            
        # Kontrollera att målsyskonet finns och är på samma nivå
        target_parts = target_sibling.split('.')
        if len(target_parts) != len(parts):
            print(f"❌ {target_sibling} är inte på samma nivå som {sub_number}!")
            return False
            
        if not self.find_sub_item(target_sibling):
            print(f"❌ Målsyskon {target_sibling} finns inte!")
            return False
            
        return self.move_sub_item(sub_number, target_sibling)
        
    def new_section(self, section_name: str):
        """Skapar en ny sektion"""
        if self.find_section(section_name):
            print(f"❌ Sektion '{section_name}' finns redan!")
            return False
            
        new_section = Section(section_name, 0, [])  # Nummer sätts vid save()
        self.sections.append(new_section)
        
        print(f"✅ Skapade ny sektion '{section_name}'")
        return True
        
    def merge_sections(self, source_section: str, target_section: str):
        """Slår ihop två sektioner"""
        source = self.find_section(source_section)
        target = self.find_section(target_section)
        
        if not source:
            print(f"❌ Sektion '{source_section}' finns inte!")
            return False
        if not target:
            print(f"❌ Sektion '{target_section}' finns inte!")
            return False
            
        # Flytta alla items från source till target
        for item in source.items:
            item.section = target_section
            target.items.append(item)
            
        # Ta bort source-sektionen
        self.sections.remove(source)
        
        print(f"✅ Slog ihop '{source_section}' med '{target_section}'")
        return True
        
    def remove_item(self, item_number: int):
        """Tar bort en huvuduppgift"""
        item = self.find_item(item_number)
        if not item:
            print(f"❌ Uppgift {item_number} finns inte!")
            return False
            
        # Hitta sektionen och ta bort uppgiften
        section = self.find_section(item.section)
        section.items.remove(item)
        
        print(f"✅ Tog bort uppgift {item_number}: '{item.text}'")
        return True
        
    def remove_multiple_items(self, item_numbers: List[int]):
        """Tar bort flera uppgifter samtidigt (innan omnumrering)"""
        items_to_remove = []
        failed_items = []
        
        # Hitta alla uppgifter som ska tas bort
        for number in item_numbers:
            item = self.find_item(number)
            if item:
                items_to_remove.append((item, self.find_section(item.section)))
                print(f"✅ Hittat för borttagning: uppgift {number} - '{item.text}'")
            else:
                failed_items.append(number)
                print(f"❌ Uppgift {number} finns inte!")
        
        # Ta bort alla hittade uppgifter
        for item, section in items_to_remove:
            section.items.remove(item)
            
        success_count = len(items_to_remove)
        print(f"\n📊 Resultat: {success_count} uppgifter borttagna")
        if failed_items:
            print(f"❌ Misslyckades med: {', '.join(map(str, failed_items))}")
            
        return success_count > 0
        
    def remove_section(self, section_name: str):
        """Tar bort en hel sektion med alla uppgifter"""
        section = self.find_section(section_name)
        if not section:
            print(f"❌ Sektion '{section_name}' finns inte!")
            return False
            
        item_count = len(section.items)
        self.sections.remove(section)
        
        print(f"✅ Tog bort sektion '{section_name}' med {item_count} uppgifter")
        return True
        
    def list_sections(self):
        """Listar alla sektioner"""
        print("📋 Sektioner:")
        for idx, section in enumerate(self.sections, 1):
            print(f"  {idx}. {section.name} ({len(section.items)} uppgifter)")
            
    def find_section(self, name: str) -> Optional[Section]:
        """Hittar sektion efter namn"""
        for section in self.sections:
            if section.name.lower() == name.lower():
                return section
        return None
        
    def find_item(self, number: int) -> Optional[TodoItem]:
        """Hittar huvuduppgift efter nummer"""
        for section in self.sections:
            for item in section.items:
                if item.number == number:
                    return item
        return None
        
    def find_sub_item(self, number: str) -> Optional[TodoSubItem]:
        """Hittar underuppgift efter nummer (hierarkisk sökning)"""
        parts = number.split('.')
        if len(parts) < 2:
            return None  # Inte en underuppgift
            
        # Hitta huvuduppgiften först
        root_number = int(parts[0])
        root_item = self.find_item(root_number)
        if not root_item:
            return None
            
        # Sök rekursivt efter underuppgiften
        def search_recursive(items: List[TodoSubItem]) -> Optional[TodoSubItem]:
            for item in items:
                if item.number == number:
                    return item
                # Sök vidare i underuppgifter
                result = search_recursive(item.sub_items)
                if result:
                    return result
            return None
            
        return search_recursive(root_item.sub_items)
        
    def list_items(self, section_name: str, only_incomplete: bool = False):
        """Listar alla uppgifter i en sektion"""
        section = self.find_section(section_name)
        if not section:
            print(f"❌ Sektion '{section_name}' finns inte!")
            return False
            
        print(f"📋 Uppgifter i sektion '{section_name}':")
        
        if not section.items:
            print("  Inga uppgifter i denna sektion")
            return True
            
        for item in section.items:
            # Filtrera på incomplete om begärt
            if only_incomplete and item.completed:
                continue
                
            # Huvuduppgift
            status_icon = "✅" if item.completed else "⏳"
            print(f"  {item.number}. {status_icon} {item.text}")
            
            # Visa alla underuppgifter rekursivt (alla 5 nivåer)
            self._list_sub_items_recursive(item.sub_items, 2, only_incomplete)
                
        return True
        
    def _list_sub_items_recursive(self, sub_items: List[TodoSubItem], level: int, only_incomplete: bool):
        """Rekursivt visar underuppgifter på alla nivåer med korrekt indentering"""
        for sub_item in sub_items:
            # Filtrera på incomplete om begärt
            if only_incomplete and sub_item.completed:
                continue
                
            # Indentering baserat på nivå (4 spaces per nivå)
            indent = "  " * level  # 2 spaces per nivå för visning (mer kompakt än save-format)
            status_icon = "✅" if sub_item.completed else "⏳"
            print(f"{indent}- {status_icon} {sub_item.number} {sub_item.text}")
            
            # Rekursivt visa underuppgifter på nästa nivå
            if sub_item.sub_items and level < 5:
                self._list_sub_items_recursive(sub_item.sub_items, level + 1, only_incomplete)
                
    def list_all_incomplete(self):
        """Listar alla oklarade uppgifter från alla sektioner"""
        print("📋 Alla oklarade uppgifter:")
        
        total_incomplete = 0
        
        for section in self.sections:
            incomplete_in_section = []
            
            # Samla alla oklarade uppgifter i denna sektion
            for item in section.items:
                if not item.completed:
                    incomplete_in_section.append(item)
                # Kontrollera även underuppgifter
                for sub_item in item.sub_items:
                    if not sub_item.completed:
                        incomplete_in_section.append(sub_item)
            
            # Visa sektionen bara om det finns oklarade uppgifter
            if incomplete_in_section:
                print(f"\n📁 {section.name}:")
                section_count = 0
                
                for item in section.items:
                    if not item.completed:
                        print(f"  {item.number}. ⏳ {item.text}")
                        section_count += 1
                        
                        # Visa oklarade underuppgifter för denna huvuduppgift
                        self._list_sub_items_recursive(item.sub_items, 2, only_incomplete=True)
                
                total_incomplete += section_count
                
        if total_incomplete == 0:
            print("  🎉 Inga oklarade uppgifter - bra jobbat!")
        else:
            print(f"\n📊 Totalt: {total_incomplete} oklarade uppgifter")
            
        return True
        
    def list_all(self):
        """Listar alla uppgifter från alla sektioner (både klara och oklara)"""
        print("📋 Alla uppgifter:")
        
        total_items = 0
        
        for section in self.sections:
            print(f"\n📁 {section.name}:")
            section_count = 0
            
            for item in section.items:
                status = "✅" if item.completed else "⏳"
                print(f"  {item.number}. {status} {item.text}")
                section_count += 1
                
                # Visa alla underuppgifter för denna huvuduppgift
                self._list_sub_items_recursive(item.sub_items, 2, only_incomplete=False)
            
            total_items += section_count
            print(f"  📊 {section_count} uppgifter i denna sektion")
                
        print(f"\n📊 Totalt: {total_items} uppgifter")
        return True
        
    def complete_multiple_items(self, item_numbers: List[int]):
        """Markerar flera uppgifter som klara"""
        success_count = 0
        failed_items = []
        
        for number in item_numbers:
            item = self.find_item(number)
            if item:
                item.completed = True
                success_count += 1
                print(f"✅ Markerade uppgift {number} som klar")
            else:
                failed_items.append(number)
                print(f"❌ Uppgift {number} finns inte!")
                
        print(f"\n📊 Resultat: {success_count} uppgifter markerade som klara")
        if failed_items:
            print(f"❌ Misslyckades med: {', '.join(map(str, failed_items))}")
            
        return success_count > 0
        
    def add_multiple_items(self, texts: List[str], section_name: str, completed: bool = False):
        """Lägger till flera nya uppgifter i angiven sektion"""
        section = self.find_section(section_name)
        if not section:
            print(f"❌ Sektion '{section_name}' finns inte!")
            return []
            
        added_items = []
        
        for text in texts:
            new_item = TodoItem(0, completed, text, [], section_name)  # Nummer sätts vid save()
            section.items.append(new_item)
            
            # Beräkna vilket nummer uppgiften kommer att få
            section_idx = self.sections.index(section) + 1
            global_num = sum(len(s.items) for s in self.sections[:section_idx-1]) + len(section.items)
            
            added_items.append(global_num)
            print(f"✅ Lade till '{text}' i sektion '{section_name}' som uppgift #{global_num}")
            
        print(f"\n📊 Resultat: {len(added_items)} uppgifter tillagda i sektion '{section_name}'")
        if added_items:
            print(f"🆔 ID-nummer: {', '.join(map(str, added_items))}")
            
        return added_items

    def stats(self):
        """Visar statistik över TODO-listan"""
        total_items = sum(len(section.items) for section in self.sections)
        completed_items = sum(sum(1 for item in section.items if item.completed) 
                            for section in self.sections)
        
        print(f"📊 TODO-statistik:")
        print(f"  📝 Totalt: {total_items} uppgifter")
        print(f"  ✅ Klara: {completed_items} uppgifter")
        print(f"  ⏳ Kvar: {total_items - completed_items} uppgifter")
        print(f"  📁 Sektioner: {len(self.sections)}")
        
        if total_items > 0:
            progress = (completed_items / total_items) * 100
            print(f"  📈 Framsteg: {progress:.1f}%")

def main():
    parser = argparse.ArgumentParser(description="TODO Manager för AxeCollection")
    subparsers = parser.add_subparsers(dest='command', help='Kommandon')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Lägg till ny uppgift')
    add_parser.add_argument('text', help='Uppgiftens text')
    add_parser.add_argument('section', help='Sektionsnamn')
    add_parser.add_argument('--completed', action='store_true', help='Markera som klar direkt')
    
    # Add multiple command
    add_multiple_parser = subparsers.add_parser('add-multiple', help='Lägg till flera uppgifter')
    add_multiple_parser.add_argument('texts', nargs='+', help='Uppgiftstexter (separerade med space)')
    add_multiple_parser.add_argument('section', help='Sektionsnamn')
    add_multiple_parser.add_argument('--completed', action='store_true', help='Markera alla som klara direkt')
    
    # Add sub-item command  
    add_sub_parser = subparsers.add_parser('add-sub', help='Lägg till underuppgift')
    add_sub_parser.add_argument('parent', help='Föräldranummer (t.ex. 42 eller 42.1)')
    add_sub_parser.add_argument('text', help='Underuppgiftens text')
    add_sub_parser.add_argument('--completed', action='store_true', help='Markera som klar direkt')
    
    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Markera uppgift som klar')
    complete_parser.add_argument('number', type=int, help='Uppgiftsnummer')
    
    # Complete multiple command  
    complete_multiple_parser = subparsers.add_parser('complete-multiple', help='Markera flera uppgifter som klara')
    complete_multiple_parser.add_argument('numbers', nargs='+', type=int, help='Uppgiftsnummer (separerade med space)')
    
    # Uncomplete command
    uncomplete_parser = subparsers.add_parser('uncomplete', help='Markera uppgift som ej klar')
    uncomplete_parser.add_argument('number', type=int, help='Uppgiftsnummer')
    
    # Complete sub-item command
    complete_sub_parser = subparsers.add_parser('complete-sub', help='Markera underuppgift som klar')
    complete_sub_parser.add_argument('number', help='Underuppgiftsnummer (t.ex. 42.1 eller 42.1.2)')
    
    # Uncomplete sub-item command
    uncomplete_sub_parser = subparsers.add_parser('uncomplete-sub', help='Markera underuppgift som ej klar')
    uncomplete_sub_parser.add_argument('number', help='Underuppgiftsnummer (t.ex. 42.1 eller 42.1.2)')
    
    # Move command
    move_parser = subparsers.add_parser('move', help='Flytta uppgift till annan sektion')
    move_parser.add_argument('number', type=int, help='Uppgiftsnummer')
    move_parser.add_argument('section', help='Målsektion')
    
    # Swap items command
    swap_parser = subparsers.add_parser('swap', help='Byter plats på två uppgifter')
    swap_parser.add_argument('item1', type=int, help='Första uppgiftsnummer')
    swap_parser.add_argument('item2', type=int, help='Andra uppgiftsnummer')
    
    # Move to position command
    move_pos_parser = subparsers.add_parser('move-to', help='Flytta uppgift till specifik position')
    move_pos_parser.add_argument('number', type=int, help='Uppgiftsnummer')
    move_pos_parser.add_argument('position', type=int, help='Målposition (globalt nummer)')
    
    # Move sub-item command
    move_sub_parser = subparsers.add_parser('move-sub', help='Flytta underuppgift till ny förälder')
    move_sub_parser.add_argument('sub_number', help='Underuppgiftsnummer (t.ex. 42.1.2)')
    move_sub_parser.add_argument('new_parent', help='Ny förälder (t.ex. 43 eller 43.1)')
    
    # Swap sub-items command
    swap_sub_parser = subparsers.add_parser('swap-sub', help='Byter plats på två underuppgifter')
    swap_sub_parser.add_argument('sub1', help='Första underuppgiftsnummer')
    swap_sub_parser.add_argument('sub2', help='Andra underuppgiftsnummer')
    
    # Promote sub-item command
    promote_parser = subparsers.add_parser('promote-sub', help='Flytta underuppgift upp en nivå')
    promote_parser.add_argument('sub_number', help='Underuppgiftsnummer (t.ex. 42.1.2)')
    
    # Demote sub-item command
    demote_parser = subparsers.add_parser('demote-sub', help='Flytta underuppgift ner en nivå')
    demote_parser.add_argument('sub_number', help='Underuppgiftsnummer (t.ex. 42.1)')
    demote_parser.add_argument('target_sibling', help='Målsyskon att flytta under (t.ex. 42.2)')
    
    # New section command
    section_parser = subparsers.add_parser('new-section', help='Skapa ny sektion')
    section_parser.add_argument('name', help='Sektionsnamn')
    
    # Merge sections command
    merge_parser = subparsers.add_parser('merge', help='Slå ihop två sektioner')
    merge_parser.add_argument('source', help='Källsektion')
    merge_parser.add_argument('target', help='Målsektion')
    
    # Remove item command
    remove_parser = subparsers.add_parser('remove', help='Ta bort uppgift')
    remove_parser.add_argument('number', type=int, help='Uppgiftsnummer')
    
    # Remove multiple items command
    remove_multiple_parser = subparsers.add_parser('remove-multiple', help='Ta bort flera uppgifter')
    remove_multiple_parser.add_argument('numbers', nargs='+', type=int, help='Uppgiftsnummer (separerade med space)')
    
    # Remove section command
    remove_section_parser = subparsers.add_parser('remove-section', help='Ta bort sektion')
    remove_section_parser.add_argument('name', help='Sektionsnamn')
    
    # List sections command
    subparsers.add_parser('sections', help='Lista alla sektioner')
    
    # List items command
    list_parser = subparsers.add_parser('list', help='Lista uppgifter i en sektion')
    list_parser.add_argument('section', help='Sektionsnamn')
    list_parser.add_argument('--incomplete', action='store_true', help='Visa bara ej slutförda uppgifter')
    
    # List all incomplete command
    subparsers.add_parser('all-incomplete', help='Lista alla oklarade uppgifter från alla sektioner')
    
    # List all command
    subparsers.add_parser('all', help='Lista alla uppgifter från alla sektioner (både klara och oklara)')
    
    # Reorder command
    subparsers.add_parser('reorder', help='Uppdatera numrering')
    
    # Stats command
    subparsers.add_parser('stats', help='Visa statistik')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    manager = TodoManager()
    if not manager.load():
        return
        
    if args.command == 'add':
        result = manager.add_item(args.text, args.section, args.completed)
        if result:
            manager.save()
    elif args.command == 'add-multiple':
        manager.add_multiple_items(args.texts, args.section, args.completed)
        manager.save()
    elif args.command == 'add-sub':
        result = manager.add_sub_item(args.parent, args.text, args.completed)
        if result:
            manager.save()
    elif args.command == 'complete':
        manager.complete_item(args.number)
        manager.save()
    elif args.command == 'complete-multiple':
        if manager.complete_multiple_items(args.numbers):
            manager.save()
    elif args.command == 'uncomplete':
        manager.uncomplete_item(args.number)
        manager.save()
    elif args.command == 'complete-sub':
        if manager.complete_sub_item(args.number):
            manager.save()
    elif args.command == 'uncomplete-sub':
        if manager.uncomplete_sub_item(args.number):
            manager.save()
    elif args.command == 'move':
        manager.move_item(args.number, args.section)
        manager.save()
    elif args.command == 'swap':
        if manager.swap_items(args.item1, args.item2):
            manager.save()
    elif args.command == 'move-to':
        if manager.move_to_position(args.number, args.position):
            manager.save()
    elif args.command == 'move-sub':
        if manager.move_sub_item(args.sub_number, args.new_parent):
            manager.save()
    elif args.command == 'swap-sub':
        if manager.swap_sub_items(args.sub1, args.sub2):
            manager.save()
    elif args.command == 'promote-sub':
        if manager.promote_sub_item(args.sub_number):
            manager.save()
    elif args.command == 'demote-sub':
        if manager.demote_sub_item(args.sub_number, args.target_sibling):
            manager.save()
    elif args.command == 'new-section':
        manager.new_section(args.name)
        manager.save()
    elif args.command == 'merge':
        manager.merge_sections(args.source, args.target)
        manager.save()
    elif args.command == 'remove':
        if manager.remove_item(args.number):
            manager.save()
    elif args.command == 'remove-multiple':
        if manager.remove_multiple_items(args.numbers):
            manager.save()
    elif args.command == 'remove-section':
        if manager.remove_section(args.name):
            manager.save()
    elif args.command == 'sections':
        manager.list_sections()
    elif args.command == 'list':
        manager.list_items(args.section, args.incomplete)
    elif args.command == 'all-incomplete':
        manager.list_all_incomplete()
    elif args.command == 'all':
        manager.list_all()
    elif args.command == 'reorder':
        manager.save()  # Save automatiskt uppdaterar numrering
    elif args.command == 'stats':
        manager.stats()

if __name__ == "__main__":
    main() 