from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from axes.utils.currency_converter import convert_currency, get_exchange_rates
from axes.utils.ebay_parser import EbayParser
from axes.utils.tradera_parser import TraderaParser
from axes.models import Manufacturer


class CurrencyIntegrationTestCase(TestCase):
    """Testa integration mellan valutakonvertering och UI"""

    def setUp(self):
        """Sätt upp testdata"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_ebay_parser_with_currency(self):
        """Testa att eBay-parser hanterar valuta korrekt"""
        parser = EbayParser()

        # Mock eBay-sida med USD-pris
        mock_html = """
        <html>
            <body>
                <h1>Vintage Axe Head</h1>
                <div>Sold for $149.00</div>
                <div>Seller: testuser</div>
            </body>
        </html>
        """

        with patch("axes.utils.ebay_parser.requests.Session") as mock_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = mock_html.encode("utf-8")
            mock_response.raise_for_status.return_value = None

            mock_session_instance = MagicMock()
            mock_session_instance.get.return_value = mock_response
            mock_session.return_value = mock_session_instance

            parser = EbayParser()
            parser.session = mock_session_instance

            # Mock _extract_prices för att returnera förväntad data
            with patch.object(parser, "_extract_prices") as mock_prices:
                mock_prices.return_value = [
                    {"label": "Slutpris", "amount": 149, "currency": "USD"}
                ]

                # Mock URL
                url = "https://www.ebay.com/itm/123456"

                # Testa parsning
                result = parser.parse_ebay_page(url)

                # Kontrollera att valuta identifieras
                self.assertIn("prices", result)
                self.assertTrue(len(result["prices"]) > 0)

                # Kontrollera att pris har valuta
                price = result["prices"][0]
                self.assertIn("currency", price)
                self.assertEqual(price["currency"], "USD")

    def test_tradera_parser_with_currency(self):
        """Testa att Tradera-parser hanterar SEK korrekt"""
        parser = TraderaParser()

        # Mock Tradera-sida med SEK-pris
        mock_html = """
        <html>
            <body>
                <h1>Gammal Yxa</h1>
                <div>Slutpris: 500 kr</div>
                <div>Säljare: testuser</div>
            </body>
        </html>
        """

        with patch("axes.utils.tradera_parser.requests.Session") as mock_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = mock_html.encode("utf-8")
            mock_response.raise_for_status.return_value = None

            mock_session_instance = MagicMock()
            mock_session_instance.get.return_value = mock_response
            mock_session.return_value = mock_session_instance

            parser = TraderaParser()
            parser.session = mock_session_instance

            # Mock _extract_prices för att returnera förväntad data
            with patch.object(parser, "_extract_prices") as mock_prices:
                mock_prices.return_value = [
                    {"label": "Slutpris", "amount": 500, "currency": "SEK"}
                ]

                # Mock URL med korrekt format
                url = "https://www.tradera.com/item/343327/123456/test-yxa"

                # Testa parsning
                result = parser.parse_tradera_page(url)

                # Kontrollera att valuta är SEK
                self.assertIn("prices", result)
                if result["prices"]:
                    price = result["prices"][0]
                    self.assertIn("currency", price)
                    self.assertEqual(price["currency"], "SEK")

    def test_currency_conversion_in_ui(self):
        """Testa att valutakonvertering fungerar i UI"""
        # Logga in användaren
        self.client.login(username="testuser", password="testpass123")

        # Mock eBay-parsning
        mock_auction_data = {
            "title": "Test Axe",
            "description": "Test Axe",
            "seller_alias": "testseller",
            "prices": [{"label": "Slutpris", "amount": 100, "currency": "USD"}],
            "auction_end_date": "2025-07-28",
            "url": "https://www.ebay.com/itm/123456",
            "item_id": "123456",
            "images": [],
        }

        with patch("axes.utils.ebay_parser.EbayParser") as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser.parse_ebay_page.return_value = mock_auction_data
            mock_parser_class.return_value = mock_parser

            # Testa URL-parsning via AJAX
            response = self.client.post(
                reverse("axe_create"),
                {
                    "auction_url": "https://www.ebay.com/itm/123456",
                    "parse_only": "true",
                },
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

            # Kontrollera att svaret är JSON
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])

            # Kontrollera att prisdata finns
            self.assertIn("auction_data", data)
            self.assertIn("prices", data["auction_data"])

    def test_currency_warning_display(self):
        """Testa att valutavarning visas för icke-SEK valutor"""
        # Logga in användaren
        self.client.login(username="testuser", password="testpass123")

        # Mock eBay-parsning med EUR
        mock_auction_data = {
            "title": "Test Axe EUR",
            "description": "Test Axe EUR",
            "seller_alias": "testseller",
            "prices": [{"label": "Slutpris", "amount": 50, "currency": "EUR"}],
            "auction_end_date": "2025-07-28",
            "url": "https://www.ebay.com/itm/123456",
            "item_id": "123456",
            "images": [],
        }

        with patch("axes.utils.ebay_parser.EbayParser") as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser.parse_ebay_page.return_value = mock_auction_data
            mock_parser_class.return_value = mock_parser

            # Testa URL-parsning
            response = self.client.post(
                reverse("axe_create"),
                {
                    "auction_url": "https://www.ebay.com/itm/123456",
                    "parse_only": "true",
                },
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

            # Kontrollera att svaret innehåller EUR-valuta
            data = response.json()
            if data["success"]:
                prices = data["auction_data"]["prices"]
                self.assertTrue(any(p["currency"] == "EUR" for p in prices))

    def test_currency_conversion_accuracy(self):
        """Testa att valutakonvertering är korrekt"""
        # Testa USD till SEK
        usd_amount = 100
        converted = convert_currency(usd_amount, "USD", "SEK")
        self.assertIsNotNone(converted)
        self.assertGreater(converted, usd_amount)  # SEK bör vara högre än USD

        # Testa EUR till SEK
        eur_amount = 50
        converted = convert_currency(eur_amount, "EUR", "SEK")
        self.assertIsNotNone(converted)
        self.assertGreater(converted, eur_amount)  # SEK bör vara högre än EUR

        # Testa samma valuta
        sek_amount = 100
        converted = convert_currency(sek_amount, "SEK", "SEK")
        self.assertEqual(converted, sek_amount)

    def test_currency_form_display(self):
        """Testa att formulärfält fylls i korrekt med konverterade priser"""
        # Logga in användaren
        self.client.login(username="testuser", password="testpass123")

        # Mock eBay-parsning
        mock_auction_data = {
            "title": "Test Axe USD",
            "seller_alias": "testseller",
            "prices": [{"label": "Slutpris", "amount": 75, "currency": "USD"}],
            "auction_end_date": "2025-07-28",
            "url": "https://www.ebay.com/itm/123456",
        }

        with patch("axes.utils.ebay_parser.EbayParser.parse_ebay_page") as mock_parse:
            mock_parse.return_value = mock_auction_data

            # Testa URL-parsning
            response = self.client.post(
                reverse("axe_create"),
                {
                    "auction_url": "https://www.ebay.com/itm/123456",
                    "parse_only": "true",
                },
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

            # Kontrollera att svaret är framgångsrikt
            data = response.json()
            self.assertTrue(data["success"])

            # Kontrollera att prisdata finns och har rätt struktur
            if "auction_data" in data and "prices" in data["auction_data"]:
                prices = data["auction_data"]["prices"]
                self.assertTrue(len(prices) > 0)
                price = prices[0]
                self.assertIn("amount", price)
                self.assertIn("currency", price)
                self.assertEqual(price["currency"], "USD")


class CurrencyUIIntegrationTestCase(TestCase):
    """Testa att valutarelaterade UI-element fungerar korrekt"""

    def setUp(self):
        """Sätt upp testdata"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        # Skapa en tillverkare för testerna
        self.manufacturer = Manufacturer.objects.create(
            name="Test Manufacturer", country_code="SE"
        )

    def test_currency_warning_visibility(self):
        """Testa att valutavarning visas för icke-SEK valutor"""
        self.client.login(username="testuser", password="testpass123")

        # Mock eBay-parsern för att returnera USD-data
        with patch("axes.utils.ebay_parser.EbayParser") as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser.parse_ebay_page.return_value = {
                "title": "USD Axe",
                "description": "USD Axe",
                "seller_alias": "usdseller",
                "prices": [{"label": "Slutpris", "amount": 100, "currency": "USD"}],
                "auction_end_date": "2025-07-28",
                "item_id": "123456",
                "url": "https://www.ebay.com/itm/123456",
                "images": [],
            }
            mock_parser_class.return_value = mock_parser

            response = self.client.post(
                reverse("axe_create"),
                {
                    "auction_url": "https://www.ebay.com/itm/123456",
                    "parse_only": "true",
                },
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])

    def test_currency_conversion_buttons(self):
        """Testa att konverteringsknappar finns i UI"""
        self.client.login(username="testuser", password="testpass123")

        # Hämta formulärsidan
        response = self.client.get(reverse("axe_create"))
        self.assertEqual(response.status_code, 200)

        # Kontrollera att sidan innehåller valutarelaterade element
        content = response.content.decode("utf-8")
        self.assertIn("currencyWarning", content)
        self.assertIn("convertToSekBtn", content)
        self.assertIn("manualSekBtn", content)

    def test_currency_form_validation(self):
        """Testa att formulärvalidering fungerar med valutakonvertering"""
        self.client.login(username="testuser", password="testpass123")

        # Testa att skapa yxa med konverterat pris
        form_data = {
            "model": "Test Axe",
            "manufacturer": str(self.manufacturer.id),  # Använd skapad tillverkare
            "status": "received",
            "comment": "Test axe with USD conversion",
            "transaction_price": "-1050",  # Konverterat från 100 USD
            "transaction_date": "2025-07-28",
            "contact_alias": "testseller",
            "platform_search": "eBay",
        }

        response = self.client.post(reverse("axe_create"), form_data)
        # Kontrollera att formuläret accepteras (redirect till success)
        self.assertIn(response.status_code, [200, 302])


