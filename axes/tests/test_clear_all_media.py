import os
import tempfile
from django.test import TestCase
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from axes.models import AxeImage, StampImage, ManufacturerImage, Stamp
from unittest.mock import patch


class ClearAllMediaCommandTest(TestCase):
    """Tester för clear_all_media management command"""

    def setUp(self):
        """Skapa testdata"""
        # Skapa temporär katalog för media
        self.temp_dir = tempfile.mkdtemp()

        # Skapa mappar som kommandot förväntar sig
        media_dirs = [
            "axe_images",
            "manufacturer_images",
            "stamps",
            "unlinked_images",
            "stamp_images",
        ]
        for dir_name in media_dirs:
            os.makedirs(os.path.join(self.temp_dir, dir_name), exist_ok=True)

        # Skapa testfiler
        self.test_file1 = os.path.join(self.temp_dir, "axe_images", "test1.jpg")
        self.test_file2 = os.path.join(self.temp_dir, "stamps", "test2.jpg")
        self.test_file3 = os.path.join(
            self.temp_dir, "manufacturer_images", "test3.jpg"
        )

        # Skapa testfiler
        with open(self.test_file1, "w") as f:
            f.write("test content 1")
        with open(self.test_file2, "w") as f:
            f.write("test content 2")
        with open(self.test_file3, "w") as f:
            f.write("test content 3")

    def tearDown(self):
        """Rensa upp efter tester"""
        # Ta bort temporär katalog
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("axes.management.commands.clear_all_media.settings")
    def test_clear_all_media_command(self, mock_settings):
        """Testa att clear_all_media command körs utan fel"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir

        # Skapa testdata med bilder
        from axes.models import Axe, Manufacturer

        manufacturer = Manufacturer.objects.create(name="Test Tillverkare")
        axe = Axe.objects.create(
            manufacturer=manufacturer, model="Test Yxa", comment="Test beskrivning"
        )

        manufacturer = Manufacturer.objects.create(name="Test Tillverkare")

        # Skapa bilder som refererar till filer
        axe_image = AxeImage.objects.create(axe=axe, image="test1.jpg", order=1)

        stamp = Stamp.objects.create(name="Test Stamp")
        stamp_image = StampImage.objects.create(stamp=stamp, image="test2.jpg", order=1)

        manufacturer_image = ManufacturerImage.objects.create(
            manufacturer=manufacturer, image="test3.jpg"
        )

        # Kontrollera att filerna finns innan
        self.assertTrue(os.path.exists(self.test_file1))
        self.assertTrue(os.path.exists(self.test_file2))
        self.assertTrue(os.path.exists(self.test_file3))

        # Kör kommandot
        call_command("clear_all_media", confirm=True)

        # Kontrollera att filerna togs bort
        self.assertFalse(os.path.exists(self.test_file1))
        self.assertFalse(os.path.exists(self.test_file2))
        self.assertFalse(os.path.exists(self.test_file3))

    @patch("axes.management.commands.clear_all_media.settings")
    def test_clear_all_media_with_nonexistent_files(self, mock_settings):
        """Testa clear_all_media med filer som inte finns"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir

        # Skapa testdata med bilder som refererar till filer som inte finns
        from axes.models import Axe, Manufacturer

        manufacturer = Manufacturer.objects.create(name="Test Tillverkare")
        axe = Axe.objects.create(
            manufacturer=manufacturer, model="Test Yxa", comment="Test beskrivning"
        )

        manufacturer = Manufacturer.objects.create(name="Test Tillverkare")

        # Skapa bilder som refererar till filer som inte finns
        AxeImage.objects.create(axe=axe, image="nonexistent1.jpg", order=1)

        stamp = Stamp.objects.create(name="Test Stamp")
        StampImage.objects.create(stamp=stamp, image="nonexistent2.jpg", order=1)

        ManufacturerImage.objects.create(
            manufacturer=manufacturer, image="nonexistent3.jpg"
        )

        # Kör kommandot - ska inte krascha även om filerna inte finns
        call_command("clear_all_media", confirm=True)

    @patch("axes.management.commands.clear_all_media.settings")
    def test_clear_all_media_empty_directory(self, mock_settings):
        """Testa clear_all_media med tom katalog"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir

        # Ta bort alla filer först
        for file in [self.test_file1, self.test_file2, self.test_file3]:
            if os.path.exists(file):
                os.remove(file)

        # Kör kommandot - ska inte krascha med tom katalog
        call_command("clear_all_media", confirm=True)

    @patch("axes.management.commands.clear_all_media.settings")
    def test_clear_all_media_with_subdirectories(self, mock_settings):
        """Testa clear_all_media med underkataloger"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir

        # Skapa filer i media-mapparna
        subfile1 = os.path.join(self.temp_dir, "axe_images", "subtest1.jpg")
        subfile2 = os.path.join(self.temp_dir, "stamps", "subtest2.jpg")

        with open(subfile1, "w") as f:
            f.write("sub content 1")
        with open(subfile2, "w") as f:
            f.write("sub content 2")

        # Kontrollera att filerna finns innan
        self.assertTrue(os.path.exists(subfile1))
        self.assertTrue(os.path.exists(subfile2))

        # Kör kommandot
        call_command("clear_all_media", confirm=True)

        # Kontrollera att filerna togs bort
        self.assertFalse(os.path.exists(subfile1))
        self.assertFalse(os.path.exists(subfile2))

    @patch("axes.management.commands.clear_all_media.settings")
    def test_clear_all_media_preserves_database_records(self, mock_settings):
        """Testa att clear_all_media inte tar bort databasposter"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir

        # Skapa testdata
        from axes.models import Axe, Manufacturer

        manufacturer = Manufacturer.objects.create(name="Test Tillverkare")
        axe = Axe.objects.create(
            manufacturer=manufacturer, model="Test Yxa", comment="Test beskrivning"
        )

        manufacturer = Manufacturer.objects.create(name="Test Tillverkare")

        # Skapa bilder
        axe_image = AxeImage.objects.create(axe=axe, image="test1.jpg", order=1)

        stamp = Stamp.objects.create(name="Test Stamp")
        stamp_image = StampImage.objects.create(stamp=stamp, image="test2.jpg", order=1)

        manufacturer_image = ManufacturerImage.objects.create(
            manufacturer=manufacturer, image="test3.jpg"
        )

        # Kontrollera att posterna finns innan
        self.assertTrue(AxeImage.objects.filter(id=axe_image.id).exists())
        self.assertTrue(StampImage.objects.filter(id=stamp_image.id).exists())
        self.assertTrue(
            ManufacturerImage.objects.filter(id=manufacturer_image.id).exists()
        )

        # Kör kommandot
        call_command("clear_all_media", confirm=True)

        # Kontrollera att posterna fortfarande finns
        self.assertTrue(AxeImage.objects.filter(id=axe_image.id).exists())
        self.assertTrue(StampImage.objects.filter(id=stamp_image.id).exists())
        self.assertTrue(
            ManufacturerImage.objects.filter(id=manufacturer_image.id).exists()
        )
