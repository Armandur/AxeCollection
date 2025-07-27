import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from axes.models import Axe, Contact, Manufacturer, Platform, Transaction, Settings, MeasurementType, MeasurementTemplate, MeasurementTemplateItem
from decimal import Decimal
from django.utils import timezone
import json
import os
import tempfile
import zipfile
from unittest.mock import patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings


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

    def test_search_contacts_by_alias(self):
        """Testa sökning efter kontakter via alias"""
        # Skapa en kontakt med alias
        contact_with_alias = Contact.objects.create(
            name="Alias Contact", 
            alias="testalias", 
            email="alias@example.com"
        )
        response = self.client.get('/api/search/contacts/', {'q': 'testalias'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['alias'], 'testalias')

    def test_search_contacts_limit_results(self):
        """Testa att sökning begränsar resultat till 10"""
        # Skapa 15 kontakter
        for i in range(15):
            Contact.objects.create(
                name=f"Contact {i}",
                email=f"contact{i}@example.com"
            )
        response = self.client.get('/api/search/contacts/', {'q': 'Contact'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertLessEqual(len(data['results']), 10)

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

    def test_search_platforms_limit_results(self):
        """Testa att plattformssökning begränsar resultat till 10"""
        # Skapa 15 plattformar
        for i in range(15):
            Platform.objects.create(name=f"Platform {i}")
        response = self.client.get('/api/search/platforms/', {'q': 'Platform'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertLessEqual(len(data['results']), 10)


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

    def test_global_search_numeric_query(self):
        """Testa global sökning med numerisk query (ID)"""
        response = self.client.get('/api/search/global/', {'q': str(self.axe.id)})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('axes', data['results'])
        self.assertGreater(len(data['results']['axes']), 0)

    def test_global_search_axes(self):
        """Testa global sökning för yxor"""
        response = self.client.get('/api/search/global/', {'q': 'Test Axe'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('axes', data['results'])
        self.assertGreater(len(data['results']['axes']), 0)

    def test_global_search_manufacturer(self):
        """Testa global sökning för tillverkare"""
        response = self.client.get('/api/search/global/', {'q': 'Test Manufacturer'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('manufacturers', data['results'])
        self.assertGreater(len(data['results']['manufacturers']), 0)

    def test_global_search_contact(self):
        """Testa global sökning för kontakter"""
        response = self.client.get('/api/search/global/', {'q': 'Test Contact'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('contacts', data['results'])
        self.assertGreater(len(data['results']['contacts']), 0)

    def test_global_search_transaction(self):
        """Testa global sökning för transaktioner"""
        response = self.client.get('/api/search/global/', {'q': 'Test Axe'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('transactions', data['results'])

    def test_global_search_axe_id(self):
        """Testa global sökning med yx-ID"""
        response = self.client.get('/api/search/global/', {'q': str(self.axe.id)})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('axes', data['results'])
        self.assertGreater(len(data['results']['axes']), 0)

    def test_global_search_contact_with_country_code(self):
        """Testa global sökning för kontakt med landskod"""
        # Skapa kontakt med svensk landskod
        swedish_contact = Contact.objects.create(
            name="Swedish Contact",
            email="swedish@example.com",
            country_code="SE"
        )
        response = self.client.get('/api/search/global/', {'q': 'Swedish'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('contacts', data['results'])
        contact_result = data['results']['contacts'][0]
        self.assertIn('🇸🇪', contact_result['subtitle'])

    def test_global_search_contact_with_finnish_country_code(self):
        """Testa global sökning för kontakt med finsk landskod"""
        # Skapa kontakt med finsk landskod
        finnish_contact = Contact.objects.create(
            name="Finnish Contact",
            email="finnish@example.com",
            country_code="FI"
        )
        response = self.client.get('/api/search/global/', {'q': 'Finnish'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('contacts', data['results'])
        contact_result = data['results']['contacts'][0]
        self.assertIn('🇫🇮', contact_result['subtitle'])

    def test_global_search_manufacturer_with_axe_count(self):
        """Testa global sökning för tillverkare med yxantal"""
        response = self.client.get('/api/search/global/', {'q': 'Test Manufacturer'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('manufacturers', data['results'])
        manufacturer_result = data['results']['manufacturers'][0]
        self.assertIn('1 yxor', manufacturer_result['subtitle'])


class PublicPrivateFilteringTest(ViewsTestCase):
    def setUp(self):
        super().setUp()
        # Skapa en yxa som inte är mottagen
        self.unreceived_axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Unreceived Axe",
            status="KÖPT"
        )
        
        # Uppdatera settings för att dölja oemottagna yxor publikt
        self.settings.show_only_received_axes_public = True
        self.settings.save()

    def test_public_search_hides_unreceived_axes(self):
        """Testa att publik sökning döljer oemottagna yxor"""
        response = self.client.get('/api/search/global/', {'q': 'Unreceived'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('axes', data['results'])
        # Den oemottagna yxan ska inte visas
        axe_titles = [axe['title'] for axe in data['results']['axes']]
        self.assertNotIn('Test Manufacturer - Unreceived Axe', axe_titles)

    def test_private_search_shows_all_axes(self):
        """Testa att privat sökning visar alla yxor"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/search/global/', {'q': 'Unreceived'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('axes', data['results'])
        # Den oemottagna yxan ska visas för inloggade användare
        axe_titles = [axe['title'] for axe in data['results']['axes']]
        self.assertIn('Test Manufacturer - Unreceived Axe', axe_titles)

    def test_public_search_hides_contacts_when_disabled(self):
        """Testa att publik sökning döljer kontakter när inställningen är av"""
        self.settings.show_contacts_public = False
        self.settings.save()
        
        response = self.client.get('/api/search/global/', {'q': 'Test Contact'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('contacts', data['results'])
        self.assertEqual(len(data['results']['contacts']), 0)

    def test_public_search_shows_contacts_when_enabled(self):
        """Testa att publik sökning visar kontakter när inställningen är på"""
        self.settings.show_contacts_public = True
        self.settings.save()
        
        response = self.client.get('/api/search/global/', {'q': 'Test Contact'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('contacts', data['results'])
        self.assertGreater(len(data['results']['contacts']), 0)

    def test_public_search_hides_platforms_when_disabled(self):
        """Testa att publik sökning döljer plattformar när inställningen är av"""
        self.settings.show_platforms_public = False
        self.settings.save()
        
        response = self.client.get('/api/search/global/', {'q': 'Test Platform'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('transactions', data['results'])
        # Transaktioner ska inte innehålla plattformsinfo
        for transaction in data['results']['transactions']:
            self.assertNotIn('Test Platform', transaction['subtitle'])

    def test_public_search_shows_platforms_when_enabled(self):
        """Testa att publik sökning visar plattformar när inställningen är på"""
        self.settings.show_platforms_public = True
        self.settings.save()
        
        response = self.client.get('/api/search/global/', {'q': 'Test Platform'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('transactions', data['results'])
        # Transaktioner ska innehålla plattformsinfo
        platform_found = False
        for transaction in data['results']['transactions']:
            if 'Test Platform' in transaction['subtitle']:
                platform_found = True
                break
        self.assertTrue(platform_found)


class AxeListViewTest(ViewsTestCase):
    def test_axe_list_view(self):
        """Testa yxlistan"""
        response = self.client.get('/yxor/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('axes', response.context)
        self.assertIn('manufacturers', response.context)
        self.assertIn('platforms', response.context)

    def test_axe_list_with_filters(self):
        """Testa yxlistan med filter"""
        response = self.client.get('/yxor/', {
            'status': 'KÖPT',
            'manufacturer': self.manufacturer.id,
            'platform': self.platform.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('status_filter', response.context)
        self.assertIn('manufacturer_filter', response.context)
        self.assertIn('platform_filter', response.context)

    def test_axe_list_with_search(self):
        """Testa yxlistan med sökning"""
        response = self.client.get('/yxor/', {'search': 'Test'})
        self.assertEqual(response.status_code, 200)

    def test_axe_list_with_sorting(self):
        """Testa yxlistan med sortering"""
        response = self.client.get('/yxor/', {'sort': 'manufacturer'})
        self.assertEqual(response.status_code, 200)

    def test_axe_list_with_pagination(self):
        """Testa yxlistan med paginering"""
        # Skapa flera yxor för att testa paginering
        for i in range(25):
            Axe.objects.create(
                manufacturer=self.manufacturer,
                model=f"Test Axe {i}",
                status="KÖPT"
            )
        
        response = self.client.get('/yxor/', {'page': '2'})
        self.assertEqual(response.status_code, 200)


class StatisticsDashboardTest(ViewsTestCase):
    def test_statistics_dashboard_public_access(self):
        """Testa att statistikdashboard är tillgänglig för alla"""
        response = self.client.get('/statistik/')
        self.assertEqual(response.status_code, 200)

    def test_statistics_dashboard_with_login(self):
        """Testa statistikdashboard med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/statistik/')
        self.assertEqual(response.status_code, 200)

    def test_statistics_dashboard_contains_data(self):
        """Testa att statistikdashboard innehåller data"""
        response = self.client.get('/statistik/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_axes', response.context)
        self.assertIn('total_manufacturers', response.context)
        self.assertIn('total_contacts', response.context)
        self.assertIn('total_transactions', response.context)


class SettingsViewTest(ViewsTestCase):
    def test_settings_view_requires_login(self):
        """Testa att settings-sidan kräver inloggning"""
        response = self.client.get('/installningar/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_settings_view_with_login(self):
        """Testa settings-sidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/installningar/')
        self.assertEqual(response.status_code, 200)

    def test_settings_view_contains_settings(self):
        """Testa att settings-sidan innehåller inställningar"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/installningar/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('settings', response.context)
        self.assertIn('backup_info', response.context)

    def test_settings_view_post_update(self):
        """Testa att uppdatera inställningar via POST"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/installningar/', {
            'show_contacts_public': 'on',
            'show_prices_public': 'on',
            'show_platforms_public': 'on',
            'show_only_received_axes_public': 'off',
            'default_axes_rows_public': '25',
            'default_transactions_rows_public': '20',
            'default_manufacturers_rows_public': '30',
            'default_axes_rows_private': '60',
            'default_transactions_rows_private': '40',
            'default_manufacturers_rows_private': '60',
            'site_title': 'Test Site',
            'site_description': 'Test Description',
            'external_hosts': 'test.com',
            'external_csrf_origins': 'https://test.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect efter sparande


class BackupViewsTest(ViewsTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='testuser', password='testpass123')
        
        # Skapa temporär backup-mapp
        self.backup_dir = tempfile.mkdtemp()
        self.original_backup_dir = getattr(settings, 'BACKUP_DIR', None)
        
    def tearDown(self):
        super().tearDown()
        # Rensa temporär mapp
        import shutil
        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)

    def test_get_backup_info(self):
        """Testa get_backup_info funktionen"""
        from axes.views import get_backup_info
        backup_info = get_backup_info(self.backup_dir)
        
        self.assertIn('backups', backup_info)
        self.assertIn('backup_dir', backup_info)
        self.assertEqual(backup_info['backup_dir'], self.backup_dir)

    def test_get_backup_stats_zip_file(self):
        """Testa get_backup_stats med ZIP-fil"""
        from axes.views import get_backup_stats
        
        # Skapa en test ZIP-fil med stats
        test_stats = {'axes': 10, 'contacts': 5}
        zip_path = os.path.join(self.backup_dir, 'test_backup.zip')
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr('backup_stats.json', json.dumps(test_stats))
        
        stats = get_backup_stats(zip_path)
        self.assertEqual(stats, test_stats)

    def test_get_backup_stats_sqlite3_file(self):
        """Testa get_backup_stats med SQLite3-fil"""
        from axes.views import get_backup_stats
        
        # Skapa en test SQLite3-fil och motsvarande stats-fil
        sqlite3_path = os.path.join(self.backup_dir, 'test_backup.sqlite3')
        stats_path = os.path.join(self.backup_dir, 'test_backup_stats.json')
        
        # Skapa tom SQLite3-fil
        with open(sqlite3_path, 'w') as f:
            f.write('')
        
        # Skapa stats-fil
        test_stats = {'axes': 10, 'contacts': 5}
        with open(stats_path, 'w') as f:
            json.dump(test_stats, f)
        
        stats = get_backup_stats(sqlite3_path)
        self.assertEqual(stats, test_stats)

    def test_get_backup_stats_invalid_file(self):
        """Testa get_backup_stats med ogiltig fil"""
        from axes.views import get_backup_stats
        
        # Skapa en fil som inte är ZIP eller SQLite3
        invalid_path = os.path.join(self.backup_dir, 'test_backup.txt')
        with open(invalid_path, 'w') as f:
            f.write('test content')
        
        stats = get_backup_stats(invalid_path)
        self.assertIsNone(stats)

    @patch('subprocess.run')
    def test_create_backup_success(self, mock_run):
        """Testa framgångsrik backup-skapning"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        response = self.client.post('/installningar/', {
            'action': 'backup',
            'backup_action': 'create_backup',
            'include_media': 'on',
            'compress': 'on'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_create_backup_failure(self, mock_run):
        """Testa misslyckad backup-skapning"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Backup failed"
        
        response = self.client.post('/installningar/', {
            'action': 'backup',
            'backup_action': 'create_backup'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_delete_backup_success(self):
        """Testa framgångsrik backup-borttagning"""
        # Skapa en test backup-fil
        backup_file = os.path.join(self.backup_dir, 'test_backup.zip')
        with open(backup_file, 'w') as f:
            f.write('test content')
        
        # Mock settings.BASE_DIR för att peka på vår test-mapp
        with patch('django.conf.settings.BASE_DIR', self.backup_dir):
            response = self.client.post('/installningar/', {
                'action': 'backup',
                'backup_action': 'delete_backup',
                'filename': 'test_backup.zip'
            })
            
            self.assertEqual(response.status_code, 302)  # Redirect
            self.assertFalse(os.path.exists(backup_file))

    def test_delete_backup_file_not_found(self):
        """Testa backup-borttagning när filen inte finns"""
        response = self.client.post('/installningar/', {
            'action': 'backup',
            'backup_action': 'delete_backup',
            'filename': 'nonexistent_backup.zip'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect

    @patch('subprocess.run')
    def test_restore_backup_success(self, mock_run):
        """Testa framgångsrik backup-återställning"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Skapa en test backup-fil
        backup_file = os.path.join(self.backup_dir, 'test_backup.zip')
        with open(backup_file, 'w') as f:
            f.write('test content')
        
        # Mock settings.BASE_DIR för att peka på vår test-mapp
        with patch('django.conf.settings.BASE_DIR', self.backup_dir):
            response = self.client.post('/installningar/', {
                'action': 'backup',
                'backup_action': 'restore_backup',
                'filename': 'test_backup.zip'
            })
            
            self.assertEqual(response.status_code, 302)  # Redirect
            mock_run.assert_called_once()

    def test_restore_backup_file_not_found(self):
        """Testa backup-återställning när filen inte finns"""
        response = self.client.post('/installningar/', {
            'action': 'backup',
            'backup_action': 'restore_backup',
            'filename': 'nonexistent_backup.zip'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_handle_backup_action_invalid(self):
        """Testa ogiltig backup-åtgärd"""
        response = self.client.post('/installningar/', {
            'action': 'backup',
            'backup_action': 'invalid_action'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_handle_backup_upload_success(self):
        """Testa framgångsrik backup-uppladdning"""
        # Skapa en test backup-fil
        backup_content = b'backup content'
        backup_file = SimpleUploadedFile(
            'test_backup.zip',
            backup_content,
            content_type='application/zip'
        )
        
        # Mock settings.BASE_DIR för att peka på vår test-mapp
        with patch('django.conf.settings.BASE_DIR', self.backup_dir):
            response = self.client.post('/installningar/', {
                'action': 'upload_backup',
                'backup_file': backup_file
            })
            
            self.assertEqual(response.status_code, 302)  # Redirect
            
            # Kontrollera att filen sparades
            saved_file = os.path.join(self.backup_dir, 'test_backup.zip')
            self.assertTrue(os.path.exists(saved_file))

    def test_handle_backup_upload_invalid_form(self):
        """Testa backup-uppladdning med ogiltigt formulär"""
        response = self.client.post('/installningar/', {
            'action': 'upload_backup'
            # Ingen fil laddad
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect


class FormTests(ViewsTestCase):
    def test_contact_form_validation(self):
        """Testa ContactForm-validering"""
        from axes.views import ContactForm
        
        # Testa giltig data
        form_data = {
            'name': 'Test Contact',
            'email': 'test@example.com',
            'phone': '070-123 45 67',
            'alias': 'testalias',
            'comment': 'Test comment',
            'is_naj_member': True
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Testa ogiltig e-post
        form_data['email'] = 'invalid-email'
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_axe_form_validation(self):
        """Testa AxeForm-validering"""
        from axes.views import AxeForm
        
        # Testa giltig data
        form_data = {
            'manufacturer': self.manufacturer.id,
            'model': 'Test Axe',
            'comment': 'Test comment',
            'status': 'KÖPT',
            'contact_search': '',
            'contact_name': 'New Contact',
            'contact_email': 'new@example.com',
            'transaction_price': '100.00',
            'transaction_date': timezone.now().date(),
            'platform_search': '',
            'platform_name': 'New Platform'
        }
        form = AxeForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Testa utan tillverkare (krävs)
        form_data.pop('manufacturer')
        form = AxeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('manufacturer', form.errors)

    def test_multiple_file_field_clean(self):
        """Testa MultipleFileField clean-metod"""
        from axes.views import MultipleFileField
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        field = MultipleFileField()
        
        # Testa med tom data
        cleaned_data = field.clean([])
        self.assertEqual(cleaned_data, [])
        
        # Testa med en fil
        test_file = SimpleUploadedFile("test.jpg", b"test content", content_type="image/jpeg")
        cleaned_data = field.clean([test_file])
        self.assertEqual(len(cleaned_data), 1)
        self.assertEqual(cleaned_data[0].name, "test.jpg")


class APITests(ViewsTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='testuser', password='testpass123')
        
        # Skapa måtttyper och mallar för API-tester
        self.measurement_type = MeasurementType.objects.create(
            name="Längd",
            unit="cm",
            description="Yxans totala längd",
            sort_order=1
        )
        
        self.measurement_template = MeasurementTemplate.objects.create(
            name="Standard yxa",
            description="Standardmått för yxor",
            sort_order=1
        )
        
        self.template_item = MeasurementTemplateItem.objects.create(
            template=self.measurement_template,
            measurement_type=self.measurement_type,
            sort_order=1
        )

    def test_api_measurement_templates_requires_login(self):
        """Testa att API för måttmallar kräver inloggning"""
        self.client.logout()
        response = self.client.get('/api/measurement-templates/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_api_measurement_types_requires_login(self):
        """Testa att API för måtttyper kräver inloggning"""
        self.client.logout()
        response = self.client.get('/api/measurement-types/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_api_measurement_templates_with_login(self):
        """Testa API för måttmallar med inloggning"""
        response = self.client.get('/api/measurement-templates/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('templates', data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['templates']), 1)
        self.assertEqual(data['templates'][0]['name'], 'Standard yxa')

    def test_api_measurement_types_with_login(self):
        """Testa API för måtttyper med inloggning"""
        response = self.client.get('/api/measurement-types/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('measurement_types', data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['measurement_types']), 1)
        self.assertEqual(data['measurement_types'][0]['name'], 'Längd')

    def test_api_create_measurement_template_requires_post(self):
        """Testa att skapa måttmall kräver POST"""
        response = self.client.get('/api/measurement-templates/create/')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_api_create_measurement_type_requires_post(self):
        """Testa att skapa måtttyp kräver POST"""
        response = self.client.get('/api/measurement-types/create/')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_api_create_measurement_template_success(self):
        """Testa framgångsrik skapning av måttmall"""
        response = self.client.post('/api/measurement-templates/create/', {
            'template_name': 'Ny mall',
            'template_description': 'Beskrivning av ny mall',
            'template_sort_order': '2',
            'measurement_types': json.dumps([self.measurement_type.id])
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('template_id', data)

    def test_api_create_measurement_template_missing_name(self):
        """Testa skapning av måttmall utan namn"""
        response = self.client.post('/api/measurement-templates/create/', {
            'template_description': 'Beskrivning',
            'measurement_types': json.dumps([self.measurement_type.id])
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Mallnamn är obligatoriskt', data['error'])

    def test_api_create_measurement_template_duplicate_name(self):
        """Testa skapning av måttmall med duplicerat namn"""
        response = self.client.post('/api/measurement-templates/create/', {
            'template_name': 'Standard yxa',  # Redan existerar
            'template_description': 'Beskrivning',
            'measurement_types': json.dumps([self.measurement_type.id])
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('finns redan', data['error'])

    def test_api_create_measurement_type_success(self):
        """Testa framgångsrik skapning av måtttyp"""
        response = self.client.post('/api/measurement-types/create/', {
            'measurement_type_name': 'Ny måtttyp',
            'measurement_type_unit': 'mm',
            'measurement_type_description': 'Beskrivning',
            'measurement_type_sort_order': '2'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('measurement_type', data)

    def test_api_create_measurement_type_missing_fields(self):
        """Testa skapning av måtttyp med saknade fält"""
        response = self.client.post('/api/measurement-types/create/', {
            'measurement_type_name': 'Ny måtttyp'
            # Saknar unit
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Namn och enhet är obligatoriska', data['error'])

    def test_api_update_measurement_type_success(self):
        """Testa framgångsrik uppdatering av måtttyp"""
        response = self.client.post(f'/api/measurement-types/{self.measurement_type.id}/update/', {
            'measurement_type_name': 'Uppdaterad längd',
            'measurement_type_unit': 'mm',
            'measurement_type_description': 'Uppdaterad beskrivning',
            'measurement_type_sort_order': '5'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['measurement_type']['name'], 'Uppdaterad längd')

    def test_api_update_measurement_type_wrong_method(self):
        """Testa uppdatering av måtttyp med fel HTTP-metod"""
        response = self.client.get(f'/api/measurement-types/{self.measurement_type.id}/update/')
        self.assertEqual(response.status_code, 200)  # Returnerar JSON-fel
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_api_delete_measurement_type_success(self):
        """Testa framgångsrik borttagning av måtttyp"""
        # Skapa en måtttyp som inte används i mallar
        unused_type = MeasurementType.objects.create(
            name="Oanvänd typ",
            unit="st",
            sort_order=10
        )
        
        response = self.client.post(f'/api/measurement-types/{unused_type.id}/delete/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att måtttypen är borttagen
        self.assertFalse(MeasurementType.objects.filter(id=unused_type.id).exists())

    def test_api_delete_measurement_type_in_use(self):
        """Testa borttagning av måtttyp som används i mallar"""
        response = self.client.post(f'/api/measurement-types/{self.measurement_type.id}/delete/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('kan inte tas bort', data['error'])

    def test_api_update_measurement_template_success(self):
        """Testa framgångsrik uppdatering av måttmall"""
        response = self.client.post(f'/api/measurement-templates/{self.measurement_template.id}/update/', {
            'template_name': 'Uppdaterad mall',
            'template_description': 'Uppdaterad beskrivning',
            'template_sort_order': '5',
            'measurement_types': json.dumps([self.measurement_type.id])
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['template_id'], self.measurement_template.id)

    def test_api_delete_measurement_template_success(self):
        """Testa framgångsrik borttagning av måttmall"""
        response = self.client.post(f'/api/measurement-templates/{self.measurement_template.id}/delete/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att mallen är borttagen
        self.assertFalse(MeasurementTemplate.objects.filter(id=self.measurement_template.id).exists())
