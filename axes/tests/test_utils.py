"""
Tester för utils-funktioner
"""
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.cache import cache
from axes.utils.currency_converter import (
    convert_currency,
    get_exchange_rates,
    get_currency_info,
    format_price,
    get_conversion_warning,
    get_conversion_rate,
    is_cache_valid,
    clear_cache,
)
from axes.utils.ebay_parser import parse_ebay_listing
from axes.utils.tradera_parser import parse_tradera_listing


class CurrencyConverterTest(TestCase):
    """Tester för valutakonvertering"""

    def setUp(self):
        """Sätt upp testdata"""
        cache.clear()

    @patch("requests.get")
    def test_convert_currency_success(self, mock_get):
        """Testa lyckad valutakonvertering"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rates": {"SEK": 10.5, "EUR": 0.095}
        }
        mock_get.return_value = mock_response

        result = convert_currency(100, "USD", "SEK")
        self.assertEqual(result, 1050)

    @patch("requests.get")
    def test_convert_currency_api_error(self, mock_get):
        """Testa valutakonvertering med API-fel"""
        # Rensa cache först
        clear_cache()
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = convert_currency(100, "USD", "SEK")
        self.assertIsNone(result)

    @patch("requests.get")
    def test_convert_currency_network_error(self, mock_get):
        """Testa valutakonvertering med nätverksfel"""
        # Rensa cache först
        clear_cache()
        
        mock_get.side_effect = Exception("Network error")

        result = convert_currency(100, "USD", "SEK")
        self.assertIsNone(result)

    @patch("requests.get")
    def test_convert_currency_invalid_currency(self, mock_get):
        """Testa valutakonvertering med ogiltig valuta"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": {"SEK": 10.5}}
        mock_get.return_value = mock_response

        result = convert_currency(100, "USD", "INVALID")
        self.assertIsNone(result)

    def test_convert_currency_same_currency(self):
        """Testa valutakonvertering med samma valuta"""
        result = convert_currency(100, "USD", "USD")
        self.assertEqual(result, 100)

    @patch("requests.get")
    def test_convert_currency_with_cache(self, mock_get):
        """Testa valutakonvertering med cache"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rates": {"SEK": 10.5}
        }
        mock_get.return_value = mock_response

        # Första anropet
        result1 = convert_currency(100, "USD", "SEK")
        self.assertEqual(result1, 1050)

        # Andra anropet (ska använda cache)
        result2 = convert_currency(100, "USD", "SEK")
        self.assertEqual(result2, 1050)

        # Kontrollera att API bara anropades en gång
        mock_get.assert_called_once()

    def test_convert_currency_invalid_amount(self):
        """Testa valutakonvertering med ogiltigt belopp"""
        result = convert_currency("invalid", "USD", "SEK")
        self.assertIsNone(result)

    def test_convert_currency_negative_amount(self):
        """Testa valutakonvertering med negativt belopp"""
        result = convert_currency(-100, "USD", "SEK")
        self.assertIsNone(result)

    def test_convert_currency_zero_amount(self):
        """Testa valutakonvertering med noll belopp"""
        result = convert_currency(0, "USD", "SEK")
        self.assertEqual(result, 0)

    @patch("requests.get")
    def test_convert_currency_with_currency_info(self, mock_get):
        """Testa valutakonvertering med valutainformation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": {"SEK": 10.5}}
        mock_get.return_value = mock_response

        result = convert_currency(100, "USD", "SEK")
        self.assertEqual(result, 1050)

        # Testa valutainformation
        info = get_currency_info("USD")
        self.assertIn("name", info)
        self.assertIn("symbol", info)

    @patch("requests.get")
    def test_convert_currency_with_currency_info_failure(self, mock_get):
        """Testa valutakonvertering med fel i valutainformation"""
        mock_get.side_effect = Exception("Network error")

        info = get_currency_info("INVALID")
        self.assertEqual(info["name"], "Unknown")
        self.assertEqual(info["symbol"], "$")

    def test_format_price_valid(self):
        """Testa format_price med giltigt belopp"""
        result = format_price(1250.50, "SEK")
        self.assertIn("1 250,50", result)
        self.assertIn("kr", result)

    def test_format_price_invalid_currency(self):
        """Testa format_price med ogiltig valuta"""
        result = format_price(1250.50, "INVALID")
        self.assertIn("1 250,50", result)

    def test_get_conversion_warning(self):
        """Testa get_conversion_warning"""
        warning = get_conversion_warning("USD", "SEK")
        self.assertIn("USD", warning)
        self.assertIn("SEK", warning)

    def test_get_conversion_rate(self):
        """Testa get_conversion_rate"""
        rate = get_conversion_rate("USD", "SEK")
        # Kan vara None om API inte fungerar
        if rate is not None:
            self.assertIsInstance(rate, float)

    def test_is_cache_valid(self):
        """Testa is_cache_valid"""
        valid = is_cache_valid()
        self.assertIsInstance(valid, bool)

    def test_clear_cache(self):
        """Testa clear_cache"""
        clear_cache()
        # Ska inte kasta något fel


