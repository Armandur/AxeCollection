from django.core.management.base import BaseCommand
from axes.models import StampSymbol


class Command(BaseCommand):
    help = "Initierar fördefinierade stämpelsymboler"

    def handle(self, *args, **options):
        predefined_symbols = [
            # Kronor
            {"name": "Krona", "symbol_type": "crown", "description": "Krona"},
            {"name": "Tre kronor", "symbol_type": "crown", "description": "Tre kronor"},
            
            # Kanoner
            {"name": "Kanon", "symbol_type": "cannon", "description": "Kanon"},
            
            # Stjärnor
            {"name": "Femuddig stjärna", "symbol_type": "star", "description": "Femuddig stjärna"},
            {"name": "Sexuddig stjärna", "symbol_type": "star", "description": "Sexuddig stjärna"},
            {"name": "Sjuuddig stjärna", "symbol_type": "star", "description": "Sjuuddig stjärna"},
            
            # Kors
            {"name": "Kryss", "symbol_type": "cross", "description": "Kryss"},
            {"name": "Kors", "symbol_type": "cross", "description": "Kors"},
            
            # Ankare
            {"name": "Ankare", "symbol_type": "anchor", "description": "Ankare"},
            
            # Spader (kortspel)
            {"name": "Hjärta", "symbol_type": "other", "description": "Hjärta"},
            {"name": "Spader", "symbol_type": "other", "description": "Spader"},
            
            # Linjer
            {"name": "Linje", "symbol_type": "other", "description": "Linje"},
            {"name": "Pil", "symbol_type": "other", "description": "Pil"},
            {"name": "Sicksackline", "symbol_type": "other", "description": "Sicksackline"},
            {"name": "W-linje", "symbol_type": "other", "description": "W-linje"},
            {"name": "Streckad linje", "symbol_type": "other", "description": "Streckad linje"},
            
            # Geometriska former
            {"name": "Ring", "symbol_type": "other", "description": "Ring"},
            {"name": "Cirkel", "symbol_type": "other", "description": "Cirkel"},
            {"name": "Oktagon", "symbol_type": "other", "description": "Oktagon"},
            {"name": "Hexagon", "symbol_type": "other", "description": "Hexagon"},
            {"name": "Pentagon", "symbol_type": "other", "description": "Pentagon"},
            {"name": "Triangel", "symbol_type": "other", "description": "Triangel"},
            {"name": "Fyrkant", "symbol_type": "other", "description": "Fyrkant"},
            {"name": "Halvcirkel", "symbol_type": "other", "description": "Halvcirkel"},
            {"name": "Halvmåne", "symbol_type": "other", "description": "Halvmåne"},
            
            # Djur
            {"name": "Oxe", "symbol_type": "other", "description": "Oxe"},
            {"name": "Bock", "symbol_type": "other", "description": "Bock"},
            {"name": "Tjur", "symbol_type": "other", "description": "Tjur"},
            {"name": "Hästsko", "symbol_type": "other", "description": "Hästsko"},
            {"name": "Bäver", "symbol_type": "other", "description": "Bäver"},
            {"name": "Katt", "symbol_type": "other", "description": "Katt"},
            {"name": "Vädur", "symbol_type": "other", "description": "Vädur"},
            
            # Människor
            {"name": "Man", "symbol_type": "other", "description": "Man"},
            
            # Symboler
            {"name": "Järnsymbol", "symbol_type": "other", "description": "Järnsymbol ♂"},
        ]

        created_count = 0
        for symbol_data in predefined_symbols:
            symbol, created = StampSymbol.objects.get_or_create(
                name=symbol_data["name"],
                symbol_type=symbol_data["symbol_type"],
                defaults={
                    "description": symbol_data["description"],
                    "is_predefined": True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Skapade symbol: {symbol}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Initiering slutförd. {created_count} nya symboler skapade."
            )
        ) 