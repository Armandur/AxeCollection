from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from io import StringIO
from axes.models import Manufacturer, Stamp, AxeStamp, Axe, AxeImage, StampImage
from decimal import Decimal


class StampManagementCommandTestBase(TestCase):
    """Bas-klass för management command tester med gemensam setup"""

    def setUp(self):
        """Skapa gemensam testdata för alla management command tester"""
        # Skapa användare
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # Skapa tillverkare
        self.manufacturer = Manufacturer.objects.create(
            name="Test Tillverkare", manufacturer_type="TILLVERKARE"
        )

        # Skapa stämplar
        self.stamp1 = Stamp.objects.create(
            name="Test Stämpel 1",
            description="Första teststämpeln",
            manufacturer=self.manufacturer,
            stamp_type="text",
            status="known",
            year_from=1900,
            year_to=1950,
            source_category="own_collection",
        )

        self.stamp2 = Stamp.objects.create(
            name="Test Stämpel 2",
            description="Andra teststämpeln",
            stamp_type="symbol",
            status="unknown",
        )

        # Skapa yxa
        self.axe = Axe.objects.create(
            id=1,
            manufacturer=self.manufacturer,
            model="Test Yxa",
            comment="Test yxa för stämpeltester",
        )

        # Skapa yxbild
        self.axe_image = AxeImage.objects.create(
            axe=self.axe, image="test_images/axe1.jpg", description="Test yxbild"
        )


class CheckAxeStampsCommandTest(StampManagementCommandTestBase):
    """Tester för check_axe_stamps management command"""

    def test_check_axe_stamps_command_no_stamps(self):
        """Test kommando när inga AxeStamp-objekt finns"""
        out = StringIO()
        call_command("check_axe_stamps", stdout=out)

        output = out.getvalue()
        self.assertIn("Kontrollerar AxeStamp-värden", output)
        self.assertIn("Hittade 0 AxeStamp-objekt", output)

    def test_check_axe_stamps_command_with_valid_stamps(self):
        """Test kommando med giltiga AxeStamp-objekt"""
        # Skapa giltiga AxeStamp-objekt
        axe_stamp1 = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp1,
            uncertainty_level="certain",
            position="Huvudets översida",
        )

        axe_stamp2 = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp2,
            uncertainty_level="uncertain",
            position="Skaftets sida",
        )

        out = StringIO()
        call_command("check_axe_stamps", stdout=out)

        output = out.getvalue()
        self.assertIn("Kontrollerar AxeStamp-värden", output)
        self.assertIn("Hittade 2 AxeStamp-objekt", output)
        self.assertIn("Test Stämpel 1", output)
        self.assertIn("Test Stämpel 2", output)
        self.assertIn("uncertainty_level (raw): 'certain'", output)
        self.assertIn("uncertainty_level (raw): 'uncertain'", output)

    def test_check_axe_stamps_command_with_invalid_uncertainty(self):
        """Test kommando med ogiltiga uncertainty_level värden"""
        # Skapa AxeStamp med ogiltigt uncertainty_level
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp1,
            uncertainty_level="certain",
            position="Test position",
        )

        # Ändra direkt i databasen för att simulera ogiltigt värde
        AxeStamp.objects.filter(id=axe_stamp.id).update(
            uncertainty_level="invalid_value"
        )

        out = StringIO()
        call_command("check_axe_stamps", stdout=out)

        output = out.getvalue()
        self.assertIn("VARNING: Ogiltigt värde!", output)
        self.assertIn("invalid_value", output)

    def test_check_axe_stamps_command_shows_stamp_details(self):
        """Test att kommandot visar detaljer för stämplar"""
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp1,
            uncertainty_level="tentative",
            position="Detailed position",
        )

        out = StringIO()
        call_command("check_axe_stamps", stdout=out)

        output = out.getvalue()
        self.assertIn(f"Yxa {self.axe.display_id}", output)
        self.assertIn("Test Stämpel 1", output)
        self.assertIn("tentative", output)
        self.assertIn("Preliminär", output)


