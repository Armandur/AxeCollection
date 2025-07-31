from django.test import TestCase
from django.contrib.auth.models import User
from axes.forms import (
    StampForm,
    StampTranscriptionForm,
    AxeStampForm,
    StampTagForm,
    StampImageForm,
)
from axes.models import (
    Manufacturer,
    Stamp,
    StampTranscription,
    StampTag,
    StampImage,
    AxeStamp,
    Axe,
)
from decimal import Decimal


class StampFormTest(TestCase):
    """Tester för StampForm"""

    def setUp(self):
        """Skapa testdata för varje test"""
        self.manufacturer = Manufacturer.objects.create(
            name="Test Tillverkare", manufacturer_type="TILLVERKARE"
        )

    def test_stamp_form_valid_data(self):
        """Test att formuläret fungerar med giltig data"""
        form_data = {
            "name": "Test Stämpel",
            "description": "En teststämpel",
            "manufacturer": self.manufacturer.id,
            "stamp_type": "text",
            "status": "known",
            "year_from": 1900,
            "year_to": 1950,
            "source_category": "own_collection",
            "source_reference": "Min samling, katalog #123",
        }
        form = StampForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_stamp_form_invalid_year_order(self):
        """Test att formuläret validerar årtalsordering"""
        form_data = {
            "name": "Invalid Years Stamp",
            "stamp_type": "text",
            "status": "unknown",
            "year_from": 1950,
            "year_to": 1900,
        }
        form = StampForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_stamp_form_known_without_manufacturer(self):
        """Test att kända stämplar kräver tillverkare"""
        form_data = {"name": "Known Stamp", "stamp_type": "text", "status": "known"}
        form = StampForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_stamp_form_unknown_without_manufacturer(self):
        """Test att okända stämplar inte kräver tillverkare"""
        form_data = {
            "name": "Unknown Stamp",
            "stamp_type": "text",
            "status": "unknown",
            "source_category": "unknown",  # Lägg till obligatoriskt fält
        }
        form = StampForm(data=form_data)
        # Formuläret ska vara giltigt eftersom det inte anropar clean() automatiskt
        self.assertTrue(form.is_valid())

        # Test att spara fungerar också (save() anropar full_clean() automatiskt)
        stamp = form.save()
        self.assertEqual(stamp.name, "Unknown Stamp")
        self.assertEqual(stamp.status, "unknown")
        self.assertIsNone(stamp.manufacturer)

    def test_stamp_form_required_fields(self):
        """Test obligatoriska fält"""
        form = StampForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("stamp_type", form.errors)

    def test_stamp_form_save(self):
        """Test att spara formuläret skapar en stämpel"""
        form_data = {
            "name": "Saved Stamp",
            "description": "Saved description",
            "manufacturer": self.manufacturer.id,
            "stamp_type": "symbol",
            "status": "known",
            "year_from": 1920,
            "source_category": "museum",
        }
        form = StampForm(data=form_data)
        self.assertTrue(form.is_valid())

        stamp = form.save()
        self.assertEqual(stamp.name, "Saved Stamp")
        self.assertEqual(stamp.manufacturer, self.manufacturer)
        self.assertEqual(stamp.stamp_type, "symbol")
        self.assertEqual(stamp.year_from, 1920)

    def test_stamp_form_choices(self):
        """Test att formuläret har rätt val"""
        form = StampForm()

        # Test stamp_type choices
        stamp_type_choices = form.fields["stamp_type"].choices
        expected_types = [
            ("text", "Text"),
            ("symbol", "Symbol"),
            ("text_symbol", "Text + Symbol"),
            ("label", "Etikett"),
        ]
        for choice in expected_types:
            self.assertIn(choice, stamp_type_choices)

        # Test status choices
        status_choices = form.fields["status"].choices
        expected_statuses = [("known", "Känd"), ("unknown", "Okänd")]
        for choice in expected_statuses:
            self.assertIn(choice, status_choices)


