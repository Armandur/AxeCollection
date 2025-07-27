from django.core.management.base import BaseCommand
from axes.models import Axe


class Command(BaseCommand):
    help = "Sätt status till MOTTAGEN för alla yxor i databasen."

    def handle(self, *args, **options):
        updated = Axe.objects.all().update(status="MOTTAGEN")
        self.stdout.write(
            self.style.SUCCESS(f"Satte status till MOTTAGEN för {updated} yxor.")
        )
