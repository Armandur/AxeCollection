import os
import tempfile
import csv
from django.test import TestCase
from django.core.management import call_command
from axes.models import (
    Manufacturer,
    Contact,
    Platform,
    Axe,
    Transaction,
    Measurement,
    AxeImage,
    ManufacturerLink,
)
from unittest.mock import patch


class ImportCSVCommandTest(TestCase):
    """Tester för import_csv management command"""

    def setUp(self):
        """Skapa testdata"""
        # Skapa temporär katalog för import
        self.temp_dir = tempfile.mkdtemp()
        
        # Skapa test CSV-filer
        self.manufacturer_csv = os.path.join(self.temp_dir, "Manufacturer.csv")
        self.contact_csv = os.path.join(self.temp_dir, "Kontakt.csv")
        self.platform_csv = os.path.join(self.temp_dir, "Platform.csv")
        self.axe_csv = os.path.join(self.temp_dir, "Axe.csv")
        self.transaction_csv = os.path.join(self.temp_dir, "Transaction.csv")
        self.measurement_csv = os.path.join(self.temp_dir, "Measurement.csv")
        self.axeimage_csv = os.path.join(self.temp_dir, "AxeImage.csv")
        self.manufacturerlink_csv = os.path.join(self.temp_dir, "ManufacturerLink.csv")
        self.manufacturerimage_csv = os.path.join(self.temp_dir, "ManufacturerImage.csv")

    def tearDown(self):
        """Rensa upp efter tester"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_csv_files(self):
        """Skapa test CSV-filer med data"""
        # Manufacturer.csv
        with open(self.manufacturer_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'comment'])
            writer.writerow([1, 'Test Tillverkare 1', 'Test information 1'])
            writer.writerow([2, 'Test Tillverkare 2', 'Test information 2'])

        # Kontakt.csv
        with open(self.contact_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'name', 'email', 'phone', 'alias', 'street',
                'postal_code', 'city', 'country', 'comment', 'is_naj_member'
            ])
            writer.writerow([
                1, 'Test Kontakt 1', 'test1@example.com', '123456789',
                'test_alias_1', 'Testgatan 1', '12345', 'Teststad 1',
                'SE', 'Test kommentar 1', 1
            ])
            writer.writerow([
                2, 'Test Kontakt 2', 'test2@example.com', '987654321',
                'test_alias_2', 'Testgatan 2', '54321', 'Teststad 2',
                'NO', 'Test kommentar 2', 0
            ])

        # Platform.csv
        with open(self.platform_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name'])
            writer.writerow([1, 'Test Platform 1'])
            writer.writerow([2, 'Test Platform 2'])

        # Axe.csv
        with open(self.axe_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'name', 'manufacturer_id', 'description', 'length',
                'weight', 'price', 'status', 'source_category'
            ])
            writer.writerow([
                1, 'Test Yxa 1', 1, 'Test beskrivning 1', 50, 1000, 500,
                'active', 'auction'
            ])
            writer.writerow([
                2, 'Test Yxa 2', 2, 'Test beskrivning 2', 60, 1200, 600,
                'active', 'private'
            ])

        # Transaction.csv
        with open(self.transaction_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'axe_id', 'transaction_type', 'amount', 'date',
                'platform_id', 'seller_alias', 'comment'
            ])
            writer.writerow([
                1, 1, 'purchase', -500, '2025-01-15', 1, 'test_seller_1',
                'Test transaktion 1'
            ])
            writer.writerow([
                2, 2, 'sale', 600, '2025-01-16', 2, 'test_buyer_2',
                'Test transaktion 2'
            ])

        # Measurement.csv
        with open(self.measurement_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'axe_id', 'measurement_type', 'value', 'unit'])
            writer.writerow([1, 1, 'length', 50.0, 'cm'])
            writer.writerow([2, 1, 'weight', 1000.0, 'g'])
            writer.writerow([3, 2, 'length', 60.0, 'cm'])

        # AxeImage.csv
        with open(self.axeimage_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'axe_id', 'image', 'order', 'is_primary'])
            writer.writerow([1, 1, 'test_image_1.jpg', 1, 1])
            writer.writerow([2, 1, 'test_image_2.jpg', 2, 0])
            writer.writerow([3, 2, 'test_image_3.jpg', 1, 1])

        # ManufacturerLink.csv
        with open(self.manufacturerlink_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'manufacturer_id', 'url', 'link_type'])
            writer.writerow([1, 1, 'https://example1.com', 'website'])
            writer.writerow([2, 2, 'https://example2.com', 'social'])

        # ManufacturerImage.csv
        with open(self.manufacturerimage_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'manufacturer_id', 'image'])
            writer.writerow([1, 1, 'manufacturer_image_1.jpg'])
            writer.writerow([2, 2, 'manufacturer_image_2.jpg'])

    @patch('axes.management.commands.import_csv.IMPORT_DIR')
    def test_import_csv_command(self, mock_import_dir):
        """Testa att import_csv command körs utan fel"""
        # Mock import directory
        mock_import_dir.return_value = self.temp_dir
        
        # Skapa test CSV-filer
        self.create_test_csv_files()
        
        # Kontrollera att databasen är tom innan
        self.assertEqual(Manufacturer.objects.count(), 0)
        self.assertEqual(Contact.objects.count(), 0)
        self.assertEqual(Platform.objects.count(), 0)
        self.assertEqual(Axe.objects.count(), 0)
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(AxeImage.objects.count(), 0)
        self.assertEqual(ManufacturerLink.objects.count(), 0)
        self.assertEqual(ManufacturerImage.objects.count(), 0)
        
        # Kör kommandot
        call_command('import_csv')
        
        # Kontrollera att data importerades
        self.assertEqual(Manufacturer.objects.count(), 2)
        self.assertEqual(Contact.objects.count(), 2)
        self.assertEqual(Platform.objects.count(), 2)
        self.assertEqual(Axe.objects.count(), 2)
        self.assertEqual(Transaction.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 3)
        self.assertEqual(AxeImage.objects.count(), 3)
        self.assertEqual(ManufacturerLink.objects.count(), 2)
        self.assertEqual(ManufacturerImage.objects.count(), 2)

    @patch('axes.management.commands.import_csv.IMPORT_DIR')
    def test_import_csv_with_missing_files(self, mock_import_dir):
        """Testa import_csv med saknade filer"""
        # Mock import directory
        mock_import_dir.return_value = self.temp_dir
        
        # Skapa bara några av CSV-filerna
        with open(self.manufacturer_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'comment'])
            writer.writerow([1, 'Test Tillverkare 1', 'Test information 1'])

        with open(self.platform_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name'])
            writer.writerow([1, 'Test Platform 1'])

        # Kör kommandot - ska inte krascha med saknade filer
        call_command('import_csv')
        
        # Kontrollera att tillgänglig data importerades
        self.assertEqual(Manufacturer.objects.count(), 1)
        self.assertEqual(Platform.objects.count(), 1)
        self.assertEqual(Contact.objects.count(), 0)  # Fil saknades
        self.assertEqual(Axe.objects.count(), 0)  # Fil saknades

    @patch('axes.management.commands.import_csv.IMPORT_DIR')
    def test_import_csv_empty_directory(self, mock_import_dir):
        """Testa import_csv med tom katalog"""
        # Mock import directory
        mock_import_dir.return_value = self.temp_dir
        
        # Kör kommandot - ska inte krascha med tom katalog
        call_command('import_csv')
        
        # Kontrollera att inget data importerades
        self.assertEqual(Manufacturer.objects.count(), 0)
        self.assertEqual(Contact.objects.count(), 0)
        self.assertEqual(Platform.objects.count(), 0)
        self.assertEqual(Axe.objects.count(), 0)

    @patch('axes.management.commands.import_csv.IMPORT_DIR')
    def test_import_csv_data_validation(self, mock_import_dir):
        """Testa att importerad data är korrekt"""
        # Mock import directory
        mock_import_dir.return_value = self.temp_dir
        
        # Skapa test CSV-filer
        self.create_test_csv_files()
        
        # Kör kommandot
        call_command('import_csv')
        
        # Kontrollera att data importerades korrekt
        manufacturer1 = Manufacturer.objects.get(id=1)
        self.assertEqual(manufacturer1.name, 'Test Tillverkare 1')
        self.assertEqual(manufacturer1.information, 'Test information 1')
        
        contact1 = Contact.objects.get(id=1)
        self.assertEqual(contact1.name, 'Test Kontakt 1')
        self.assertEqual(contact1.email, 'test1@example.com')
        self.assertEqual(contact1.phone, '123456789')
        self.assertEqual(contact1.alias, 'test_alias_1')
        self.assertEqual(contact1.street, 'Testgatan 1')
        self.assertEqual(contact1.postal_code, '12345')
        self.assertEqual(contact1.city, 'Teststad 1')
        self.assertEqual(contact1.country, 'SE')
        self.assertEqual(contact1.comment, 'Test kommentar 1')
        self.assertTrue(contact1.is_naj_member)
        
        platform1 = Platform.objects.get(id=1)
        self.assertEqual(platform1.name, 'Test Platform 1')
        
        axe1 = Axe.objects.get(id=1)
        self.assertEqual(axe1.name, 'Test Yxa 1')
        self.assertEqual(axe1.manufacturer, manufacturer1)
        self.assertEqual(axe1.description, 'Test beskrivning 1')
        self.assertEqual(axe1.length, 50)
        self.assertEqual(axe1.weight, 1000)
        self.assertEqual(axe1.price, 500)
        self.assertEqual(axe1.status, 'active')
        self.assertEqual(axe1.source_category, 'auction')
        
        transaction1 = Transaction.objects.get(id=1)
        self.assertEqual(transaction1.axe, axe1)
        self.assertEqual(transaction1.transaction_type, 'purchase')
        self.assertEqual(transaction1.amount, -500)
        self.assertEqual(transaction1.date, '2025-01-15')
        self.assertEqual(transaction1.platform, platform1)
        self.assertEqual(transaction1.seller_alias, 'test_seller_1')
        self.assertEqual(transaction1.comment, 'Test transaktion 1')
        
        measurement1 = Measurement.objects.get(id=1)
        self.assertEqual(measurement1.axe, axe1)
        self.assertEqual(measurement1.measurement_type, 'length')
        self.assertEqual(measurement1.value, 50.0)
        self.assertEqual(measurement1.unit, 'cm')
        
        axe_image1 = AxeImage.objects.get(id=1)
        self.assertEqual(axe_image1.axe, axe1)
        self.assertEqual(axe_image1.image, 'test_image_1.jpg')
        self.assertEqual(axe_image1.order, 1)
        self.assertTrue(axe_image1.is_primary)
        
        manufacturer_link1 = ManufacturerLink.objects.get(id=1)
        self.assertEqual(manufacturer_link1.manufacturer, manufacturer1)
        self.assertEqual(manufacturer_link1.url, 'https://example1.com')
        self.assertEqual(manufacturer_link1.link_type, 'website')
        
        manufacturer_image1 = ManufacturerImage.objects.get(id=1)
        self.assertEqual(manufacturer_image1.manufacturer, manufacturer1)
        self.assertEqual(manufacturer_image1.image, 'manufacturer_image_1.jpg')

    @patch('axes.management.commands.import_csv.IMPORT_DIR')
    def test_import_csv_with_invalid_data(self, mock_import_dir):
        """Testa import_csv med ogiltig data"""
        # Mock import directory
        mock_import_dir.return_value = self.temp_dir
        
        # Skapa CSV-fil med ogiltig data
        with open(self.manufacturer_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'comment'])
            writer.writerow(['invalid_id', 'Test Tillverkare', 'Test information'])
            writer.writerow([2, 'Test Tillverkare 2', 'Test information 2'])

        # Kör kommandot - ska hantera ogiltig data gracefully
        call_command('import_csv')
        
        # Kontrollera att giltig data importerades
        self.assertEqual(Manufacturer.objects.count(), 1)  # Endast giltig rad
        manufacturer = Manufacturer.objects.get(id=2)
        self.assertEqual(manufacturer.name, 'Test Tillverkare 2') 