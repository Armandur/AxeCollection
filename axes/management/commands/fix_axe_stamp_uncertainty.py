from django.core.management.base import BaseCommand
from axes.models import AxeStamp


class Command(BaseCommand):
    help = 'Fixa inkonsistens i AxeStamp uncertainty_level-värden'

    def handle(self, *args, **options):
        self.stdout.write("Fixing AxeStamp uncertainty_level values...")
        
        # Mappning från svenska till engelska värden
        swedish_to_english = {
            'säker': 'certain',
            'osäker': 'uncertain', 
            'preliminär': 'tentative'
        }
        
        # Hämta alla AxeStamp-objekt med ogiltiga värden
        axe_stamps = AxeStamp.objects.all()
        fixed_count = 0
        
        for axe_stamp in axe_stamps:
            current_value = axe_stamp.uncertainty_level
            
            # Kontrollera om värdet är svenska
            if current_value in swedish_to_english:
                new_value = swedish_to_english[current_value]
                self.stdout.write(f"Fixing yxa {axe_stamp.axe.display_id} - stämpel {axe_stamp.stamp.name}:")
                self.stdout.write(f"  '{current_value}' -> '{new_value}'")
                
                axe_stamp.uncertainty_level = new_value
                axe_stamp.save()
                fixed_count += 1
        
        self.stdout.write(f"\nFixed {fixed_count} AxeStamp objects")
        
        # Verifiera att alla värden nu är korrekta
        self.stdout.write("\nVerifying fixes...")
        valid_choices = [choice[0] for choice in AxeStamp.UNCERTAINTY_CHOICES]
        
        for axe_stamp in AxeStamp.objects.all():
            if axe_stamp.uncertainty_level not in valid_choices:
                self.stdout.write(f"VARNING: Yxa {axe_stamp.axe.display_id} har fortfarande ogiltigt värde: '{axe_stamp.uncertainty_level}'")
            else:
                self.stdout.write(f"✓ Yxa {axe_stamp.axe.display_id}: '{axe_stamp.uncertainty_level}' -> '{axe_stamp.get_uncertainty_level_display()}'")
        
        self.stdout.write("\nFix completed!") 