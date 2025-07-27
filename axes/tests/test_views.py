import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from axes.models import Axe, Contact, Manufacturer, Platform, Transaction, Settings
from decimal import Decimal
from django.utils import timezone
import json


class ViewsTestCase(TestCase):
    def setUp(self):
        # Skapa testanvändare
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        
        # Skapa settings för att undvika problem med publik filtrering
        self.settings = Settings.objects.create(
            id=1,  # Använd ID=1 för att matcha Settings.get_settings()
            show_contacts_public=True,
            show_prices_public=True,
            show_platforms_public=True,
            show_only_received_axes_public=False
        )
        
        # Skapa testdata
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.contact = Contact.objects.create(name="Test Contact", email="test@example.com")
        self.platform = Platform.objects.create(name="Test Platform")
        
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
    
    def _add_public_settings_to_request(self, request):
        """Lägg till publika inställningar till request för sökfunktioner"""
        request.public_settings = {
            'show_contacts': self.settings.show_contacts_public,
            'show_prices': self.settings.show_prices_public,
            'show_platforms': self.settings.show_platforms_public,
            'show_only_received_axes': self.settings.show_only_received_axes_public,
        }
        return request


class SearchViewsTest(ViewsTestCase):
    def test_search_contacts_empty_query(self):
        """Testa sökning efter kontakter med tom query"""
        response = self.client.get('/api/search/contacts/', {'q': ''})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['results'], [])

    def test_search_contacts_short_query(self):
        """Testa sökning efter kontakter med för kort query"""
        response = self.client.get('/api/search/contacts/', {'q': 'a'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['results'], [])

    def test_search_contacts_valid_query(self):
        """Testa sökning efter kontakter med giltig query"""
        response = self.client.get('/api/search/contacts/', {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['name'], 'Test Contact')

    def test_search_contacts_by_email(self):
        """Testa sökning efter kontakter via e-post"""
        response = self.client.get('/api/search/contacts/', {'q': 'test@example.com'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['email'], 'test@example.com')

    def test_search_platforms_empty_query(self):
        """Testa sökning efter plattformar med tom query"""
        response = self.client.get('/api/search/platforms/', {'q': ''})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['results'], [])

    def test_search_platforms_short_query(self):
        """Testa sökning efter plattformar med för kort query"""
        response = self.client.get('/api/search/platforms/', {'q': 'a'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['results'], [])

    def test_search_platforms_valid_query(self):
        """Testa sökning efter plattformar med giltig query"""
        response = self.client.get('/api/search/platforms/', {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['name'], 'Test Platform')


class GlobalSearchTest(ViewsTestCase):
    def test_global_search_empty_query(self):
        """Testa global sökning med tom query"""
        response = self.client.get('/api/search/global/', {'q': ''})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['results'], {})

    def test_global_search_short_query(self):
        """Testa global sökning med för kort query"""
        response = self.client.get('/api/search/global/', {'q': 'a'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['results'], {})

    def test_global_search_axes(self):
        """Testa global sökning efter yxor"""
        response = self.client.get('/api/search/global/', {'q': 'Test Axe'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('axes', data['results'])
        # Kontrollera att yxan finns i resultatet
        axes_results = data['results']['axes']
        self.assertGreater(len(axes_results), 0)
        self.assertIn('Test Axe', str(axes_results))

    def test_global_search_manufacturer(self):
        """Testa global sökning efter tillverkare"""
        response = self.client.get('/api/search/global/', {'q': 'Test Manufacturer'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('manufacturers', data['results'])
        # Kontrollera att tillverkaren finns i resultatet
        manufacturers_results = data['results']['manufacturers']
        self.assertGreater(len(manufacturers_results), 0)
        self.assertIn('Test Manufacturer', str(manufacturers_results))

    def test_global_search_contact(self):
        """Testa global sökning efter kontakt"""
        # Logga in för att säkerställa att kontakter visas
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/search/global/', {'q': 'Test Contact'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('contacts', data['results'])
        # Kontrollera att kontakten finns i resultatet
        contacts_results = data['results']['contacts']
        self.assertGreater(len(contacts_results), 0)
        self.assertIn('Test Contact', str(contacts_results))

    def test_global_search_transaction(self):
        """Testa global sökning efter transaktion"""
        response = self.client.get('/api/search/global/', {'q': '100.00'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('transactions', data['results'])

    def test_global_search_axe_id(self):
        """Testa global sökning efter yx-ID"""
        response = self.client.get('/api/search/global/', {'q': str(self.axe.id)})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('axes', data['results'])
        # Kontrollera att yxan finns i resultatet
        axes_results = data['results']['axes']
        self.assertGreater(len(axes_results), 0)
        self.assertIn(str(self.axe.id), str(axes_results))


class PublicPrivateFilteringTest(ViewsTestCase):
    def setUp(self):
        super().setUp()
        # Uppdatera settings för publik filtrering
        self.settings.show_only_received_axes_public = True
        self.settings.save()
        
        # Skapa en yxa som inte är mottagen
        self.unreceived_axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Unreceived Axe",
            status="KÖPT"
        )

    def test_public_search_hides_unreceived_axes(self):
        """Testa att publik sökning döljer oemottagna yxor"""
        # Sök utan att vara inloggad
        response = self.client.get('/api/search/global/', {'q': 'Unreceived'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Kontrollera att den oemottagna yxan inte visas
        axes_results = data['results'].get('axes', [])
        unreceived_found = any('Unreceived Axe' in str(result) for result in axes_results)
        self.assertFalse(unreceived_found)

    def test_private_search_shows_all_axes(self):
        """Testa att privat sökning visar alla yxor"""
        # Logga in och sök
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/search/global/', {'q': 'Unreceived'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Kontrollera att den oemottagna yxan visas
        axes_results = data['results'].get('axes', [])
        unreceived_found = any('Unreceived Axe' in str(result) for result in axes_results)
        self.assertTrue(unreceived_found)


class AxeListViewTest(ViewsTestCase):
    def test_axe_list_view(self):
        """Testa yxlistan"""
        response = self.client.get('/yxor/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_list.html')
        # Kontrollera att yxan finns i listan
        self.assertContains(response, 'Test Axe')

    def test_axe_list_with_filters(self):
        """Testa yxlistan med filter"""
        response = self.client.get('/yxor/', {
            'manufacturer': self.manufacturer.id,
            'status': 'KÖPT'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_list.html')
        # Kontrollera att yxan finns i listan
        self.assertContains(response, 'Test Axe')

    def test_axe_list_with_search(self):
        """Testa yxlistan med sökning"""
        response = self.client.get('/yxor/', {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_list.html')
        # Kontrollera att yxan finns i listan
        self.assertContains(response, 'Test Axe')


class StatisticsDashboardTest(ViewsTestCase):
    def test_statistics_dashboard_public_access(self):
        """Testa att statistikdashboard är tillgänglig för alla"""
        response = self.client.get('/statistik/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/statistics_dashboard.html')

    def test_statistics_dashboard_with_login(self):
        """Testa statistikdashboard med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/statistik/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/statistics_dashboard.html')


class SettingsViewTest(ViewsTestCase):
    def test_settings_view_requires_login(self):
        """Testa att inställningssidan kräver inloggning"""
        response = self.client.get('/installningar/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_settings_view_with_login(self):
        """Testa inställningssidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/installningar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/settings.html')
