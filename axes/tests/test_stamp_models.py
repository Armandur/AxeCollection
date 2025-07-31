from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from axes.models import (
    Manufacturer,
    Stamp,
    StampTranscription,
    StampTag,
    StampImage,
    AxeStamp,
    StampVariant,
    StampUncertaintyGroup,
    Axe,
)
from decimal import Decimal


class StampModelTest(TestCase):
    """Tester för Stamp-modellen"""

    def setUp(self):
        """Skapa testdata för varje test"""
        self.manufacturer = Manufacturer.objects.create(
            name="Test Tillverkare", manufacturer_type="TILLVERKARE"
        )

        self.stamp = Stamp.objects.create(
            name="Test Stämpel",
            description="En teststämpel",
            manufacturer=self.manufacturer,
            stamp_type="text",
            status="known",
            year_from=1900,
            year_to=1950,
            source_category="own_collection",
        )

    def test_stamp_creation(self):
        """Test att skapa en stämpel"""
        self.assertIsNotNone(self.stamp.id)
        self.assertEqual(self.stamp.name, "Test Stämpel")
        self.assertEqual(self.stamp.manufacturer, self.manufacturer)
        self.assertEqual(self.stamp.stamp_type, "text")
        self.assertEqual(self.stamp.status, "known")

    def test_stamp_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        self.assertEqual(str(self.stamp), "Test Stämpel")

    def test_stamp_display_name_with_manufacturer(self):
        """Test display_name property med tillverkare"""
        expected = "Test Stämpel (Test Tillverkare)"
        self.assertEqual(self.stamp.display_name, expected)

    def test_stamp_display_name_without_manufacturer(self):
        """Test display_name property utan tillverkare"""
        stamp_no_manufacturer = Stamp.objects.create(
            name="Ensam Stämpel", stamp_type="symbol", status="unknown"
        )
        self.assertEqual(stamp_no_manufacturer.display_name, "Ensam Stämpel")

    def test_year_range_property_both_years(self):
        """Test year_range property med både från- och till-år"""
        self.assertEqual(self.stamp.year_range, "1900-1950")

    def test_year_range_property_same_year(self):
        """Test year_range property med samma år"""
        stamp = Stamp.objects.create(name="Single Year", year_from=1925, year_to=1925)
        self.assertEqual(stamp.year_range, "1925")

    def test_year_range_property_only_from_year(self):
        """Test year_range property med endast från-år"""
        stamp = Stamp.objects.create(name="From Year Only", year_from=1900)
        self.assertEqual(stamp.year_range, "från 1900")

    def test_year_range_property_only_to_year(self):
        """Test year_range property med endast till-år"""
        stamp = Stamp.objects.create(name="To Year Only", year_to=1950)
        self.assertEqual(stamp.year_range, "till 1950")

    def test_year_range_property_no_years(self):
        """Test year_range property utan årtal"""
        stamp = Stamp.objects.create(name="No Years")
        self.assertEqual(stamp.year_range, "Okänt årtal")

    def test_stamp_validation_year_order(self):
        """Test validering att från-år inte kan vara senare än till-år"""
        with self.assertRaises(ValidationError):
            stamp = Stamp(name="Invalid Years", year_from=1950, year_to=1900)
            stamp.full_clean()

    def test_stamp_validation_known_requires_manufacturer(self):
        """Test validering att kända stämplar måste ha tillverkare"""
        with self.assertRaises(ValidationError):
            stamp = Stamp(name="Known Without Manufacturer", status="known")
            stamp.full_clean()

    def test_stamp_validation_unknown_no_manufacturer_required(self):
        """Test att okända stämplar inte behöver tillverkare"""
        stamp = Stamp(name="Unknown No Manufacturer", status="unknown")
        try:
            stamp.full_clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly")

    def test_stamp_choices(self):
        """Test att val-konstanter fungerar korrekt"""
        # Test STAMP_TYPE_CHOICES
        valid_types = ["text", "symbol", "text_symbol", "label"]
        for stamp_type in valid_types:
            stamp = Stamp.objects.create(
                name=f"Type {stamp_type}", stamp_type=stamp_type
            )
            self.assertEqual(stamp.stamp_type, stamp_type)

        # Test STATUS_CHOICES
        valid_statuses = ["known", "unknown"]
        for status in valid_statuses:
            stamp = Stamp.objects.create(
                name=f"Status {status}",
                status=status,
                manufacturer=self.manufacturer if status == "known" else None,
            )
            self.assertEqual(stamp.status, status)


