from decimal import Decimal
from django.test import TestCase
from django.template import Template, Context
from django.utils.safestring import mark_safe
from axes.models import Manufacturer, Axe, Contact, Platform, Transaction
from axes.templatetags.axe_filters import (
    format_decimal,
    format_currency,
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
)


class TemplateFiltersTest(TestCase):
    """Tester för template filters"""

    def setUp(self):
        """Skapa testdata för varje test"""
        from django.core.management import call_command

        call_command(
            "generate_test_data",
            "--clear",
            "--manufacturers",
            "3",
            "--axes",
            "5",
            "--contacts",
            "3",
        )

    def test_format_decimal(self):
        """Test format_decimal filter"""
        # Test heltal
        self.assertEqual(format_decimal(1000), mark_safe("1\u00A0000"))
        self.assertEqual(format_decimal(1234567), mark_safe("1\u00A0234\u00A0567"))

        # Test decimaltal
        self.assertEqual(format_decimal(1000.50), mark_safe("1\u00A0000,50"))
        self.assertEqual(format_decimal(1234.56), mark_safe("1\u00A0234,56"))

        # Test None
        self.assertEqual(format_decimal(None), "0")

        # Test Decimal-objekt
        self.assertEqual(format_decimal(Decimal("1234.56")), mark_safe("1\u00A0234,56"))

    def test_format_currency(self):
        """Test format_currency filter"""
        # Test med standardvaluta (kr)
        self.assertEqual(format_currency(1000), mark_safe("1\u00A0000\u00A0kr"))
        self.assertEqual(format_currency(1234.56), mark_safe("1\u00A0234,56\u00A0kr"))

        # Test med annan valuta
        self.assertEqual(format_currency(1000, "€"), mark_safe("1\u00A0000\u00A0€"))

        # Test None
        self.assertEqual(format_currency(None), "")

        # Test tom sträng
        self.assertEqual(format_currency(""), "")

    def test_status_badge(self):
        """Test status_badge filter"""
        # Test köpt status (KÖPT mappas till bg-warning text-dark)
        self.assertEqual(status_badge("KÖPT"), "bg-warning text-dark")

        # Test mottagen status (MOTTAGEN mappas till bg-success)
        self.assertEqual(status_badge("MOTTAGEN"), "bg-success")

        # Test okänd status
        self.assertEqual(status_badge("Okänd"), "bg-secondary")

    def test_transaction_badge(self):
        """Test transaction_badge filter"""
        # Test köp
        self.assertEqual(transaction_badge("KÖP"), "bg-danger")

        # Test försäljning
        self.assertEqual(transaction_badge("SÄLJ"), "bg-success")

        # Test okänd typ
        self.assertEqual(transaction_badge("Okänd"), "bg-secondary")

    def test_transaction_icon(self):
        """Test transaction_icon filter"""
        # Test köp
        self.assertEqual(transaction_icon("KÖP"), "bi-arrow-down-circle")

        # Test försäljning
        self.assertEqual(transaction_icon("SÄLJ"), "bi-arrow-up-circle")

        # Test okänd typ
        self.assertEqual(transaction_icon("Okänd"), "bi-question-circle")

    def test_default_if_empty(self):
        """Test default_if_empty filter"""
        # Test med tom sträng
        self.assertEqual(default_if_empty("", "Standard"), "Standard")

        # Test med None
        self.assertEqual(default_if_empty(None, "Standard"), "Standard")

        # Test med värde
        self.assertEqual(default_if_empty("Värde", "Standard"), "Värde")

        # Test med standardvärde
        self.assertEqual(default_if_empty("", "-"), "-")

    def test_breadcrumb_item(self):
        """Test breadcrumb_item template tag"""
        # Test aktiv länk
        expected_active = (
            '<li class="breadcrumb-item active" aria-current="page">Test</li>'
        )
        self.assertEqual(
            breadcrumb_item("Test", is_active=True), mark_safe(expected_active)
        )

        # Test länk
        expected_link = '<li class="breadcrumb-item"><a href="/test/">Test</a></li>'
        self.assertEqual(breadcrumb_item("Test", "/test/"), mark_safe(expected_link))

        # Test utan länk
        expected_no_link = '<li class="breadcrumb-item">Test</li>'
        self.assertEqual(breadcrumb_item("Test"), mark_safe(expected_no_link))

    def test_markdown(self):
        """Test markdown filter"""
        # Test grundläggande markdown
        markdown_text = "**Bold text** and *italic text*"
        result = markdown(markdown_text)
        self.assertIn("<strong>Bold text</strong>", result)
        self.assertIn("<em>italic text</em>", result)

        # Test länkar
        link_text = "[Link text](https://example.com)"
        result = markdown(link_text)
        self.assertIn('<a href="https://example.com" target="_blank">', result)

        # Test tom sträng
        self.assertEqual(markdown(""), "")

        # Test None
        self.assertEqual(markdown(None), "")

    def test_strip_markdown_and_truncate(self):
        """Test strip_markdown_and_truncate filter"""
        # Test med markdown
        markdown_text = "**Bold text** and *italic text* with more content"
        result = strip_markdown_and_truncate(markdown_text, 20)
        self.assertNotIn("**", result)
        self.assertNotIn("*", result)
        self.assertLessEqual(len(result), 20)

        # Test med länk
        link_text = "[Link text](https://example.com) with description"
        result = strip_markdown_and_truncate(link_text, 30)
        self.assertNotIn("[", result)
        self.assertNotIn("]", result)
        self.assertNotIn("(", result)
        self.assertNotIn(")", result)

        # Test tom sträng
        self.assertEqual(strip_markdown_and_truncate("", 50), "")

        # Test None
        self.assertEqual(strip_markdown_and_truncate(None, 50), "")

    def test_times(self):
        """Test times filter"""
        # Test med heltal - times returnerar range
        self.assertEqual(list(times(3)), [0, 1, 2])

        # Test med sträng
        self.assertEqual(list(times("5")), [0, 1, 2, 3, 4])

        # Test med None
        self.assertEqual(list(times(None)), [])

    def test_hierarchy_prefix(self):
        """Test hierarchy_prefix filter"""
        # Skapa hierarkisk struktur
        parent = Manufacturer.objects.create(name="Parent Manufacturer")
        child = Manufacturer.objects.create(name="Child Manufacturer", parent=parent)

        manufacturers_list = [parent, child]

        # Test för parent
        result = hierarchy_prefix(parent, manufacturers_list)
        self.assertEqual(result, "")

        # Test för child
        result = hierarchy_prefix(child, manufacturers_list)
        self.assertIn("└─", result)  # Ska innehålla └─ för indentering

    def test_basename(self):
        """Test basename filter"""
        # Test med sökväg
        self.assertEqual(basename("/path/to/file.txt"), "file.txt")

        # Test med filnamn
        self.assertEqual(basename("file.txt"), "file.txt")

        # Test med tom sträng
        self.assertEqual(basename(""), "")

    def test_country_flag(self):
        """Test country_flag filter"""
        # Test kända länder
        self.assertEqual(country_flag("SE"), "🇸🇪")
        self.assertEqual(country_flag("FI"), "🇫🇮")
        self.assertEqual(country_flag("NO"), "🇳🇴")

        # Test okänt land
        self.assertEqual(country_flag("XX"), "")

        # Test None
        self.assertEqual(country_flag(None), "")

        # Test tom sträng
        self.assertEqual(country_flag(""), "")

    def test_div(self):
        """Test div filter"""
        # Test division
        self.assertEqual(div(10, 2), 5.0)
        self.assertEqual(div(15, 3), 5.0)

        # Test med decimaler
        self.assertEqual(div(10, 3), 10 / 3)

        # Test division med noll
        self.assertEqual(div(10, 0), 0)

    def test_country_name(self):
        """Test country_name filter"""
        # Test kända länder
        self.assertEqual(country_name("SE"), "Sverige")
        self.assertEqual(country_name("FI"), "Finland")
        self.assertEqual(country_name("NO"), "Norge")

        # Test okänt land
        self.assertEqual(country_name("XX"), "XX")

        # Test None
        self.assertEqual(country_name(None), "")

        # Test tom sträng
        self.assertEqual(country_name(""), "")


