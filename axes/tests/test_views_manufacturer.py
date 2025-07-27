import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from axes.models import (
    Manufacturer, ManufacturerImage, ManufacturerLink, 
    Axe, Transaction, Contact, Platform, Settings
)


class ViewsManufacturerTestCase(TestCase):
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
            show_only_received_axes_public=False,
            default_manufacturers_rows_private=25,
            default_manufacturers_rows_public=10
        )
        
        # Skapa testdata
        self.parent_manufacturer = Manufacturer.objects.create(
            name="Parent Manufacturer",
            manufacturer_type="TILLVERKARE"
        )
        
        self.manufacturer = Manufacturer.objects.create(
            name="Test Manufacturer",
            information="Test information",
            parent=self.parent_manufacturer,
            manufacturer_type="TILLVERKARE"
        )
        
        self.sub_manufacturer = Manufacturer.objects.create(
            name="Sub Manufacturer",
            parent=self.manufacturer,
            manufacturer_type="SMED"
        )
        
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
        
        # Skapa tillverkarbild
        self.manufacturer_image = ManufacturerImage.objects.create(
            manufacturer=self.manufacturer,
            image_type="STAMP",
            caption="Test Caption",
            description="Test Description",
            order=1
        )
        
        # Skapa tillverkarlänk
        self.manufacturer_link = ManufacturerLink.objects.create(
            manufacturer=self.manufacturer,
            title="Test Link",
            url="https://example.com",
            link_type="WEBSITE",
            description="Test Description",
            is_active=True,
            order=1
        )


class ManufacturerListViewTest(ViewsManufacturerTestCase):
    def test_manufacturer_list_view_public_access(self):
        """Testa att tillverkarlistan är tillgänglig för alla"""
        response = self.client.get('/tillverkare/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/manufacturer_list.html')
    
    def test_manufacturer_list_view_contains_manufacturers(self):
        """Testa att tillverkarlistan innehåller tillverkare"""
        response = self.client.get('/tillverkare/')
        self.assertIn('manufacturers', response.context)
        self.assertIn('total_manufacturers', response.context)
        self.assertIn('total_axes', response.context)
        self.assertIn('total_transactions', response.context)
        self.assertIn('average_axes_per_manufacturer', response.context)
        self.assertIn('default_page_length', response.context)
    
    def test_manufacturer_list_view_statistics(self):
        """Testa att statistik beräknas korrekt"""
        response = self.client.get('/tillverkare/')
        context = response.context
        
        self.assertEqual(context['total_manufacturers'], 3)  # parent, manufacturer, sub
        self.assertEqual(context['total_axes'], 1)
        self.assertEqual(context['total_transactions'], 1)
        self.assertGreater(context['average_axes_per_manufacturer'], 0)


class ManufacturerDetailViewTest(ViewsManufacturerTestCase):
    def test_manufacturer_detail_view_public_access(self):
        """Testa att tillverkardetaljsidan är tillgänglig för alla"""
        response = self.client.get(f'/tillverkare/{self.manufacturer.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/manufacturer_detail.html')
    
    def test_manufacturer_detail_view_invalid_id(self):
        """Testa att ogiltigt ID ger 404"""
        response = self.client.get('/tillverkare/99999/')
        self.assertEqual(response.status_code, 404)
    
    def test_manufacturer_detail_view_contains_manufacturer_data(self):
        """Testa att tillverkardetaljsidan innehåller rätt data"""
        response = self.client.get(f'/tillverkare/{self.manufacturer.id}/')
        context = response.context
        
        self.assertEqual(context['manufacturer'], self.manufacturer)
        self.assertIn('axes', context)
        self.assertIn('images', context)
        self.assertIn('links', context)
        self.assertIn('transactions', context)
        self.assertIn('total_axes', context)
        self.assertIn('total_transactions', context)
        self.assertIn('breadcrumbs', context)
    
    def test_manufacturer_detail_view_sub_manufacturers(self):
        """Testa att undertillverkare visas korrekt"""
        response = self.client.get(f'/tillverkare/{self.manufacturer.id}/')
        context = response.context
        
        self.assertIn('sub_tillverkare', context)
        self.assertIn('sub_smeder', context)
        # Sub manufacturer är av typ SMED, så den ska vara i sub_smeder
        self.assertIn(self.sub_manufacturer, context['sub_smeder'])


