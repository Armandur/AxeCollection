import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from axes.utils.tradera_parser import TraderaParser, parse_tradera_url
from bs4 import BeautifulSoup


class TraderaParserTest(TestCase):
    """Tester för TraderaParser"""

    def setUp(self):
        """Skapa parser-instans"""
        self.parser = TraderaParser()

    def test_is_tradera_url_valid(self):
        """Testa giltiga Tradera URLs"""
        valid_urls = [
            "https://www.tradera.com/item/343327/683953821/yxa-saw-stamplat-ph-",
            "https://www.tradera.com/item/123/456/test-item",
            "http://www.tradera.com/item/789/012/another-item",
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.parser.is_tradera_url(url))

    def test_is_tradera_url_invalid(self):
        """Testa ogiltiga Tradera URLs"""
        invalid_urls = [
            "https://www.tradera.com/",
            "https://www.tradera.com/search",
            "https://www.google.com/item/123/456/test",
            "not-a-url",
            "",
            None,
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.parser.is_tradera_url(url))

    def test_extract_item_id(self):
        """Testa extrahering av objekt-ID från URL"""
        test_cases = [
            (
                "https://www.tradera.com/item/343327/683953821/yxa-saw-stamplat-ph-",
                "683953821",
            ),
            ("https://www.tradera.com/item/123/456/test-item", "456"),
            ("https://www.tradera.com/item/789/012/another-item", "012"),
        ]

        for url, expected_id in test_cases:
            with self.subTest(url=url):
                item_id = self.parser.extract_item_id(url)
                self.assertEqual(item_id, expected_id)

    def test_extract_item_id_invalid(self):
        """Testa extrahering av objekt-ID från ogiltiga URLs"""
        invalid_urls = [
            "https://www.tradera.com/",
            "https://www.tradera.com/item/123",
            "not-a-url",
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                item_id = self.parser.extract_item_id(url)
                self.assertIsNone(item_id)

    def test_parse_tradera_page_success(self):
        """Testa lyckad parsning av Tradera-sida"""
        # Mock response med mer realistisk HTML
        mock_response = Mock()
        mock_response.content = """
        <html>
            <head><title>Test Auction</title></head>
            <body>
                <h1>Test Auction Title</h1>
                <div class="seller">Test Seller</div>
                <div class="price">500 kr</div>
                <img src="https://img.tradera.net/902/607442902_small-square.jpg">
                <img src="https://img.tradera.net/902/607442902_medium-fit.jpg">
            </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None

        # Mock session direkt på instansen
        with patch.object(self.parser, "session") as mock_session:
            mock_session.get.return_value = mock_response

            # Testa parsning
            result = self.parser.parse_tradera_page(
                "https://www.tradera.com/item/123/456/test"
            )

            # Kontrollera resultat
            self.assertIn("title", result)
            self.assertIn("description", result)
            self.assertIn("seller_alias", result)
            self.assertIn("prices", result)
            self.assertIn("item_id", result)
            self.assertIn("images", result)
            self.assertIn("auction_end_date", result)
            self.assertIn("url", result)

            self.assertEqual(result["item_id"], "456")
            self.assertEqual(result["url"], "https://www.tradera.com/item/123/456/test")

    def test_parse_tradera_page_invalid_url(self):
        """Testa parsning med ogiltig URL"""
        with self.assertRaises(ValueError):
            self.parser.parse_tradera_page("https://www.google.com")

    def test_parse_tradera_page_request_error(self):
        """Testa parsning med nätverksfel"""
        # Mock session direkt på instansen
        with patch.object(self.parser, "session") as mock_session:
            mock_session.get.side_effect = Exception("Network error")

            with self.assertRaises(ValueError):
                self.parser.parse_tradera_page(
                    "https://www.tradera.com/item/123/456/test"
                )

    def test_extract_title(self):
        """Testa extrahering av titel från HTML"""
        html = """
        <html>
            <head><title>Test Auction Title</title></head>
            <body>
                <h1>Main Title</h1>
                <h2>Subtitle</h2>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        title = self.parser._extract_title(soup)
        self.assertIsInstance(title, str)
        self.assertGreater(len(title), 0)

    def test_extract_seller_alias(self):
        """Testa extrahering av säljare från HTML"""
        html = """
        <html>
            <body>
                <div class="seller">Test Seller</div>
                <span class="seller-name">Another Seller</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        seller = self.parser._extract_seller_alias(soup)
        self.assertIsInstance(seller, str)

    def test_extract_prices(self):
        """Testa extrahering av priser från HTML"""
        html = """
        <html>
            <body>
                <div class="price">500 kr</div>
                <span class="current-price">750 SEK</span>
                <div class="bid">1000</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        prices = self.parser._extract_prices(soup)
        self.assertIsInstance(prices, list)

    def test_extract_images(self):
        """Testa extrahering av bilder från HTML"""
        html = """
        <html>
            <body>
                <img src="https://img.tradera.net/902/607442902_small-square.jpg">
                <img src="https://img.tradera.net/902/607442902_medium-fit.jpg">
                <img src="https://img.tradera.net/902/607442902_large-fit.jpg">
                <img src="https://img.tradera.net/902/607442902_heroimages.jpg">
                <img src="https://other-site.com/image.jpg">
                <a href="https://img.tradera.net/902/607442902_small-square.jpg">Link</a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        images = self.parser._extract_images(soup)

        # Kontrollera att vi fick bilder från tradera.net
        self.assertGreater(len(images), 0)
        # Kontrollera att alla bilder är från tradera.net och konverterade till _images.jpg-format
        for image in images:
            self.assertIn("img.tradera.net", image)
            self.assertIn("_images.jpg", image)

    def test_extract_auction_end_date(self):
        """Testa extrahering av auktionsslutdatum"""
        html = """
        <html>
            <body>
                <div>avslutad 27 jul 14:00</div>
                <span>slutade 15 augusti 2025</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        end_date = self.parser._extract_auction_end_date(soup)
        # Kan vara None om inget datum hittas
        if end_date is not None:
            self.assertIsInstance(end_date, str)

    def test_parse_price(self):
        """Testa parsning av pristext"""
        test_cases = [
            ("500 kr", 500),
            ("750 SEK", 750),
            ("1000", 1000),
            ("1,250 kr", 1250),
            ("2.500 SEK", 2500),
            ("invalid", None),
            ("", None),
            (None, None),
        ]

        for price_text, expected in test_cases:
            with self.subTest(price_text=price_text):
                result = self.parser._parse_price(price_text)
                self.assertEqual(result, expected)

    def test_parse_price_with_currency(self):
        """Testa parsning av pris med valuta"""
        test_cases = [
            ("500 kr", "SEK", {"amount": 500, "currency": "SEK"}),
            ("750 SEK", "SEK", {"amount": 750, "currency": "SEK"}),
            ("1000", "EUR", {"amount": 1000, "currency": "EUR"}),
            ("invalid", "SEK", None),
            ("", "SEK", None),
            (None, "SEK", None),
        ]

        for price_text, currency, expected in test_cases:
            with self.subTest(price_text=price_text, currency=currency):
                result = self.parser._parse_price_with_currency(price_text, currency)
                self.assertEqual(result, expected)


class ParseTraderaURLTest(TestCase):
    """Tester för parse_tradera_url funktionen"""

    @patch("axes.utils.tradera_parser.TraderaParser")
    def test_parse_tradera_url_success(self, mock_parser_class):
        """Testa lyckad användning av parse_tradera_url"""
        # Mock parser
        mock_parser = Mock()
        mock_parser.parse_tradera_page.return_value = {
            "title": "Test Auction",
            "description": "Test Description",
            "seller_alias": "Test Seller",
            "prices": [],
            "item_id": "123",
            "images": [],
            "auction_end_date": None,
            "url": "https://www.tradera.com/item/123/456/test",
        }
        mock_parser_class.return_value = mock_parser

        # Testa funktionen
        result = parse_tradera_url("https://www.tradera.com/item/123/456/test")

        # Kontrollera att parser anropades
        mock_parser.parse_tradera_page.assert_called_once_with(
            "https://www.tradera.com/item/123/456/test"
        )

        # Kontrollera resultat
        self.assertIsInstance(result, dict)
        self.assertIn("title", result)

    @patch("axes.utils.tradera_parser.TraderaParser")
    def test_parse_tradera_url_invalid_url(self, mock_parser_class):
        """Testa parse_tradera_url med ogiltig URL"""
        mock_parser = Mock()
        mock_parser.parse_tradera_page.side_effect = ValueError("Invalid URL")
        mock_parser_class.return_value = mock_parser

        with self.assertRaises(ValueError):
            parse_tradera_url("https://www.google.com")
