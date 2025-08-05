"""
Tester för template tags
"""
from django.test import TestCase
from django.template import Context, Template
from axes.templatetags.axe_filters import (
    format_currency,
    format_decimal,
    status_badge,
    transaction_badge,
    transaction_icon,
    default_if_empty,
    breadcrumb_item,
    markdown,
    strip_markdown_and_truncate,
    times,
    hierarchy_prefix,
    basename,
    country_flag,
    div,
    country_name,
    sort_by_quality,
)


class AxeFiltersTest(TestCase):
    """Tester för axe_filters template tags"""

    def test_format_currency_valid(self):
        """Testa format_currency med giltigt värde"""
        result = format_currency(1250)
        self.assertEqual(result, "1\xa0250\xa0kr")

    def test_format_currency_with_decimal(self):
        """Testa format_currency med decimaler"""
        result = format_currency(1250.50)
        self.assertEqual(result, "1\xa0250,50\xa0kr")

    def test_format_currency_zero(self):
        """Testa format_currency med noll"""
        result = format_currency(0)
        self.assertEqual(result, "0\xa0kr")

    def test_format_currency_none(self):
        """Testa format_currency med None"""
        result = format_currency(None)
        self.assertEqual(result, "")

    def test_format_currency_invalid(self):
        """Testa format_currency med ogiltigt värde"""
        result = format_currency("invalid")
        self.assertEqual(result, "")

    def test_format_currency_negative(self):
        """Testa format_currency med negativt värde"""
        result = format_currency(-1250)
        self.assertEqual(result, "-1\xa0250\xa0kr")

    def test_format_decimal_valid(self):
        """Testa format_decimal med giltigt värde"""
        result = format_decimal(1234567)
        self.assertEqual(result, "1\xa0234\xa0567")

    def test_format_decimal_with_decimal(self):
        """Testa format_decimal med decimaler"""
        result = format_decimal(1234567.89)
        self.assertEqual(result, "1\xa0234\xa0567,89")

    def test_format_decimal_zero(self):
        """Testa format_decimal med noll"""
        result = format_decimal(0)
        self.assertEqual(result, "0")

    def test_format_decimal_none(self):
        """Testa format_decimal med None"""
        result = format_decimal(None)
        self.assertEqual(result, "0")

    def test_format_decimal_invalid(self):
        """Testa format_decimal med ogiltigt värde"""
        result = format_decimal("invalid")
        self.assertEqual(result, "")  # Returnerar tom sträng för ogiltiga värden

    def test_status_badge_valid(self):
        """Testa status_badge med giltig status"""
        result = status_badge("KÖPT")
        self.assertIn("bg-warning", result)

    def test_status_badge_invalid(self):
        """Testa status_badge med ogiltig status"""
        result = status_badge("Invalid")
        self.assertIn("bg-secondary", result)

    def test_transaction_badge_valid(self):
        """Testa transaction_badge med giltig typ"""
        result = transaction_badge("KÖP")
        self.assertIn("bg-danger", result)

    def test_transaction_badge_invalid(self):
        """Testa transaction_badge med ogiltig typ"""
        result = transaction_badge("Invalid")
        self.assertIn("bg-secondary", result)

    def test_transaction_icon_valid(self):
        """Testa transaction_icon med giltig typ"""
        result = transaction_icon("KÖP")
        self.assertIn("bi-arrow-down-circle", result)

    def test_transaction_icon_invalid(self):
        """Testa transaction_icon med ogiltig typ"""
        result = transaction_icon("Invalid")
        self.assertIn("bi-question-circle", result)

    def test_default_if_empty_with_value(self):
        """Testa default_if_empty med värde"""
        result = default_if_empty("test", "default")
        self.assertEqual(result, "test")

    def test_default_if_empty_with_none(self):
        """Testa default_if_empty med None"""
        result = default_if_empty(None, "default")
        self.assertEqual(result, "default")

    def test_default_if_empty_with_empty_string(self):
        """Testa default_if_empty med tom sträng"""
        result = default_if_empty("", "default")
        self.assertEqual(result, "default")

    def test_breadcrumb_item_active(self):
        """Testa breadcrumb_item med aktiv länk"""
        result = breadcrumb_item("Test", "/test/", True)
        self.assertIn("active", result)
        self.assertIn("Test", result)

    def test_breadcrumb_item_inactive(self):
        """Testa breadcrumb_item med inaktiv länk"""
        result = breadcrumb_item("Test", "/test/", False)
        self.assertNotIn("active", result)
        self.assertIn("Test", result)

    def test_markdown_basic(self):
        """Testa markdown med grundläggande markdown"""
        result = markdown("**bold**")
        self.assertIn("<strong>", result)

    def test_markdown_none(self):
        """Testa markdown med None"""
        result = markdown(None)
        self.assertEqual(result, "")

    def test_strip_markdown_and_truncate(self):
        """Testa strip_markdown_and_truncate"""
        text = "**Bold text** that is longer than 10 characters"
        result = strip_markdown_and_truncate(text, 10)
        self.assertLessEqual(len(result), 10)
        self.assertNotIn("**", result)

    def test_times_filter(self):
        """Testa times filter"""
        result = times(3)
        self.assertEqual(list(result), [0, 1, 2])  # times returnerar en range

    def test_hierarchy_prefix(self):
        """Testa hierarchy_prefix"""
        # Skapa mock-objekt med parent-attribut
        class MockManufacturer:
            def __init__(self, id, name, parent=None):
                self.id = id
                self.name = name
                self.parent = parent
        
        parent = MockManufacturer(1, "Parent")
        child = MockManufacturer(2, "Child", parent)
        manufacturers = [parent, child]
        
        result = hierarchy_prefix(child, manufacturers)
        self.assertIn("└─", result)  # hierarchy_prefix använder └─ symbol

    def test_basename(self):
        """Testa basename filter"""
        result = basename("/path/to/file.txt")
        self.assertEqual(result, "file.txt")

    def test_country_flag_valid(self):
        """Testa country_flag med giltig landskod"""
        result = country_flag("SE")
        self.assertEqual(result, "🇸🇪")

    def test_country_flag_invalid(self):
        """Testa country_flag med ogiltig landskod"""
        result = country_flag("XX")
        self.assertEqual(result, "")

    def test_div_filter(self):
        """Testa div filter"""
        result = div(10, 2)
        self.assertEqual(result, 5)

    def test_country_name_valid(self):
        """Testa country_name med giltig landskod"""
        result = country_name("SE")
        self.assertEqual(result, "Sverige")

    def test_country_name_invalid(self):
        """Testa country_name med ogiltig landskod"""
        result = country_name("XX")
        self.assertEqual(result, "XX")

    def test_sort_by_quality(self):
        """Testa sort_by_quality"""
        # Skapa mock-objekt med quality-attribut
        class MockTranscription:
            def __init__(self, quality, text):
                self.quality = quality
                self.text = text
        
        transcriptions = [
            MockTranscription("low", "Low"),
            MockTranscription("high", "High"),
            MockTranscription("medium", "Medium"),
        ]
        result = sort_by_quality(transcriptions)
        # Högsta kvalitet först
        self.assertEqual(result[0].quality, "high")


