from django.core.management.base import BaseCommand
from axes.models import Transaction


class Command(BaseCommand):
    help = "Rensa alla transaktioner från databasen"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Bekräfta att du vill radera alla transaktioner",
        )

    def handle(self, *args, **options):
        transaction_count = Transaction.objects.count()

        if not options["confirm"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Du är på väg att radera {transaction_count} transaktioner!"
                )
            )
            self.stdout.write("Kör kommandot igen med --confirm för att bekräfta.")
            return

        self.stdout.write(f"Raderar {transaction_count} transaktioner...")

        deleted_count, _ = Transaction.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(f"SUCCESS: Raderade {deleted_count} transaktioner!")
        )
