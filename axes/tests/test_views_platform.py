import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from axes.models import Axe, Contact, Manufacturer, Platform, Transaction, Settings
from decimal import Decimal
from django.utils import timezone
import json


class ViewsPlatformTestCase(TestCase):
    def setUp(self):
        # Skapa testanvändare
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        
        # Skapa settings för att undvika problem med publik filtrering
        self.settings = Settings.objects.create(
            show_contacts_public=True,
            show_prices_public=True,
            show_platforms_public=True,
            show_only_received_axes_public=False
        )
        
        # Skapa testdata
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.contact = Contact.objects.create(name="Test Contact", email="test@example.com")
        self.platform = Platform.objects.create(name="Test Platform", color_class="bg-primary")
        
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Axe",
            status="KÖPT"
        )
        
        self.transaction = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="KÖP",
            price=Decimal("100.00"),
            shipping_cost=Decimal("10.00")
        )


class PlatformListViewTest(ViewsPlatformTestCase):
    def test_platform_list_view_requires_login(self):
        """Testa att plattformlista-sidan kräver inloggning"""
        response = self.client.get('/plattformar/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_platform_list_view_with_login(self):
        """Testa plattformlista-sidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/plattformar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/platform_list.html')

    def test_platform_list_view_contains_platforms(self):
        """Testa att plattformlista-sidan innehåller plattformar"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/plattformar/')
        self.assertIn('platforms', response.context)
        self.assertGreater(len(response.context['platforms']), 0)
        self.assertIn('page_title', response.context)
        self.assertEqual(response.context['page_title'], 'Plattformar')

    def test_platform_list_view_platform_statistics(self):
        """Testa att plattformlista-sidan innehåller statistik för plattformar"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/plattformar/')
        platform = response.context['platforms'].first()
        self.assertIsNotNone(platform)
        self.assertEqual(platform.transaction_count, 1)
        self.assertEqual(platform.buy_count, 1)
        self.assertEqual(platform.sale_count, 0)
        self.assertEqual(platform.total_buy_value, Decimal('100.00'))
        # Django Sum returnerar None när det inte finns några värden
        self.assertIsNone(platform.total_sale_value)


class PlatformDetailViewTest(ViewsPlatformTestCase):
    def test_platform_detail_view_requires_login(self):
        """Testa att plattformdetail-sidan kräver inloggning"""
        response = self.client.get(f'/plattformar/{self.platform.id}/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_platform_detail_view_with_login(self):
        """Testa plattformdetail-sidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/plattformar/{self.platform.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/platform_detail.html')
        self.assertEqual(response.context['platform'], self.platform)

    def test_platform_detail_view_invalid_id(self):
        """Testa plattformdetail-sidan med ogiltigt ID"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/plattformar/99999/')
        self.assertEqual(response.status_code, 404)

    def test_platform_detail_view_contains_platform_info(self):
        """Testa att plattformdetail-sidan innehåller plattformsinformation"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/plattformar/{self.platform.id}/')
        self.assertContains(response, 'Test Platform')
        self.assertIn('transactions', response.context)
        self.assertIn('buy_transactions', response.context)
        self.assertIn('sale_transactions', response.context)
        self.assertIn('total_buy_value', response.context)
        self.assertIn('total_sale_value', response.context)
        self.assertIn('total_buy_shipping', response.context)
        self.assertIn('total_sale_shipping', response.context)
        self.assertIn('profit_loss', response.context)
        self.assertIn('profit_loss_with_shipping', response.context)
        self.assertIn('unique_axes', response.context)
        self.assertIn('page_title', response.context)

    def test_platform_detail_view_with_transactions(self):
        """Testa plattformdetail-sidan med transaktioner"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/plattformar/{self.platform.id}/')
        self.assertEqual(len(response.context['transactions']), 1)
        self.assertEqual(len(response.context['buy_transactions']), 1)
        self.assertEqual(len(response.context['sale_transactions']), 0)
        self.assertEqual(response.context['total_buy_value'], Decimal('100.00'))
        self.assertEqual(response.context['total_sale_value'], 0)
        self.assertEqual(response.context['total_buy_shipping'], Decimal('10.00'))
        self.assertEqual(response.context['total_sale_shipping'], 0)
        self.assertEqual(response.context['profit_loss'], Decimal('-100.00'))
        self.assertEqual(response.context['profit_loss_with_shipping'], Decimal('-110.00'))


class PlatformCreateViewTest(ViewsPlatformTestCase):
    def test_platform_create_view_requires_login(self):
        """Testa att plattformcreate-sidan kräver inloggning"""
        response = self.client.get('/plattformar/ny/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_platform_create_view_with_login(self):
        """Testa plattformcreate-sidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/plattformar/ny/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/platform_form.html')

    def test_platform_create_view_post_valid_data(self):
        """Testa att skapa en ny plattform med giltig data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'name': 'New Test Platform',
            'color_class': 'bg-success'
        }
        
        response = self.client.post('/plattformar/ny/', data)
        self.assertEqual(response.status_code, 302)  # Redirect efter skapande
        
        # Kontrollera att plattformen skapades
        new_platform = Platform.objects.filter(name='New Test Platform').first()
        self.assertIsNotNone(new_platform)
        self.assertEqual(new_platform.color_class, 'bg-success')

    def test_platform_create_view_post_invalid_data(self):
        """Testa att skapa en ny plattform med ogiltig data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'color_class': 'bg-success'
            # Saknar name (obligatoriskt)
        }
        
        response = self.client.post('/plattformar/ny/', data)
        self.assertEqual(response.status_code, 200)  # Stannar på formuläret
        self.assertTemplateUsed(response, 'axes/platform_form.html')
        
        # Kontrollera att plattformen inte skapades
        new_platform = Platform.objects.filter(color_class='bg-success').first()
        self.assertIsNone(new_platform)


class PlatformEditViewTest(ViewsPlatformTestCase):
    def test_platform_edit_view_requires_login(self):
        """Testa att plattformedit-sidan kräver inloggning"""
        response = self.client.get(f'/plattformar/{self.platform.id}/redigera/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_platform_edit_view_with_login(self):
        """Testa plattformedit-sidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/plattformar/{self.platform.id}/redigera/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/platform_form.html')
        self.assertEqual(response.context['platform'], self.platform)

    def test_platform_edit_view_post_valid_data(self):
        """Testa att redigera en plattform med giltig data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'name': 'Updated Test Platform',
            'color_class': 'bg-warning'
        }
        
        response = self.client.post(f'/plattformar/{self.platform.id}/redigera/', data)
        self.assertEqual(response.status_code, 302)  # Redirect efter uppdatering
        
        # Kontrollera att plattformen uppdaterades
        self.platform.refresh_from_db()
        self.assertEqual(self.platform.name, 'Updated Test Platform')
        self.assertEqual(self.platform.color_class, 'bg-warning')

    def test_platform_edit_view_invalid_id(self):
        """Testa plattformedit-sidan med ogiltigt ID"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/plattformar/99999/redigera/')
        self.assertEqual(response.status_code, 404)


class PlatformDeleteViewTest(ViewsPlatformTestCase):
    def test_platform_delete_view_requires_login(self):
        """Testa att plattformdelete-sidan kräver inloggning"""
        response = self.client.get(f'/plattformar/{self.platform.id}/ta-bort/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_platform_delete_view_with_login_get(self):
        """Testa plattformdelete-sidan med GET-request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/plattformar/{self.platform.id}/ta-bort/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/platform_delete.html')
        self.assertEqual(response.context['platform'], self.platform)
        self.assertEqual(response.context['transaction_count'], 1)

    def test_platform_delete_view_with_login_post_with_transactions(self):
        """Testa att ta bort plattform med transaktioner (ska misslyckas)"""
        self.client.login(username='testuser', password='testpass123')
        
        # Kontrollera att transaktionen finns
        self.assertEqual(Transaction.objects.count(), 1)
        
        response = self.client.post(f'/plattformar/{self.platform.id}/ta-bort/')
        self.assertEqual(response.status_code, 302)  # Redirect till plattformdetail
        
        # Kontrollera att plattformen inte är borta
        self.assertEqual(Platform.objects.count(), 1)

    def test_platform_delete_view_with_login_post_without_transactions(self):
        """Testa att ta bort plattform utan transaktioner"""
        self.client.login(username='testuser', password='testpass123')
        
        # Ta bort transaktionen först
        Transaction.objects.all().delete()
        
        # Kontrollera att ingen transaktion finns
        self.assertEqual(Transaction.objects.count(), 0)
        
        response = self.client.post(f'/plattformar/{self.platform.id}/ta-bort/')
        self.assertEqual(response.status_code, 302)  # Redirect till plattformlista
        
        # Kontrollera att plattformen är borta
        self.assertEqual(Platform.objects.count(), 0)

    def test_platform_delete_view_invalid_id(self):
        """Testa plattformdelete-sidan med ogiltigt ID"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/plattformar/99999/ta-bort/')
        self.assertEqual(response.status_code, 404) 