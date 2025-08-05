from django.core.management.base import BaseCommand
from axes.models import StampSymbol


class Command(BaseCommand):
    help = "Uppdaterar piktogram för befintliga symboler"

    def handle(self, *args, **options):
        # Mappning av symbolnamn till piktogram
        pictogram_mapping = {
            "Krona": "👑",
            "Cirkel": "⭕",
            "Halvcirkel": "◐",
            "Pil": "↑",
            "Pil upp": "↑",
            "Pil ner": "↓",
            "Pil vänster": "←",
            "Pil höger": "→",
            "Fyrkant": "⬜",
            "Kvadrat": "⬜",
            "Triangel": "▲",
            "Triangel upp": "▲",
            "Triangel ner": "▼",
            "Diamant": "♦",
            "Romb": "♦",
            "Hjärta": "♥",
            "Ring": "⭕",
            "Blomma": "🌸",
            "Ros": "🌹",
            "Löv": "🍃",
            "Eklöv": "🍂",
            "Sköld": "🛡️",
            "Ankare": "⚓",
            "Spader": "♠",
            "Linje": "━",
            "Sicksackline": "⚡",
            "W-linje": "〰️",
            "Streckad linje": "┄",
            "Oktagon": "⬡",
            "Hexagon": "⬡",
            "Pentagon": "⬟",
            "Halvmåne": "☾",
            "Oxe": "🐂",
            "Bock": "🐐",
            "Tjur": "🐃",
            "Hästsko": "🐎",
            "Bäver": "🦫",
            "Katt": "🐱",
            "Vädur": "🐏",
            "Man": "👤",
            "Järnsymbol": "♂",
            "Kanon": "💥",
            "Femuddig stjärna": "⭐",
            "Sexuddig stjärna": "⭐",
            "Sjuuddig stjärna": "⭐",
            "Kryss": "✝",
            "Kors": "✝",
        }

        updated_count = 0
        for symbol_name, pictogram in pictogram_mapping.items():
            symbols = StampSymbol.objects.filter(name=symbol_name)
            if symbols.exists():
                # Uppdatera alla symboler med samma namn
                for symbol in symbols:
                    if symbol.pictogram != pictogram:
                        symbol.pictogram = pictogram
                        symbol.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Uppdaterade {symbol_name} (ID {symbol.id}): {pictogram}"
                            )
                        )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Symbol {symbol_name} finns inte")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Uppdatering slutförd. {updated_count} symboler uppdaterade."
            )
        )
