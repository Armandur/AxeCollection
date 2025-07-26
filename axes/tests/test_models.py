import pytest
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from axes.models import (
    Manufacturer, Axe, Contact, Platform, Transaction, 
    MeasurementType, MeasurementTemplate, Measurement,
    NextAxeID, Settings
)
from .factories import (
    ManufacturerFactory, SubManufacturerFactory, AxeFactory,
    ContactFactory, PlatformFactory, TransactionFactory,
    MeasurementTypeFactory, MeasurementTemplateFactory,
    MeasurementFactory, SettingsFactory
)


class ManufacturerModelTest(TestCase):
    """Tester för Manufacturer-modellen"""
    
    def test_manufacturer_creation(self):
        """Test att skapa en tillverkare"""
        manufacturer = ManufacturerFactory()
        self.assertIsNotNone(manufacturer.id)
        self.assertIsInstance(manufacturer.name, str)
        self.assertIsInstance(manufacturer.manufacturer_type, str)
    
    def test_manufacturer_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        manufacturer = ManufacturerFactory(name="Test Tillverkare")
        self.assertEqual(str(manufacturer), "Test Tillverkare")
    
    def test_manufacturer_hierarchy_properties(self):
        """Test hierarki-relaterade properties"""
        main_manufacturer = ManufacturerFactory()
        sub_manufacturer = SubManufacturerFactory(parent=main_manufacturer)
        
        # Test huvudtillverkare
        self.assertTrue(main_manufacturer.is_main_manufacturer)
        self.assertFalse(main_manufacturer.is_sub_manufacturer)
        self.assertEqual(main_manufacturer.hierarchy_level, 0)
        self.assertEqual(main_manufacturer.full_name, main_manufacturer.name)
        
        # Test undertillverkare
        self.assertFalse(sub_manufacturer.is_main_manufacturer)
        self.assertTrue(sub_manufacturer.is_sub_manufacturer)
        self.assertEqual(sub_manufacturer.hierarchy_level, 1)
        self.assertEqual(sub_manufacturer.full_name, f"{main_manufacturer.name} - {sub_manufacturer.name}")
    
    def test_manufacturer_axe_count_properties(self):
        """Test properties för antal yxor"""
        manufacturer = ManufacturerFactory()
        axe1 = AxeFactory(manufacturer=manufacturer)
        axe2 = AxeFactory(manufacturer=manufacturer)
        
        self.assertEqual(manufacturer.axe_count, 2)
        self.assertEqual(manufacturer.axe_count_including_sub_manufacturers, 2)
    
    def test_manufacturer_with_sub_manufacturers_axe_count(self):
        """Test antal yxor inklusive undertillverkare"""
        main_manufacturer = ManufacturerFactory()
        sub_manufacturer = SubManufacturerFactory(parent=main_manufacturer)
        
        # Skapa yxor för båda
        AxeFactory(manufacturer=main_manufacturer)
        AxeFactory(manufacturer=sub_manufacturer)
        AxeFactory(manufacturer=sub_manufacturer)
        
        self.assertEqual(main_manufacturer.axe_count, 1)
        self.assertEqual(main_manufacturer.axe_count_including_sub_manufacturers, 3)
        self.assertEqual(sub_manufacturer.axe_count, 2)
        self.assertEqual(sub_manufacturer.axe_count_including_sub_manufacturers, 2)


