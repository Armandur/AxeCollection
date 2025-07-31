from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil


class Command(BaseCommand):
    help = "Rensar alla bildfiler från media-mapparna"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Bekräfta att du vill ta bort alla bildfiler",
        )

    def handle(self, *args, **options):
        if not options["confirm"]:
            self.stdout.write(
                self.style.WARNING(
                    "Detta kommando kommer att ta bort ALLA bildfiler från media-mapparna!\n"
                    "Använd --confirm för att bekräfta."
                )
            )
            return

        media_root = settings.MEDIA_ROOT
        media_dirs = [
            "axe_images",
            "manufacturer_images",
            "stamps",
            "unlinked_images",
            "stamp_images",
        ]

        total_removed = 0

        for dir_name in media_dirs:
            dir_path = os.path.join(media_root, dir_name)
            if os.path.exists(dir_path):
                try:
                    # Räkna filer innan borttagning
                    file_count = 0
                    for root, dirs, files in os.walk(dir_path):
                        file_count += len(files)

                    # Ta bort hela mappen och skapa den igen
                    shutil.rmtree(dir_path)
                    os.makedirs(dir_path, exist_ok=True)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Rensade {dir_name}/: {file_count} filer borttagna"
                        )
                    )
                    total_removed += file_count

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Fel vid rensning av {dir_name}/: {e}")
                    )
            else:
                self.stdout.write(self.style.WARNING(f"Mappen {dir_name}/ finns inte"))

        self.stdout.write(
            self.style.SUCCESS(f"\nTotalt borttagna filer: {total_removed}")
        )
