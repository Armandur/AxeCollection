import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from axes.models import Axe, Contact, Manufacturer, Platform, Transaction, Settings, AxeImage
from decimal import Decimal
from django.utils import timezone
import json
from django.core.files.uploadedfile import SimpleUploadedFile
import os


class ViewsAxeTestCase(TestCase):
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


class AxeDetailViewTest(ViewsAxeTestCase):
    def test_axe_detail_view_public(self):
        """Testa att yxdetail-sidan är tillgänglig för alla"""
        response = self.client.get(f'/yxor/{self.axe.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_detail.html')
        self.assertEqual(response.context['axe'], self.axe)

    def test_axe_detail_view_with_login(self):
        """Testa yxdetail-sidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/yxor/{self.axe.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_detail.html')
        self.assertEqual(response.context['axe'], self.axe)

    def test_axe_detail_view_invalid_id(self):
        """Testa yxdetail-sidan med ogiltigt ID"""
        response = self.client.get('/yxor/99999/')
        self.assertEqual(response.status_code, 404)

    def test_axe_detail_view_contains_axe_info(self):
        """Testa att yxdetail-sidan innehåller yxinformation"""
        response = self.client.get(f'/yxor/{self.axe.id}/')
        self.assertContains(response, 'Test Axe')
        self.assertContains(response, 'Test Manufacturer')


class AxeCreateViewTest(ViewsAxeTestCase):
    def test_axe_create_view_requires_login(self):
        """Testa att yxcreate-sidan kräver inloggning"""
        response = self.client.get('/yxor/ny/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_axe_create_view_with_login(self):
        """Testa yxcreate-sidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/yxor/ny/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_form.html')

    def test_axe_create_view_post_valid_data(self):
        """Testa att skapa en ny yxa med giltig data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'manufacturer': self.manufacturer.id,
            'model': 'New Test Axe',
            'status': 'KÖPT',
            'comment': 'Test comment'
        }
        
        response = self.client.post('/yxor/ny/', data)
        self.assertEqual(response.status_code, 302)  # Redirect efter skapande
        
        # Kontrollera att yxan skapades
        new_axe = Axe.objects.filter(model='New Test Axe').first()
        self.assertIsNotNone(new_axe)
        self.assertEqual(new_axe.manufacturer, self.manufacturer)
        self.assertEqual(new_axe.status, 'KÖPT')

    def test_axe_create_view_post_invalid_data(self):
        """Testa att skapa en ny yxa med ogiltig data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'model': 'New Test Axe',
            'status': 'KÖPT',
            # Saknar manufacturer (obligatoriskt)
        }
        
        response = self.client.post('/yxor/ny/', data)
        self.assertEqual(response.status_code, 200)  # Stannar på formuläret
        self.assertTemplateUsed(response, 'axes/axe_form.html')
        
        # Kontrollera att yxan inte skapades
        new_axe = Axe.objects.filter(model='New Test Axe').first()
        self.assertIsNone(new_axe)


class AxeEditViewTest(ViewsAxeTestCase):
    def test_axe_edit_view_requires_login(self):
        """Testa att yxedit-sidan kräver inloggning"""
        response = self.client.get(f'/yxor/{self.axe.id}/redigera/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_axe_edit_view_with_login(self):
        """Testa yxedit-sidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/yxor/{self.axe.id}/redigera/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_form.html')
        self.assertEqual(response.context['axe'], self.axe)

    def test_axe_edit_view_post_valid_data(self):
        """Testa att redigera en yxa med giltig data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'manufacturer': self.manufacturer.id,
            'model': 'Updated Test Axe',
            'status': 'MOTTAGEN',
            'comment': 'Updated comment'
        }
        
        response = self.client.post(f'/yxor/{self.axe.id}/redigera/', data)
        self.assertEqual(response.status_code, 302)  # Redirect efter uppdatering
        
        # Kontrollera att yxan uppdaterades
        self.axe.refresh_from_db()
        self.assertEqual(self.axe.model, 'Updated Test Axe')
        self.assertEqual(self.axe.status, 'MOTTAGEN')

    def test_axe_edit_view_invalid_id(self):
        """Testa yxedit-sidan med ogiltigt ID"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/yxor/99999/redigera/')
        self.assertEqual(response.status_code, 404)


class AxeGalleryViewTest(ViewsAxeTestCase):
    def test_axe_gallery_view_public(self):
        """Testa att yxgalleri-sidan är tillgänglig för alla"""
        response = self.client.get('/galleri/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_gallery.html')

    def test_axe_gallery_view_with_login(self):
        """Testa yxgalleri-sidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/galleri/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_gallery.html')

    def test_axe_gallery_view_contains_axe_info(self):
        """Testa att yxgalleri-sidan innehåller yxinformation"""
        response = self.client.get('/galleri/')
        self.assertIn('current_axe', response.context)
        self.assertIn('total_axes', response.context)
        self.assertGreater(response.context['total_axes'], 0)


