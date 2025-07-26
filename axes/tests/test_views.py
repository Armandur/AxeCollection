from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.management import call_command
from axes.models import Manufacturer, Axe, Contact, Platform


class ViewsTestCase(TestCase):
    """Basal testklass för views med gemensam setup"""

    def setUp(self):
        """Skapa testdata och användare för varje test"""
        # Skapa testanvändare
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )

        # Skapa testdata
        call_command('generate_test_data', '--clear', '--manufacturers', '3', '--axes', '5', '--contacts', '3')

        # Skapa klient
        self.client = Client()

    def login_user(self):
        """Logga in användaren"""
        return self.client.login(username='testuser', password='testpass123')


class AxeViewsTest(ViewsTestCase):
    """Tester för axe-relaterade views"""

    def test_axe_list_view_authenticated(self):
        """Test att axe_list view fungerar för inloggade användare"""
        self.login_user()
        response = self.client.get(reverse('axe_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_list.html')

        # Kontrollera att yxor finns i context
        self.assertIn('axes', response.context)
        self.assertGreater(len(response.context['axes']), 0)

    def test_axe_list_view_unauthenticated(self):
        """Test att axe_list view fungerar för oinloggade användare (publik)"""
        response = self.client.get(reverse('axe_list'))
        self.assertEqual(response.status_code, 200)  # Publik view
        self.assertTemplateUsed(response, 'axes/axe_list.html')

    def test_axe_detail_view_authenticated(self):
        """Test att axe_detail view fungerar"""
        self.login_user()
        axe = Axe.objects.first()
        response = self.client.get(reverse('axe_detail', args=[axe.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_detail.html')
        self.assertEqual(response.context['axe'], axe)

    def test_axe_detail_view_unauthenticated(self):
        """Test att axe_detail view fungerar för oinloggade användare (publik)"""
        axe = Axe.objects.first()
        response = self.client.get(reverse('axe_detail', args=[axe.id]))
        self.assertEqual(response.status_code, 200)  # Publik view
        self.assertTemplateUsed(response, 'axes/axe_detail.html')

    def test_axe_detail_view_invalid_id(self):
        """Test att axe_detail view hanterar ogiltiga ID:n"""
        self.login_user()
        response = self.client.get(reverse('axe_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)


class ManufacturerViewsTest(ViewsTestCase):
    """Tester för manufacturer-relaterade views"""

    def test_manufacturer_list_view_authenticated(self):
        """Test att manufacturer_list view fungerar"""
        self.login_user()
        response = self.client.get(reverse('manufacturer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/manufacturer_list.html')

        # Kontrollera att tillverkare finns i context
        self.assertIn('manufacturers', response.context)
        self.assertGreater(len(response.context['manufacturers']), 0)

    def test_manufacturer_list_view_unauthenticated(self):
        """Test att manufacturer_list view fungerar för oinloggade användare (publik)"""
        response = self.client.get(reverse('manufacturer_list'))
        self.assertEqual(response.status_code, 200)  # Publik view
        self.assertTemplateUsed(response, 'axes/manufacturer_list.html')

    def test_manufacturer_detail_view_authenticated(self):
        """Test att manufacturer_detail view fungerar"""
        self.login_user()
        manufacturer = Manufacturer.objects.first()
        response = self.client.get(reverse('manufacturer_detail', args=[manufacturer.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/manufacturer_detail.html')
        self.assertEqual(response.context['manufacturer'], manufacturer)

    def test_manufacturer_detail_view_unauthenticated(self):
        """Test att manufacturer_detail view fungerar för oinloggade användare (publik)"""
        manufacturer = Manufacturer.objects.first()
        response = self.client.get(reverse('manufacturer_detail', args=[manufacturer.id]))
        self.assertEqual(response.status_code, 200)  # Publik view
        self.assertTemplateUsed(response, 'axes/manufacturer_detail.html')


class ContactViewsTest(ViewsTestCase):
    """Tester för contact-relaterade views"""

    def test_contact_list_view_authenticated(self):
        """Test att contact_list view fungerar"""
        self.login_user()
        response = self.client.get(reverse('contact_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/contact_list.html')

        # Kontrollera att kontakter finns i context
        self.assertIn('contacts', response.context)
        self.assertGreater(len(response.context['contacts']), 0)

    def test_contact_list_view_unauthenticated(self):
        """Test att contact_list view fungerar för oinloggade användare (publik)"""
        response = self.client.get(reverse('contact_list'))
        self.assertEqual(response.status_code, 200)  # Publik view
        self.assertTemplateUsed(response, 'axes/contact_list.html')

    def test_contact_detail_view_authenticated(self):
        """Test att contact_detail view fungerar"""
        self.login_user()
        contact = Contact.objects.first()
        response = self.client.get(reverse('contact_detail', args=[contact.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/contact_detail.html')
        self.assertEqual(response.context['contact'], contact)

    def test_contact_detail_view_unauthenticated(self):
        """Test att contact_detail view fungerar för oinloggade användare (publik)"""
        contact = Contact.objects.first()
        response = self.client.get(reverse('contact_detail', args=[contact.id]))
        self.assertEqual(response.status_code, 200)  # Publik view
        self.assertTemplateUsed(response, 'axes/contact_detail.html')


class PlatformViewsTest(ViewsTestCase):
    """Tester för platform-relaterade views"""

    def test_platform_list_view_authenticated(self):
        """Test att platform_list view fungerar"""
        self.login_user()
        response = self.client.get(reverse('platform_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/platform_list.html')

        # Kontrollera att plattformar finns i context
        self.assertIn('platforms', response.context)
        self.assertGreater(len(response.context['platforms']), 0)

    def test_platform_list_view_unauthenticated(self):
        """Test att platform_list view kräver inloggning"""
        response = self.client.get(reverse('platform_list'))
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_platform_detail_view_authenticated(self):
        """Test att platform_detail view fungerar"""
        self.login_user()
        platform = Platform.objects.first()
        response = self.client.get(reverse('platform_detail', args=[platform.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/platform_detail.html')
        self.assertEqual(response.context['platform'], platform)

    def test_platform_detail_view_unauthenticated(self):
        """Test att platform_detail view kräver inloggning"""
        platform = Platform.objects.first()
        response = self.client.get(reverse('platform_detail', args=[platform.id]))
        self.assertEqual(response.status_code, 302)  # Redirect till login


class TransactionViewsTest(ViewsTestCase):
    """Tester för transaction-relaterade views"""

    def test_transaction_list_view_authenticated(self):
        """Test att transaction_list view fungerar"""
        self.login_user()
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/transaction_list.html')

        # Kontrollera att transaktioner finns i context
        self.assertIn('transactions', response.context)

    def test_transaction_list_view_unauthenticated(self):
        """Test att transaction_list view fungerar för oinloggade användare (publik)"""
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)  # Publik view
        self.assertTemplateUsed(response, 'axes/transaction_list.html')


class StatisticsViewsTest(ViewsTestCase):
    """Tester för statistik-relaterade views"""

    def test_statistics_dashboard_view_authenticated(self):
        """Test att statistics_dashboard view fungerar"""
        self.login_user()
        response = self.client.get(reverse('statistics_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/statistics_dashboard.html')

        # Kontrollera att statistik finns i context
        self.assertIn('total_axes', response.context)
        self.assertIn('total_manufacturers', response.context)
        self.assertIn('total_contacts', response.context)

    def test_statistics_dashboard_view_unauthenticated(self):
        """Test att statistics_dashboard view fungerar för oinloggade användare (publik)"""
        response = self.client.get(reverse('statistics_dashboard'))
        self.assertEqual(response.status_code, 200)  # Publik view
        self.assertTemplateUsed(response, 'axes/statistics_dashboard.html')


class SettingsViewsTest(ViewsTestCase):
    """Tester för settings-relaterade views"""

    def test_settings_view_authenticated(self):
        """Test att settings view fungerar"""
        self.login_user()
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/settings.html')

        # Kontrollera att inställningar finns i context
        self.assertIn('settings', response.context)

    def test_settings_view_unauthenticated(self):
        """Test att settings view kräver inloggning"""
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 302)  # Redirect till login
