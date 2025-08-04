from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from axes.models import (
    Stamp,
    StampTranscription,
    StampImage,
    StampTag,
    AxeStamp,
    StampVariant,
    StampUncertaintyGroup,
    StampSymbol,
    Manufacturer,
    Axe,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
import tempfile
import os


class StampModelTest(TestCase):
    """Tester för Stamp-modellen"""

    def setUp(self):
        """Sätt upp testdata"""
        self.manufacturer = Manufacturer.objects.create(
            name="Gränsfors Bruk", country_code="SE"
        )
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Modell",
        )

    def test_stamp_creation(self):
        """Testa grundläggande skapande av stämpel"""
        stamp = Stamp.objects.create(
            name="GRÄNSFORS",
            description="Tillverkarens namnskilt",
            manufacturer=self.manufacturer,
            stamp_type="text",
            status="known",
        )

        self.assertEqual(stamp.name, "GRÄNSFORS")
        self.assertEqual(stamp.manufacturer, self.manufacturer)
        self.assertEqual(stamp.stamp_type, "text")
        self.assertEqual(stamp.status, "known")
        self.assertIsNotNone(stamp.created_at)
        self.assertIsNotNone(stamp.updated_at)

    def test_stamp_str_representation(self):
        """Testa strängrepresentation av stämpel"""
        stamp = Stamp.objects.create(name="HULTS BRUK")
        self.assertEqual(str(stamp), "HULTS BRUK")

    def test_stamp_without_manufacturer(self):
        """Testa stämpel utan tillverkare (okänd stämpel)"""
        stamp = Stamp.objects.create(
            name="Okänd stämpel",
            description="En okänd stämpel",
            manufacturer=None,
            status="unknown",
        )

        self.assertIsNone(stamp.manufacturer)
        self.assertEqual(stamp.status, "unknown")

    def test_stamp_type_choices(self):
        """Testa alla giltigga stämpeltyper"""
        valid_types = ["text", "image", "symbol"]

        for stamp_type in valid_types:
            stamp = Stamp.objects.create(
                name=f"Test {stamp_type}",
                stamp_type=stamp_type,
            )
            self.assertEqual(stamp.stamp_type, stamp_type)

    def test_stamp_status_choices(self):
        """Testa alla giltiga statusar"""
        valid_statuses = ["known", "unknown"]

        for status in valid_statuses:
            stamp = Stamp.objects.create(
                name=f"Test {status}",
                status=status,
            )
            self.assertEqual(stamp.status, status)

    def test_stamp_source_category_choices(self):
        """Testa alla giltiga källkategorier"""
        valid_sources = [
            "own_collection",
            "ebay_auction",
            "museum",
            "private_collector",
            "book_article",
            "internet",
            "unknown",
        ]

        for source in valid_sources:
            stamp = Stamp.objects.create(
                name=f"Test {source}",
                source_category=source,
            )
            self.assertEqual(stamp.source_category, source)

    def test_stamp_year_fields(self):
        """Testa årtalshantering"""
        stamp = Stamp.objects.create(
            name="Årtalsstämpel",
            year_from=1900,
            year_to=1950,
            year_uncertainty=True,
            year_notes="Ungefärliga årtal baserat på stil",
        )

        self.assertEqual(stamp.year_from, 1900)
        self.assertEqual(stamp.year_to, 1950)
        self.assertTrue(stamp.year_uncertainty)
        self.assertEqual(stamp.year_notes, "Ungefärliga årtal baserat på stil")

    def test_stamp_ordering(self):
        """Testa att stämplar sorteras efter namn som standard"""
        stamp_b = Stamp.objects.create(name="B Stämpel")
        stamp_a = Stamp.objects.create(name="A Stämpel")
        stamp_c = Stamp.objects.create(name="C Stämpel")

        stamps = list(Stamp.objects.all())
        self.assertEqual(stamps[0], stamp_a)
        self.assertEqual(stamps[1], stamp_b)
        self.assertEqual(stamps[2], stamp_c)