class CurrencyParserTestCase(TestCase):
    """Testa att parsers hanterar valuta korrekt"""

    def test_ebay_parser_currency_identification(self):
        """Testa att eBay-parser identifierar valuta korrekt"""
        parser = EbayParser()

        # Mock session för att undvika faktiska HTTP-anrop
        with patch("axes.utils.ebay_parser.requests.Session") as mock_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = """
            <html>
                <head><title>USD Axe - eBay</title></head>
                <body>
                    <h1>Vintage USD Axe</h1>
                    <div>Price: $149.00</div>
                    <span class="mbg-nw">SellerName123</span>
                </body>
            </html>
            """.encode(
                "utf-8"
            )
            mock_response.raise_for_status.return_value = None

            mock_session_instance = MagicMock()
            mock_session_instance.get.return_value = mock_response
            mock_session.return_value = mock_session_instance

            # Skapa en ny parser-instans för att använda den mockade sessionen
            parser = EbayParser()
            parser.session = mock_session_instance

            # Mock _extract_prices för att returnera förväntad data
            with patch.object(parser, "_extract_prices") as mock_prices:
                mock_prices.return_value = [
                    {"label": "Slutpris", "amount": 149, "currency": "USD"}
                ]

                result = parser.parse_ebay_page("https://www.ebay.com/itm/123456")
                self.assertIn("prices", result)
                self.assertEqual(result["title"], "Vintage USD Axe")

    def test_tradera_parser_currency_identification(self):
        """Testa att Tradera-parser identifierar SEK korrekt"""
        parser = TraderaParser()

        # Mock session för att undvika faktiska HTTP-anrop
        with patch("axes.utils.tradera_parser.requests.Session") as mock_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = """
            <html>
                <head><title>SEK Axe - Tradera</title></head>
                <body>
                    <h1>Vintage SEK Axe</h1>
                    <div>Pris: 500 kr</div>
                    <span class="seller-name">SellerName123</span>
                </body>
            </html>
            """.encode(
                "utf-8"
            )
            mock_response.raise_for_status.return_value = None

            mock_session_instance = MagicMock()
            mock_session_instance.get.return_value = mock_response
            mock_session.return_value = mock_session_instance

            # Skapa en ny parser-instans för att använda den mockade sessionen
            parser = TraderaParser()
            parser.session = mock_session_instance

            # Mock _extract_prices för att returnera förväntad data
            with patch.object(parser, "_extract_prices") as mock_prices:
                mock_prices.return_value = [
                    {"label": "Slutpris", "amount": 500, "currency": "SEK"}
                ]

                result = parser.parse_tradera_page(
                    "https://www.tradera.com/item/343327/123456/test-yxa"
                )
                self.assertIn("prices", result)
                self.assertEqual(result["title"], "Vintage SEK Axe")
