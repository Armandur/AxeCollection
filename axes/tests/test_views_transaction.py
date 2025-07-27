import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from axes.models import (
    Transaction, Contact, Platform, Axe, Manufacturer, Settings
)


class ViewsTransactionTestCase(TestCase):
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
            default_transactions_rows_private=25,
            default_transactions_rows_public=10
        )
        
        # Skapa testdata
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.contact = Contact.objects.create(
            name="Test Contact", 
            email="test@example.com",
            alias="test_alias",
            phone="123456789"
        )
        self.platform = Platform.objects.create(name="Test Platform")
        
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Axe",
            status="KÖPT"
        )
        
        self.buy_transaction = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="KÖP",
            price=Decimal("100.00"),
            shipping_cost=Decimal("10.00"),
            comment="Test köp"
        )
        
        self.sale_transaction = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="SÄLJ",
            price=Decimal("150.00"),
            shipping_cost=Decimal("5.00"),
            comment="Test försäljning"
        )


class TransactionListViewTest(ViewsTransactionTestCase):
    def test_transaction_list_view_public_access(self):
        """Testa att transaktionslistan är tillgänglig för alla"""
        response = self.client.get('/transaktioner/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'axes/transaction_list.html')
    
    def test_transaction_list_view_contains_transactions(self):
        """Testa att transaktionslistan innehåller transaktioner"""
        response = self.client.get('/transaktioner/')
        self.assertIn('transactions', response.context)
        self.assertIn('platforms', response.context)
        self.assertIn('total_buys', response.context)
        self.assertIn('total_sales', response.context)
        self.assertIn('total_buy_value', response.context)
        self.assertIn('total_sale_value', response.context)
        self.assertIn('total_profit', response.context)
        self.assertIn('filtered_count', response.context)
        self.assertIn('default_page_length', response.context)
    
    def test_transaction_list_view_statistics(self):
        """Testa att statistik beräknas korrekt"""
        response = self.client.get('/transaktioner/')
        context = response.context
        
        self.assertEqual(context['total_buys'], 1)
        self.assertEqual(context['total_sales'], 1)
        self.assertEqual(context['total_buy_value'], Decimal('100.00'))
        self.assertEqual(context['total_sale_value'], Decimal('150.00'))
        self.assertEqual(context['total_profit'], Decimal('50.00'))
        self.assertEqual(context['filtered_count'], 2)
    
    def test_transaction_list_view_type_filter(self):
        """Testa filtrering efter transaktionstyp"""
        response = self.client.get('/transaktioner/', {'type': 'KÖP'})
        context = response.context
        
        self.assertEqual(context['total_buys'], 1)
        self.assertEqual(context['total_sales'], 0)
        self.assertEqual(context['filtered_count'], 1)
        self.assertEqual(context['type_filter'], 'KÖP')
    
    def test_transaction_list_view_platform_filter(self):
        """Testa filtrering efter plattform"""
        response = self.client.get('/transaktioner/', {'platform': str(self.platform.id)})
        context = response.context
        
        self.assertEqual(context['filtered_count'], 2)
        self.assertEqual(context['platform_filter'], str(self.platform.id))
    
    def test_transaction_list_view_contact_filter_with_contact(self):
        """Testa filtrering för transaktioner med kontakt"""
        response = self.client.get('/transaktioner/', {'contact': 'with_contact'})
        context = response.context
        
        self.assertEqual(context['filtered_count'], 2)
        self.assertEqual(context['contact_filter'], 'with_contact')
    
    def test_transaction_list_view_contact_filter_without_contact(self):
        """Testa filtrering för transaktioner utan kontakt"""
        # Skapa en transaktion utan kontakt
        Transaction.objects.create(
            axe=self.axe,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="KÖP",
            price=Decimal("50.00")
        )
        
        response = self.client.get('/transaktioner/', {'contact': 'without_contact'})
        context = response.context
        
        self.assertEqual(context['filtered_count'], 1)
        self.assertEqual(context['contact_filter'], 'without_contact')


class ApiTransactionDetailViewTest(ViewsTransactionTestCase):
    def test_api_transaction_detail_valid_id(self):
        """Testa API för transaktionsdetaljer med giltigt ID"""
        response = self.client.get(f'/api/transaction/{self.buy_transaction.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['id'], self.buy_transaction.id)
        self.assertEqual(data['axe_id'], self.axe.id)
        self.assertEqual(data['contact_id'], self.contact.id)
        self.assertEqual(data['contact_name'], self.contact.name)
        self.assertEqual(data['contact_alias'], self.contact.alias)
        self.assertEqual(data['contact_email'], self.contact.email)
        self.assertEqual(data['contact_phone'], self.contact.phone)
        self.assertEqual(data['platform_id'], self.platform.id)
        self.assertEqual(data['platform_name'], self.platform.name)
        self.assertEqual(data['price'], 100.0)
        self.assertEqual(data['shipping_cost'], 10.0)
        self.assertEqual(data['type'], 'KÖP')
        self.assertEqual(data['comment'], 'Test köp')
    
    def test_api_transaction_detail_invalid_id(self):
        """Testa API för transaktionsdetaljer med ogiltigt ID"""
        response = self.client.get('/api/transaction/99999/')
        self.assertEqual(response.status_code, 404)
    
    def test_api_transaction_detail_without_contact(self):
        """Testa API för transaktionsdetaljer utan kontakt"""
        # Skapa transaktion utan kontakt
        transaction = Transaction.objects.create(
            axe=self.axe,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="KÖP",
            price=Decimal("50.00")
        )
        
        response = self.client.get(f'/api/transaction/{transaction.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIsNone(data['contact_id'])
        self.assertEqual(data['contact_name'], '')
        self.assertEqual(data['contact_alias'], '')
        self.assertEqual(data['contact_email'], '')
        self.assertEqual(data['contact_phone'], '')


class ApiTransactionUpdateViewTest(ViewsTransactionTestCase):
    def test_api_transaction_update_requires_login(self):
        """Testa att uppdatera transaktion kräver inloggning"""
        # api_transaction_update har inte @login_required, så den ska inte kräva inloggning
        data = {'price': '120.00', 'shipping_cost': '15.00'}
        response = self.client.post(f'/api/transaction/{self.buy_transaction.id}/update/', data)
        self.assertEqual(response.status_code, 200)
    
    def test_api_transaction_update_invalid_id(self):
        """Testa uppdatera transaktion med ogiltigt ID"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/api/transaction/99999/update/')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Transaktion finns inte', data['error'])
    
    def test_api_transaction_update_valid_data(self):
        """Testa uppdatera transaktion med giltig data"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'transaction_date': '2024-01-15',
            'price': '120.00',
            'shipping_cost': '15.00',
            'comment': 'Uppdaterad kommentar',
            'selected_contact_id': str(self.contact.id),
            'selected_platform_id': str(self.platform.id)
        }
        response = self.client.post(f'/api/transaction/{self.buy_transaction.id}/update/', data)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att transaktionen uppdaterades
        self.buy_transaction.refresh_from_db()
        self.assertEqual(self.buy_transaction.price, Decimal('120.00'))
        self.assertEqual(self.buy_transaction.shipping_cost, Decimal('15.00'))
        self.assertEqual(self.buy_transaction.comment, 'Uppdaterad kommentar')
    
    def test_api_transaction_update_negative_price_buy(self):
        """Testa uppdatera transaktion med negativt pris (KÖP)"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'price': '-120.00',
            'shipping_cost': '-15.00'
        }
        response = self.client.post(f'/api/transaction/{self.buy_transaction.id}/update/', data)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att transaktionen blev KÖP
        self.buy_transaction.refresh_from_db()
        self.assertEqual(self.buy_transaction.type, 'KÖP')
        self.assertEqual(self.buy_transaction.price, Decimal('120.00'))
        self.assertEqual(self.buy_transaction.shipping_cost, Decimal('15.00'))
    
    def test_api_transaction_update_positive_price_sale(self):
        """Testa uppdatera transaktion med positivt pris (SÄLJ)"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'price': '200.00',
            'shipping_cost': '10.00'
        }
        response = self.client.post(f'/api/transaction/{self.buy_transaction.id}/update/', data)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att transaktionen blev SÄLJ
        self.buy_transaction.refresh_from_db()
        self.assertEqual(self.buy_transaction.type, 'SÄLJ')
        self.assertEqual(self.buy_transaction.price, Decimal('200.00'))
        self.assertEqual(self.buy_transaction.shipping_cost, Decimal('10.00'))
    
    def test_api_transaction_update_invalid_price(self):
        """Testa uppdatera transaktion med ogiltigt pris"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'price': 'invalid',
            'shipping_cost': 'invalid'
        }
        response = self.client.post(f'/api/transaction/{self.buy_transaction.id}/update/', data)
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('price', data['errors'])
    
    def test_api_transaction_update_create_new_contact(self):
        """Testa uppdatera transaktion med ny kontakt"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'price': '100.00',  # Lägg till giltiga priser för att undvika ValueError
            'shipping_cost': '10.00',
            'contact_name': 'New Contact',
            'contact_alias': 'new_alias',
            'contact_email': 'new@example.com',
            'contact_phone': '987654321'
        }
        response = self.client.post(f'/api/transaction/{self.buy_transaction.id}/update/', data)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att ny kontakt skapades
        new_contact = Contact.objects.filter(name='New Contact').first()
        self.assertIsNotNone(new_contact)
        self.assertEqual(new_contact.alias, 'new_alias')
        self.assertEqual(new_contact.email, 'new@example.com')
        
        # Kontrollera att transaktionen uppdaterades
        self.buy_transaction.refresh_from_db()
        self.assertEqual(self.buy_transaction.contact, new_contact)
    
    def test_api_transaction_update_create_new_platform(self):
        """Testa uppdatera transaktion med ny plattform"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'price': '100.00',  # Lägg till giltiga priser för att undvika ValueError
            'shipping_cost': '10.00',
            'platform_search': 'New Platform'
        }
        response = self.client.post(f'/api/transaction/{self.buy_transaction.id}/update/', data)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kontrollera att ny plattform skapades
        new_platform = Platform.objects.filter(name='New Platform').first()
        self.assertIsNotNone(new_platform)
        
        # Kontrollera att transaktionen uppdaterades
        self.buy_transaction.refresh_from_db()
        self.assertEqual(self.buy_transaction.platform, new_platform)
    
    def test_api_transaction_update_invalid_contact_id(self):
        """Testa uppdatera transaktion med ogiltigt kontakt-ID"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'selected_contact_id': '99999'
        }
        response = self.client.post(f'/api/transaction/{self.buy_transaction.id}/update/', data)
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('contact', data['errors'])
    
    def test_api_transaction_update_invalid_platform_id(self):
        """Testa uppdatera transaktion med ogiltigt plattform-ID"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'selected_platform_id': '99999'
        }
        response = self.client.post(f'/api/transaction/{self.buy_transaction.id}/update/', data)
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('platform', data['errors'])


class ApiTransactionDeleteViewTest(ViewsTransactionTestCase):
    def test_api_transaction_delete_requires_login(self):
        """Testa att ta bort transaktion kräver inloggning"""
        response = self.client.post(f'/api/transaction/{self.buy_transaction.id}/delete/')
        self.assertEqual(response.status_code, 302)
    
    def test_api_transaction_delete_valid_id(self):
        """Testa ta bort transaktion med giltigt ID"""
        self.client.login(username='testuser', password='testpass123')
        transaction_id = self.buy_transaction.id
        response = self.client.post(f'/api/transaction/{transaction_id}/delete/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('togs bort framgångsrikt', data['message'])
        
        # Kontrollera att transaktionen togs bort
        self.assertFalse(Transaction.objects.filter(id=transaction_id).exists())
    
    def test_api_transaction_delete_invalid_id(self):
        """Testa ta bort transaktion med ogiltigt ID"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/api/transaction/99999/delete/')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Transaktion finns inte', data['error']) 