class AxeModelTest(TestCase):
    """Tester för Axe-modellen"""
    
    def test_axe_creation(self):
        """Test att skapa en yxa"""
        axe = AxeFactory()
        self.assertIsNotNone(axe.id)
        self.assertIsInstance(axe.model, str)
        self.assertIsInstance(axe.status, str)
    
    def test_axe_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        manufacturer = ManufacturerFactory(name="Test Tillverkare")
        axe = AxeFactory(manufacturer=manufacturer, model="Test Modell")
        expected = f"{manufacturer.name} - {axe.model}"
        self.assertEqual(str(axe), expected)
    
    def test_axe_display_id(self):
        """Test display_id property"""
        axe = AxeFactory()
        self.assertEqual(axe.display_id, axe.id)
    
    def test_axe_transaction_properties(self):
        """Test properties för transaktioner"""
        axe = AxeFactory()
        contact = ContactFactory()
        platform = PlatformFactory()
        
        # Skapa köp-transaktioner
        TransactionFactory(
            axe=axe, contact=contact, platform=platform,
            type='KÖP', price=Decimal('100.00'), shipping_cost=Decimal('10.00')
        )
        TransactionFactory(
            axe=axe, contact=contact, platform=platform,
            type='KÖP', price=Decimal('50.00'), shipping_cost=Decimal('5.00')
        )
        
        # Skapa sälj-transaktion
        TransactionFactory(
            axe=axe, contact=contact, platform=platform,
            type='SÄLJ', price=Decimal('200.00'), shipping_cost=Decimal('15.00')
        )
        
        self.assertEqual(axe.total_buy_value, Decimal('150.00'))
        self.assertEqual(axe.total_buy_shipping, Decimal('15.00'))
        self.assertEqual(axe.total_sale_value, Decimal('200.00'))
        self.assertEqual(axe.total_sale_shipping, Decimal('15.00'))
        self.assertEqual(axe.net_value, Decimal('50.00'))  # 200 - 150
        self.assertEqual(axe.profit_loss, Decimal('50.00'))  # 200 - 150
    
    def test_axe_measurement_count(self):
        """Test measurement_count property"""
        axe = AxeFactory()
        MeasurementFactory(axe=axe)
        MeasurementFactory(axe=axe)
        MeasurementFactory(axe=axe)
        
        self.assertEqual(axe.measurement_count, 3)


class NextAxeIDModelTest(TestCase):
    """Tester för NextAxeID-modellen"""
    
    def test_get_next_id(self):
        """Test att hämta nästa ID"""
        # Första anropet ska returnera 1
        next_id = NextAxeID.get_next_id()
        self.assertEqual(next_id, 1)
        
        # Andra anropet ska returnera 2
        next_id = NextAxeID.get_next_id()
        self.assertEqual(next_id, 2)
    
    def test_peek_next_id(self):
        """Test att kolla nästa ID utan att öka räknaren"""
        # Skapa en instans först
        NextAxeID.get_next_id()

        # Peek ska returnera samma värde som nästa get_next_id
        peeked_id = NextAxeID.peek_next_id()
        next_id = NextAxeID.get_next_id()
        self.assertEqual(peeked_id, next_id)
    
    def test_reset_if_last_axe_deleted(self):
        """Test återställning av nästa ID"""
        # Skapa en yxa och hämta nästa ID
        axe = AxeFactory()
        current_next_id = NextAxeID.peek_next_id()
        
        # Ta bort yxan
        axe.delete()
        
        # Nästa ID ska vara återställt till yxans ID
        new_next_id = NextAxeID.peek_next_id()
        self.assertEqual(new_next_id, 1)  # Återställs till 1 när yxan tas bort


class ContactModelTest(TestCase):
    """Tester för Contact-modellen"""
    
    def test_contact_creation(self):
        """Test att skapa en kontakt"""
        contact = ContactFactory()
        self.assertIsNotNone(contact.id)
        self.assertIsInstance(contact.name, str)
    
    def test_contact_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        contact = ContactFactory(name="Test Kontakt")
        self.assertEqual(str(contact), "Test Kontakt")
    
    def test_contact_transaction_properties(self):
        """Test properties för transaktioner"""
        contact = ContactFactory()
        axe = AxeFactory()
        platform = PlatformFactory()
        
        # Skapa transaktioner
        TransactionFactory(
            contact=contact, axe=axe, platform=platform,
            type='KÖP', price=Decimal('100.00')
        )
        TransactionFactory(
            contact=contact, axe=axe, platform=platform,
            type='SÄLJ', price=Decimal('150.00')
        )
        
        self.assertEqual(contact.total_transactions, 2)
        self.assertEqual(contact.buy_count, 1)
        self.assertEqual(contact.sale_count, 1)
        self.assertEqual(contact.total_buy_value, Decimal('100.00'))
        self.assertEqual(contact.total_sale_value, Decimal('150.00'))
        self.assertEqual(contact.net_value, Decimal('50.00'))


