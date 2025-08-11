from django.core.management.base import BaseCommand
from django.apps import apps
import os
import json
from axes.models import StampSymbol, SymbolCategory


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

        # Om det redan finns symboler i databasen, gör ingenting (men säkerställ kategori "Övrigt")
        if StampSymbol.objects.exists():
            # Skapa/uppdatera standardkategori "Övrigt"
            other_cat, _ = SymbolCategory.objects.get_or_create(
                name="Övrigt", defaults={"description": "Standardkategori"}
            )
            # Sätt kategori för de symboler som saknar
            StampSymbol.objects.filter(category__isnull=True).update(category=other_cat)
            if not quiet:
                self.stdout.write(
                    "Stämpelsymboler finns redan – hoppar över initiering."
                )
            return

        # Försök ladda fixture om den finns
        app_config = apps.get_app_config("axes")
        fixture_path = os.path.join(app_config.path, "fixtures", "stamp_symbols.json")
        if os.path.exists(fixture_path):
            # Läs JSON och skapa via ORM (inte loaddata) så auto_now_add/auto_now sätts korrekt
            try:
                with open(fixture_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                created_count = 0
                updated_count = 0

                # Säkerställ standardkategori "Övrigt"
                other_cat, _ = SymbolCategory.objects.get_or_create(
                    name="Övrigt", defaults={"description": "Standardkategori"}
                )
                for item in data:
                    fields = item.get("fields", {})
                    name = fields.get("name")
                    symbol_type = fields.get("symbol_type") or "other"
                    description = fields.get("description") or None
                    pictogram = fields.get("pictogram") or None
                    is_predefined = (
                        True  # frysd uppsättning betraktas som fördefinierad
                    )

                    if not name:
                        continue

                    # Matcha på namn, symbol_type ignoreras (vi använder kategori nu)
                    existing = (
                        StampSymbol.objects.filter(name__iexact=name)
                        .order_by("id")
                        .first()
                    )
                    if existing:
                        changed = False
                        if existing.description != description:
                            existing.description = description
                            changed = True
                        if existing.pictogram != pictogram:
                            existing.pictogram = pictogram
                            changed = True
                        if existing.is_predefined is not True:
                            existing.is_predefined = True
                            changed = True
                        # Sätt kategori om saknas
                        if existing.category is None:
                            existing.category = other_cat
                            changed = True
                        if changed:
                            existing.save()
                            updated_count += 1
                    else:
                        StampSymbol.objects.create(
                            name=name,
                            symbol_type="other",
                            description=description,
                            pictogram=pictogram,
                            is_predefined=is_predefined,
                            category=other_cat,
                        )
                        created_count += 1

                if not quiet:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Stämpelsymboler initierade från fixture (skapade: {created_count}, uppdaterade: {updated_count})."
                        )
                    )
                return
            except Exception as e:
                if not quiet:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Kunde inte initiera symboler från fixture: {e}"
                        )
                    )
                # Fortsätt vidare till tom initiering nedan

        # Ingen fixture hittades – lämna databasen tom (användaren kan skapa manuellt)
        if not quiet:
            self.stdout.write(
                "Ingen fixture hittades för stämpelsymboler. Ingen initiering utförd."
            )