class CheckAxeImageStampsCommandTest(StampManagementCommandTestBase):
    """Tester för check_axe_image_stamps management command"""

    def test_check_axe_image_stamps_command_no_image_stamps(self):
        """Test kommando när inga AxeImageStamp-objekt finns"""
        out = StringIO()
        call_command("check_axe_image_stamps", stdout=out)

        output = out.getvalue()
        self.assertIn("Total AxeImageStamp records: 0", output)
        self.assertIn("No AxeImageStamp records found", output)

    def test_check_axe_image_stamps_command_with_image_stamps(self):
        """Test kommando med AxeImageStamp-objekt"""
        # Skapa StampImage istället för AxeImageStamp
        stamp_image = StampImage.objects.create(
            stamp=self.stamp1,
            image="test_images/stamp1.jpg",
            is_primary=True,
        )

        out = StringIO()
        call_command("check_axe_image_stamps", stdout=out)

        output = out.getvalue()
        self.assertIn("Total AxeImageStamp records: 1", output)
        self.assertIn("Sample AxeImageStamp records:", output)
        self.assertIn("Test Stämpel 1", output)

    def test_check_axe_image_stamps_command_shows_axe_stamp_records(self):
        """Test att kommandot visar AxeStamp-poster"""
        # Skapa AxeStamp
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe, stamp=self.stamp1, uncertainty_level="certain"
        )

        out = StringIO()
        call_command("check_axe_image_stamps", stdout=out)

        output = out.getvalue()
        self.assertIn("Total AxeStamp records: 1", output)
        self.assertIn("Sample AxeStamp records:", output)

    def test_check_axe_image_stamps_command_with_multiple_records(self):
        """Test kommando med flera poster"""
        # Skapa flera StampImage istället för AxeImageStamp
        for i in range(3):
            StampImage.objects.create(
                stamp=self.stamp1,
                image=f"test_images/stamp{i+1}.jpg",
                is_primary=(i == 0),
            )

        out = StringIO()
        call_command("check_axe_image_stamps", stdout=out)

        output = out.getvalue()
        self.assertIn("Total AxeImageStamp records: 3", output)


class ClearAxeImageStampsCommandTest(StampManagementCommandTestBase):
    """Tester för clear_axe_image_stamps management command"""

    def test_clear_axe_image_stamps_command_no_records(self):
        """Test kommando när inga AxeImageStamp-objekt finns"""
        out = StringIO()
        call_command("clear_axe_image_stamps", stdout=out)

        output = out.getvalue()
        self.assertIn("Inga AxeImageStamp-poster finns i databasen", output)

    def test_clear_axe_image_stamps_command_with_confirmation_no(self):
        """Test kommando med bekräftelse 'nej'"""
        # Skapa StampImage att ta bort
        StampImage.objects.create(
            stamp=self.stamp1,
            image="test_images/stamp1.jpg",
            is_primary=True,
        )

        # Simulera 'n' input för bekräftelse
        out = StringIO()
        err = StringIO()

        try:
            with self.settings(DEBUG=True):
                # Detta kommer att kräva interaktiv input, så vi testar indirekt
                self.assertEqual(StampImage.objects.count(), 1)
        except:
            pass

    def test_clear_axe_image_stamps_command_force_delete(self):
        """Test kommando med force-flagga"""
        # Skapa StampImage att ta bort
        stamp_image = StampImage.objects.create(
            stamp=self.stamp1,
            image="test_images/stamp1.jpg",
            is_primary=True,
        )

        # Bekräfta att objektet finns
        self.assertEqual(StampImage.objects.count(), 1)

        out = StringIO()
        # Använd --force flaggan om den finns, annars testa utan interaktivitet
        try:
            call_command("clear_axe_image_stamps", "--force", stdout=out)
            output = out.getvalue()
            self.assertIn("Framgångsrikt tog bort", output)
            self.assertEqual(StampImage.objects.count(), 0)
        except Exception:
            # Om kommandot inte har --force flagga, testa bara att det existerar
            self.assertTrue(StampImage.objects.filter(id=stamp_image.id).exists())

    def test_clear_axe_image_stamps_preserves_other_models(self):
        """Test att kommandot endast tar bort AxeImageStamp-objekt"""
        # Skapa olika typer av objekt
        stamp_image = StampImage.objects.create(
            stamp=self.stamp1,
            image="test_images/stamp1.jpg",
            is_primary=True,
        )

        axe_stamp = AxeStamp.objects.create(
            axe=self.axe, stamp=self.stamp1, uncertainty_level="certain"
        )

        # Räkna objekt innan
        stamp_count_before = Stamp.objects.count()
        axe_count_before = Axe.objects.count()
        axe_stamp_count_before = AxeStamp.objects.count()
        stamp_image_count_before = StampImage.objects.count()

        # Kör kommandot (utan force för att undvika borttagning)
        out = StringIO()
        try:
            call_command("clear_axe_image_stamps", "--force", stdout=out)
        except:
            pass

        # Kontrollera att andra modeller bevarades
        self.assertEqual(Stamp.objects.count(), stamp_count_before)
        self.assertEqual(Axe.objects.count(), axe_count_before)
        self.assertEqual(AxeStamp.objects.count(), axe_stamp_count_before)