class ManufacturerCreateViewTest(ViewsManufacturerTestCase):
    def test_manufacturer_create_view_requires_login(self):
        """Testa att skapa tillverkare kräver inloggning"""
        response = self.client.get('/tillverkare/ny/')
        self.assertEqual(response.status_code, 302)
    
    def test_manufacturer_create_view_login_access(self):
        """Testa att inloggad användare kan komma åt formuläret"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tillverkare/ny/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/manufacturer_form.html')
    
    def test_manufacturer_create_view_valid_post(self):
        """Testa att skapa tillverkare med giltig data"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': 'New Manufacturer',
            'information': 'New information',
            'manufacturer_type': 'TILLVERKARE'
        }
        response = self.client.post('/tillverkare/ny/', data)
        self.assertEqual(response.status_code, 302)  # Redirect efter skapande
        
        # Kontrollera att tillverkaren skapades
        new_manufacturer = Manufacturer.objects.filter(name='New Manufacturer').first()
        self.assertIsNotNone(new_manufacturer)
        self.assertEqual(new_manufacturer.information, 'New information')
    
    def test_manufacturer_create_view_invalid_post(self):
        """Testa att skapa tillverkare med ogiltig data"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': '',  # Tomt namn
            'information': 'Test information',
            'manufacturer_type': 'TILLVERKARE'
        }
        response = self.client.post('/tillverkare/ny/', data)
        self.assertEqual(response.status_code, 200)  # Formuläret visas igen
        self.assertTemplateUsed(response, 'axes/manufacturer_form.html')
    
    def test_manufacturer_create_view_duplicate_name(self):
        """Testa att skapa tillverkare med redan befintligt namn"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': 'Test Manufacturer',  # Redan befintligt namn
            'information': 'Test information',
            'manufacturer_type': 'TILLVERKARE'
        }
        response = self.client.post('/tillverkare/ny/', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/manufacturer_form.html')


class ManufacturerEditViewTest(ViewsManufacturerTestCase):
    def test_manufacturer_edit_view_requires_login(self):
        """Testa att redigera tillverkare kräver inloggning"""
        response = self.client.get(f'/tillverkare/{self.manufacturer.id}/redigera/')
        self.assertEqual(response.status_code, 302)
    
    def test_manufacturer_edit_view_login_access(self):
        """Testa att inloggad användare kan komma åt formuläret"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tillverkare/{self.manufacturer.id}/redigera/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/manufacturer_form.html')
    
    def test_manufacturer_edit_view_valid_post(self):
        """Testa att redigera tillverkare med giltig data"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': 'Updated Manufacturer',
            'information': 'Updated information',
            'manufacturer_type': 'TILLVERKARE'
        }
        response = self.client.post(f'/tillverkare/{self.manufacturer.id}/redigera/', data)
        self.assertEqual(response.status_code, 302)  # Redirect efter uppdatering
        
        # Kontrollera att tillverkaren uppdaterades
        self.manufacturer.refresh_from_db()
        self.assertEqual(self.manufacturer.name, 'Updated Manufacturer')
        self.assertEqual(self.manufacturer.information, 'Updated information')
    
    def test_manufacturer_edit_view_invalid_id(self):
        """Testa att redigera tillverkare med ogiltigt ID"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tillverkare/99999/redigera/')
        self.assertEqual(response.status_code, 404)


class ManufacturerDeleteViewTest(ViewsManufacturerTestCase):
    def test_manufacturer_delete_view_requires_login(self):
        """Testa att ta bort tillverkare kräver inloggning"""
        response = self.client.post(f'/tillverkare/{self.manufacturer.id}/ta-bort/')
        self.assertEqual(response.status_code, 302)
    
    def test_manufacturer_delete_view_login_access(self):
        """Testa att inloggad användare kan ta bort tillverkare"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'axe_action': 'move',
            'delete_images': 'false'
        }
        response = self.client.post(f'/tillverkare/{self.manufacturer.id}/ta-bort/', data)
        self.assertEqual(response.status_code, 200)
        
        # Kontrollera JSON-svar
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_manufacturer_delete_view_with_axes(self):
        """Testa att ta bort tillverkare med yxor"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'axe_action': 'move',
            'delete_images': 'false'
        }
        response = self.client.post(f'/tillverkare/{self.manufacturer.id}/ta-bort/', data)
        self.assertEqual(response.status_code, 200)
        
        # Kontrollera att yxan flyttades till "Okänd tillverkare"
        unknown_manufacturer = Manufacturer.objects.filter(name="Okänd tillverkare").first()
        self.assertIsNotNone(unknown_manufacturer)
        self.axe.refresh_from_db()
        self.assertEqual(self.axe.manufacturer, unknown_manufacturer)


class ManufacturerAJAXViewsTest(ViewsManufacturerTestCase):
    def test_edit_manufacturer_information(self):
        """Testa AJAX-redigering av tillverkarinformation"""
        data = {
            'information': 'Updated information via AJAX'
        }
        response = self.client.post(
            f'/tillverkare/{self.manufacturer.id}/redigera-information/',
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att informationen uppdaterades
        self.manufacturer.refresh_from_db()
        self.assertEqual(self.manufacturer.information, 'Updated information via AJAX')
    
    def test_edit_manufacturer_name(self):
        """Testa AJAX-redigering av tillverkarnamn"""
        data = {
            'name': 'Updated Name via AJAX'
        }
        response = self.client.post(
            f'/tillverkare/{self.manufacturer.id}/redigera-namn/',
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att namnet uppdaterades
        self.manufacturer.refresh_from_db()
        self.assertEqual(self.manufacturer.name, 'Updated Name via AJAX')
    
    def test_edit_manufacturer_image(self):
        """Testa AJAX-redigering av tillverkarbild"""
        data = {
            'caption': 'Updated Caption',
            'description': 'Updated Description',
            'image_type': 'LOGO'
        }
        response = self.client.post(
            f'/tillverkare/bild/{self.manufacturer_image.id}/redigera/',
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att bilden uppdaterades
        self.manufacturer_image.refresh_from_db()
        self.assertEqual(self.manufacturer_image.caption, 'Updated Caption')
        self.assertEqual(self.manufacturer_image.image_type, 'LOGO')
    
    def test_delete_manufacturer_image(self):
        """Testa AJAX-borttagning av tillverkarbild"""
        image_id = self.manufacturer_image.id
        response = self.client.post(f'/tillverkare/bild/{image_id}/ta-bort/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att bilden togs bort
        self.assertFalse(ManufacturerImage.objects.filter(id=image_id).exists())
    
    def test_edit_manufacturer_link(self):
        """Testa AJAX-redigering av tillverkarlänk"""
        data = {
            'title': 'Updated Link Title',
            'url': 'https://updated-example.com',
            'link_type': 'SOCIAL',
            'description': 'Updated Description',
            'is_active': False
        }
        response = self.client.post(
            f'/tillverkare/lank/{self.manufacturer_link.id}/redigera/',
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att länken uppdaterades
        self.manufacturer_link.refresh_from_db()
        self.assertEqual(self.manufacturer_link.title, 'Updated Link Title')
        self.assertEqual(self.manufacturer_link.url, 'https://updated-example.com')
        self.assertEqual(self.manufacturer_link.link_type, 'SOCIAL')
        self.assertFalse(self.manufacturer_link.is_active)
    
    def test_delete_manufacturer_link(self):
        """Testa AJAX-borttagning av tillverkarlänk"""
        link_id = self.manufacturer_link.id
        response = self.client.post(f'/tillverkare/lank/{link_id}/ta-bort/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att länken togs bort
        self.assertFalse(ManufacturerLink.objects.filter(id=link_id).exists())
    
    def test_get_manufacturers_for_dropdown(self):
        """Testa AJAX-hämtning av tillverkare för dropdown"""
        response = self.client.get('/tillverkare/dropdown/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('manufacturers', data)
        self.assertGreater(len(data['manufacturers']), 0)
    
    def test_check_manufacturer_name(self):
        """Testa AJAX-kontroll av tillverkarnamn"""
        # Testa befintligt namn
        response = self.client.get('/tillverkare/check-name/', {'name': 'Test Manufacturer'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['exists'])
        self.assertIsNotNone(data['manufacturer'])
        
        # Testa nytt namn
        response = self.client.get('/tillverkare/check-name/', {'name': 'New Manufacturer'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertFalse(data['exists'])
        self.assertIsNone(data['manufacturer'])


class ManufacturerUtilityFunctionsTest(ViewsManufacturerTestCase):
    def test_get_available_parents_no_current(self):
        """Testa get_available_parents utan aktuell tillverkare"""
        from axes.views_manufacturer import get_available_parents
        
        available_parents = get_available_parents()
        self.assertIn(self.parent_manufacturer, available_parents)
        self.assertIn(self.manufacturer, available_parents)
        self.assertIn(self.sub_manufacturer, available_parents)
    
    def test_get_available_parents_with_current(self):
        """Testa get_available_parents med aktuell tillverkare"""
        from axes.views_manufacturer import get_available_parents
        
        # Tillverkaren ska inte kunna välja sig själv eller sina undertillverkare
        available_parents = get_available_parents(self.manufacturer)
        self.assertNotIn(self.manufacturer, available_parents)
        self.assertNotIn(self.sub_manufacturer, available_parents)
        self.assertIn(self.parent_manufacturer, available_parents)
    
    def test_get_available_parents_hierarchical_sorting(self):
        """Testa att get_available_parents sorterar hierarkiskt"""
        from axes.views_manufacturer import get_available_parents
        
        available_parents = get_available_parents()
        
        # Huvudtillverkare (hierarchy_level=0) ska komma först
        main_manufacturers = [m for m in available_parents if m.hierarchy_level == 0]
        sub_manufacturers = [m for m in available_parents if m.hierarchy_level > 0]
        
        # Kontrollera att huvudtillverkare kommer först i listan
        for main in main_manufacturers:
            main_index = list(available_parents).index(main)
            for sub in sub_manufacturers:
                if sub.parent == main:
                    sub_index = list(available_parents).index(sub)
                    self.assertGreater(sub_index, main_index) 