class StampTranscriptionModelTest(TestCase):
    """Tester för StampTranscription-modellen"""

    def setUp(self):
        """Sätt upp testdata"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.stamp = Stamp.objects.create(name="Test Stämpel")

    def test_transcription_creation(self):
        """Testa grundläggande skapande av transkribering"""
        transcription = StampTranscription.objects.create(
            stamp=self.stamp,
            text="GRÄNSFORS BRUK",
            quality="high",
            created_by=self.user,
        )

        self.assertEqual(transcription.stamp, self.stamp)
        self.assertEqual(transcription.text, "GRÄNSFORS BRUK")
        self.assertEqual(transcription.quality, "high")
        self.assertEqual(transcription.created_by, self.user)
        self.assertIsNotNone(transcription.created_at)

    def test_transcription_str_representation(self):
        """Testa strängrepresentation av transkribering"""
        transcription = StampTranscription.objects.create(
            stamp=self.stamp,
            text="TEST TEXT",
        )
        expected = f"TEST TEXT (Test Stämpel)"
        self.assertEqual(str(transcription), expected)

    def test_transcription_quality_choices(self):
        """Testa alla giltiga kvalitetsnivåer"""
        valid_qualities = ["high", "medium", "low"]

        for quality in valid_qualities:
            transcription = StampTranscription.objects.create(
                stamp=self.stamp,
                text=f"Test {quality}",
                quality=quality,
            )
            self.assertEqual(transcription.quality, quality)

    def test_transcription_without_user(self):
        """Testa transkribering utan användare"""
        transcription = StampTranscription.objects.create(
            stamp=self.stamp,
            text="Anonym transkribering",
            created_by=None,
        )

        self.assertIsNone(transcription.created_by)
        self.assertEqual(transcription.text, "Anonym transkribering")

    def test_transcription_ordering(self):
        """Testa att transkriberingar sorteras efter datum (nyaste först)"""
        first = StampTranscription.objects.create(stamp=self.stamp, text="Första")
        second = StampTranscription.objects.create(stamp=self.stamp, text="Andra")
        third = StampTranscription.objects.create(stamp=self.stamp, text="Tredje")

        transcriptions = list(StampTranscription.objects.all())
        self.assertEqual(transcriptions[0], third)
        self.assertEqual(transcriptions[1], second)
        self.assertEqual(transcriptions[2], first)

    def test_transcription_related_manager(self):
        """Testa related manager från Stamp till transkriberingar"""
        transcription1 = StampTranscription.objects.create(
            stamp=self.stamp, text="Första transkribering"
        )
        transcription2 = StampTranscription.objects.create(
            stamp=self.stamp, text="Andra transkribering"
        )

        self.assertEqual(self.stamp.transcriptions.count(), 2)
        self.assertIn(transcription1, self.stamp.transcriptions.all())
        self.assertIn(transcription2, self.stamp.transcriptions.all())


class StampImageModelTest(TestCase):
    """Tester för StampImage-modellen"""

    def setUp(self):
        """Sätt upp testdata"""
        self.stamp = Stamp.objects.create(name="Test Stämpel")

    def create_test_image(self, name="test.jpg", size=(100, 100)):
        """Hjälpfunktion för att skapa testbild"""
        image = Image.new("RGB", size, color="red")
        temp_file = io.BytesIO()
        image.save(temp_file, format="JPEG")
        temp_file.seek(0)
        return SimpleUploadedFile(name, temp_file.read(), content_type="image/jpeg")

    def test_stamp_image_creation(self):
        """Testa grundläggande skapande av stämpelbild"""
        test_image = self.create_test_image()

        stamp_image = StampImage.objects.create(
            stamp=self.stamp,
            image=test_image,
            quality="high",
        )

        self.assertEqual(stamp_image.stamp, self.stamp)
        self.assertEqual(stamp_image.quality, "high")
        self.assertIsNotNone(stamp_image.uploaded_at)
        self.assertTrue(stamp_image.image.name.startswith("stamps/"))

    def test_stamp_image_str_representation(self):
        """Testa strängrepresentation av stämpelbild"""
        test_image = self.create_test_image("cool_stamp.jpg")

        stamp_image = StampImage.objects.create(
            stamp=self.stamp,
            image=test_image,
        )

        expected = f"cool_stamp.jpg (Test Stämpel)"
        self.assertEqual(str(stamp_image), expected)

    def test_stamp_image_quality_choices(self):
        """Testa alla giltiga kvalitetsnivåer"""
        valid_qualities = ["high", "medium", "low"]

        for quality in valid_qualities:
            test_image = self.create_test_image(f"{quality}.jpg")
            stamp_image = StampImage.objects.create(
                stamp=self.stamp,
                image=test_image,
                quality=quality,
            )
            self.assertEqual(stamp_image.quality, quality)

    def test_stamp_image_ordering(self):
        """Testa att stämpelbilder sorteras efter uppladdningsdatum (nyaste först)"""
        first_image = self.create_test_image("first.jpg")
        second_image = self.create_test_image("second.jpg")
        third_image = self.create_test_image("third.jpg")

        first = StampImage.objects.create(stamp=self.stamp, image=first_image)
        second = StampImage.objects.create(stamp=self.stamp, image=second_image)
        third = StampImage.objects.create(stamp=self.stamp, image=third_image)

        images = list(StampImage.objects.all())
        self.assertEqual(images[0], third)
        self.assertEqual(images[1], second)
        self.assertEqual(images[2], first)

    def test_stamp_image_related_manager(self):
        """Testa related manager från Stamp till bilder"""
        image1 = self.create_test_image("image1.jpg")
        image2 = self.create_test_image("image2.jpg")

        stamp_image1 = StampImage.objects.create(stamp=self.stamp, image=image1)
        stamp_image2 = StampImage.objects.create(stamp=self.stamp, image=image2)

        self.assertEqual(self.stamp.images.count(), 2)
        self.assertIn(stamp_image1, self.stamp.images.all())
        self.assertIn(stamp_image2, self.stamp.images.all())


class AxeStampModelTest(TestCase):
    """Tester för AxeStamp-modellen (koppling mellan yxor och stämplar)"""

    def setUp(self):
        """Sätt upp testdata"""
        self.manufacturer = Manufacturer.objects.create(
            name="Hults Bruk", country_code="SE"
        )
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Modell",
        )
        self.stamp = Stamp.objects.create(
            name="HULTS BRUK", manufacturer=self.manufacturer
        )

    def test_axe_stamp_creation(self):
        """Testa grundläggande skapande av yxstämpel-koppling"""
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp,
            comment="Tydligt synlig stämpel",
            position="öga",
            uncertainty_level="certain",
        )

        self.assertEqual(axe_stamp.axe, self.axe)
        self.assertEqual(axe_stamp.stamp, self.stamp)
        self.assertEqual(axe_stamp.comment, "Tydligt synlig stämpel")
        self.assertEqual(axe_stamp.position, "öga")
        self.assertEqual(axe_stamp.uncertainty_level, "certain")
        self.assertIsNotNone(axe_stamp.created_at)

    def test_axe_stamp_str_representation(self):
        """Testa strängrepresentation av yxstämpel"""
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp,
        )

        expected = f"HULTS BRUK på Yxa #{self.axe.id}"
        self.assertEqual(str(axe_stamp), expected)

    def test_axe_stamp_uncertainty_levels(self):
        """Testa alla giltiga osäkerhetsnivåer"""
        valid_levels = ["certain", "uncertain", "tentative"]

        for level in valid_levels:
            # Skapa ny yxa för varje test p.g.a. unique constraint
            axe = Axe.objects.create(
                manufacturer=self.manufacturer,
                model=f"Test Modell {level}",
            )

            axe_stamp = AxeStamp.objects.create(
                axe=axe,
                stamp=self.stamp,
                uncertainty_level=level,
            )
            self.assertEqual(axe_stamp.uncertainty_level, level)

    def test_axe_stamp_unique_constraint(self):
        """Testa att samma stämpel inte kan kopplas till samma yxa två gånger"""
        AxeStamp.objects.create(axe=self.axe, stamp=self.stamp)

        with self.assertRaises(IntegrityError):
            AxeStamp.objects.create(axe=self.axe, stamp=self.stamp)

    def test_axe_stamp_related_managers(self):
        """Testa related managers från båda modeller"""
        axe_stamp = AxeStamp.objects.create(axe=self.axe, stamp=self.stamp)

        # Testa från yxa till stämplar
        self.assertEqual(self.axe.stamps.count(), 1)
        self.assertIn(axe_stamp, self.axe.stamps.all())

        # Testa från stämpel till yxor
        self.assertEqual(self.stamp.axes.count(), 1)
        self.assertIn(axe_stamp, self.stamp.axes.all())

    def test_axe_stamp_ordering(self):
        """Testa att yxstämplar sorteras efter datum (nyaste först)"""
        # Skapa ytterligare yxor för testning
        axe2 = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Modell 2",
        )

        stamp2 = Stamp.objects.create(name="MADE IN SWEDEN")

        first = AxeStamp.objects.create(axe=self.axe, stamp=self.stamp)
        second = AxeStamp.objects.create(axe=axe2, stamp=stamp2)

        axe_stamps = list(AxeStamp.objects.all())
        self.assertEqual(axe_stamps[0], second)
        self.assertEqual(axe_stamps[1], first)


class StampVariantModelTest(TestCase):
    """Tester för StampVariant-modellen"""

    def setUp(self):
        """Sätt upp testdata"""
        self.main_stamp = Stamp.objects.create(name="GRÄNSFORS")
        self.variant_stamp = Stamp.objects.create(name="GRÄNSFORS (variant)")

    def test_stamp_variant_creation(self):
        """Testa grundläggande skapande av stämpelvariant"""
        variant = StampVariant.objects.create(
            main_stamp=self.main_stamp,
            variant_stamp=self.variant_stamp,
            description="Variant med annorlunda typsnitt",
        )

        self.assertEqual(variant.main_stamp, self.main_stamp)
        self.assertEqual(variant.variant_stamp, self.variant_stamp)
        self.assertEqual(variant.description, "Variant med annorlunda typsnitt")
        self.assertIsNotNone(variant.created_at)

    def test_stamp_variant_str_representation(self):
        """Testa strängrepresentation av stämpelvariant"""
        variant = StampVariant.objects.create(
            main_stamp=self.main_stamp,
            variant_stamp=self.variant_stamp,
        )

        expected = "GRÄNSFORS (variant) variant av GRÄNSFORS"
        self.assertEqual(str(variant), expected)

    def test_stamp_variant_unique_constraint(self):
        """Testa att samma variant inte kan skapas två gånger"""
        StampVariant.objects.create(
            main_stamp=self.main_stamp,
            variant_stamp=self.variant_stamp,
        )

        with self.assertRaises(IntegrityError):
            StampVariant.objects.create(
                main_stamp=self.main_stamp,
                variant_stamp=self.variant_stamp,
            )

    def test_stamp_variant_related_managers(self):
        """Testa related managers"""
        variant = StampVariant.objects.create(
            main_stamp=self.main_stamp,
            variant_stamp=self.variant_stamp,
        )

        # Testa från huvudstämpel till varianter
        self.assertEqual(self.main_stamp.variants.count(), 1)
        self.assertIn(variant, self.main_stamp.variants.all())

        # Testa från variant till huvudstämpel
        self.assertEqual(self.variant_stamp.main_stamp.count(), 1)
        self.assertIn(variant, self.variant_stamp.main_stamp.all())


class StampTagModelTest(TestCase):
    """Tester för StampTag-modellen"""

    def test_stamp_tag_creation(self):
        """Testa grundläggande skapande av stämpeltagg"""
        tag = StampTag.objects.create(
            name="tillverkarnamn",
            description="Taggar för tillverkarnamn",
            color="#ff0000",
        )

        self.assertEqual(tag.name, "tillverkarnamn")
        self.assertEqual(tag.description, "Taggar för tillverkarnamn")
        self.assertEqual(tag.color, "#ff0000")
        self.assertIsNotNone(tag.created_at)

    def test_stamp_tag_str_representation(self):
        """Testa strängrepresentation av stämpeltagg"""
        tag = StampTag.objects.create(name="kvalitet")
        self.assertEqual(str(tag), "kvalitet")

    def test_stamp_tag_default_color(self):
        """Testa standardfärg för taggar"""
        tag = StampTag.objects.create(name="testtagg")
        self.assertEqual(tag.color, "#007bff")

    def test_stamp_tag_ordering(self):
        """Testa att taggar sorteras efter namn"""
        tag_c = StampTag.objects.create(name="C-tagg")
        tag_a = StampTag.objects.create(name="A-tagg")
        tag_b = StampTag.objects.create(name="B-tagg")

        tags = list(StampTag.objects.all())
        self.assertEqual(tags[0], tag_a)
        self.assertEqual(tags[1], tag_b)
        self.assertEqual(tags[2], tag_c)


class StampUncertaintyGroupModelTest(TestCase):
    """Tester för StampUncertaintyGroup-modellen"""

    def setUp(self):
        """Sätt upp testdata"""
        self.stamp1 = Stamp.objects.create(name="Stämpel 1")
        self.stamp2 = Stamp.objects.create(name="Stämpel 2")
        self.stamp3 = Stamp.objects.create(name="Stämpel 3")

    def test_uncertainty_group_creation(self):
        """Testa grundläggande skapande av osäkerhetsgrupp"""
        group = StampUncertaintyGroup.objects.create(
            name="Okända stämplar från 1800-talet",
            description="Grupp av stämplar från 1800-talet med okänd tillverkare",
            confidence_level="low",
        )

        self.assertEqual(group.name, "Okända stämplar från 1800-talet")
        self.assertEqual(group.confidence_level, "low")
        self.assertIsNotNone(group.created_at)

    def test_uncertainty_group_str_representation(self):
        """Testa strängrepresentation av osäkerhetsgrupp"""
        group = StampUncertaintyGroup.objects.create(
            name="Testgrupp",
        )
        self.assertEqual(str(group), "Testgrupp")

    def test_uncertainty_group_confidence_levels(self):
        """Testa alla giltiga konfidensnivåer"""
        valid_levels = ["high", "medium", "low"]

        for level in valid_levels:
            group = StampUncertaintyGroup.objects.create(
                name=f"Grupp {level}",
                confidence_level=level,
            )
            self.assertEqual(group.confidence_level, level)

    def test_uncertainty_group_many_to_many(self):
        """Testa many-to-many relation med stämplar"""
        group = StampUncertaintyGroup.objects.create(
            name="Testgrupp",
        )

        # Lägg till stämplar i gruppen
        group.stamps.add(self.stamp1, self.stamp2)

        self.assertEqual(group.stamps.count(), 2)
        self.assertIn(self.stamp1, group.stamps.all())
        self.assertIn(self.stamp2, group.stamps.all())

        # Testa reverse relation
        self.assertEqual(self.stamp1.uncertainty_groups.count(), 1)
        self.assertIn(group, self.stamp1.uncertainty_groups.all())

    def test_uncertainty_group_ordering(self):
        """Testa att grupper sorteras efter datum (nyaste först)"""
        first = StampUncertaintyGroup.objects.create(name="Första gruppen")
        second = StampUncertaintyGroup.objects.create(name="Andra gruppen")
        third = StampUncertaintyGroup.objects.create(name="Tredje gruppen")

        groups = list(StampUncertaintyGroup.objects.all())
        self.assertEqual(groups[0], third)
        self.assertEqual(groups[1], second)
        self.assertEqual(groups[2], first)


class StampSymbolModelTest(TestCase):
    """Tester för StampSymbol-modellen"""

    def test_stamp_symbol_creation(self):
        """Testa grundläggande skapande av stämpelsymbol"""
        symbol = StampSymbol.objects.create(
            name="Krona",
            symbol="♔",
            symbol_type="pictogram",
            description="Kunglig krona symbol",
        )

        self.assertEqual(symbol.name, "Krona")
        self.assertEqual(symbol.symbol, "♔")
        self.assertEqual(symbol.symbol_type, "pictogram")
        self.assertEqual(symbol.description, "Kunglig krona symbol")
        self.assertIsNotNone(symbol.created_at)

    def test_stamp_symbol_str_representation(self):
        """Testa strängrepresentation av stämpelsymbol"""
        symbol = StampSymbol.objects.create(
            name="Stjärna",
            symbol="★",
        )
        expected = "Stjärna (★)"
        self.assertEqual(str(symbol), expected)

    def test_stamp_symbol_ordering(self):
        """Testa att symboler sorteras efter namn"""
        symbol_c = StampSymbol.objects.create(name="C-symbol", symbol="C")
        symbol_a = StampSymbol.objects.create(name="A-symbol", symbol="A")
        symbol_b = StampSymbol.objects.create(name="B-symbol", symbol="B")

        symbols = list(StampSymbol.objects.all())
        self.assertEqual(symbols[0], symbol_a)
        self.assertEqual(symbols[1], symbol_b)
        self.assertEqual(symbols[2], symbol_c)

    def test_stamp_symbol_unique_name(self):
        """Testa att symbolnamn är unika"""
        StampSymbol.objects.create(name="Unik Symbol", symbol="U")

        with self.assertRaises(IntegrityError):
            StampSymbol.objects.create(name="Unik Symbol", symbol="V")

    def tearDown(self):
        """Städa upp efter varje test"""
        # Ta bort alla temporära bildfiler som skapats under testerna
        for stamp_image in StampImage.objects.all():
            if stamp_image.image and os.path.exists(stamp_image.image.path):
                os.remove(stamp_image.image.path)