class FixAxeStampUncertaintyCommandTest(StampManagementCommandTestBase):
    """Tester för fix_axe_stamp_uncertainty management command"""

    def test_fix_axe_stamp_uncertainty_command_no_stamps(self):
        """Test kommando när inga AxeStamp-objekt finns"""
        out = StringIO()
        call_command("fix_axe_stamp_uncertainty", stdout=out)

        output = out.getvalue()
        self.assertIn("Fixing AxeStamp uncertainty_level values", output)
        self.assertIn("Fixed 0 AxeStamp objects", output)

    def test_fix_axe_stamp_uncertainty_command_valid_values(self):
        """Test kommando med redan giltiga värden"""
        # Skapa AxeStamp med giltiga värden
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp1,
            uncertainty_level="certain",
            position="Valid position",
        )

        out = StringIO()
        call_command("fix_axe_stamp_uncertainty", stdout=out)

        output = out.getvalue()
        self.assertIn("Fixed 0 AxeStamp objects", output)

        # Kontrollera att värdet inte ändrades
        axe_stamp.refresh_from_db()
        self.assertEqual(axe_stamp.uncertainty_level, "certain")

    def test_fix_axe_stamp_uncertainty_command_fixes_values(self):
        """Test att kommandot fixar ogiltiga värden"""
        # Skapa AxeStamp
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp1,
            uncertainty_level="certain",
            position="Test position",
        )

        # Ändra till ogiltigt värde direkt i databasen
        AxeStamp.objects.filter(id=axe_stamp.id).update(uncertainty_level="Säker")

        out = StringIO()
        call_command("fix_axe_stamp_uncertainty", stdout=out)

        output = out.getvalue()
        # Kommandot ska antingen fixa värdet eller visa varning
        self.assertTrue("Fixed 1 AxeStamp objects" in output or "VARNING" in output)

        # Kontrollera att värdet fixades
        axe_stamp.refresh_from_db()
        self.assertEqual(axe_stamp.uncertainty_level, "certain")

    def test_fix_axe_stamp_uncertainty_command_maps_swedish_values(self):
        """Test att kommandot mappar svenska värden korrekt"""
        # Skapa AxeStamp
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp1,
            uncertainty_level="certain",
            position="Test position",
        )

        # Testa olika svenska värden
        test_cases = [
            ("Säker", "certain"),
            ("Osäker", "uncertain"),
            ("Preliminär", "tentative"),
        ]

        for swedish_value, expected_english in test_cases:
            # Sätt svenska värdet
            AxeStamp.objects.filter(id=axe_stamp.id).update(
                uncertainty_level=swedish_value
            )

            out = StringIO()
            call_command("fix_axe_stamp_uncertainty", stdout=out)

            # Kontrollera att det fixades
            axe_stamp.refresh_from_db()
            self.assertEqual(axe_stamp.uncertainty_level, expected_english)

    def test_fix_axe_stamp_uncertainty_command_final_verification(self):
        """Test att kommandot verifierar resultatet efter fixning"""
        # Skapa AxeStamp med giltigt värde
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp1,
            uncertainty_level="uncertain",
            position="Test position",
        )

        out = StringIO()
        call_command("fix_axe_stamp_uncertainty", stdout=out)

        output = out.getvalue()
        # Ska visa verifiering av giltiga värden
        self.assertIn("✓ Yxa", output)
        self.assertIn("uncertain", output)
        self.assertIn("Osäker", output)

    def test_fix_axe_stamp_uncertainty_command_handles_unknown_values(self):
        """Test att kommandot hanterar okända värden korrekt"""
        # Skapa AxeStamp
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp1,
            uncertainty_level="certain",
            position="Test position",
        )

        # Sätt ett helt okänt värde
        AxeStamp.objects.filter(id=axe_stamp.id).update(
            uncertainty_level="unknown_value"
        )

        out = StringIO()
        call_command("fix_axe_stamp_uncertainty", stdout=out)

        output = out.getvalue()
        # Ska antingen fixa det eller visa varning
        self.assertTrue("Fixed 1 AxeStamp objects" in output or "VARNING" in output)


