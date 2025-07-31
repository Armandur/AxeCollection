from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Nollställer hela systemet - databas och bildfiler"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Bekräfta att du vill nollställa hela systemet",
        )
        parser.add_argument(
            "--skip-media",
            action="store_true",
            help="Hoppa över rensning av bildfiler",
        )
        parser.add_argument(
            "--no-images",
            action="store_true",
            help="Generera testdata utan bildfiler",
        )

    def handle(self, *args, **options):
        if not options["confirm"]:
            self.stdout.write(
                self.style.WARNING(
                    "Detta kommando kommer att:\n"
                    "1. Ta bort ALLA data från databasen\n"
                    "2. Ta bort ALLA bildfiler från media-mapparna\n"
                    "3. Generera ny testdata\n"
                    "Använd --confirm för att bekräfta."
                )
            )
            return

        self.stdout.write(self.style.SUCCESS("Startar komplett nollställning..."))

        # Steg 1: Rensa alla bildfiler
        if not options["skip_media"]:
            self.stdout.write("Rensar alla bildfiler...")
            call_command("clear_all_media", confirm=True)
        else:
            self.stdout.write("Hoppar över rensning av bildfiler...")

        # Steg 2: Återställ databasen till testdata
        self.stdout.write("Återställer databasen...")
        if options["no_images"]:
            # Använd generate_test_data direkt med --no-images istället för reset_to_test_data
            call_command("generate_test_data", clear=True, no_images=True)
        else:
            call_command("reset_to_test_data")

        # Steg 3: Generera ny testdata (endast om vi inte redan gjort det i steg 2)
        if not options["no_images"]:
            self.stdout.write("Genererar ny testdata...")
            call_command("generate_test_data")

        # Steg 4: Initiera grundläggande data
        self.stdout.write("Initierar grundläggande data...")
        call_command("init_platforms")
        call_command("init_measurements")
        call_command("init_next_axe_id")

        self.stdout.write(
            self.style.SUCCESS(
                "\n✅ Komplett nollställning slutförd!\n"
                "Systemet har återställts med ny testdata."
            )
        )
