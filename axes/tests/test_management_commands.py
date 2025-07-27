import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from io import StringIO
from axes.models import Transaction, Axe, Contact, Platform, Manufacturer, NextAxeID
from decimal import Decimal
from django.utils import timezone


class ClearTransactionsCommandTest(TestCase):
    def setUp(self):
        # Skapa testdata
        self.contact = Contact.objects.create(name="Test Contact")
        self.platform = Platform.objects.create(name="Test Platform")
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Axe",
            status="KÖPT"
        )
        
        # Skapa några transaktioner
        self.transaction1 = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="KÖP",
            price=Decimal("100.00"),
            shipping_cost=Decimal("10.00")
        )
        
        self.transaction2 = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="SÄLJ",
            price=Decimal("150.00"),
            shipping_cost=Decimal("15.00")
        )

    def test_clear_transactions_without_confirm(self):
        """Testa att kommandot kräver bekräftelse"""
        out = StringIO()
        call_command('clear_transactions', stdout=out)
        
        output = out.getvalue()
        self.assertIn("Du är på väg att radera 2 transaktioner!", output)
        self.assertIn("Kör kommandot igen med --confirm för att bekräfta.", output)
        
        # Kontrollera att transaktionerna fortfarande finns
        self.assertEqual(Transaction.objects.count(), 2)

    def test_clear_transactions_with_confirm(self):
        """Testa att kommandot raderar transaktioner med bekräftelse"""
        out = StringIO()
        call_command('clear_transactions', confirm=True, stdout=out)
        
        output = out.getvalue()
        self.assertIn("Raderar 2 transaktioner...", output)
        self.assertIn("SUCCESS: Raderade 2 transaktioner!", output)
        
        # Kontrollera att transaktionerna är raderade
        self.assertEqual(Transaction.objects.count(), 0)

    def test_clear_transactions_no_transactions(self):
        """Testa kommandot när det inte finns några transaktioner"""
        # Rensa alla transaktioner först
        Transaction.objects.all().delete()
        
        out = StringIO()
        call_command('clear_transactions', confirm=True, stdout=out)
        
        output = out.getvalue()
        self.assertIn("Raderar 0 transaktioner...", output)
        self.assertIn("SUCCESS: Raderade 0 transaktioner!", output)
        
        # Kontrollera att det fortfarande inte finns några transaktioner
        self.assertEqual(Transaction.objects.count(), 0)


class MarkAllAxesReceivedCommandTest(TestCase):
    def setUp(self):
        # Skapa testdata
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        
        # Skapa yxor med olika status
        self.axe1 = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Axe 1",
            status="KÖPT"
        )
        
        self.axe2 = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Axe 2",
            status="MOTTAGEN"
        )
        
        self.axe3 = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Axe 3",
            status="KÖPT"
        )

    def test_mark_all_axes_received(self):
        """Testa att kommandot sätter alla yxor till MOTTAGEN"""
        out = StringIO()
        call_command('mark_all_axes_received', stdout=out)
        
        output = out.getvalue()
        self.assertIn("Satte status till MOTTAGEN för 3 yxor.", output)
        
        # Kontrollera att alla yxor har status MOTTAGEN
        self.axe1.refresh_from_db()
        self.axe2.refresh_from_db()
        self.axe3.refresh_from_db()
        
        self.assertEqual(self.axe1.status, "MOTTAGEN")
        self.assertEqual(self.axe2.status, "MOTTAGEN")
        self.assertEqual(self.axe3.status, "MOTTAGEN")

    def test_mark_all_axes_received_no_axes(self):
        """Testa kommandot när det inte finns några yxor"""
        # Rensa alla yxor först
        Axe.objects.all().delete()
        
        out = StringIO()
        call_command('mark_all_axes_received', stdout=out)
        
        output = out.getvalue()
        self.assertIn("Satte status till MOTTAGEN för 0 yxor.", output)
        
        # Kontrollera att det fortfarande inte finns några yxor
        self.assertEqual(Axe.objects.count(), 0)


class InitNextAxeIDCommandTest(TestCase):
    def setUp(self):
        # Rensa befintliga NextAxeID objekt
        NextAxeID.objects.all().delete()
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")

    def test_init_next_axe_id_with_existing_axes(self):
        """Testa att kommandot sätter rätt nästa ID när det finns befintliga yxor"""
        # Skapa några yxor med specifika ID:n
        axe1 = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Axe 1",
            status="KÖPT"
        )
        axe2 = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Axe 2",
            status="KÖPT"
        )
        
        # Hitta högsta ID:t
        max_id = max(axe1.id, axe2.id)
        expected_next_id = max_id + 1
        
        out = StringIO()
        call_command('init_next_axe_id', stdout=out)
        
        output = out.getvalue()
        self.assertIn(f"Nästa yx-ID satt till {expected_next_id}", output)
        
        # Kontrollera att NextAxeID är korrekt satt
        next_axe_id = NextAxeID.objects.get(id=1)
        self.assertEqual(next_axe_id.next_id, expected_next_id)

    def test_init_next_axe_id_no_axes(self):
        """Testa att kommandot sätter nästa ID till 1 när det inte finns några yxor"""
        # Rensa alla yxor
        Axe.objects.all().delete()
        
        out = StringIO()
        call_command('init_next_axe_id', stdout=out)
        
        output = out.getvalue()
        self.assertIn("Nästa yx-ID satt till 1", output)
        
        # Kontrollera att NextAxeID är korrekt satt
        next_axe_id = NextAxeID.objects.get(id=1)
        self.assertEqual(next_axe_id.next_id, 1)

    def test_init_next_axe_id_updates_existing(self):
        """Testa att kommandot uppdaterar befintligt NextAxeID objekt"""
        # Skapa ett befintligt NextAxeID objekt
        existing_next_id = NextAxeID.objects.create(id=1, next_id=999)
        
        # Skapa en yxa
        axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Axe",
            status="KÖPT"
        )
        
        expected_next_id = axe.id + 1
        
        out = StringIO()
        call_command('init_next_axe_id', stdout=out)
        
        output = out.getvalue()
        self.assertIn(f"Nästa yx-ID satt till {expected_next_id}", output)
        
        # Kontrollera att NextAxeID är uppdaterat
        existing_next_id.refresh_from_db()
        self.assertEqual(existing_next_id.next_id, expected_next_id) 