class StampTranscriptionModelTest(TestCase):
    """Tester för StampTranscription-modellen"""

    def setUp(self):
        """Skapa testdata för varje test"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        self.stamp = Stamp.objects.create(
            name="Transcription Test Stamp", stamp_type="text"
        )

        self.transcription = StampTranscription.objects.create(
            stamp=self.stamp,
            text="TILLVERKARE AB",
            quality="high",
            created_by=self.user,
        )

    def test_transcription_creation(self):
        """Test att skapa en transkribering"""
        self.assertIsNotNone(self.transcription.id)
        self.assertEqual(self.transcription.stamp, self.stamp)
        self.assertEqual(self.transcription.text, "TILLVERKARE AB")
        self.assertEqual(self.transcription.quality, "high")
        self.assertEqual(self.transcription.created_by, self.user)

    def test_transcription_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        expected = "Transcription Test Stamp: TILLVERKARE AB"
        self.assertEqual(str(self.transcription), expected)

    def test_transcription_quality_choices(self):
        """Test kvalitetsval"""
        qualities = ["high", "medium", "low"]
        for quality in qualities:
            transcription = StampTranscription.objects.create(
                stamp=self.stamp, text=f"Text with {quality} quality", quality=quality
            )
            self.assertEqual(transcription.quality, quality)

    def test_transcription_ordering(self):
        """Test att transkriberingar sorteras efter created_at desc"""
        # Skapa ytterligare transkribering
        newer_transcription = StampTranscription.objects.create(
            stamp=self.stamp, text="Newer transcription", quality="medium"
        )

        transcriptions = list(StampTranscription.objects.all())
        self.assertEqual(transcriptions[0], newer_transcription)
        self.assertEqual(transcriptions[1], self.transcription)


class StampTagModelTest(TestCase):
    """Tester för StampTag-modellen"""

    def setUp(self):
        """Skapa testdata för varje test"""
        self.tag = StampTag.objects.create(
            name="Militär",
            description="Stämplar från militära tillverkare",
            color="#ff0000",
        )

    def test_tag_creation(self):
        """Test att skapa en tag"""
        self.assertIsNotNone(self.tag.id)
        self.assertEqual(self.tag.name, "Militär")
        self.assertEqual(self.tag.description, "Stämplar från militära tillverkare")
        self.assertEqual(self.tag.color, "#ff0000")

    def test_tag_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        self.assertEqual(str(self.tag), "Militär")

    def test_tag_default_color(self):
        """Test standardfärg för tag"""
        tag = StampTag.objects.create(name="Default Color Tag")
        self.assertEqual(tag.color, "#007bff")

    def test_tag_ordering(self):
        """Test att taggar sorteras alfabetiskt"""
        tag_z = StampTag.objects.create(name="Zebra")
        tag_a = StampTag.objects.create(name="Alfa")

        tags = list(StampTag.objects.all())
        # Kontrollera att Alfa kommer före Militär som kommer före Zebra
        tag_names = [tag.name for tag in tags]
        expected_order = ["Alfa", "Militär", "Zebra"]
        self.assertEqual(tag_names, expected_order)


class StampImageModelTest(TestCase):
    """Tester för StampImage-modellen"""

    def setUp(self):
        """Skapa testdata för varje test"""
        self.stamp = Stamp.objects.create(name="Image Test Stamp", stamp_type="symbol")

        self.image = StampImage.objects.create(
            stamp=self.stamp,
            image="test_images/stamp1.jpg",
            is_primary=True,
            order=1,
            comment="Primary image",
        )

    def test_image_creation(self):
        """Test att skapa en stämpelbild"""
        self.assertIsNotNone(self.image.id)
        self.assertEqual(self.image.stamp, self.stamp)
        self.assertEqual(self.image.image, "test_images/stamp1.jpg")
        self.assertTrue(self.image.is_primary)
        # Ta bort width/height test eftersom dessa fält inte finns i modellen
        # self.assertEqual(self.image.width, 800)
        # self.assertEqual(self.image.height, 600)

    def test_image_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        # Uppdatera för att matcha den faktiska __str__ implementationen
        expected = "Image Test Stamp - Fristående stämpelbild"
        self.assertEqual(str(self.image), expected)

    def test_image_default_values(self):
        """Test standardvärden för bild"""
        image = StampImage.objects.create(
            stamp=self.stamp, image="test_images/stamp2.jpg"
        )
        self.assertFalse(image.is_primary)
        self.assertEqual(image.order, 0)


class AxeStampModelTest(TestCase):
    """Tester för AxeStamp-modellen"""

    def setUp(self):
        """Skapa testdata för varje test"""
        self.manufacturer = Manufacturer.objects.create(
            name="Axe Manufacturer", manufacturer_type="TILLVERKARE"
        )

        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Modell"
        )

        self.stamp = Stamp.objects.create(name="Axe Stamp", stamp_type="text")

        self.axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp,
            position="Huvudets översida",
            comment="Tydlig stämpel",
            uncertainty_level="certain",
        )

    def test_axe_stamp_creation(self):
        """Test att skapa en yxstämpel"""
        self.assertIsNotNone(self.axe_stamp.id)
        self.assertEqual(self.axe_stamp.axe, self.axe)
        self.assertEqual(self.axe_stamp.stamp, self.stamp)
        self.assertEqual(self.axe_stamp.position, "Huvudets översida")
        self.assertEqual(self.axe_stamp.uncertainty_level, "certain")

    def test_axe_stamp_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        expected = "1 - Axe Stamp"
        self.assertEqual(str(self.axe_stamp), expected)

    def test_axe_stamp_uncertainty_choices(self):
        """Test osäkerhetsval"""
        uncertainties = ["certain", "uncertain", "tentative"]
        for uncertainty in uncertainties:
            axe_stamp = AxeStamp.objects.create(
                axe=self.axe, stamp=self.stamp, uncertainty_level=uncertainty
            )
            self.assertEqual(axe_stamp.uncertainty_level, uncertainty)

    def test_multiple_same_stamps_allowed(self):
        """Test att samma stämpel kan finnas flera gånger på samma yxa"""
        # Detta ska fungera eftersom unique_together togs bort
        axe_stamp2 = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp,
            position="Huvudets undersida",
            uncertainty_level="uncertain",
        )

        self.assertIsNotNone(axe_stamp2.id)
        self.assertEqual(
            AxeStamp.objects.filter(axe=self.axe, stamp=self.stamp).count(), 2
        )


class StampVariantModelTest(TestCase):
    """Tester för StampVariant-modellen"""

    def setUp(self):
        """Skapa testdata för varje test"""
        self.main_stamp = Stamp.objects.create(name="Huvudstämpel", stamp_type="text")

        self.variant_stamp = Stamp.objects.create(
            name="Variantstämpel", stamp_type="text"
        )

        self.variant = StampVariant.objects.create(
            main_stamp=self.main_stamp,
            variant_stamp=self.variant_stamp,
            description="Skillnad i typsnitt",
        )

    def test_variant_creation(self):
        """Test att skapa en stämpelvariant"""
        self.assertIsNotNone(self.variant.id)
        self.assertEqual(self.variant.main_stamp, self.main_stamp)
        self.assertEqual(self.variant.variant_stamp, self.variant_stamp)
        self.assertEqual(self.variant.description, "Skillnad i typsnitt")

    def test_variant_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        expected = "Huvudstämpel - variant av Variantstämpel"
        self.assertEqual(str(self.variant), expected)

    def test_variant_unique_constraint(self):
        """Test att samma variantrelation inte kan skapas två gånger"""
        with self.assertRaises(Exception):  # IntegrityError förväntas
            StampVariant.objects.create(
                main_stamp=self.main_stamp,
                variant_stamp=self.variant_stamp,
                description="Duplicate relation",
            )


class StampUncertaintyGroupModelTest(TestCase):
    """Tester för StampUncertaintyGroup-modellen"""

    def setUp(self):
        """Skapa testdata för varje test"""
        self.stamp1 = Stamp.objects.create(name="Osäker Stämpel 1", stamp_type="text")

        self.stamp2 = Stamp.objects.create(name="Osäker Stämpel 2", stamp_type="text")

        self.uncertainty_group = StampUncertaintyGroup.objects.create(
            name="Liknande Militärstämplar",
            description="Grupp av stämplar som kan vara samma tillverkare",
            confidence_level="medium",
        )

        self.uncertainty_group.stamps.add(self.stamp1, self.stamp2)

    def test_uncertainty_group_creation(self):
        """Test att skapa en osäkerhetsgrupp"""
        self.assertIsNotNone(self.uncertainty_group.id)
        self.assertEqual(self.uncertainty_group.name, "Liknande Militärstämplar")
        self.assertEqual(self.uncertainty_group.confidence_level, "medium")
        self.assertEqual(self.uncertainty_group.stamps.count(), 2)

    def test_uncertainty_group_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        self.assertEqual(str(self.uncertainty_group), "Liknande Militärstämplar")

    def test_uncertainty_group_confidence_choices(self):
        """Test konfidensval"""
        confidences = ["high", "medium", "low"]
        for confidence in confidences:
            group = StampUncertaintyGroup.objects.create(
                name=f"Group {confidence}", confidence_level=confidence
            )
            self.assertEqual(group.confidence_level, confidence)

    def test_stamp_relationships(self):
        """Test relationer mellan stämplar och osäkerhetsgrupper"""
        # Test att stämplar kan kommas åt från gruppen
        stamps_in_group = list(self.uncertainty_group.stamps.all())
        self.assertIn(self.stamp1, stamps_in_group)
        self.assertIn(self.stamp2, stamps_in_group)

        # Test att grupper kan kommas åt från stämpeln
        groups_for_stamp1 = list(self.stamp1.uncertainty_groups.all())
        self.assertIn(self.uncertainty_group, groups_for_stamp1)