class AxeListViewTest(ViewsAxeTestCase):
    def test_axe_list_view_public(self):
        """Testa att yxlista-sidan är tillgänglig för alla"""
        response = self.client.get('/yxor/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_list.html')

    def test_axe_list_view_with_login(self):
        """Testa yxlista-sidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/yxor/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_list.html')

    def test_axe_list_view_contains_axes(self):
        """Testa att yxlista-sidan innehåller yxor"""
        response = self.client.get('/yxor/')
        self.assertIn('axes', response.context)
        self.assertGreater(len(response.context['axes']), 0)

    def test_axe_list_view_with_filters(self):
        """Testa yxlista-sidan med filter"""
        response = self.client.get('/yxor/', {
            'manufacturer': self.manufacturer.id,
            'status': 'KÖPT'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_list.html')

    def test_axe_list_view_with_search(self):
        """Testa yxlista-sidan med sökning"""
        response = self.client.get('/yxor/', {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/axe_list.html')


class StatisticsDashboardViewTest(ViewsAxeTestCase):
    def test_statistics_dashboard_view_public(self):
        """Testa att statistikdashboard är tillgänglig för alla"""
        response = self.client.get('/statistik/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/statistics_dashboard.html')

    def test_statistics_dashboard_view_with_login(self):
        """Testa statistikdashboard med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/statistik/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/statistics_dashboard.html')

    def test_statistics_dashboard_contains_stats(self):
        """Testa att statistikdashboard innehåller statistik"""
        response = self.client.get('/statistik/')
        self.assertIn('total_axes', response.context)
        self.assertIn('total_manufacturers', response.context)
        self.assertIn('total_contacts', response.context)
        self.assertIn('total_transactions', response.context)


class UnlinkedImagesViewTest(ViewsAxeTestCase):
    def test_unlinked_images_view_requires_login(self):
        """Testa att okopplade bilder-sidan kräver inloggning"""
        response = self.client.get('/okopplade-bilder/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_unlinked_images_view_with_login(self):
        """Testa okopplade bilder-sidan med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/okopplade-bilder/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/unlinked_images.html')

    def test_unlinked_images_view_contains_context(self):
        """Testa att okopplade bilder-sidan innehåller rätt context"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/okopplade-bilder/')
        self.assertIn('axe_groups', response.context)
        self.assertIn('manufacturer_groups', response.context)
        self.assertIn('total_count', response.context)
        self.assertIn('total_size', response.context)


class ReceivingWorkflowViewTest(ViewsAxeTestCase):
    def test_receiving_workflow_view_requires_login(self):
        """Testa att mottagningsarbetsflöde kräver inloggning"""
        response = self.client.get(f'/yxor/{self.axe.id}/mottagning/')
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_receiving_workflow_view_with_login(self):
        """Testa mottagningsarbetsflöde med inloggning"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/yxor/{self.axe.id}/mottagning/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/receiving_workflow.html')
        self.assertEqual(response.context['axe'], self.axe)

    def test_receiving_workflow_view_invalid_id(self):
        """Testa mottagningsarbetsflöde med ogiltigt ID"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/yxor/99999/mottagning/')
        self.assertEqual(response.status_code, 404) 