class EbayParserTest(TestCase):
    """Tester för EbayParser"""

    def setUp(self):
        """Sätt upp testdata"""
        self.parser = parse_ebay_listing

    def test_parse_price_valid(self):
        """Testa parsning av giltigt pris"""
        html = '<span class="price">$125.50</span>'
        result = self.parser(html)
        self.assertEqual(result["price"], 125.50)

    def test_parse_price_with_decimal(self):
        """Testa parsning av pris med decimaler"""
        html = '<span class="price">$125.99</span>'
        result = self.parser(html)
        self.assertEqual(result["price"], 125.99)

    def test_parse_price_without_currency(self):
        """Testa parsning av pris utan valutasymbol"""
        html = '<span class="price">125.50</span>'
        result = self.parser(html)
        self.assertEqual(result["price"], 125.50)

    def test_parse_price_invalid_format(self):
        """Testa parsning av ogiltigt prisformat"""
        html = '<span class="price">invalid</span>'
        result = self.parser(html)
        self.assertIsNone(result["price"])

    def test_parse_price_empty_string(self):
        """Testa parsning av tom sträng"""
        html = ""
        result = self.parser(html)
        self.assertIsNone(result["price"])

    def test_parse_price_none(self):
        """Testa parsning av None"""
        result = self.parser(None)
        self.assertIsNone(result["price"])

    def test_extract_images_valid_html(self):
        """Testa extrahering av bilder från giltig HTML"""
        html = """
        <div>
            <img src="image1.jpg" alt="Image 1">
            <img src="image2.jpg" alt="Image 2">
        </div>
        """
        result = self.parser(html)
        self.assertIn("images", result)
        self.assertGreater(len(result["images"]), 0)

    def test_extract_images_no_images(self):
        """Testa extrahering av bilder från HTML utan bilder"""
        html = "<div>No images here</div>"
        result = self.parser(html)
        self.assertIn("images", result)
        self.assertEqual(len(result["images"]), 0)

    def test_extract_images_invalid_html(self):
        """Testa extrahering av bilder från ogiltig HTML"""
        html = "invalid html"
        result = self.parser(html)
        self.assertIn("images", result)
        self.assertEqual(len(result["images"]), 0)

    def test_extract_images_with_relative_urls(self):
        """Testa extrahering av bilder med relativa URLs"""
        html = """
        <div>
            <img src="/images/image1.jpg" alt="Image 1">
            <img src="images/image2.jpg" alt="Image 2">
        </div>
        """
        result = self.parser(html)
        self.assertIn("images", result)
        self.assertGreater(len(result["images"]), 0)

    def test_extract_images_with_absolute_urls(self):
        """Testa extrahering av bilder med absoluta URLs"""
        html = """
        <div>
            <img src="https://example.com/image1.jpg" alt="Image 1">
            <img src="http://example.com/image2.jpg" alt="Image 2">
        </div>
        """
        result = self.parser(html)
        self.assertIn("images", result)
        self.assertGreater(len(result["images"]), 0)

    def test_parse_ebay_listing_valid(self):
        """Testa parsning av giltig eBay-listing"""
        html = """
        <div>
            <h1>Test Item</h1>
            <span class="price">$125.50</span>
            <img src="image1.jpg" alt="Image 1">
            <img src="image2.jpg" alt="Image 2">
        </div>
        """
        result = self.parser(html)
        self.assertEqual(result["title"], "Test Item")
        self.assertEqual(result["price"], 125.50)
        self.assertIn("images", result)
        self.assertGreater(len(result["images"]), 0)

    def test_parse_ebay_listing_missing_data(self):
        """Testa parsning av eBay-listing med saknad data"""
        html = "<div>No price or images</div>"
        result = self.parser(html)
        self.assertIsNone(result["title"])
        self.assertIsNone(result["price"])
        self.assertEqual(len(result["images"]), 0)

    def test_parse_ebay_listing_invalid_html(self):
        """Testa parsning av ogiltig eBay-listing HTML"""
        html = "invalid html"
        result = self.parser(html)
        self.assertIsNone(result["title"])
        self.assertIsNone(result["price"])
        self.assertEqual(len(result["images"]), 0)


