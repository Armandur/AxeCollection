from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock
from axes.utils.ebay_parser import EbayParser
from axes.utils.tradera_parser import TraderaParser
from axes.utils.currency_converter import (
    convert_currency,
    get_currency_info,
    format_price,
    get_conversion_warning,
    get_exchange_rates,
    get_conversion_rate,
    is_cache_valid,
    clear_cache,
)


class CurrencyConverterTestCase(SimpleTestCase):
    """Testa valutakonvertering och formatering"""

    def test_convert_currency_usd_to_sek(self):
        """Testa konvertering från USD till SEK"""
        result = convert_currency(100, "USD", "SEK")
        self.assertIsNotNone(result)
        # Kontrollera att resultatet är rimligt (mellan 800-1200 SEK för 100 USD)
        self.assertTrue(800 <= result <= 1200)

    def test_convert_currency_eur_to_sek(self):
        """Testa konvertering från EUR till SEK"""
        result = convert_currency(100, "EUR", "SEK")
        self.assertIsNotNone(result)
        # Kontrollera att resultatet är rimligt (mellan 1000-1400 SEK för 100 EUR)
        self.assertTrue(1000 <= result <= 1400)

    def test_convert_currency_same_currency(self):
        """Testa konvertering mellan samma valuta"""
        result = convert_currency(100, "SEK", "SEK")
        self.assertEqual(result, 100)

    def test_get_currency_info(self):
        """Testa hämtning av valuta-information"""
        usd_info = get_currency_info("USD")
        self.assertEqual(usd_info["symbol"], "$")
        self.assertEqual(usd_info["name"], "US Dollar")

        sek_info = get_currency_info("SEK")
        self.assertEqual(sek_info["symbol"], "kr")
        self.assertEqual(sek_info["name"], "Swedish Krona")

    def test_format_price(self):
        """Testa formatering av priser"""
        usd_price = format_price(199.99, "USD")
        self.assertEqual(usd_price, "$199.99")

        sek_price = format_price(199, "SEK")
        self.assertEqual(sek_price, "199 kr")

    def test_get_conversion_warning(self):
        """Testa varningsmeddelanden för valutakonvertering"""
        warning = get_conversion_warning("USD", "SEK")
        self.assertIn("USD", warning)
        self.assertIn("SEK", warning)
        self.assertIn("US Dollar", warning)
        self.assertIn("Swedish Krona", warning)

        # Ingen varning för samma valuta
        no_warning = get_conversion_warning("SEK", "SEK")
        self.assertEqual(no_warning, "")

    def test_get_exchange_rates(self):
        """Testa hämtning av valutakurser"""
        rates = get_exchange_rates()
        self.assertIsInstance(rates, dict)
        # Kontrollera att vi har kurser för de viktigaste valutorna
        self.assertTrue(len(rates) > 0)

    def test_get_conversion_rate(self):
        """Testa hämtning av konverteringskurs"""
        # Testa samma valuta
        rate = get_conversion_rate("SEK", "SEK")
        self.assertEqual(rate, 1.0)

        # Testa olika valutor
        rate = get_conversion_rate("USD", "SEK")
        if rate:
            self.assertIsInstance(rate, float)
            self.assertTrue(rate > 0)

    def test_cache_functions(self):
        """Testa cache-funktioner"""
        # Testa cache-status (kan vara True eller False beroende på om cache finns)
        cache_valid = is_cache_valid()
        self.assertIsInstance(cache_valid, bool)

        # Testa cache-rensning (ska inte krascha)
        try:
            clear_cache()
        except Exception as e:
            self.fail(f"clear_cache() kraschade: {e}")


class EbayParserCurrencyTestCase(SimpleTestCase):
    """Testa eBay-parsern med olika valutor"""

    def setUp(self):
        self.parser = EbayParser()

    def test_identify_currency_usd(self):
        """Testa identifiering av USD"""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <head>
                <meta property="og:url" content="https://www.ebay.com/itm/123" />
            </head>
            <body>
                <span>Sold for $199</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        currency = self.parser._identify_currency(soup)
        self.assertEqual(currency, "USD")

    def test_identify_currency_eur(self):
        """Testa identifiering av EUR"""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <head>
                <meta property="og:url" content="https://www.ebay.de/itm/123" />
            </head>
            <body>
                <span>Sold for €150</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        currency = self.parser._identify_currency(soup)
        self.assertEqual(currency, "EUR")

    def test_extract_prices_with_currency(self):
        """Testa extrahering av priser med valuta"""
        from bs4 import BeautifulSoup

        html = """
        <div>
            <span>Sold for $199</span>
            <span>Shipping $15</span>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        prices = self.parser._extract_prices(soup)

        # Kontrollera att priser har valuta-information
        for price in prices:
            self.assertIn("currency", price)
            self.assertIn("original_amount", price)
            self.assertIn("original_currency", price)
            self.assertEqual(price["currency"], "USD")


class TraderaParserCurrencyTestCase(SimpleTestCase):
    """Testa Tradera-parsern med SEK"""

    def setUp(self):
        self.parser = TraderaParser()

    def test_extract_prices_with_sek(self):
        """Testa extrahering av priser med SEK"""
        from bs4 import BeautifulSoup

        html = """
        <div>
            <span>Slutpris 199 kr</span>
            <span>med köparskydd 210 kr</span>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        prices = self.parser._extract_prices(soup)

        # Kontrollera att priser har SEK som valuta
        for price in prices:
            self.assertIn("currency", price)
            self.assertEqual(price["currency"], "SEK")
            self.assertIn("original_amount", price)
            self.assertIn("original_currency", price)


class CurrencyIntegrationTestCase(SimpleTestCase):
    """Testa integration mellan parsers och valutakonvertering"""

    def test_ebay_parser_with_conversion(self):
        """Testa eBay-parser med valutakonvertering"""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <head>
                <meta property="og:url" content="https://www.ebay.com/itm/123" />
            </head>
            <body>
                <span>Sold for $199</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        # Testa parser
        parser = EbayParser()
        prices = parser._extract_prices(soup)

        # Kontrollera att vi får USD-priser
        usd_prices = [p for p in prices if p.get("currency") == "USD"]
        self.assertTrue(len(usd_prices) > 0)

        # Testa konvertering av det första priset
        if usd_prices:
            price = usd_prices[0]
            converted = convert_currency(price["amount"], "USD", "SEK")
            self.assertIsNotNone(converted)
            self.assertTrue(converted > price["amount"])  # SEK bör vara högre än USD

    def test_tradera_parser_no_conversion_needed(self):
        """Testa Tradera-parser (ingen konvertering behövs)"""
        from bs4 import BeautifulSoup

        html = """
        <div>
            <span>Slutpris 199 kr</span>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        parser = TraderaParser()
        prices = parser._extract_prices(soup)

        # Kontrollera att vi får SEK-priser
        sek_prices = [p for p in prices if p.get("currency") == "SEK"]
        self.assertTrue(len(sek_prices) > 0)

        # Ingen konvertering behövs för SEK
        if sek_prices:
            price = sek_prices[0]
            converted = convert_currency(price["amount"], "SEK", "SEK")
            self.assertEqual(converted, price["amount"])
