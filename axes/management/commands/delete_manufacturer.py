import os
import shutil
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from axes.models import Manufacturer


class Command(BaseCommand):
    help = "Ta bort tillverkare och hantera deras bilder och yxor"

    def add_arguments(self, parser):
        parser.add_argument(
            "manufacturer_id",
            type=int,
            help="ID för tillverkaren som ska tas bort",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Tvinga borttagning utan bekräftelse",
        )
        parser.add_argument(
            "--move-axes-to-unknown",
            action="store_true",
            help='Flytta yxor till "Okänd tillverkare" istället för att förhindra borttagning',
        )
        parser.add_argument(
            "--move-axes-to",
            type=int,
            help="ID för tillverkare att flytta yxor till",
        )
        parser.add_argument(
            "--delete-axes",
            action="store_true",
            help="Ta bort alla yxor som tillhör tillverkaren (VARNING: Detta raderar all data!)",
        )

    def handle(self, *args, **options):
        manufacturer_id = options["manufacturer_id"]

        try:
            manufacturer = Manufacturer.objects.get(id=manufacturer_id)
        except Manufacturer.DoesNotExist:
            raise CommandError(f"Tillverkare med ID {manufacturer_id} finns inte")

        axe_count = manufacturer.axe_count
        image_count = manufacturer.images.count()

        self.stdout.write(f"Tillverkare: {manufacturer.name}")
        self.stdout.write(f"Antal yxor: {axe_count}")
        self.stdout.write(f"Antal bilder: {image_count}")

        if (
            axe_count > 0
            and not options["move_axes_to_unknown"]
            and not options["delete_axes"]
            and not options["move_axes_to"]
        ):
            self.stdout.write(
                self.style.ERROR(
                    f"Kan inte ta bort tillverkare med {axe_count} yxor. "
                    'Använd --move-axes-to-unknown för att flytta yxor till "Okänd tillverkare", '
                    "--move-axes-to <id> för att flytta till specifik tillverkare, "
                    "eller --delete-axes för att ta bort alla yxor (VARNING: raderar all data!)"
                )
            )
            return

        if not options["force"]:
            if axe_count > 0:
                if options["delete_axes"]:
                    confirm = input(
                        f"Är du säker på att du vill ta bort tillverkaren och alla {axe_count} yxor? (ja/nej): "
                    )
                elif options["move_axes_to"]:
                    try:
                        target_manufacturer = Manufacturer.objects.get(
                            id=options["move_axes_to"]
                        )
                        confirm = input(
                            f'Är du säker på att du vill flytta {axe_count} yxor till "{target_manufacturer.name}"? (ja/nej): '
                        )
                    except Manufacturer.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(
                                f'Tillverkare med ID {options["move_axes_to"]} finns inte'
                            )
                        )
                        return
                else:
                    confirm = input(
                        f'Är du säker på att du vill flytta {axe_count} yxor till "Okänd tillverkare"? (ja/nej): '
                    )
            else:
                confirm = input(
                    "Är du säker på att du vill ta bort tillverkaren? (ja/nej): "
                )

            if confirm.lower() not in ["ja", "yes", "y"]:
                self.stdout.write("Borttagning avbruten")
                return

        # Hantera yxor
        if axe_count > 0:
            if options["delete_axes"]:
                # Ta bort alla yxor (och deras bilder flyttas automatiskt till unlinked_images)
                self.stdout.write(f"Raderar {axe_count} yxor...")
                for axe in manufacturer.axes:
                    axe.delete()
                self.stdout.write(self.style.SUCCESS(f"Raderade {axe_count} yxor"))
            elif options["move_axes_to"]:
                # Flytta yxor till specifik tillverkare
                target_manufacturer = Manufacturer.objects.get(
                    id=options["move_axes_to"]
                )
                self.stdout.write(
                    f'Flyttar {axe_count} yxor till "{target_manufacturer.name}"...'
                )
                manufacturer.axe_set.update(manufacturer=target_manufacturer)
                self.stdout.write(self.style.SUCCESS(f"Flyttade {axe_count} yxor"))
            else:
                # Flytta yxor till "Okänd tillverkare"
                unknown_manufacturer, created = Manufacturer.objects.get_or_create(
                    name="Okänd tillverkare"
                )
                self.stdout.write(
                    f'Flyttar {axe_count} yxor till "{unknown_manufacturer.name}"...'
                )
                manufacturer.axe_set.update(manufacturer=unknown_manufacturer)
                self.stdout.write(self.style.SUCCESS(f"Flyttade {axe_count} yxor"))

        # Hantera tillverkarbilder
        if image_count > 0:
            self.move_manufacturer_images_to_unlinked(manufacturer)

        # Ta bort tillverkaren
        manufacturer_name = manufacturer.name
        manufacturer.delete()

        self.stdout.write(
            self.style.SUCCESS(f'Tillverkare "{manufacturer_name}" har tagits bort')
        )

    def move_manufacturer_images_to_unlinked(self, manufacturer):
        """Flyttar tillverkarbilder till unlinked_images-mappen med tillverkarnamn"""
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")

        # Skapa mapp för okopplade tillverkarbilder
        unlinked_folder = os.path.join(
            settings.MEDIA_ROOT, "unlinked_images", "manufacturers"
        )
        os.makedirs(unlinked_folder, exist_ok=True)

        moved_count = 0
        error_count = 0

        # Skapa ett säkert filnamn från tillverkarnamnet
        safe_manufacturer_name = "".join(
            c for c in manufacturer.name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_manufacturer_name = safe_manufacturer_name.replace(" ", "_")

        # Sortera bilder efter typ och ordning
        sorted_images = manufacturer.images.order_by("image_type", "order")

        for index, manufacturer_image in enumerate(sorted_images):
            try:
                if manufacturer_image.image and manufacturer_image.image.name:
                    # Bestäm filnamn (a, b, c, etc.)
                    letter = chr(97 + index)  # 97 = 'a' i ASCII

                    # Hämta filändelse från originalfilen
                    original_ext = os.path.splitext(manufacturer_image.image.name)[1]
                    new_filename = f"{safe_manufacturer_name}-{manufacturer.id}-{timestamp}-{letter}{original_ext}"
                    new_path = os.path.join(unlinked_folder, new_filename)

                    # Kopiera filen
                    if os.path.exists(manufacturer_image.image.path):
                        shutil.copy2(manufacturer_image.image.path, new_path)

                        # Kopiera även .webp-filen om den finns
                        webp_path = (
                            os.path.splitext(manufacturer_image.image.path)[0] + ".webp"
                        )
                        if os.path.exists(webp_path):
                            webp_new_path = os.path.join(
                                unlinked_folder,
                                f"{safe_manufacturer_name}-{manufacturer.id}-{timestamp}-{letter}.webp",
                            )
                            shutil.copy2(webp_path, webp_new_path)

                        moved_count += 1

                    # Ta bort originalbilden från databasen och filsystemet
                    manufacturer_image.delete()

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    f"Fel vid flytt av bild {manufacturer_image.image.name}: {e}"
                )

        if moved_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Flyttade {moved_count} tillverkarbilder till okopplade bilder"
                )
            )

        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(f"{error_count} bilder kunde inte flyttas")
            )