class PlatformModelTest(TestCase):
    """Tester för Platform-modellen"""
    
    def test_platform_creation(self):
        """Test att skapa en plattform"""
        platform = PlatformFactory()
        self.assertIsNotNone(platform.id)
        self.assertIsInstance(platform.name, str)
        self.assertIsInstance(platform.color_class, str)
    
    def test_platform_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        platform = PlatformFactory(name="Test Plattform")
        self.assertEqual(str(platform), "Test Plattform")
    
    def test_platform_transaction_properties(self):
        """Test properties för transaktioner"""
        platform = PlatformFactory()
        contact = ContactFactory()
        axe = AxeFactory()
        
        # Skapa transaktioner
        TransactionFactory(
            platform=platform, contact=contact, axe=axe,
            type='KÖP', price=Decimal('100.00')
        )
        TransactionFactory(
            platform=platform, contact=contact, axe=axe,
            type='SÄLJ', price=Decimal('150.00')
        )
        
        self.assertEqual(platform.get_transaction_count(), 2)
        self.assertEqual(platform.get_buy_count(), 1)
        self.assertEqual(platform.get_sale_count(), 1)
        self.assertEqual(platform.get_total_buy_value(), Decimal('100.00'))
        self.assertEqual(platform.get_total_sale_value(), Decimal('150.00'))
        self.assertEqual(platform.get_profit_loss(), Decimal('50.00'))


class SettingsModelTest(TestCase):
    """Tester för Settings-modellen"""
    
    def test_settings_creation(self):
        """Test att skapa inställningar"""
        settings = SettingsFactory()
        self.assertIsNotNone(settings.id)
    
    def test_settings_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        settings = SettingsFactory(site_title="Test Site")
        self.assertEqual(str(settings), "Systeminställningar")
    
    def test_get_settings_class_method(self):
        """Test get_settings class method"""
        # Skapa inställningar
        settings = SettingsFactory()
        
        # Hämta inställningar
        retrieved_settings = Settings.get_settings()
        self.assertEqual(retrieved_settings, settings)
        
        # Test att skapa nya inställningar om inga finns
        Settings.objects.all().delete()
        new_settings = Settings.get_settings()
        self.assertIsNotNone(new_settings.id)


class MeasurementTypeModelTest(TestCase):
    """Tester för MeasurementType-modellen"""
    
    def test_measurement_type_creation(self):
        """Test att skapa en måtttyp"""
        measurement_type = MeasurementTypeFactory()
        self.assertIsNotNone(measurement_type.id)
        self.assertIsInstance(measurement_type.name, str)
        self.assertIsInstance(measurement_type.unit, str)
    
    def test_measurement_type_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        measurement_type = MeasurementTypeFactory(name="Test Måtttyp")
        self.assertEqual(str(measurement_type), "Test Måtttyp (gram)")


class MeasurementTemplateModelTest(TestCase):
    """Tester för MeasurementTemplate-modellen"""
    
    def test_measurement_template_creation(self):
        """Test att skapa en måttmall"""
        template = MeasurementTemplateFactory()
        self.assertIsNotNone(template.id)
        self.assertIsInstance(template.name, str)
    
    def test_measurement_template_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        template = MeasurementTemplateFactory(name="Test Mall")
        self.assertEqual(str(template), "Test Mall")


class MeasurementModelTest(TestCase):
    """Tester för Measurement-modellen"""
    
    def test_measurement_creation(self):
        """Test att skapa ett mått"""
        measurement = MeasurementFactory()
        self.assertIsNotNone(measurement.id)
        self.assertIsInstance(measurement.name, str)
        self.assertIsInstance(measurement.value, Decimal)
        self.assertIsInstance(measurement.unit, str)
    
    def test_measurement_str_representation(self):
        """Test att __str__ returnerar rätt värde"""
        measurement = MeasurementFactory(name="Test Mått", value=Decimal('100.50'), unit="mm")
        expected = f"{measurement.axe}: Test Mått är 100.50 mm"
        self.assertEqual(str(measurement), expected) 