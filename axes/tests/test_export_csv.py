import os
import tempfile
import csv
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
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


class ExportCSVCommandTest(TestCase):
    """Tester för export_csv management command"""

    def setUp(self):
        """Skapa testdata"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        
        # Skapa testdata
        self.manufacturer = Manufacturer.objects.create(
            name="Test Tillverkare",
            information="Test information"
        )
        
        self.contact = Contact.objects.create(
            name="Test Kontakt",
            email="test@example.com",
            phone="123456789",
            alias="test_alias",
            street="Testgatan 1",
            postal_code="12345",
            city="Teststad",
            country="SE",
            comment="Test kommentar",
            is_naj_member=True
        )
        
        self.platform = Platform.objects.create(name="Test Platform")
        
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Yxa",
            comment="Test beskrivning"
        )
        
        self.transaction = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            transaction_date="2025-01-15",
            type="KÖP",
            price=500,
            shipping_cost=0,
            comment="Test transaktion"
        )
        
        self.measurement = Measurement.objects.create(
            axe=self.axe,
            name="Längd",
            value=50.0,
            unit="cm"
        )
        
        self.axe_image = AxeImage.objects.create(
            axe=self.axe,
            image="test_image.jpg",
            order=1
        )
        
        self.manufacturer_link = ManufacturerLink.objects.create(
            manufacturer=self.manufacturer,
            url="https://example.com",
            link_type="website"
        )

    def test_export_csv_command(self):
        """Testa att export_csv command körs utan fel"""
        # Skapa temporär katalog för export
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock EXPORT_DIR genom att monkey patcha
            import axes.management.commands.export_csv
            original_export_dir = axes.management.commands.export_csv.EXPORT_DIR
            axes.management.commands.export_csv.EXPORT_DIR = temp_dir
            
            try:
                # Kör kommandot
                call_command('export_csv')
                
                # Kontrollera att filerna skapades
                expected_files = [
                    "Manufacturer.csv",
                    "Kontakt.csv", 
                    "Platform.csv",
                    "Axe.csv",  # Ändra från Yxa.csv
                    "Transaction.csv",  # Ändra från Transaktioner.csv
                    "Measurement.csv",  # Ändra från Mått.csv
                    "AxeImage.csv",
                    "ManufacturerLink.csv",
                    "ManufacturerImage.csv"
                ]
                
                for filename in expected_files:
                    file_path = os.path.join(temp_dir, filename)
                    self.assertTrue(os.path.exists(file_path), f"Filen {filename} skapades inte")
                    
            finally:
                # Återställ original EXPORT_DIR
                axes.management.commands.export_csv.EXPORT_DIR = original_export_dir

    def test_export_manufacturers(self):
        """Testa export av tillverkare"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import axes.management.commands.export_csv
            original_export_dir = axes.management.commands.export_csv.EXPORT_DIR
            axes.management.commands.export_csv.EXPORT_DIR = temp_dir
            
            try:
                call_command('export_csv')
                
                # Kontrollera Manufacturer.csv
                manufacturer_file = os.path.join(temp_dir, "Manufacturer.csv")
                self.assertTrue(os.path.exists(manufacturer_file))
                
                with open(manufacturer_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    
                # Kontrollera header
                self.assertEqual(rows[0], ["id", "name", "comment"])
                
                # Kontrollera data
                self.assertEqual(len(rows), 2)  # Header + 1 data rad
                self.assertEqual(rows[1][1], "Test Tillverkare")
                self.assertEqual(rows[1][2], "Test information")
                
            finally:
                axes.management.commands.export_csv.EXPORT_DIR = original_export_dir

    def test_export_contacts(self):
        """Testa export av kontakter"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import axes.management.commands.export_csv
            original_export_dir = axes.management.commands.export_csv.EXPORT_DIR
            axes.management.commands.export_csv.EXPORT_DIR = temp_dir
            
            try:
                call_command('export_csv')
                
                # Kontrollera Kontakt.csv
                contact_file = os.path.join(temp_dir, "Kontakt.csv")
                self.assertTrue(os.path.exists(contact_file))
                
                with open(contact_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    
                # Kontrollera header
                expected_header = [
                    "id", "name", "email", "phone", "alias", "street",
                    "postal_code", "city", "country", "comment", "is_naj_member"
                ]
                self.assertEqual(rows[0], expected_header)
                
                # Kontrollera data
                self.assertEqual(len(rows), 2)  # Header + 1 data rad
                self.assertEqual(rows[1][1], "Test Kontakt")
                self.assertEqual(rows[1][2], "test@example.com")
                
            finally:
                axes.management.commands.export_csv.EXPORT_DIR = original_export_dir

    def test_export_axes(self):
        """Testa export av yxor"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import axes.management.commands.export_csv
            original_export_dir = axes.management.commands.export_csv.EXPORT_DIR
            axes.management.commands.export_csv.EXPORT_DIR = temp_dir
            
            try:
                call_command('export_csv')
                
                # Kontrollera Axe.csv (ändra från Yxa.csv)
                axe_file = os.path.join(temp_dir, "Axe.csv")
                self.assertTrue(os.path.exists(axe_file))
                
                with open(axe_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    
                # Kontrollera header
                expected_header = ["id", "manufacturer_id", "manufacturer_name", "model", "comment"]
                self.assertEqual(rows[0], expected_header)
                
                # Kontrollera data
                self.assertEqual(len(rows), 2)  # Header + 1 data rad
                self.assertEqual(rows[1][3], "Test Yxa")  # model
                self.assertEqual(rows[1][4], "Test beskrivning")  # comment
                
            finally:
                axes.management.commands.export_csv.EXPORT_DIR = original_export_dir

    def test_export_transactions(self):
        """Testa export av transaktioner"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import axes.management.commands.export_csv
            original_export_dir = axes.management.commands.export_csv.EXPORT_DIR
            axes.management.commands.export_csv.EXPORT_DIR = temp_dir
            
            try:
                call_command('export_csv')
                
                # Kontrollera Transaction.csv (ändra från Transaktioner.csv)
                transaction_file = os.path.join(temp_dir, "Transaction.csv")
                self.assertTrue(os.path.exists(transaction_file))
                
                with open(transaction_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    
                # Kontrollera header
                expected_header = [
                    "id", "axe_id", "axe_model", "contact_id", "contact_name",
                    "platform_id", "platform_name", "transaction_date", "type",
                    "price", "shipping_cost", "comment"
                ]
                self.assertEqual(rows[0], expected_header)
                
                # Kontrollera data
                self.assertEqual(len(rows), 2)  # Header + 1 data rad
                self.assertEqual(rows[1][8], "KÖP")  # type
                self.assertEqual(rows[1][9], "500.00")  # price (ändra från "500" till "500.00")
                
            finally:
                axes.management.commands.export_csv.EXPORT_DIR = original_export_dir

    def test_clean_text_method(self):
        """Testa clean_text metoden"""
        from axes.management.commands.export_csv import Command
        
        command = Command()
        
        # Testa normal text
        self.assertEqual(command.clean_text("Normal text"), "Normal text")
        
        # Testa text med radbrytningar
        self.assertEqual(command.clean_text("Text\nmed\nradbrytningar"), "Text med radbrytningar")
        
        # Testa text med extra whitespace
        self.assertEqual(command.clean_text("  Text   med   extra   whitespace  "), "Text med extra whitespace")
        
        # Testa None
        self.assertEqual(command.clean_text(None), "")
        
        # Testa tom sträng
        self.assertEqual(command.clean_text(""), "") 