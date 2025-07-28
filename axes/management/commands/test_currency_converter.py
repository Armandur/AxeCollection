from django.core.management.base import BaseCommand
from axes.utils.currency_converter import (
    convert_currency,
    get_exchange_rates,
    get_currency_info,
    format_price,
    is_cache_valid,
    clear_cache,
)


class Command(BaseCommand):
    help = "Testa valutakonvertering och live-kurser"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Rensa valutacache innan test",
        )
        parser.add_argument(
            "--amount",
            type=float,
            default=100.0,
            help="Belopp att konvertera (standard: 100)",
        )

    def handle(self, *args, **options):
        amount = options["amount"]

        if options["clear_cache"]:
            self.stdout.write("🧹 Rensar valutacache...")
            clear_cache()
            self.stdout.write(self.style.SUCCESS("✅ Cache rensad"))

        self.stdout.write("🔄 Testar valutakonvertering...")
        self.stdout.write("=" * 50)

        # Testa cache-status
        cache_valid = is_cache_valid()
        self.stdout.write(f"Cache giltig: {'✅' if cache_valid else '❌'}")

        # Hämta valutakurser
        self.stdout.write("\n📊 Hämter valutakurser...")
        try:
            rates = get_exchange_rates()
            self.stdout.write(self.style.SUCCESS("✅ Kurser hämtade"))

            # Visa kurser
            self.stdout.write("\n💱 Aktuella kurser:")
            for from_curr in ["USD", "EUR", "GBP"]:
                if from_curr in rates and "SEK" in rates[from_curr]:
                    rate = rates[from_curr]["SEK"]
                    self.stdout.write(f"  1 {from_curr} = {rate:.2f} SEK")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Fel vid hämtning av kurser: {e}"))

        # Testa konverteringar
        self.stdout.write(f"\n💰 Testar konvertering av {amount}:")
        test_currencies = ["USD", "EUR", "GBP"]

        for currency in test_currencies:
            try:
                converted = convert_currency(amount, currency, "SEK")
                if converted:
                    currency_info = get_currency_info(currency)
                    original_formatted = format_price(amount, currency)
                    sek_formatted = format_price(converted, "SEK")

                    self.stdout.write(
                        f"  {original_formatted} → {sek_formatted} "
                        f"({currency_info['name']})"
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠️ Kunde inte konvertera {currency}")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Fel vid konvertering {currency}: {e}")
                )

        # Testa formatering
        self.stdout.write("\n🎨 Testar prisformatering:")
        for currency in ["USD", "EUR", "GBP", "SEK"]:
            formatted = format_price(amount, currency)
            self.stdout.write(f"  {amount} {currency} = {formatted}")

        # Testa valutainformation
        self.stdout.write("\nℹ️ Valutainformation:")
        for currency in ["USD", "EUR", "GBP", "SEK"]:
            info = get_currency_info(currency)
            self.stdout.write(f"  {currency}: {info['name']} ({info['symbol']})")

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("✅ Valutatest slutfört!"))
