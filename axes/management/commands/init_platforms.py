from django.core.management.base import BaseCommand
from axes.models import Platform


class Command(BaseCommand):
    help = "Skapa standardplattformarna Tradera och eBay"

    def handle(self, *args, **options):
        self.stdout.write("Skapar standardplattformar...")

        # Skapa Tradera-plattform
        tradera_platform, created = Platform.objects.get_or_create(
            name="Tradera",
            defaults={
                "url": "https://www.tradera.com",
                "comment": "Tradera-auktionsplattform",
                "color_class": "bg-primary",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✅ Tradera-plattform skapad"))
        else:
            self.stdout.write("ℹ️ Tradera-plattform fanns redan")

        # Skapa eBay-plattform
        ebay_platform, created = Platform.objects.get_or_create(
            name="eBay",
            defaults={
                "url": "https://www.ebay.com",
                "comment": "eBay-auktionsplattform",
                "color_class": "bg-success",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✅ eBay-plattform skapad"))
        else:
            self.stdout.write("ℹ️ eBay-plattform fanns redan")

        self.stdout.write(self.style.SUCCESS("✅ Standardplattformar initierade!"))