class TemplateTagsIntegrationTest(TestCase):
    """Integrationstester för template tags i riktiga templates"""

    def setUp(self):
        """Skapa testdata för varje test"""
        from django.core.management import call_command

        call_command(
            "generate_test_data",
            "--clear",
            "--manufacturers",
            "3",
            "--axes",
            "5",
            "--contacts",
            "3",
        )

    def test_template_with_filters(self):
        """Test att filters fungerar i riktiga templates"""
        # Skapa en enkel template med olika filters
        template_string = """
        {% load axe_filters %}
        <div>
            <p>Pris: {{ 1234.56|format_currency }}</p>
            <p>Status: {{ "KÖPT"|status_badge }}</p>
            <p>Land: {{ "SE"|country_flag }} {{ "SE"|country_name }}</p>
            <p>Default: {{ ""|default_if_empty:"Inget värde" }}</p>
        </div>
        """

        template = Template(template_string)
        context = Context({})
        result = template.render(context)

        # Verifiera att resultatet innehåller förväntad HTML
        self.assertIn(
            "1 234,56 kr", result.replace("\xa0", " ")
        )  # Ersätt non-breaking spaces
        self.assertIn(
            "bg-warning text-dark", result
        )  # KÖPT mappas till bg-warning text-dark
        self.assertIn("🇸🇪", result)
        self.assertIn("Sverige", result)
        self.assertIn("Inget värde", result)

    def test_template_with_markdown(self):
        """Test markdown filter i template"""
        template_string = """
        {% load axe_filters %}
        <div>
            {{ "**Bold text** and *italic text*"|markdown }}
        </div>
        """

        template = Template(template_string)
        context = Context({})
        result = template.render(context)

        self.assertIn("<strong>Bold text</strong>", result)
        self.assertIn("<em>italic text</em>", result)

    def test_template_with_hierarchy(self):
        """Test hierarchy_prefix i template med riktig data"""
        # Skapa hierarkisk struktur
        parent = Manufacturer.objects.create(name="Parent Manufacturer")
        child = Manufacturer.objects.create(name="Child Manufacturer", parent=parent)

        template_string = """
        {% load axe_filters %}
        <ul>
        {% for manufacturer in manufacturers %}
            <li>{{ manufacturer|hierarchy_prefix:manufacturers }} {{ manufacturer.name }}</li>
        {% endfor %}
        </ul>
        """

        template = Template(template_string)
        context = Context({"manufacturers": [parent, child]})
        result = template.render(context)

        # Verifiera att hierarkin renderas korrekt
        self.assertIn("Parent Manufacturer", result)
        self.assertIn("Child Manufacturer", result)
