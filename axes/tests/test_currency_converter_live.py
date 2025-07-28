from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock
from axes.utils.currency_converter import (
    get_live_rates,
    get_exchange_rates,
    convert_currency,
    get_conversion_rate,
    is_cache_valid,
    clear_cache,
)


class LiveCurrencyConverterTestCase(SimpleTestCase):
    """Testa live valutakonvertering med exchangerate-api.com"""

    def test_get_live_rates_success(self):
        """Testa hämtning av live-kurser"""
        with patch("axes.utils.currency_converter.requests.get") as mock_get:
            # Mock API-svar
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "base": "USD",
                "date": "2025-07-28",
                "rates": {"EUR": 0.85, "GBP": 0.75, "SEK": 9.51},
            }
            mock_get.return_value = mock_response

            rates = get_live_rates()

            # Kontrollera att kurser hämtades
            self.assertIn("USD", rates)
            self.assertIn("EUR", rates)
            self.assertIn("GBP", rates)
            self.assertIn("SEK", rates)

            # Kontrollera att SEK-kurser finns
            self.assertIn("SEK", rates["USD"])
            self.assertIn("SEK", rates["EUR"])
            self.assertIn("SEK", rates["GBP"])

    def test_get_live_rates_api_failure(self):
        """Testa fallback när API misslyckas"""
        with patch("axes.utils.currency_converter.requests.get") as mock_get:
            # Mock API-fel
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            rates = get_live_rates()

            # Kontrollera att fallback-kurser används
            self.assertIn("USD", rates)
            self.assertIn("SEK", rates["USD"])
            self.assertEqual(rates["USD"]["SEK"], 10.5)  # Fallback-kurs

    def test_convert_currency_with_live_rates(self):
        """Testa konvertering med live-kurser"""
        with patch("axes.utils.currency_converter.get_exchange_rates") as mock_rates:
            # Mock live-kurser
            mock_rates.return_value = {
                "USD": {"SEK": 9.51, "EUR": 0.85, "GBP": 0.75},
                "EUR": {"SEK": 11.18, "USD": 1.18, "GBP": 0.88},
                "GBP": {"SEK": 12.78, "USD": 1.33, "EUR": 1.14},
                "SEK": {"USD": 0.105, "EUR": 0.089, "GBP": 0.078},
            }

            # Testa konverteringar
            result = convert_currency(100, "USD", "SEK")
            self.assertIsNotNone(result)
            self.assertEqual(result, 951.0)  # 100 * 9.51

            result = convert_currency(100, "EUR", "SEK")
            self.assertIsNotNone(result)
            self.assertEqual(result, 1118.0)  # 100 * 11.18

    def test_get_conversion_rate_live(self):
        """Testa hämtning av live konverteringskurser"""
        with patch("axes.utils.currency_converter.get_exchange_rates") as mock_rates:
            mock_rates.return_value = {"USD": {"SEK": 9.51}, "EUR": {"SEK": 11.18}}

            # Testa kurser
            rate = get_conversion_rate("USD", "SEK")
            self.assertEqual(rate, 9.51)

            rate = get_conversion_rate("EUR", "SEK")
            self.assertEqual(rate, 11.18)

            # Testa samma valuta
            rate = get_conversion_rate("SEK", "SEK")
            self.assertEqual(rate, 1.0)

    def test_cache_functions(self):
        """Testa cache-funktioner"""
        # Testa cache-rensning
        try:
            clear_cache()
        except Exception as e:
            self.fail(f"clear_cache() kraschade: {e}")

        # Testa cache-status
        cache_valid = is_cache_valid()
        self.assertIsInstance(cache_valid, bool)

    def test_currency_conversion_edge_cases(self):
        """Testa edge cases för valutakonvertering"""
        # Testa samma valuta
        result = convert_currency(100, "SEK", "SEK")
        self.assertEqual(result, 100)

        # Testa med None/ogiltig valuta
        result = convert_currency(100, "INVALID", "SEK")
        self.assertIsNone(result)

        # Testa med negativt belopp (ska hantera som positivt)
        result = convert_currency(-100, "USD", "SEK")
        self.assertIsNotNone(result)
        self.assertEqual(result, -951.0)  # Negativt belopp konverteras

    def test_api_timeout_handling(self):
        """Testa hantering av API-timeout"""
        with patch("axes.utils.currency_converter.requests.get") as mock_get:
            # Mock timeout
            mock_get.side_effect = Exception("Timeout")

            rates = get_live_rates()

            # Kontrollera att fallback används
            self.assertIn("USD", rates)
            self.assertIn("SEK", rates["USD"])


class CurrencyConverterIntegrationTestCase(SimpleTestCase):
    """Testa integration mellan olika valutakonverteringsfunktioner"""

    def test_full_conversion_workflow(self):
        """Testa hela konverteringsflödet"""
        with patch("axes.utils.currency_converter.get_exchange_rates") as mock_rates:
            # Mock kurser
            mock_rates.return_value = {
                "USD": {"SEK": 9.51, "EUR": 0.85},
                "EUR": {"SEK": 11.18, "USD": 1.18},
                "SEK": {"USD": 0.105, "EUR": 0.089},
            }

            # Testa olika konverteringar
            test_cases = [
                (100, "USD", "SEK", 951.0),
                (100, "EUR", "SEK", 1118.0),
                (100, "SEK", "USD", 10.5),
                (100, "SEK", "EUR", 8.9),
            ]

            for amount, from_curr, to_curr, expected in test_cases:
                result = convert_currency(amount, from_curr, to_curr)
                self.assertIsNotNone(result)
                self.assertAlmostEqual(result, expected, places=1)

    def test_currency_rate_consistency(self):
        """Testa att kurser är konsistenta"""
        with patch("axes.utils.currency_converter.get_exchange_rates") as mock_rates:
            mock_rates.return_value = {
                "USD": {"SEK": 9.51, "EUR": 0.85},
                "EUR": {"SEK": 11.18, "USD": 1.18},
                "SEK": {"USD": 0.105, "EUR": 0.089},
            }

            # Testa att USD->SEK och SEK->USD är konsistenta
            usd_to_sek = get_conversion_rate("USD", "SEK")
            sek_to_usd = get_conversion_rate("SEK", "USD")

            # Kontrollera att de är inverser (med liten tolerans för avrundning)
            self.assertAlmostEqual(usd_to_sek * sek_to_usd, 1.0, places=2)