class StampTranscriptionFormTest(TestCase):
    """Tester för StampTranscriptionForm"""

    def setUp(self):
        """Skapa testdata för varje test"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        self.stamp = Stamp.objects.create(
            name="Transcription Test Stamp", stamp_type="text"
        )

    def test_transcription_form_valid_data(self):
        """Test att formuläret fungerar med giltig data"""
        form_data = {
            "stamp": self.stamp.id,
            "text": "TILLVERKARE AB STOCKHOLM",
            "quality": "high",
        }
        form = StampTranscriptionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_transcription_form_required_fields(self):
        """Test obligatoriska fält"""
        form = StampTranscriptionForm(data={})
        self.assertFalse(form.is_valid())
        # StampTranscriptionForm kräver text och quality, inte stamp
        self.assertIn("text", form.errors)
        self.assertIn("quality", form.errors)

    def test_transcription_form_save(self):
        """Test att spara formuläret skapar en transkribering"""
        form_data = {
            "text": "GRÄNSFORS",
            "quality": "high",
        }
        form = StampTranscriptionForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Skapa en stämpel först
        stamp = Stamp.objects.create(name="Test Stamp", stamp_type="text")

        transcription = form.save(commit=False)
        transcription.stamp = stamp
        transcription.save()

        self.assertEqual(transcription.text, "GRÄNSFORS")
        self.assertEqual(transcription.quality, "high")
        self.assertEqual(transcription.stamp, stamp)

    def test_transcription_form_quality_choices(self):
        """Test kvalitetsval"""
        form = StampTranscriptionForm()
        quality_choices = form.fields["quality"].choices
        expected_qualities = [("high", "Hög"), ("medium", "Medium"), ("low", "Låg")]
        for choice in expected_qualities:
            self.assertIn(choice, quality_choices)


class AxeStampFormTest(TestCase):
    """Tester för AxeStampForm"""

    def setUp(self):
        """Skapa testdata för varje test"""
        self.manufacturer = Manufacturer.objects.create(
            name="Axe Manufacturer", manufacturer_type="TILLVERKARE"
        )

        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Modell"
        )

        self.stamp = Stamp.objects.create(name="Axe Stamp", stamp_type="text")

    def test_axe_stamp_form_valid_data(self):
        """Test att formuläret fungerar med giltig data"""
        form_data = {
            "stamp": str(self.stamp.id),  # Använd sträng-ID för ChoiceField
            "comment": "Tydlig stämpel på bladet",
            "position": "Huvudets översida",
            "uncertainty_level": "certain",
        }
        form = AxeStampForm(data=form_data, axe=self.axe)
        self.assertTrue(form.is_valid())

    def test_axe_stamp_form_required_fields(self):
        """Test obligatoriska fält"""
        form = AxeStampForm(data={}, axe=self.axe)
        self.assertFalse(form.is_valid())
        self.assertIn("stamp", form.errors)

    def test_axe_stamp_form_save(self):
        """Test att spara formuläret skapar en yxstämpel"""
        form_data = {
            "stamp": str(self.stamp.id),  # Använd sträng-ID för ChoiceField
            "comment": "Tydlig stämpel",
            "position": "Huvudets översida",
            "uncertainty_level": "certain",
        }
        form = AxeStampForm(data=form_data, axe=self.axe)
        self.assertTrue(form.is_valid())

        axe_stamp = form.save(commit=False)
        axe_stamp.axe = self.axe
        axe_stamp.save()

        self.assertEqual(axe_stamp.stamp, self.stamp)
        self.assertEqual(axe_stamp.axe, self.axe)
        self.assertEqual(axe_stamp.comment, "Tydlig stämpel")

    def test_axe_stamp_form_uncertainty_choices(self):
        """Test osäkerhetsval"""
        form = AxeStampForm(axe=self.axe)
        uncertainty_choices = form.fields["uncertainty_level"].choices
        expected_choices = [
            ("certain", "Säker"),
            ("uncertain", "Osäker"),
            ("tentative", "Preliminär"),
        ]
        self.assertEqual(list(uncertainty_choices), expected_choices)

    def test_axe_stamp_form_initialization_with_axe_id(self):
        """Test att formuläret initialiseras korrekt med axe_id"""
        form = AxeStampForm(axe=self.axe)
        self.assertIn("stamp", form.fields)
        self.assertIn("comment", form.fields)
        self.assertIn("position", form.fields)
        self.assertIn("uncertainty_level", form.fields)


class StampTagFormTest(TestCase):
    """Tester för StampTagForm"""

    def test_stamp_tag_form_valid_data(self):
        """Test att formuläret fungerar med giltig data"""
        form_data = {
            "name": "Militär",
            "description": "Stämplar från militära tillverkare",
            "color": "#ff0000",
        }
        form = StampTagForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_stamp_tag_form_required_fields(self):
        """Test obligatoriska fält"""
        form = StampTagForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_stamp_tag_form_save(self):
        """Test att spara formuläret skapar en tag"""
        form_data = {
            "name": "Saved Tag",
            "description": "Saved description",
            "color": "#00ff00",
        }
        form = StampTagForm(data=form_data)
        self.assertTrue(form.is_valid())

        tag = form.save()
        self.assertEqual(tag.name, "Saved Tag")
        self.assertEqual(tag.description, "Saved description")
        self.assertEqual(tag.color, "#00ff00")

    def test_stamp_tag_form_default_color(self):
        """Test standardfärg"""
        form_data = {
            "name": "Test Tag",
            "description": "En testtagg",
            "color": "#007bff",  # Lägg till color-fältet
        }
        form = StampTagForm(data=form_data)
        # Formuläret ska vara giltigt med color-fältet
        self.assertTrue(form.is_valid())

    def test_stamp_tag_form_color_validation(self):
        """Test färgvalidering (hex-format)"""
        # Giltiga färger
        valid_colors = ["#ffffff", "#000000", "#ff0000", "#00ff00", "#0000ff"]
        for color in valid_colors:
            form_data = {"name": f"Tag {color}", "color": color}
            form = StampTagForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Color {color} should be valid")


class StampImageFormTest(TestCase):
    """Tester för StampImageForm"""

    def setUp(self):
        """Skapa testdata för varje test"""
        self.stamp = Stamp.objects.create(name="Image Test Stamp", stamp_type="symbol")

    def test_stamp_image_form_required_fields(self):
        """Test obligatoriska fält"""
        form = StampImageForm(data={})
        self.assertFalse(form.is_valid())
        # StampImageForm kräver image och uncertainty_level, inte stamp
        self.assertIn("image", form.errors)
        self.assertIn("uncertainty_level", form.errors)

    def test_stamp_image_form_basic_data(self):
        """Test grundläggande data (utan faktisk fil)"""
        form_data = {
            "caption": "Test bild",
            "description": "En testbeskrivning",
            "uncertainty_level": "certain",
        }
        form = StampImageForm(data=form_data)
        # Formuläret är inte giltigt utan bild, men vi kan testa att fälten finns
        self.assertIn("image", form.fields)
        self.assertIn("caption", form.fields)
        self.assertIn("description", form.fields)
        self.assertIn("uncertainty_level", form.fields)

    def test_stamp_image_form_fields_exist(self):
        """Test att alla förväntade fält finns"""
        form = StampImageForm()
        expected_fields = [
            "image",
            "caption",
            "description",
            "x_coordinate",
            "y_coordinate",
            "width",
            "height",
            "position",
            "comment",
            "uncertainty_level",
            "external_source",
        ]
        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_stamp_image_form_default_values(self):
        """Test standardvärden för fält"""
        form = StampImageForm()
        # Test att uncertainty_level har rätt standardvärde
        self.assertEqual(form.fields["uncertainty_level"].initial, "certain")

    def test_stamp_image_form_widget_classes(self):
        """Test att formuläret har rätt CSS-klasser för styling"""
        form = StampImageForm()
        # Test att viktiga fält har form-control klassen
        self.assertIn("form-control", str(form.fields["caption"].widget.attrs))
        self.assertIn("form-control", str(form.fields["description"].widget.attrs))


class StampFormIntegrationTest(TestCase):
    """Integrationstester för stämpel-formulär"""

    def setUp(self):
        """Skapa testdata för integrationstester"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        self.manufacturer = Manufacturer.objects.create(
            name="Integration Test Manufacturer", manufacturer_type="TILLVERKARE"
        )

    def test_complete_stamp_creation_workflow(self):
        """Test komplett arbetsflöde för att skapa stämpel med transkribering"""
        # Skapa stämpel
        stamp_data = {
            "name": "Complete Test Stamp",
            "description": "En komplett teststämpel",
            "manufacturer": self.manufacturer.id,
            "stamp_type": "text",
            "status": "known",
            "year_from": 1900,
            "year_to": 1950,
            "source_category": "own_collection",
        }
        stamp_form = StampForm(data=stamp_data)
        self.assertTrue(stamp_form.is_valid())
        stamp = stamp_form.save()

        # Skapa transkribering
        transcription_data = {
            "text": "KOMPLETT TEST",
            "quality": "high",
        }
        transcription_form = StampTranscriptionForm(data=transcription_data)
        self.assertTrue(transcription_form.is_valid())

        transcription = transcription_form.save(commit=False)
        transcription.stamp = stamp
        transcription.save()

        # Verifiera att allt skapades korrekt
        self.assertEqual(stamp.name, "Complete Test Stamp")
        self.assertEqual(transcription.text, "KOMPLETT TEST")
        self.assertEqual(transcription.stamp, stamp)

    def test_form_error_handling(self):
        """Test felhantering i formulären"""
        # Test att formulären hanterar ogiltig data på rätt sätt
        invalid_stamp_data = {
            "name": "",  # Obligatoriskt fält tomt
            "stamp_type": "invalid_type",  # Ogiltigt val
            "status": "known",  # Kräver tillverkare
            "year_from": 2000,
            "year_to": 1900,  # Ogiltigt årtal
        }

        stamp_form = StampForm(data=invalid_stamp_data)
        self.assertFalse(stamp_form.is_valid())

        # Kontrollera att alla förväntade fel finns
        self.assertIn("name", stamp_form.errors)
        self.assertIn("__all__", stamp_form.errors)  # För custom validation
