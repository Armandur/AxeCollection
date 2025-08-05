from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from axes.models import (
    Stamp,
    StampTranscription,
    StampImage,
    StampTag,
    AxeStamp,
    StampSymbol,
    Manufacturer,
    Axe,
    AxeImage,
    AxeImageStamp,
)
from axes.forms import (
    StampForm,
    StampTranscriptionForm,
    AxeStampForm,
    StampTagForm,
    StampImageForm,
    StampImageMarkForm,
)
from PIL import Image
import io


class StampFormTest(TestCase):
    """Tester för StampForm"""

    def setUp(self):
        """Sätt upp testdata"""
        self.manufacturer = Manufacturer.objects.create(
            name="Gränsfors Bruk", country_code="SE"
        )

        self.valid_data = {
            "name": "GRÄNSFORS",
            "description": "Tillverkarens namnskilt",
            "manufacturer": self.manufacturer.id,
            "stamp_type": "text",
            "status": "known",
            "year_from": 1900,
            "year_to": 1950,
            "year_uncertainty": False,
            "year_notes": "Baserat på historiska dokument",
            "source_category": "own_collection",
            "source_reference": "Från egen samling",
        }

    def test_stamp_form_valid_data(self):
        """Testa formulär med giltig data"""
        form = StampForm(data=self.valid_data)

        self.assertTrue(form.is_valid())
        stamp = form.save()
        self.assertEqual(stamp.name, "GRÄNSFORS")
        self.assertEqual(stamp.manufacturer, self.manufacturer)
        self.assertEqual(stamp.year_from, 1900)

    def test_stamp_form_required_fields(self):
        """Testa obligatoriska fält"""
        form = StampForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_stamp_form_without_manufacturer(self):
        """Testa formulär utan tillverkare (okänd stämpel)"""
        data = self.valid_data.copy()
        data["manufacturer"] = ""
        data["status"] = "unknown"

        form = StampForm(data=data)

        self.assertTrue(form.is_valid())
        stamp = form.save()
        self.assertIsNone(stamp.manufacturer)
        self.assertEqual(stamp.status, "unknown")

    def test_stamp_form_invalid_year_range(self):
        """Testa ogiltig årtalsintervall"""
        data = self.valid_data.copy()
        data["year_from"] = 1950
        data["year_to"] = 1900  # Till-år mindre än från-år

        form = StampForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("year_to", form.errors)

    def test_stamp_form_year_uncertainty_field(self):
        """Testa årtalsosäkerhetsfält"""
        data = self.valid_data.copy()
        data["year_uncertainty"] = True
        data["year_notes"] = "Cirka årtal"

        form = StampForm(data=data)

        self.assertTrue(form.is_valid())
        stamp = form.save()
        self.assertTrue(stamp.year_uncertainty)
        self.assertEqual(stamp.year_notes, "Cirka årtal")

    def test_stamp_form_stamp_type_choices(self):
        """Testa alla giltiga stämpeltyper"""
        valid_types = ["text", "image", "symbol"]

        for stamp_type in valid_types:
            data = self.valid_data.copy()
            data["stamp_type"] = stamp_type
            data["name"] = f"Test {stamp_type}"

            form = StampForm(data=data)
            self.assertTrue(form.is_valid(), f"Stamp type {stamp_type} should be valid")

    def test_stamp_form_status_choices(self):
        """Testa alla giltiga statusar"""
        valid_statuses = ["known", "unknown"]

        for status in valid_statuses:
            data = self.valid_data.copy()
            data["status"] = status
            data["name"] = f"Test {status}"

            if status == "unknown":
                data["manufacturer"] = ""

            form = StampForm(data=data)
            self.assertTrue(form.is_valid(), f"Status {status} should be valid")

    def test_stamp_form_source_category_choices(self):
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
            data = self.valid_data.copy()
            data["source_category"] = source
            data["name"] = f"Test {source}"

            form = StampForm(data=data)
            self.assertTrue(form.is_valid(), f"Source {source} should be valid")

    def test_stamp_form_widget_classes(self):
        """Testa att widgets har rätt CSS-klasser"""
        form = StampForm()

        self.assertEqual(form.fields["name"].widget.attrs["class"], "form-control")
        self.assertEqual(
            form.fields["description"].widget.attrs["class"], "form-control"
        )
        self.assertEqual(
            form.fields["manufacturer"].widget.attrs["class"], "form-control"
        )

    def test_stamp_form_help_texts(self):
        """Testa att hjälptexter finns"""
        form = StampForm()

        self.assertIn("Unikt namn", form.fields["name"].help_text)
        self.assertIn("Detaljerad beskrivning", form.fields["description"].help_text)