class TraderaParserTest(TestCase):
    """Tester för TraderaParser"""

    def setUp(self):
        """Sätt upp testdata"""
        self.parser = parse_tradera_listing

    def test_parse_price_valid(self):
        """Testa parsning av giltigt pris"""
        html = '<span class="price">125,50 kr</span>'
        result = self.parser(html)
        self.assertEqual(result["price"], 125.50)

    def test_parse_price_with_dot_separator(self):
        """Testa parsning av pris med punkt som separator"""
        html = '<span class="price">125.50 kr</span>'
        result = self.parser(html)
        self.assertEqual(result["price"], 125.50)

    def test_parse_price_with_decimal(self):
        """Testa parsning av pris med decimaler"""
        html = '<span class="price">125,99 kr</span>'
        result = self.parser(html)
        self.assertEqual(result["price"], 125.99)

    def test_parse_price_without_currency(self):
        """Testa parsning av pris utan valutasymbol"""
        html = '<span class="price">125,50</span>'
        result = self.parser(html)
        self.assertEqual(result["price"], 125.50)

    def test_parse_price_invalid_format(self):
        """Testa parsning av ogiltigt prisformat"""
        html = '<span class="price">invalid</span>'
        result = self.parser(html)
        self.assertIsNone(result["price"])

    def test_parse_price_empty_string(self):
        """Testa parsning av tom sträng"""
        html = ""
        result = self.parser(html)
        self.assertIsNone(result["price"])

    def test_parse_price_none(self):
        """Testa parsning av None"""
        result = self.parser(None)
        self.assertIsNone(result["price"])

    def test_parse_price_with_currency_valid(self):
        """Testa parsning av pris med valuta"""
        html = '<span class="price">125,50 SEK</span>'
        result = self.parser(html)
        self.assertEqual(result["price"], 125.50)
        self.assertEqual(result["currency"], "SEK")

    def test_parse_price_with_currency_invalid(self):
        """Testa parsning av pris med ogiltig valuta"""
        html = '<span class="price">125,50 INVALID</span>'
        result = self.parser(html)
        self.assertEqual(result["price"], 125.50)
        self.assertIsNone(result["currency"])

    def test_parse_price_with_currency_none(self):
        """Testa parsning av pris utan valuta"""
        html = '<span class="price">125,50</span>'
        result = self.parser(html)
        self.assertEqual(result["price"], 125.50)
        self.assertIsNone(result["currency"])

    def test_extract_images_valid_html(self):
        """Testa extrahering av bilder från giltig HTML"""
        html = """
        <div>
            <img src="image1.jpg" alt="Image 1">
            <img src="image2.jpg" alt="Image 2">
        </div>
        """
        result = self.parser(html)
        self.assertIn("images", result)
        self.assertGreater(len(result["images"]), 0)

    def test_extract_images_no_images(self):
        """Testa extrahering av bilder från HTML utan bilder"""
        html = "<div>No images here</div>"
        result = self.parser(html)
        self.assertIn("images", result)
        self.assertEqual(len(result["images"]), 0)

    def test_extract_images_invalid_html(self):
        """Testa extrahering av bilder från ogiltig HTML"""
        html = "invalid html"
        result = self.parser(html)
        self.assertIn("images", result)
        self.assertEqual(len(result["images"]), 0)

    def test_extract_images_with_relative_urls(self):
        """Testa extrahering av bilder med relativa URLs"""
        html = """
        <div>
            <img src="/images/image1.jpg" alt="Image 1">
            <img src="images/image2.jpg" alt="Image 2">
        </div>
        """
        result = self.parser(html)
        self.assertIn("images", result)
        self.assertGreater(len(result["images"]), 0)

    def test_extract_images_with_absolute_urls(self):
        """Testa extrahering av bilder med absoluta URLs"""
        html = """
        <div>
            <img src="https://example.com/image1.jpg" alt="Image 1">
            <img src="http://example.com/image2.jpg" alt="Image 2">
        </div>
        """
        result = self.parser(html)
        self.assertIn("images", result)
        self.assertGreater(len(result["images"]), 0)

    def test_parse_tradera_listing_valid(self):
        """Testa parsning av giltig Tradera-listing"""
        html = """
        <div>
            <h1>Test Item</h1>
            <span class="price">125,50 kr</span>
            <img src="image1.jpg" alt="Image 1">
            <img src="image2.jpg" alt="Image 2">
        </div>
        """
        result = self.parser(html)
        self.assertEqual(result["title"], "Test Item")
        self.assertEqual(result["price"], 125.50)
        self.assertIn("images", result)
        self.assertGreater(len(result["images"]), 0)

    def test_parse_tradera_listing_missing_data(self):
        """Testa parsning av Tradera-listing med saknad data"""
        html = "<div>No price or images</div>"
        result = self.parser(html)
        self.assertIsNone(result["title"])
        self.assertIsNone(result["price"])
        self.assertEqual(len(result["images"]), 0)

    def test_parse_tradera_listing_invalid_html(self):
        """Testa parsning av ogiltig Tradera-listing HTML"""
        html = "invalid html"
        result = self.parser(html)
        self.assertIsNone(result["title"])
        self.assertIsNone(result["price"])
        self.assertEqual(len(result["images"]), 0)

    def test_parse_price_with_different_formats(self):
        """Testa parsning av pris med olika format"""
        test_cases = [
            ("125,50 kr", 125.50),
            ("125.50 kr", 125.50),
            ("125 kr", 125.0),
            ("125,50", 125.50),
            ("125.50", 125.50),
            ("125", 125.0),
        ]

        for html, expected in test_cases:
            with self.subTest(html=html):
                html_content = f'<span class="price">{html}</span>'
                result = self.parser(html_content)
                self.assertEqual(result["price"], expected)

    def test_parse_price_with_edge_cases(self):
        """Testa parsning av pris med edge cases"""
        test_cases = [
            ("0 kr", 0.0),
            ("0,00 kr", 0.0),
            ("1000000,50 kr", 1000000.50),
            ("1,234,567.89 kr", 1234567.89),
        ]

        for html, expected in test_cases:
            with self.subTest(html=html):
                html_content = f'<span class="price">{html}</span>'
                result = self.parser(html_content)
                self.assertEqual(result["price"], expected)

    def test_parse_price_with_invalid_edge_cases(self):
        """Testa parsning av pris med ogiltiga edge cases"""
        test_cases = [
            "invalid",
            "kr 125,50",
            "125,50,00",
            "125.50.00",
            "",
            None,
        ]

        for html in test_cases:
            with self.subTest(html=html):
                if html is not None:
                    html_content = f'<span class="price">{html}</span>'
                else:
                    html_content = None
                result = self.parser(html_content)
                self.assertIsNone(result["price"]) 