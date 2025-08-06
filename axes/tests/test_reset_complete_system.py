import os
import tempfile
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from axes.models import (
    Axe,
    Manufacturer,
    Contact,
    Platform,
    Transaction,
    Measurement,
    AxeImage,
    Stamp,
    StampTranscription,
    StampImage,
    AxeStamp,
    StampSymbol,
    ManufacturerImage,
    ManufacturerLink,
)
from unittest.mock import patch


class ResetCompleteSystemCommandTest(TestCase):
    """Tester för reset_complete_system management command"""

    def setUp(self):
        """Skapa testdata"""
        # Skapa temporär katalog för media
        self.temp_dir = tempfile.mkdtemp()

        # Skapa testfiler
        self.test_file1 = os.path.join(self.temp_dir, "test1.jpg")
        self.test_file2 = os.path.join(self.temp_dir, "test2.jpg")

        with open(self.test_file1, "w") as f:
            f.write("test content 1")
        with open(self.test_file2, "w") as f:
            f.write("test content 2")

    def tearDown(self):
        """Rensa upp efter tester"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_reset_complete_system_command(self):
        """Testa att reset_complete_system command körs utan fel"""
        # Skapa testdata först
        user = User.objects.create_user(username="testuser", password="testpass123")

        manufacturer = Manufacturer.objects.create(
            name="Test Tillverkare", information="Test information"
        )

        contact = Contact.objects.create(name="Test Kontakt", email="test@example.com")

        platform = Platform.objects.create(name="Test Platform")

        axe = Axe.objects.create(
            manufacturer=manufacturer, model="Test Yxa", comment="Test beskrivning"
        )

        transaction = Transaction.objects.create(
            axe=axe,
            transaction_type="purchase",
            amount=-500,
            date="2025-01-15",
            platform=platform,
        )

        measurement = Measurement.objects.create(
            axe=axe, name="Längd", value=50.0, unit="cm"
        )

        axe_image = AxeImage.objects.create(axe=axe, image="test1.jpg", order=1)

        stamp = Stamp.objects.create(
            name="Test Stämpel",
            manufacturer=manufacturer,
            description="Test beskrivning",
        )

        transcription = StampTranscription.objects.create(
            stamp=stamp, text="TEST STÄMPEL", quality="high"
        )

        stamp_image = StampImage.objects.create(stamp=stamp, image="test2.jpg", order=1)

        axe_stamp = AxeStamp.objects.create(axe=axe, stamp=stamp, confidence="high")

        stamp_symbol = StampSymbol.objects.create(
            name="Test Symbol", description="Test symbol beskrivning"
        )

        manufacturer_image = ManufacturerImage.objects.create(
            manufacturer=manufacturer, image="test1.jpg"
        )

        manufacturer_link = ManufacturerLink.objects.create(
            manufacturer=manufacturer, url="https://example.com", link_type="website"
        )

        # Kontrollera att data finns innan
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertTrue(Manufacturer.objects.filter(name="Test Tillverkare").exists())
        self.assertTrue(Contact.objects.filter(name="Test Kontakt").exists())
        self.assertTrue(Platform.objects.filter(name="Test Platform").exists())
        self.assertTrue(Axe.objects.filter(name="Test Yxa").exists())
        self.assertTrue(Transaction.objects.filter(axe=axe).exists())
        self.assertTrue(Measurement.objects.filter(axe=axe).exists())
        self.assertTrue(AxeImage.objects.filter(axe=axe).exists())
        self.assertTrue(Stamp.objects.filter(name="Test Stämpel").exists())
        self.assertTrue(StampTranscription.objects.filter(stamp=stamp).exists())
        self.assertTrue(StampImage.objects.filter(stamp=stamp).exists())
        self.assertTrue(AxeStamp.objects.filter(axe=axe, stamp=stamp).exists())
        self.assertTrue(StampSymbol.objects.filter(name="Test Symbol").exists())
        self.assertTrue(
            ManufacturerImage.objects.filter(manufacturer=manufacturer).exists()
        )
        self.assertTrue(
            ManufacturerLink.objects.filter(manufacturer=manufacturer).exists()
        )

        # Kontrollera att filerna finns innan
        self.assertTrue(os.path.exists(self.test_file1))
        self.assertTrue(os.path.exists(self.test_file2))

        # Kör kommandot
        call_command("reset_complete_system")

        # Kontrollera att all data togs bort
        self.assertFalse(User.objects.filter(username="testuser").exists())
        self.assertFalse(Manufacturer.objects.filter(name="Test Tillverkare").exists())
        self.assertFalse(Contact.objects.filter(name="Test Kontakt").exists())
        self.assertFalse(Platform.objects.filter(name="Test Platform").exists())
        self.assertFalse(Axe.objects.filter(name="Test Yxa").exists())
        self.assertFalse(Transaction.objects.filter(axe=axe).exists())
        self.assertFalse(Measurement.objects.filter(axe=axe).exists())
        self.assertFalse(AxeImage.objects.filter(axe=axe).exists())
        self.assertFalse(Stamp.objects.filter(name="Test Stämpel").exists())
        self.assertFalse(StampTranscription.objects.filter(stamp=stamp).exists())
        self.assertFalse(StampImage.objects.filter(stamp=stamp).exists())
        self.assertFalse(AxeStamp.objects.filter(axe=axe, stamp=stamp).exists())
        self.assertFalse(StampSymbol.objects.filter(name="Test Symbol").exists())
        self.assertFalse(
            ManufacturerImage.objects.filter(manufacturer=manufacturer).exists()
        )
        self.assertFalse(
            ManufacturerLink.objects.filter(manufacturer=manufacturer).exists()
        )

        # Kontrollera att filerna togs bort
        self.assertFalse(os.path.exists(self.test_file1))
        self.assertFalse(os.path.exists(self.test_file2))

    @patch("axes.management.commands.reset_complete_system.settings")
    def test_reset_complete_system_with_media_root(self, mock_settings):
        """Testa reset_complete_system med MEDIA_ROOT"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir

        # Skapa testdata
        user = User.objects.create_user(username="testuser", password="testpass123")

        manufacturer = Manufacturer.objects.create(name="Test Tillverkare")

        axe = Axe.objects.create(
            name="Test Yxa", manufacturer=manufacturer, description="Test beskrivning"
        )

        # Skapa bilder som refererar till filer
        AxeImage.objects.create(axe=axe, image="test1.jpg", order=1)

        # Kontrollera att data finns innan
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertTrue(Manufacturer.objects.filter(name="Test Tillverkare").exists())
        self.assertTrue(Axe.objects.filter(name="Test Yxa").exists())
        self.assertTrue(AxeImage.objects.filter(axe=axe).exists())

        # Kontrollera att filerna finns innan
        self.assertTrue(os.path.exists(self.test_file1))
        self.assertTrue(os.path.exists(self.test_file2))

        # Kör kommandot
        call_command("reset_complete_system")

        # Kontrollera att all data togs bort
        self.assertFalse(User.objects.filter(username="testuser").exists())
        self.assertFalse(Manufacturer.objects.filter(name="Test Tillverkare").exists())
        self.assertFalse(Axe.objects.filter(name="Test Yxa").exists())
        self.assertFalse(AxeImage.objects.filter(axe=axe).exists())

        # Kontrollera att filerna togs bort
        self.assertFalse(os.path.exists(self.test_file1))
        self.assertFalse(os.path.exists(self.test_file2))

    def test_reset_complete_system_empty_database(self):
        """Testa reset_complete_system med tom databas"""
        # Kontrollera att databasen är tom innan
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Manufacturer.objects.count(), 0)
        self.assertEqual(Contact.objects.count(), 0)
        self.assertEqual(Platform.objects.count(), 0)
        self.assertEqual(Axe.objects.count(), 0)
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(AxeImage.objects.count(), 0)
        self.assertEqual(Stamp.objects.count(), 0)
        self.assertEqual(StampTranscription.objects.count(), 0)
        self.assertEqual(StampImage.objects.count(), 0)
        self.assertEqual(AxeStamp.objects.count(), 0)
        self.assertEqual(StampSymbol.objects.count(), 0)
        self.assertEqual(ManufacturerImage.objects.count(), 0)
        self.assertEqual(ManufacturerLink.objects.count(), 0)

        # Kör kommandot - ska inte krascha med tom databas
        call_command("reset_complete_system")

        # Kontrollera att databasen fortfarande är tom
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Manufacturer.objects.count(), 0)
        self.assertEqual(Contact.objects.count(), 0)
        self.assertEqual(Platform.objects.count(), 0)
        self.assertEqual(Axe.objects.count(), 0)
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(AxeImage.objects.count(), 0)
        self.assertEqual(Stamp.objects.count(), 0)
        self.assertEqual(StampTranscription.objects.count(), 0)
        self.assertEqual(StampImage.objects.count(), 0)
        self.assertEqual(AxeStamp.objects.count(), 0)
        self.assertEqual(StampSymbol.objects.count(), 0)
        self.assertEqual(ManufacturerImage.objects.count(), 0)
        self.assertEqual(ManufacturerLink.objects.count(), 0)

    def test_reset_complete_system_preserves_superuser(self):
        """Testa att reset_complete_system inte tar bort superuser"""
        # Skapa superuser
        superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        # Skapa vanlig användare
        regular_user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # Skapa testdata
        manufacturer = Manufacturer.objects.create(name="Test Tillverkare")

        axe = Axe.objects.create(
            name="Test Yxa", manufacturer=manufacturer, description="Test beskrivning"
        )

        # Kontrollera att data finns innan
        self.assertTrue(User.objects.filter(username="admin").exists())
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertTrue(Manufacturer.objects.filter(name="Test Tillverkare").exists())
        self.assertTrue(Axe.objects.filter(name="Test Yxa").exists())

        # Kör kommandot
        call_command("reset_complete_system")

        # Kontrollera att superuser finns kvar men vanlig användare togs bort
        self.assertTrue(User.objects.filter(username="admin").exists())
        self.assertFalse(User.objects.filter(username="testuser").exists())
        self.assertFalse(Manufacturer.objects.filter(name="Test Tillverkare").exists())
        self.assertFalse(Axe.objects.filter(name="Test Yxa").exists())
