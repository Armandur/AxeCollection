from django.core.management.base import BaseCommand
from axes.utils.ebay_parser import parse_ebay_url


class Command(BaseCommand):
    help = "Testa eBay-parsern med en URL"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="eBay-auktions-URL att testa")

    def handle(self, *args, **options):
        url = options["url"]

        self.stdout.write(f"Testar eBay-parsern med URL: {url}")

        try:
            result = parse_ebay_url(url)

            self.stdout.write(self.style.SUCCESS("✅ Parsning lyckades!"))
            self.stdout.write(f"Titel: {result.get('title', 'N/A')}")
            self.stdout.write(f"Säljare: {result.get('seller_alias', 'N/A')}")
            self.stdout.write(f"Objekt-ID: {result.get('item_id', 'N/A')}")
            self.stdout.write(f"Slutdatum: {result.get('auction_end_date', 'N/A')}")

            prices = result.get("prices", [])
            if prices:
                self.stdout.write("Priser:")
                for price in prices:
                    self.stdout.write(f"  - {price['label']}: {price['amount']}")
            else:
                self.stdout.write("Inga priser hittade")

            images = result.get("images", [])
            if images:
                self.stdout.write(f"Bilder ({len(images)} st):")
                for i, image in enumerate(images[:3]):  # Visa bara första 3
                    self.stdout.write(f"  {i+1}. {image}")
                if len(images) > 3:
                    self.stdout.write(f"  ... och {len(images) - 3} till")
            else:
                self.stdout.write("Inga bilder hittade")

            description = result.get("description", "")
            if description:
                self.stdout.write(
                    f"Beskrivning (första 200 tecken): {description[:200]}..."
                )
            else:
                self.stdout.write("Ingen beskrivning hittad")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Fel vid parsning: {e}"))