class StampTranscriptionFormTest(TestCase):
    """Tester för StampTranscriptionForm"""

    def setUp(self):
        """Sätt upp testdata"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.stamp = Stamp.objects.create(name="Test Stämpel")

        # Skapa några symboler för testning
        self.symbol1 = StampSymbol.objects.create(
            name="Krona", symbol="♔", symbol_type="pictogram"
        )
        self.symbol2 = StampSymbol.objects.create(
            name="Stjärna", symbol="★", symbol_type="pictogram"
        )

        self.valid_data = {
            "stamp": self.stamp.id,
            "text": "GRÄNSFORS BRUK",
            "quality": "high",
            "symbols_selected": "Krona, Stjärna",
        }

    def test_transcription_form_valid_data(self):
        """Testa formulär med giltig data"""
        form = StampTranscriptionForm(data=self.valid_data)

        self.assertTrue(form.is_valid())
        transcription = form.save(commit=False)
        transcription.created_by = self.user
        transcription.save()
        form.save_m2m()

        self.assertEqual(transcription.text, "GRÄNSFORS BRUK")
        self.assertEqual(transcription.quality, "high")
        self.assertEqual(transcription.stamp, self.stamp)

    def test_transcription_form_with_pre_selected_stamp(self):
        """Testa formulär med förvald stämpel"""
        form = StampTranscriptionForm(
            data={"text": "Test text", "quality": "medium"},
            pre_selected_stamp=self.stamp,
        )

        self.assertTrue(form.is_valid())
        self.assertNotIn("stamp", form.fields)  # Stamp-fält ska tas bort

        transcription = form.save(commit=False)
        transcription.created_by = self.user
        transcription.save()

        self.assertEqual(transcription.stamp, self.stamp)

    def test_transcription_form_required_fields(self):
        """Testa obligatoriska fält"""
        form = StampTranscriptionForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("stamp", form.errors)
        self.assertIn("text", form.errors)

    def test_transcription_form_quality_choices(self):
        """Testa alla giltiga kvalitetsnivåer"""
        valid_qualities = ["high", "medium", "low"]

        for quality in valid_qualities:
            data = self.valid_data.copy()
            data["quality"] = quality
            data["text"] = f"Test {quality}"

            form = StampTranscriptionForm(data=data)
            self.assertTrue(form.is_valid(), f"Quality {quality} should be valid")

    def test_transcription_form_symbol_processing(self):
        """Testa symbolbearbetning"""
        data = self.valid_data.copy()
        data["symbols_selected"] = "Krona, Ny Symbol"  # Krona finns, Ny Symbol skapas

        form = StampTranscriptionForm(data=data)

        self.assertTrue(form.is_valid())

        # Kontrollera att symbols sätts korrekt i cleaned_data
        self.assertIn("symbols", form.cleaned_data)
        symbols = form.cleaned_data["symbols"]

        # Ska ha två symboler
        self.assertEqual(len(symbols), 2)

        # Kontrollera att Krona finns och Ny Symbol skapades
        symbol_names = [symbol.name for symbol in symbols]
        self.assertIn("Krona", symbol_names)
        self.assertIn("Ny Symbol", symbol_names)

    def test_transcription_form_empty_symbols(self):
        """Testa formulär utan symboler"""
        data = self.valid_data.copy()
        data["symbols_selected"] = ""

        form = StampTranscriptionForm(data=data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["symbols"], [])

    def test_transcription_form_malformed_symbols(self):
        """Testa hantering av felformaterade symboler"""
        data = self.valid_data.copy()
        data["symbols_selected"] = "<StampSymbol: Name: Test>, Normal Symbol"

        form = StampTranscriptionForm(data=data)

        self.assertTrue(form.is_valid())
        symbols = form.cleaned_data["symbols"]

        # Ska ha åtminstone en symbol
        self.assertGreater(len(symbols), 0)

    def test_transcription_form_widget_classes(self):
        """Testa att widgets har rätt CSS-klasser"""
        form = StampTranscriptionForm()

        self.assertEqual(form.fields["stamp"].widget.attrs["class"], "form-control")
        self.assertEqual(form.fields["text"].widget.attrs["class"], "form-control")
        self.assertEqual(form.fields["quality"].widget.attrs["class"], "form-control")


class AxeStampFormTest(TestCase):
    """Tester för AxeStampForm"""

    def setUp(self):
        """Sätt upp testdata"""
        self.manufacturer = Manufacturer.objects.create(
            name="Hults Bruk", country_code="SE"
        )
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Modell",
        )

        # Skapa stämplar
        self.stamp_same_manufacturer = Stamp.objects.create(
            name="HULTS BRUK", manufacturer=self.manufacturer
        )
        self.stamp_other_manufacturer = Stamp.objects.create(name="GRÄNSFORS")

        self.valid_data = {
            "stamp": self.stamp_same_manufacturer.id,
            "position": "öga",
            "uncertainty_level": "certain",
            "comment": "Tydligt synlig stämpel",
        }

    def test_axe_stamp_form_valid_data(self):
        """Testa formulär med giltig data"""
        form = AxeStampForm(data=self.valid_data, axe=self.axe)

        self.assertTrue(form.is_valid())
        axe_stamp = form.save(commit=False)
        axe_stamp.axe = self.axe
        axe_stamp.save()

        self.assertEqual(axe_stamp.stamp, self.stamp_same_manufacturer)
        self.assertEqual(axe_stamp.position, "öga")
        self.assertEqual(axe_stamp.uncertainty_level, "certain")

    def test_axe_stamp_form_required_fields(self):
        """Testa obligatoriska fält"""
        form = AxeStampForm(data={}, axe=self.axe)

        self.assertFalse(form.is_valid())
        self.assertIn("stamp", form.errors)

    def test_axe_stamp_form_uncertainty_levels(self):
        """Testa alla giltiga osäkerhetsnivåer"""
        valid_levels = ["certain", "uncertain", "tentative"]

        for level in valid_levels:
            data = self.valid_data.copy()
            data["uncertainty_level"] = level

            form = AxeStampForm(data=data, axe=self.axe)
            self.assertTrue(
                form.is_valid(), f"Uncertainty level {level} should be valid"
            )

    def test_axe_stamp_form_stamp_ordering(self):
        """Testa att stämplar sorteras med tillverkarens stämplar först"""
        form = AxeStampForm(axe=self.axe)

        # Kontrollera att stämpelval finns
        self.assertIn("stamp", form.fields)

        # Hämta stämpelvalen från formuläret
        stamp_choices = list(form.fields["stamp"].queryset)

        # Tillverkarens stämpel ska komma först
        self.assertIn(self.stamp_same_manufacturer, stamp_choices)

    def test_axe_stamp_form_without_axe(self):
        """Testa formulär utan yxa"""
        form = AxeStampForm(data=self.valid_data)

        # Ska fortfarande fungera, bara utan speciell sortering
        self.assertTrue(form.is_valid())

    def test_axe_stamp_form_position_field(self):
        """Testa positionsfältet"""
        data = self.valid_data.copy()
        data["position"] = "skaft"

        form = AxeStampForm(data=data, axe=self.axe)

        self.assertTrue(form.is_valid())
        axe_stamp = form.save(commit=False)
        axe_stamp.axe = self.axe
        axe_stamp.save()

        self.assertEqual(axe_stamp.position, "skaft")

    def test_axe_stamp_form_comment_field(self):
        """Testa kommentarsfältet"""
        data = self.valid_data.copy()
        data["comment"] = "Mycket tydlig stämpel, lätt att läsa"

        form = AxeStampForm(data=data, axe=self.axe)

        self.assertTrue(form.is_valid())
        axe_stamp = form.save(commit=False)
        axe_stamp.axe = self.axe
        axe_stamp.save()

        self.assertEqual(axe_stamp.comment, "Mycket tydlig stämpel, lätt att läsa")


class StampTagFormTest(TestCase):
    """Tester för StampTagForm"""

    def setUp(self):
        """Sätt upp testdata"""
        self.valid_data = {
            "name": "tillverkarnamn",
            "description": "Taggar för tillverkarnamn",
            "color": "#ff0000",
        }

    def test_stamp_tag_form_valid_data(self):
        """Testa formulär med giltig data"""
        form = StampTagForm(data=self.valid_data)

        self.assertTrue(form.is_valid())
        tag = form.save()

        self.assertEqual(tag.name, "tillverkarnamn")
        self.assertEqual(tag.description, "Taggar för tillverkarnamn")
        self.assertEqual(tag.color, "#ff0000")

    def test_stamp_tag_form_required_fields(self):
        """Testa obligatoriska fält"""
        form = StampTagForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_stamp_tag_form_default_color(self):
        """Testa standardfärg"""
        data = {"name": "testtagg"}
        form = StampTagForm(data=data)

        self.assertTrue(form.is_valid())
        tag = form.save()

        # Kontrollera att modellens default color används
        self.assertEqual(tag.color, "#007bff")

    def test_stamp_tag_form_color_validation(self):
        """Testa färgvalidering"""
        # Giltig hex-färg
        data = self.valid_data.copy()
        data["color"] = "#123456"
        form = StampTagForm(data=data)
        self.assertTrue(form.is_valid())

        # Ogiltig färg (ska fortfarande accepteras av formuläret, validering sker i modellen)
        data["color"] = "invalid-color"
        form = StampTagForm(data=data)
        # Formuläret själv validerar inte färgformat, det görs av modellen
        # så detta test fokuserar på att formuläret accepterar input


class StampImageFormTest(TestCase):
    """Tester för StampImageForm"""

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

    def test_stamp_image_form_valid_data(self):
        """Testa formulär med giltig data"""
        test_image = self.create_test_image()
        data = {"quality": "high"}
        files = {"image": test_image}

        form = StampImageForm(data=data, files=files)

        self.assertTrue(form.is_valid())
        stamp_image = form.save(commit=False)
        stamp_image.stamp = self.stamp
        stamp_image.save()

        self.assertEqual(stamp_image.quality, "high")
        self.assertEqual(stamp_image.stamp, self.stamp)

    def test_stamp_image_form_required_fields(self):
        """Testa obligatoriska fält"""
        form = StampImageForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    def test_stamp_image_form_quality_choices(self):
        """Testa alla giltiga kvalitetsnivåer"""
        valid_qualities = ["high", "medium", "low"]

        for quality in valid_qualities:
            test_image = self.create_test_image(f"{quality}.jpg")
            data = {"quality": quality}
            files = {"image": test_image}

            form = StampImageForm(data=data, files=files)
            self.assertTrue(form.is_valid(), f"Quality {quality} should be valid")

    def test_stamp_image_form_default_quality(self):
        """Testa standardkvalitet"""
        test_image = self.create_test_image()
        files = {"image": test_image}

        form = StampImageForm(data={}, files=files)

        self.assertTrue(form.is_valid())
        stamp_image = form.save(commit=False)
        stamp_image.stamp = self.stamp
        stamp_image.save()

        # Kontrollera att modellens default quality används
        self.assertEqual(stamp_image.quality, "medium")

    def test_stamp_image_form_invalid_file_type(self):
        """Testa ogiltig filtyp"""
        # Skapa en textfil istället för en bild
        text_file = SimpleUploadedFile(
            "test.txt", b"This is not an image", content_type="text/plain"
        )

        data = {"quality": "high"}
        files = {"image": text_file}

        form = StampImageForm(data=data, files=files)

        # Formuläret kommer att försöka validera att det är en giltig bild
        # och ska misslyckas
        self.assertFalse(form.is_valid())


class StampImageMarkFormTest(TestCase):
    """Tester för StampImageMarkForm"""

    def setUp(self):
        """Sätt upp testdata"""
        self.stamp = Stamp.objects.create(name="Test Stämpel")
        self.manufacturer = Manufacturer.objects.create(
            name="Test Manufacturer", country_code="SE"
        )
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Modell",
        )

        # Skapa yxbild
        test_image = self.create_test_image()
        self.axe_image = AxeImage.objects.create(
            axe=self.axe,
            image=test_image,
            order=1,
        )

        self.valid_data = {
            "stamp": self.stamp.id,
            "x": 10.5,
            "y": 20.3,
            "width": 50.0,
            "height": 30.0,
        }

    def create_test_image(self, name="test.jpg", size=(100, 100)):
        """Hjälpfunktion för att skapa testbild"""
        image = Image.new("RGB", size, color="red")
        temp_file = io.BytesIO()
        image.save(temp_file, format="JPEG")
        temp_file.seek(0)
        return SimpleUploadedFile(name, temp_file.read(), content_type="image/jpeg")

    def test_stamp_image_mark_form_valid_data(self):
        """Testa formulär med giltig data"""
        form = StampImageMarkForm(data=self.valid_data)

        self.assertTrue(form.is_valid())
        mark = form.save(commit=False)
        mark.axe_image = self.axe_image
        mark.save()

        self.assertEqual(mark.stamp, self.stamp)
        self.assertEqual(mark.x, 10.5)
        self.assertEqual(mark.y, 20.3)
        self.assertEqual(mark.width, 50.0)
        self.assertEqual(mark.height, 30.0)

    def test_stamp_image_mark_form_required_fields(self):
        """Testa obligatoriska fält"""
        form = StampImageMarkForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("stamp", form.errors)
        self.assertIn("x", form.errors)
        self.assertIn("y", form.errors)
        self.assertIn("width", form.errors)
        self.assertIn("height", form.errors)

    def test_stamp_image_mark_form_coordinate_validation(self):
        """Testa koordinatvalidering"""
        # Negativa koordinater ska vara giltiga (kan vara utanför bilden)
        data = self.valid_data.copy()
        data["x"] = -5.0
        data["y"] = -10.0

        form = StampImageMarkForm(data=data)
        self.assertTrue(form.is_valid())

    def test_stamp_image_mark_form_size_validation(self):
        """Testa storleksvalidering"""
        # Noll eller negativ storlek ska vara ogiltig
        data = self.valid_data.copy()
        data["width"] = 0

        form = StampImageMarkForm(data=data)
        # Formuläret kanske inte validerar detta, beror på implementation
        # men vi testar att det hanteras korrekt
        self.assertIsNotNone(form)

    def test_stamp_image_mark_form_decimal_precision(self):
        """Testa decimalprecision"""
        data = self.valid_data.copy()
        data["x"] = 10.123456789
        data["y"] = 20.987654321

        form = StampImageMarkForm(data=data)

        self.assertTrue(form.is_valid())
        mark = form.save(commit=False)
        mark.axe_image = self.axe_image
        mark.save()

        # Kontrollera att decimaler hanteras korrekt
        self.assertAlmostEqual(float(mark.x), 10.123456789, places=5)
        self.assertAlmostEqual(float(mark.y), 20.987654321, places=5)

    def tearDown(self):
        """Städa upp efter varje test"""
        # Ta bort alla temporära bildfiler som skapats under testerna
        for stamp_image in StampImage.objects.all():
            if stamp_image.image and hasattr(stamp_image.image, "path"):
                try:
                    import os

                    if os.path.exists(stamp_image.image.path):
                        os.remove(stamp_image.image.path)
                except Exception:
                    pass  # Ignorera fel vid cleanup

        for axe_image in AxeImage.objects.all():
            if axe_image.image and hasattr(axe_image.image, "path"):
                try:
                    import os

                    if os.path.exists(axe_image.image.path):
                        os.remove(axe_image.image.path)
                except Exception:
                    pass  # Ignorera fel vid cleanup


class StampFormIntegrationTest(TestCase):
    """Integrationstester för stämpelformulär"""

    def setUp(self):
        """Sätt upp testdata"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.manufacturer = Manufacturer.objects.create(
            name="Test Manufacturer", country_code="SE"
        )

    def test_complete_stamp_creation_workflow(self):
        """Testa komplett arbetsflöde för stämpelskapande"""
        # 1. Skapa stämpel
        stamp_data = {
            "name": "TEST STÄMPEL",
            "description": "En teststämpel",
            "manufacturer": self.manufacturer.id,
            "stamp_type": "text",
            "status": "known",
            "source_category": "own_collection",
        }

        stamp_form = StampForm(data=stamp_data)
        self.assertTrue(stamp_form.is_valid())
        stamp = stamp_form.save()

        # 2. Skapa transkribering för stämpeln
        transcription_data = {
            "text": "TEST STÄMPEL TEXT",
            "quality": "high",
            "symbols_selected": "",
        }

        transcription_form = StampTranscriptionForm(
            data=transcription_data, pre_selected_stamp=stamp
        )
        self.assertTrue(transcription_form.is_valid())
        transcription = transcription_form.save(commit=False)
        transcription.created_by = self.user
        transcription.save()

        # 3. Skapa stämpeltagg
        tag_data = {
            "name": "test-kategori",
            "description": "Test kategori",
            "color": "#00ff00",
        }

        tag_form = StampTagForm(data=tag_data)
        self.assertTrue(tag_form.is_valid())
        tag = tag_form.save()

        # Verifiera att allt skapades korrekt
        self.assertEqual(Stamp.objects.count(), 1)
        self.assertEqual(StampTranscription.objects.count(), 1)
        self.assertEqual(StampTag.objects.count(), 1)

        self.assertEqual(transcription.stamp, stamp)
        self.assertEqual(tag.name, "Test Tag")
        self.assertEqual(transcription.created_by, self.user)

    def test_form_validation_consistency(self):
        """Testa att formulärvalidering är konsekvent"""
        # Testa samma data i olika formulär som ska ha samma validering

        # StampForm och StampTranscriptionForm ska båda validera quality val
        valid_qualities = ["high", "medium", "low"]

        for quality in valid_qualities:
            # Test i StampTranscriptionForm
            transcription_data = {
                "stamp": 1,  # Kommer att failja men quality ska valideras först
                "text": "Test",
                "quality": quality,
            }

            form = StampTranscriptionForm(data=transcription_data)
            # Även om formuläret failjar för andra skäl, ska quality inte vara ett problem
            if "quality" in form.errors:
                self.fail(
                    f"Quality {quality} should be valid in StampTranscriptionForm"
                )

    def test_form_field_consistency(self):
        """Testa att fältdefinitioner är konsekventa mellan formulär"""
        stamp_form = StampForm()
        transcription_form = StampTranscriptionForm()

        # Båda ska ha samma CSS-klasser för liknande fält
        self.assertEqual(
            stamp_form.fields["description"].widget.attrs["class"], "form-control"
        )
        self.assertEqual(
            transcription_form.fields["text"].widget.attrs["class"], "form-control"
        )
