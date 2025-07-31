from django.core.management.base import BaseCommand
from axes.models import Platform


class Command(BaseCommand):
    help = "Skapa standardplattformarna Tradera och eBay"

    def handle(self, *args, **options):
        self.stdout.write("Skapar standardplattformar...")

        # Rensa befintliga plattformar först
        Platform.objects.filter(name__in=["Tradera", "eBay"]).delete()
        self.stdout.write("Rensade befintliga plattformar...")

        # Skapa Tradera-plattform
        tradera_platform = Platform.objects.create(
            name="Tradera",
            url="https://www.tradera.com",
            comment="Tradera-auktionsplattform",
            color_class="bg-primary",
        )
        self.stdout.write(self.style.SUCCESS("✅ Tradera-plattform skapad"))

        # Skapa eBay-plattform
        ebay_platform = Platform.objects.create(
            name="eBay",
            url="https://www.ebay.com",
            comment="eBay-auktionsplattform",
            color_class="bg-success",
        )
        self.stdout.write(self.style.SUCCESS("✅ eBay-plattform skapad"))

        self.stdout.write(self.style.SUCCESS("✅ Standardplattformar initierade!"))
