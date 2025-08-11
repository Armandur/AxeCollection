from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock
from datetime import datetime
from axes.utils.ebay_parser import EbayParser, parse_ebay_url


class EbayParserTestCase(SimpleTestCase):
    def setUp(self):
        self.parser = EbayParser()

    def test_is_ebay_url_valid(self):
        """Testa att eBay URL-validering fungerar"""
        valid_urls = [
            "https://www.ebay.com/itm/123456789012",
            "https://www.ebay.co.uk/itm/123456789012",
            "https://www.ebay.de/itm/123456789012",
            "https://www.ebay.se/itm/123456789012",
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.parser.is_ebay_url(url))

    def test_is_ebay_url_invalid(self):
        """Testa att ogiltiga URL:er avvisas"""
        invalid_urls = [
            "https://www.tradera.com/item/123",
            "https://www.ebay.com/search?q=axe",
            "https://www.google.com",
            "not-a-url",
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.parser.is_ebay_url(url))

    def test_extract_item_id(self):
        """Testa extrahering av objekt-ID från URL"""
        test_cases = [
            ("https://www.ebay.com/itm/123456789012", "123456789012"),
            ("https://www.ebay.co.uk/itm/987654321098?hash=abc", "987654321098"),
            ("https://www.ebay.de/itm/111222333444", "111222333444"),
        ]

        for url, expected_id in test_cases:
            with self.subTest(url=url):
                self.assertEqual(self.parser.extract_item_id(url), expected_id)

    @patch("axes.utils.ebay_parser.requests.Session")
    def test_parse_ebay_page_success(self, mock_session):
        """Testa lyckad parsning av eBay-sida"""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = """
        <html>
            <head><title>Vintage Axe - eBay</title></head>
            <body>
                <h1>Vintage Gränsfors Bruk Axe</h1>
                <div class="x-item-description__content">
                    <p>Beautiful vintage axe in excellent condition. This is a rare Gränsfors Bruk axe from the 1950s with original handle and perfect blade. The axe shows some signs of use but is in very good condition for its age. Perfect for collectors or practical use.</p>
                </div>
                <span class="mbg-nw">SellerName123</span>
                <div>Sold for $199</div>
            </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None

        # Mock session-instansen
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        # Skapa en ny parser-instans för att använda den mockade sessionen
        parser = EbayParser()
        parser.session = mock_session_instance

        # Testa parsning
        result = parser.parse_ebay_page("https://www.ebay.com/itm/123456789012")

        # Verifiera resultat
        self.assertEqual(result["title"], "Vintage Gränsfors Bruk Axe")
        # Beskrivningen är nu samma som titeln
        self.assertEqual(result["description"], "Vintage Gränsfors Bruk Axe")
        self.assertEqual(result["seller_alias"], "SellerName123")
        self.assertEqual(result["item_id"], "123456789012")
        self.assertEqual(result["url"], "https://www.ebay.com/itm/123456789012")

    @patch("axes.utils.ebay_parser.requests.Session")
    def test_parse_ebay_page_invalid_url(self, mock_session):
        """Testa att ogiltig URL ger fel"""
        with self.assertRaises(ValueError, msg="Ogiltig eBay URL"):
            self.parser.parse_ebay_page("https://www.tradera.com/item/123")

    @patch("axes.utils.ebay_parser.requests.Session")
    def test_parse_ebay_page_request_error(self, mock_session):
        """Testa hantering av nätverksfel"""
        mock_session_instance = MagicMock()
        mock_session_instance.get.side_effect = Exception("Connection error")
        mock_session.return_value = mock_session_instance

        with self.assertRaises(ValueError):
            self.parser.parse_ebay_page("https://www.ebay.com/itm/123456789012")

    def test_extract_prices(self):
        """Testa extrahering av priser"""
        from bs4 import BeautifulSoup

        html = """
        <div>
            <span>Sold for $199</span>
            <span>Shipping $15</span>
            <span>Final price $214</span>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        prices = self.parser._extract_prices(soup)

        # Verifiera att priser extraheras korrekt
        price_labels = [price["label"] for price in prices]
        self.assertIn("Slutpris", price_labels)
        self.assertIn("Frakt", price_labels)

    def test_extract_auction_end_date(self):
        """Testa extrahering av auktionsslutdatum"""
        from bs4 import BeautifulSoup

        html = """
        <div>
            <span>Ended Jan 27, 2025</span>
            <span>Sold for $199 on Jan 27, 2025</span>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        end_date = self.parser._extract_auction_end_date(soup)

        # Verifiera att datum extraheras korrekt
        # Koden använder aktuellt år (2025) för "Jan 27" utan år
        # Men logiken för kring nyår kan göra att det blir 2026 om vi är i augusti
        current_year = datetime.now().year
        current_month = datetime.now().month

        # Om vi är i augusti och datumet är "Jan 27", så blir det 2026
        # beroende på kring nyår-logiken (januari är 7 månader bakåt)
        expected_year = current_year
        if current_month >= 7:  # Juli eller senare
            expected_year = current_year + 1

        self.assertEqual(end_date, f"{expected_year}-01-27")

    def test_parse_ebay_url_function(self):
        """Testa den enkla parse_ebay_url-funktionen"""
        with patch("axes.utils.ebay_parser.EbayParser") as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser.parse_ebay_page.return_value = {"title": "Test Axe"}
            mock_parser_class.return_value = mock_parser

            result = parse_ebay_url("https://www.ebay.com/itm/123")

            mock_parser.parse_ebay_page.assert_called_once_with(
                "https://www.ebay.com/itm/123"
            )
            self.assertEqual(result, {"title": "Test Axe"})

    def test_title_extraction(self):
        """Testa att titel extraheras korrekt"""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <head><title>Vintage Axe - eBay</title></head>
            <body>
                <h1>Vintage Gränsfors Bruk Axe</h1>
                <!-- Ingen beskrivning extraheras längre -->
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        # Testa att titeln extraheras korrekt
        title = self.parser._extract_title(soup)

        # Verifiera att titeln extraheras korrekt
        self.assertEqual(title, "Vintage Gränsfors Bruk Axe")

    def test_extract_images_high_resolution(self):
        """Testa att högre upplösa bilder extraheras"""
        from bs4 import BeautifulSoup

        html = """
        <div>
            <img src="https://i.ebayimg.com/images/g/8SgAAOSwvd1oNfNR/s-l140.jpg" />
            <img src="https://i.ebayimg.com/images/g/5GAAAOSw2YdoNfNQ/s-l500.jpg" />
            <img src="https://i.ebayimg.com/images/g/YrQAAOSwt11oNfNQ/s-m.jpg" />
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        images = self.parser._extract_images(soup)

        # Verifiera att alla bilder har högre upplösning
        for image in images:
            # Kontrollera att bilderna har rätt format
            self.assertIn("i.ebayimg.com", image)
            self.assertIn(".jpg", image)
            # Kontrollera att de inte har de gamla formaten
            self.assertNotIn("/s-l140", image)
            self.assertNotIn("/s-l500", image)

    def test_extract_images_no_duplicates(self):
        """Testa att inga duplicerade bilder returneras"""
        from bs4 import BeautifulSoup

        html = """
        <div>
            <img src="https://i.ebayimg.com/images/g/8SgAAOSwvd1oNfNR/s-l140.jpg" />
            <img src="https://i.ebayimg.com/images/g/8SgAAOSwvd1oNfNR/s-l140.webp" />
            <img src="https://i.ebayimg.com/images/g/8SgAAOSwvd1oNfNR/s-l500.jpg" />
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        images = self.parser._extract_images(soup)

        # Verifiera att bara en bild returneras (ingen duplicering)
        self.assertEqual(len(images), 1)
        self.assertIn(".jpg", images[0])
        self.assertNotIn(".webp", images[0])

    def test_parse_ebay_page_with_title_as_description(self):
        """Testa att parsning använder titeln som beskrivning"""
        with patch("axes.utils.ebay_parser.requests.Session") as mock_session:
            # Mock response
            mock_response = MagicMock()
            mock_response.content = """
            <html>
                <head><title>Vintage Axe - eBay</title></head>
                <body>
                    <h1>Vintage Gränsfors Bruk Axe</h1>
                    <span class="mbg-nw">SellerName123</span>
                    <div>Sold for $199</div>
                </body>
            </html>
            """
            mock_response.raise_for_status.return_value = None

            mock_session_instance = MagicMock()
            mock_session_instance.get.return_value = mock_response
            mock_session.return_value = mock_session_instance

            parser = EbayParser()
            parser.session = mock_session_instance

            result = parser.parse_ebay_page("https://www.ebay.com/itm/123456789012")

            # Verifiera att titeln används som beskrivning
            self.assertEqual(result["description"], "Vintage Gränsfors Bruk Axe")
            self.assertEqual(result["title"], "Vintage Gränsfors Bruk Axe")
