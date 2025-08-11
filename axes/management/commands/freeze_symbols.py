import json
import os
from django.core.management.base import BaseCommand
from django.apps import apps
from axes.models import StampSymbol, SymbolCategory


class Command(BaseCommand):
    help = "Markerar nuvarande stämpelsymboler som fördefinierade och exporterar dem som fixture"

    def add_arguments(self, parser):
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Minska output till endast viktiga meddelanden",
        )

    def handle(self, *args, **options):
        quiet = options.get("quiet", False)

        # 1) Markera alla befintliga symboler som fördefinierade
        symbols = list(StampSymbol.objects.all().order_by("symbol_type", "name"))
        # Säkerställ att standardkategori "Övrigt" finns och sätts
        other_cat, _ = SymbolCategory.objects.get_or_create(
            name="Övrigt", defaults={"description": "Standardkategori"}
        )
        for s in symbols:
            if not s.is_predefined:
                s.is_predefined = True
                # sätt även kategori om saknas
                if s.category_id is None:
                    s.category = other_cat
                    s.save(update_fields=["is_predefined", "category"])
                else:
                    s.save(update_fields=["is_predefined"])
            elif s.category_id is None:
                s.category = other_cat
                s.save(update_fields=["category"])

        if not quiet:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Markerade {len(symbols)} symboler som fördefinierade"
                )
            )

        # 2) Exportera till fixture i appens fixtures-katalog
        app_config = apps.get_app_config("axes")
        fixtures_dir = os.path.join(app_config.path, "fixtures")
        os.makedirs(fixtures_dir, exist_ok=True)
        fixture_path = os.path.join(fixtures_dir, "stamp_symbols.json")

        data = []
        for s in symbols:
            data.append(
                {
                    "model": "axes.stampsymbol",
                    "pk": s.pk,
                    "fields": {
                        "name": s.name,
                        "symbol_type": s.symbol_type,
                        "description": s.description,
                        "pictogram": s.pictogram,
                        "is_predefined": True,
                    },
                }
            )

        with open(fixture_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        if not quiet:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Exporterade {len(data)} symboler till {fixture_path}"
                )
            )
