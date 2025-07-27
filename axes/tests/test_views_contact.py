import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from axes.models import Axe, Contact, Manufacturer, Platform, Transaction, Settings
from decimal import Decimal
from django.utils import timezone
import json


class ViewsContactTestCase(TestCase):
    def setUp(self):
        # Skapa testanvändare
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = Client()

        # Skapa settings för att undvika problem med publik filtrering
        self.settings = Settings.objects.create(
            show_contacts_public=True,
            show_prices_public=True,
            show_platforms_public=True,
            show_only_received_axes_public=False,
        )

        # Skapa testdata
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.contact = Contact.objects.create(
            name="Test Contact", email="test@example.com"
        )
        self.platform = Platform.objects.create(name="Test Platform")

        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe", status="KÖPT"
        )

        self.transaction = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="KÖP",
            price=Decimal("100.00"),
            shipping_cost=Decimal("10.00"),
        )


class ContactListViewTest(ViewsContactTestCase):
    def test_contact_list_view_public(self):
        """Testa att kontaktlista-sidan är tillgänglig för alla"""
        response = self.client.get("/kontakter/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "axes/contact_list.html")

    def test_contact_list_view_with_login(self):
        """Testa kontaktlista-sidan med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/kontakter/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "axes/contact_list.html")

    def test_contact_list_view_contains_contacts(self):
        """Testa att kontaktlista-sidan innehåller kontakter"""
        response = self.client.get("/kontakter/")
        self.assertIn("contacts", response.context)
        self.assertGreater(len(response.context["contacts"]), 0)
        self.assertIn("total_contacts", response.context)
        self.assertIn("total_transactions", response.context)
        self.assertIn("total_naj_members", response.context)

    def test_contact_list_view_with_sort(self):
        """Testa kontaktlista-sidan med sortering"""
        response = self.client.get("/kontakter/", {"sort": "senast"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "axes/contact_list.html")
        self.assertEqual(response.context["sort"], "senast")

    def test_contact_list_view_default_sort(self):
        """Testa kontaktlista-sidan med standardsortering"""
        response = self.client.get("/kontakter/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "axes/contact_list.html")
        # Standardsortering är alfabetisk
        contacts = response.context["contacts"]
        if len(contacts) > 1:
            self.assertLessEqual(contacts[0].name.lower(), contacts[1].name.lower())


class ContactDetailViewTest(ViewsContactTestCase):
    def test_contact_detail_view_public(self):
        """Testa att kontaktdetail-sidan är tillgänglig för alla"""
        response = self.client.get(f"/kontakter/{self.contact.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "axes/contact_detail.html")
        self.assertEqual(response.context["contact"], self.contact)

    def test_contact_detail_view_with_login(self):
        """Testa kontaktdetail-sidan med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(f"/kontakter/{self.contact.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "axes/contact_detail.html")
        self.assertEqual(response.context["contact"], self.contact)

    def test_contact_detail_view_invalid_id(self):
        """Testa kontaktdetail-sidan med ogiltigt ID"""
        response = self.client.get("/kontakter/99999/")
        self.assertEqual(response.status_code, 404)

    def test_contact_detail_view_contains_contact_info(self):
        """Testa att kontaktdetail-sidan innehåller kontaktinformation"""
        response = self.client.get(f"/kontakter/{self.contact.id}/")
        self.assertContains(response, "Test Contact")
        self.assertIn("transactions", response.context)
        self.assertIn("total_transactions", response.context)
        self.assertIn("total_buy_value", response.context)
        self.assertIn("total_sale_value", response.context)
        self.assertIn("total_profit", response.context)
        self.assertIn("unique_axes", response.context)
        self.assertIn("buy_count", response.context)
        self.assertIn("sale_count", response.context)

    def test_contact_detail_view_with_transactions(self):
        """Testa kontaktdetail-sidan med transaktioner"""
        response = self.client.get(f"/kontakter/{self.contact.id}/")
        self.assertEqual(response.context["total_transactions"], 1)
        self.assertEqual(response.context["buy_count"], 1)
        self.assertEqual(response.context["sale_count"], 0)
        self.assertEqual(response.context["total_buy_value"], Decimal("100.00"))
        self.assertEqual(response.context["total_sale_value"], 0)
        self.assertEqual(response.context["total_profit"], Decimal("-100.00"))


class ContactCreateViewTest(ViewsContactTestCase):
    def test_contact_create_view_requires_login(self):
        """Testa att kontaktcreate-sidan kräver inloggning"""
        response = self.client.get("/kontakter/ny/")
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_contact_create_view_with_login(self):
        """Testa kontaktcreate-sidan med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/kontakter/ny/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "axes/contact_form.html")

    def test_contact_create_view_post_valid_data(self):
        """Testa att skapa en ny kontakt med giltig data"""
        self.client.login(username="testuser", password="testpass123")

        data = {
            "name": "New Test Contact",
            "email": "newtest@example.com",
            "country_code": "SE",
        }

        response = self.client.post("/kontakter/ny/", data)
        self.assertEqual(response.status_code, 302)  # Redirect efter skapande

        # Kontrollera att kontakten skapades
        new_contact = Contact.objects.filter(name="New Test Contact").first()
        self.assertIsNotNone(new_contact)
        self.assertEqual(new_contact.email, "newtest@example.com")
        self.assertEqual(new_contact.country_code, "SE")

    def test_contact_create_view_post_invalid_data(self):
        """Testa att skapa en ny kontakt med ogiltig data"""
        self.client.login(username="testuser", password="testpass123")

        data = {
            "email": "newtest@example.com",
            # Saknar name (obligatoriskt)
        }

        response = self.client.post("/kontakter/ny/", data)
        self.assertEqual(response.status_code, 200)  # Stannar på formuläret
        self.assertTemplateUsed(response, "axes/contact_form.html")

        # Kontrollera att kontakten inte skapades
        new_contact = Contact.objects.filter(email="newtest@example.com").first()
        self.assertIsNone(new_contact)


class ContactEditViewTest(ViewsContactTestCase):
    def test_contact_edit_view_requires_login(self):
        """Testa att kontaktedit-sidan kräver inloggning"""
        response = self.client.get(f"/kontakter/{self.contact.id}/redigera/")
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_contact_edit_view_with_login(self):
        """Testa kontaktedit-sidan med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(f"/kontakter/{self.contact.id}/redigera/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "axes/contact_form.html")
        self.assertEqual(response.context["contact"], self.contact)

    def test_contact_edit_view_post_valid_data(self):
        """Testa att redigera en kontakt med giltig data"""
        self.client.login(username="testuser", password="testpass123")

        data = {
            "name": "Updated Test Contact",
            "email": "updated@example.com",
            "country_code": "NO",
        }

        response = self.client.post(f"/kontakter/{self.contact.id}/redigera/", data)
        self.assertEqual(response.status_code, 302)  # Redirect efter uppdatering

        # Kontrollera att kontakten uppdaterades
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.name, "Updated Test Contact")
        self.assertEqual(self.contact.email, "updated@example.com")
        self.assertEqual(self.contact.country_code, "NO")

    def test_contact_edit_view_invalid_id(self):
        """Testa kontaktedit-sidan med ogiltigt ID"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/kontakter/99999/redigera/")
        self.assertEqual(response.status_code, 404)


class ContactDeleteViewTest(ViewsContactTestCase):
    def test_contact_delete_view_requires_login(self):
        """Testa att kontaktdelete-sidan kräver inloggning"""
        response = self.client.post(f"/kontakter/{self.contact.id}/ta-bort/")
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_contact_delete_view_with_login_delete_transactions(self):
        """Testa att ta bort kontakt med transaktioner"""
        self.client.login(username="testuser", password="testpass123")

        # Kontrollera att transaktionen finns
        self.assertEqual(Transaction.objects.count(), 1)

        response = self.client.post(
            f"/kontakter/{self.contact.id}/ta-bort/", {"delete_transactions": "true"}
        )
        self.assertEqual(response.status_code, 302)  # Redirect efter borttagning

        # Kontrollera att kontakten och transaktionen är borta
        self.assertEqual(Contact.objects.count(), 0)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_contact_delete_view_with_login_keep_transactions(self):
        """Testa att ta bort kontakt men behålla transaktioner"""
        self.client.login(username="testuser", password="testpass123")

        # Kontrollera att transaktionen finns
        self.assertEqual(Transaction.objects.count(), 1)

        response = self.client.post(
            f"/kontakter/{self.contact.id}/ta-bort/", {"delete_transactions": "false"}
        )
        self.assertEqual(response.status_code, 302)  # Redirect efter borttagning

        # Kontrollera att kontakten är borta men transaktionen finns kvar
        self.assertEqual(Contact.objects.count(), 0)
        self.assertEqual(Transaction.objects.count(), 1)

        # Kontrollera att transaktionen inte längre har en kontakt
        transaction = Transaction.objects.first()
        self.assertIsNone(transaction.contact)

    def test_contact_delete_view_invalid_id(self):
        """Testa kontaktdelete-sidan med ogiltigt ID"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            "/kontakter/99999/ta-bort/", {"delete_transactions": "true"}
        )
        self.assertEqual(response.status_code, 404)
