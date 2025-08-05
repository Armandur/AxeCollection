import os
import tempfile
from django.test import TestCase
from django.core.management import call_command
from axes.models import Manufacturer, ManufacturerImage
from unittest.mock import patch, Mock


class UpdatePictogramsCommandTest(TestCase):
    """Tester för update_pictograms management command"""

    def setUp(self):
        """Skapa testdata"""
        # Skapa temporär katalog för media
        self.temp_dir = tempfile.mkdtemp()
        
        # Skapa testfiler
        self.test_file1 = os.path.join(self.temp_dir, "test1.jpg")
        self.test_file2 = os.path.join(self.temp_dir, "test2.jpg")
        
        with open(self.test_file1, 'w') as f:
            f.write("test content 1")
        with open(self.test_file2, 'w') as f:
            f.write("test content 2")

    def tearDown(self):
        """Rensa upp efter tester"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('axes.management.commands.update_pictograms.settings')
    def test_update_pictograms_command(self, mock_settings):
        """Testa att update_pictograms command körs utan fel"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir
        
        # Skapa testdata
        manufacturer = Manufacturer.objects.create(
            name="Test Tillverkare",
            information="Test information"
        )
        
        manufacturer_image = ManufacturerImage.objects.create(
            manufacturer=manufacturer,
            image="test1.jpg"
        )
        
        # Kontrollera att data finns innan
        self.assertTrue(Manufacturer.objects.filter(name="Test Tillverkare").exists())
        self.assertTrue(ManufacturerImage.objects.filter(manufacturer=manufacturer).exists())
        
        # Kontrollera att filen finns innan
        self.assertTrue(os.path.exists(self.test_file1))
        
        # Kör kommandot
        call_command('update_pictograms')
        
        # Kontrollera att data fortfarande finns (kommandot ska inte ta bort data)
        self.assertTrue(Manufacturer.objects.filter(name="Test Tillverkare").exists())
        self.assertTrue(ManufacturerImage.objects.filter(manufacturer=manufacturer).exists())

    @patch('axes.management.commands.update_pictograms.settings')
    def test_update_pictograms_empty_database(self, mock_settings):
        """Testa update_pictograms med tom databas"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir
        
        # Kontrollera att databasen är tom innan
        self.assertEqual(Manufacturer.objects.count(), 0)
        self.assertEqual(ManufacturerImage.objects.count(), 0)
        
        # Kör kommandot - ska inte krascha med tom databas
        call_command('update_pictograms')
        
        # Kontrollera att databasen fortfarande är tom
        self.assertEqual(Manufacturer.objects.count(), 0)
        self.assertEqual(ManufacturerImage.objects.count(), 0)

    @patch('axes.management.commands.update_pictograms.settings')
    def test_update_pictograms_with_multiple_manufacturers(self, mock_settings):
        """Testa update_pictograms med flera tillverkare"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir
        
        # Skapa flera tillverkare
        manufacturer1 = Manufacturer.objects.create(
            name="Test Tillverkare 1",
            information="Test information 1"
        )
        
        manufacturer2 = Manufacturer.objects.create(
            name="Test Tillverkare 2",
            information="Test information 2"
        )
        
        manufacturer3 = Manufacturer.objects.create(
            name="Test Tillverkare 3",
            information="Test information 3"
        )
        
        # Skapa bilder för tillverkare
        ManufacturerImage.objects.create(
            manufacturer=manufacturer1,
            image="test1.jpg"
        )
        
        ManufacturerImage.objects.create(
            manufacturer=manufacturer2,
            image="test2.jpg"
        )
        
        # Kontrollera att data finns innan
        self.assertEqual(Manufacturer.objects.count(), 3)
        self.assertEqual(ManufacturerImage.objects.count(), 2)
        
        # Kör kommandot
        call_command('update_pictograms')
        
        # Kontrollera att data fortfarande finns
        self.assertEqual(Manufacturer.objects.count(), 3)
        self.assertEqual(ManufacturerImage.objects.count(), 2)

    @patch('axes.management.commands.update_pictograms.settings')
    def test_update_pictograms_with_nonexistent_files(self, mock_settings):
        """Testa update_pictograms med filer som inte finns"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir
        
        # Skapa testdata med bilder som refererar till filer som inte finns
        manufacturer = Manufacturer.objects.create(
            name="Test Tillverkare",
            information="Test information"
        )
        
        ManufacturerImage.objects.create(
            manufacturer=manufacturer,
            image="nonexistent.jpg"
        )
        
        # Kontrollera att data finns innan
        self.assertTrue(Manufacturer.objects.filter(name="Test Tillverkare").exists())
        self.assertTrue(ManufacturerImage.objects.filter(manufacturer=manufacturer).exists())
        
        # Kör kommandot - ska inte krascha även om filerna inte finns
        call_command('update_pictograms')
        
        # Kontrollera att data fortfarande finns
        self.assertTrue(Manufacturer.objects.filter(name="Test Tillverkare").exists())
        self.assertTrue(ManufacturerImage.objects.filter(manufacturer=manufacturer).exists())

    @patch('axes.management.commands.update_pictograms.settings')
    def test_update_pictograms_with_subdirectories(self, mock_settings):
        """Testa update_pictograms med underkataloger"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir
        
        # Skapa underkataloger och filer
        subdir1 = os.path.join(self.temp_dir, "subdir1")
        subdir2 = os.path.join(self.temp_dir, "subdir2")
        os.makedirs(subdir1, exist_ok=True)
        os.makedirs(subdir2, exist_ok=True)
        
        # Skapa filer i underkataloger
        subfile1 = os.path.join(subdir1, "subtest1.jpg")
        subfile2 = os.path.join(subdir2, "subtest2.jpg")
        
        with open(subfile1, 'w') as f:
            f.write("sub content 1")
        with open(subfile2, 'w') as f:
            f.write("sub content 2")
        
        # Skapa testdata med bilder som refererar till filer i underkataloger
        manufacturer1 = Manufacturer.objects.create(
            name="Test Tillverkare 1",
            information="Test information 1"
        )
        
        manufacturer2 = Manufacturer.objects.create(
            name="Test Tillverkare 2",
            information="Test information 2"
        )
        
        ManufacturerImage.objects.create(
            manufacturer=manufacturer1,
            image="subdir1/subtest1.jpg"
        )
        
        ManufacturerImage.objects.create(
            manufacturer=manufacturer2,
            image="subdir2/subtest2.jpg"
        )
        
        # Kontrollera att data finns innan
        self.assertEqual(Manufacturer.objects.count(), 2)
        self.assertEqual(ManufacturerImage.objects.count(), 2)
        
        # Kontrollera att filerna finns innan
        self.assertTrue(os.path.exists(subfile1))
        self.assertTrue(os.path.exists(subfile2))
        
        # Kör kommandot
        call_command('update_pictograms')
        
        # Kontrollera att data fortfarande finns
        self.assertEqual(Manufacturer.objects.count(), 2)
        self.assertEqual(ManufacturerImage.objects.count(), 2)

    @patch('axes.management.commands.update_pictograms.settings')
    def test_update_pictograms_preserves_manufacturer_data(self, mock_settings):
        """Testa att update_pictograms inte ändrar tillverkar-data"""
        # Mock settings för att använda temporär katalog
        mock_settings.MEDIA_ROOT = self.temp_dir
        
        # Skapa testdata
        manufacturer = Manufacturer.objects.create(
            name="Test Tillverkare",
            information="Test information",
            country="SE",
            website="https://example.com"
        )
        
        manufacturer_image = ManufacturerImage.objects.create(
            manufacturer=manufacturer,
            image="test1.jpg"
        )
        
        # Kontrollera att data finns innan
        self.assertTrue(Manufacturer.objects.filter(name="Test Tillverkare").exists())
        self.assertTrue(ManufacturerImage.objects.filter(manufacturer=manufacturer).exists())
        
        # Kör kommandot
        call_command('update_pictograms')
        
        # Kontrollera att tillverkar-data inte ändrades
        manufacturer.refresh_from_db()
        self.assertEqual(manufacturer.name, "Test Tillverkare")
        self.assertEqual(manufacturer.information, "Test information")
        self.assertEqual(manufacturer.country, "SE")
        self.assertEqual(manufacturer.website, "https://example.com")
        
        # Kontrollera att bild-data inte ändrades
        manufacturer_image.refresh_from_db()
        self.assertEqual(manufacturer_image.manufacturer, manufacturer)
        self.assertEqual(manufacturer_image.image, "test1.jpg") 