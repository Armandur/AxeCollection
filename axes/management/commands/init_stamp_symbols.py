from django.core.management.base import BaseCommand
from axes.models import StampSymbol


class Command(BaseCommand):
    help = "Initierar fördefinierade stämpelsymboler"

    def add_arguments(self, parser):
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Minska output till endast viktiga meddelanden",
        )

    def handle(self, *args, **options):
        quiet = options.get("quiet", False)
        predefined_symbols = [
            # Kronor
            {
                "name": "Krona",
                "symbol_type": "crown",
                "description": "Krona",
                "pictogram": "👑",
            },
            {
                "name": "Tre kronor",
                "symbol_type": "crown",
                "description": "Tre kronor",
                "pictogram": "👑👑👑",
            },
            # Kanoner
            {
                "name": "Kanon",
                "symbol_type": "cannon",
                "description": "Kanon",
                "pictogram": "💥",
            },
            # Stjärnor
            {
                "name": "Femuddig stjärna",
                "symbol_type": "star",
                "description": "Femuddig stjärna",
                "pictogram": "⭐",
            },
            {
                "name": "Sexuddig stjärna",
                "symbol_type": "star",
                "description": "Sexuddig stjärna",
                "pictogram": "⭐",
            },
            {
                "name": "Sjuuddig stjärna",
                "symbol_type": "star",
                "description": "Sjuuddig stjärna",
                "pictogram": "⭐",
            },
            # Kors
            {
                "name": "Kryss",
                "symbol_type": "cross",
                "description": "Kryss",
                "pictogram": "✝",
            },
            {
                "name": "Kors",
                "symbol_type": "cross",
                "description": "Kors",
                "pictogram": "✝",
            },
            # Sköldar
            {
                "name": "Sköld",
                "symbol_type": "shield",
                "description": "Sköld",
                "pictogram": "🛡️",
            },
            # Ankare
            {
                "name": "Ankare",
                "symbol_type": "anchor",
                "description": "Ankare",
                "pictogram": "⚓",
            },
            # Blommor
            {
                "name": "Blomma",
                "symbol_type": "flower",
                "description": "Blomma",
                "pictogram": "🌸",
            },
            {
                "name": "Ros",
                "symbol_type": "flower",
                "description": "Ros",
                "pictogram": "🌹",
            },
            # Löv
            {
                "name": "Löv",
                "symbol_type": "leaf",
                "description": "Löv",
                "pictogram": "🍃",
            },
            {
                "name": "Eklöv",
                "symbol_type": "leaf",
                "description": "Eklöv",
                "pictogram": "🍂",
            },
            # Pilar
            {
                "name": "Pil",
                "symbol_type": "arrow",
                "description": "Pil",
                "pictogram": "↑",
            },
            {
                "name": "Pil upp",
                "symbol_type": "arrow",
                "description": "Pil upp",
                "pictogram": "↑",
            },
            {
                "name": "Pil ner",
                "symbol_type": "arrow",
                "description": "Pil ner",
                "pictogram": "↓",
            },
            {
                "name": "Pil vänster",
                "symbol_type": "arrow",
                "description": "Pil vänster",
                "pictogram": "←",
            },
            {
                "name": "Pil höger",
                "symbol_type": "arrow",
                "description": "Pil höger",
                "pictogram": "→",
            },
            # Cirkel
            {
                "name": "Cirkel",
                "symbol_type": "circle",
                "description": "Cirkel",
                "pictogram": "⭕",
            },
            {
                "name": "Ring",
                "symbol_type": "circle",
                "description": "Ring",
                "pictogram": "⭕",
            },
            # Fyrkant
            {
                "name": "Fyrkant",
                "symbol_type": "square",
                "description": "Fyrkant",
                "pictogram": "⬜",
            },
            {
                "name": "Kvadrat",
                "symbol_type": "square",
                "description": "Kvadrat",
                "pictogram": "⬜",
            },
            # Triangel
            {
                "name": "Triangel",
                "symbol_type": "triangle",
                "description": "Triangel",
                "pictogram": "▲",
            },
            {
                "name": "Triangel upp",
                "symbol_type": "triangle",
                "description": "Triangel upp",
                "pictogram": "▲",
            },
            {
                "name": "Triangel ner",
                "symbol_type": "triangle",
                "description": "Triangel ner",
                "pictogram": "▼",
            },
            # Diamant
            {
                "name": "Diamant",
                "symbol_type": "diamond",
                "description": "Diamant",
                "pictogram": "♦",
            },
            {
                "name": "Romb",
                "symbol_type": "diamond",
                "description": "Romb",
                "pictogram": "♦",
            },
            # Hjärta
            {
                "name": "Hjärta",
                "symbol_type": "heart",
                "description": "Hjärta",
                "pictogram": "♥",
            },
            # Spader (kortspel)
            {
                "name": "Spader",
                "symbol_type": "other",
                "description": "Spader",
                "pictogram": "♠",
            },
            # Linjer
            {
                "name": "Linje",
                "symbol_type": "other",
                "description": "Linje",
                "pictogram": "━",
            },
            {
                "name": "Sicksackline",
                "symbol_type": "other",
                "description": "Sicksackline",
                "pictogram": "⚡",
            },
            {
                "name": "W-linje",
                "symbol_type": "other",
                "description": "W-linje",
                "pictogram": "〰️",
            },
            {
                "name": "Streckad linje",
                "symbol_type": "other",
                "description": "Streckad linje",
                "pictogram": "┄",
            },
            # Geometriska former
            {
                "name": "Oktagon",
                "symbol_type": "other",
                "description": "Oktagon",
                "pictogram": "⬡",
            },
            {
                "name": "Hexagon",
                "symbol_type": "other",
                "description": "Hexagon",
                "pictogram": "⬡",
            },
            {
                "name": "Pentagon",
                "symbol_type": "other",
                "description": "Pentagon",
                "pictogram": "⬟",
            },
            {
                "name": "Halvcirkel",
                "symbol_type": "other",
                "description": "Halvcirkel",
                "pictogram": "◐",
            },
            {
                "name": "Halvmåne",
                "symbol_type": "other",
                "description": "Halvmåne",
                "pictogram": "☾",
            },
            # Djur
            {
                "name": "Oxe",
                "symbol_type": "other",
                "description": "Oxe",
                "pictogram": "🐂",
            },
            {
                "name": "Bock",
                "symbol_type": "other",
                "description": "Bock",
                "pictogram": "🐐",
            },
            {
                "name": "Tjur",
                "symbol_type": "other",
                "description": "Tjur",
                "pictogram": "🐃",
            },
            {
                "name": "Hästsko",
                "symbol_type": "other",
                "description": "Hästsko",
                "pictogram": "🐎",
            },
            {
                "name": "Bäver",
                "symbol_type": "other",
                "description": "Bäver",
                "pictogram": "🦫",
            },
            {
                "name": "Katt",
                "symbol_type": "other",
                "description": "Katt",
                "pictogram": "🐱",
            },
            {
                "name": "Vädur",
                "symbol_type": "other",
                "description": "Vädur",
                "pictogram": "🐏",
            },
            # Människor
            {
                "name": "Man",
                "symbol_type": "other",
                "description": "Man",
                "pictogram": "👤",
            },
            # Symboler
            {
                "name": "Järnsymbol",
                "symbol_type": "other",
                "description": "Järnsymbol",
                "pictogram": "♂",
            },
        ]

        created_count = 0
        for symbol_data in predefined_symbols:
            symbol, created = StampSymbol.objects.get_or_create(
                name=symbol_data["name"],
                symbol_type=symbol_data["symbol_type"],
                defaults={
                    "description": symbol_data["description"],
                    "pictogram": symbol_data.get("pictogram", ""),
                    "is_predefined": True,
                },
            )
            if created:
                created_count += 1
                if not quiet:
                    self.stdout.write(self.style.SUCCESS(f"Skapade symbol: {symbol}"))

        if not quiet:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Initiering slutförd. {created_count} nya symboler skapade."
                )
            )