class TemplateTagIntegrationTest(TestCase):
    """Integrationstester för template tags"""

    def test_format_currency_in_template(self):
        """Testa format_currency i template"""
        template = Template('{% load axe_filters %}{{ value|format_currency }}')
        context = Context({"value": 1250})
        result = template.render(context)
        self.assertIn("1\xa0250\xa0kr", result)

    def test_format_currency_none_in_template(self):
        """Testa format_currency med None i template"""
        template = Template('{% load axe_filters %}{{ value|format_currency }}')
        context = Context({"value": None})
        result = template.render(context)
        self.assertEqual(result.strip(), "")

    def test_format_decimal_in_template(self):
        """Testa format_decimal i template"""
        template = Template('{% load axe_filters %}{{ value|format_decimal }}')
        context = Context({"value": 1234567})
        result = template.render(context)
        self.assertIn("1\xa0234\xa0567", result)

    def test_status_badge_in_template(self):
        """Testa status_badge i template"""
        template = Template('{% load axe_filters %}{{ value|status_badge }}')
        context = Context({"value": "KÖPT"})
        result = template.render(context)
        self.assertIn("bg-warning", result)

    def test_transaction_badge_in_template(self):
        """Testa transaction_badge i template"""
        template = Template('{% load axe_filters %}{{ value|transaction_badge }}')
        context = Context({"value": "KÖP"})
        result = template.render(context)
        self.assertIn("bg-danger", result)

    def test_default_if_empty_in_template(self):
        """Testa default_if_empty i template"""
        template = Template('{% load axe_filters %}{{ value|default_if_empty:"default" }}')
        context = Context({"value": None})
        result = template.render(context)
        self.assertIn("default", result)

    def test_country_flag_in_template(self):
        """Testa country_flag i template"""
        template = Template('{% load axe_filters %}{{ value|country_flag }}')
        context = Context({"value": "SE"})
        result = template.render(context)
        self.assertIn("🇸🇪", result)

    def test_breadcrumb_item_in_template(self):
        """Testa breadcrumb_item i template"""
        template = Template('{% load axe_filters %}{% breadcrumb_item "Test" "/test/" True %}')
        context = Context({})
        result = template.render(context)
        self.assertIn("Test", result)
        self.assertIn("active", result) 