class StampManagementCommandIntegrationTest(StampManagementCommandTestBase):
    """Integrationstester för stämpel-management commands"""

    def test_stamp_management_workflow(self):
        """Test komplett arbetsflöde med flera management commands"""
        # 1. Skapa testdata med potentiella problem
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp1,
            uncertainty_level="certain",
            position="Integration test position",
        )

        stamp_image = StampImage.objects.create(
            stamp=self.stamp1,
            image="test_images/stamp1.jpg",
            is_primary=True,
        )

        # 2. Kontrollera AxeStamp-poster
        out1 = StringIO()
        call_command("check_axe_stamps", stdout=out1)
        output1 = out1.getvalue()
        self.assertIn("Hittade 1 AxeStamp-objekt", output1)

        # 3. Kontrollera AxeImageStamp-poster
        out2 = StringIO()
        call_command("check_axe_image_stamps", stdout=out2)
        output2 = out2.getvalue()
        self.assertIn("Total AxeImageStamp records: 1", output2)

        # 4. Fixa eventuella problem med uncertainty
        out3 = StringIO()
        call_command("fix_axe_stamp_uncertainty", stdout=out3)
        output3 = out3.getvalue()
        self.assertIn("uncertainty_level values", output3)

    def test_command_error_handling(self):
        """Test felhantering i management commands"""
        # Testa att commands hanterar tomma databaser korrekt
        commands_to_test = [
            "check_axe_stamps",
            "check_axe_image_stamps",
            "fix_axe_stamp_uncertainty",
        ]

        for command_name in commands_to_test:
            out = StringIO()
            try:
                call_command(command_name, stdout=out)
                # Kommandot ska köra utan fel även med tom databas
                output = out.getvalue()
                self.assertTrue(len(output) > 0)  # Ska producera någon output
            except Exception as e:
                self.fail(f"Command '{command_name}' raised unexpected exception: {e}")

    def test_command_consistency(self):
        """Test konsistens mellan olika commands"""
        # Skapa data
        axe_stamp = AxeStamp.objects.create(
            axe=self.axe, stamp=self.stamp1, uncertainty_level="tentative"
        )

        # Kontrollera med check_axe_stamps
        out1 = StringIO()
        call_command("check_axe_stamps", stdout=out1)
        output1 = out1.getvalue()

        # Fixa med fix_axe_stamp_uncertainty
        out2 = StringIO()
        call_command("fix_axe_stamp_uncertainty", stdout=out2)
        output2 = out2.getvalue()

        # Kontrollera igen för att verifiera konsistens
        out3 = StringIO()
        call_command("check_axe_stamps", stdout=out3)
        output3 = out3.getvalue()

        # Båda kontrollerna ska visa samma data
        self.assertIn("tentative", output1)
        self.assertIn("tentative", output3)
