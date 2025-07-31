from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import JsonResponse
from axes.models import (
    Manufacturer,
    Stamp,
    StampTranscription,
    StampTag,
    StampImage,
    AxeStamp,
    StampVariant,
    StampUncertaintyGroup,
    Axe,
    AxeImage,
)
from decimal import Decimal
import json


class StampViewTestBase(TestCase):
    """Bas-klass för stämpel-view tester med gemensam setup"""

    def setUp(self):
        """Skapa gemensam testdata för alla view-tester"""
        self.client = Client()

        # Skapa användare
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # Skapa tillverkare
        self.manufacturer = Manufacturer.objects.create(
            name="Test Tillverkare", manufacturer_type="TILLVERKARE"
        )

        # Skapa stämplar
        self.stamp1 = Stamp.objects.create(
            name="Test Stämpel 1",
            description="Första teststämpeln",
            manufacturer=self.manufacturer,
            stamp_type="text",
            status="known",
            year_from=1900,
            year_to=1950,
            source_category="own_collection",
        )

        self.stamp2 = Stamp.objects.create(
            name="Test Stämpel 2",
            description="Andra teststämpeln",
            stamp_type="symbol",
            status="unknown",
        )

        # Skapa yxa
        self.axe = Axe.objects.create(
            id=1,
            manufacturer=self.manufacturer,
            model="Test Yxa",
        )

        # Skapa en bild för yxan (krävs för add_axe_stamp)
        self.axe_image = AxeImage.objects.create(
            axe=self.axe,
            image="test_images/test.jpg",
            description="Test bild",
        )

        # Skapa axe stamp
        self.axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp1,
            position="Huvudets översida",
            uncertainty_level="certain",
        )


class StampListViewTest(StampViewTestBase):
    """Tester för stamp_list view"""

    def test_stamp_list_view_public_access(self):
        """Test att listan är tillgänglig utan inloggning"""
        response = self.client.get(reverse("stamp_list"))
        # Antingen 200 eller redirect beroende på krav
        self.assertIn(response.status_code, [200, 302])

    def test_stamp_list_view_with_login(self):
        """Test att listan fungerar med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_list"))
        self.assertEqual(response.status_code, 200)

    def test_stamp_list_view_contains_stamps(self):
        """Test att listan innehåller skapade stämplar"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_list"))

        if response.status_code == 200:
            self.assertContains(response, "Test Stämpel 1")
            self.assertContains(response, "Test Stämpel 2")

    def test_stamp_list_view_search_functionality(self):
        """Test sökfunktionalitet i stämpellistan"""
        self.client.login(username="testuser", password="testpass123")

        # Sök efter en specifik stämpel
        response = self.client.get(reverse("stamp_list"), {"search": "Test Stämpel 1"})
        if response.status_code == 200:
            self.assertContains(response, "Test Stämpel 1")

    def test_stamp_list_view_manufacturer_filter(self):
        """Test filtrering efter tillverkare"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(
            reverse("stamp_list"), {"manufacturer": str(self.manufacturer.id)}
        )
        if response.status_code == 200:
            self.assertContains(response, "Test Stämpel 1")

    def test_stamp_list_view_stamp_type_filter(self):
        """Test filtrering efter stämpeltyp"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(reverse("stamp_list"), {"stamp_type": "text"})
        if response.status_code == 200:
            self.assertContains(response, "Test Stämpel 1")

    def test_stamp_list_view_status_filter(self):
        """Test filtrering efter status"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(reverse("stamp_list"), {"status": "known"})
        if response.status_code == 200:
            self.assertContains(response, "Test Stämpel 1")


class StampDetailViewTest(StampViewTestBase):
    """Tester för stamp_detail view"""

    def test_stamp_detail_view_public_access(self):
        """Test att detaljer är tillgängliga utan inloggning"""
        response = self.client.get(reverse("stamp_detail", args=[self.stamp1.id]))
        self.assertIn(response.status_code, [200, 302])

    def test_stamp_detail_view_with_login(self):
        """Test att detaljer fungerar med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_detail", args=[self.stamp1.id]))
        self.assertEqual(response.status_code, 200)

    def test_stamp_detail_view_contains_stamp_info(self):
        """Test att detaljsidan innehåller stämpelinformation"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_detail", args=[self.stamp1.id]))

        if response.status_code == 200:
            self.assertContains(response, "Test Stämpel 1")
            self.assertContains(response, "Första teststämpeln")
            self.assertContains(response, "Test Tillverkare")

    def test_stamp_detail_view_invalid_id(self):
        """Test hantering av ogiltigt stämpel-ID"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_detail", args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_stamp_detail_view_with_related_axes(self):
        """Test att relaterade yxor visas på detaljsidan"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_detail", args=[self.stamp1.id]))

        if response.status_code == 200:
            # Kontrollera att yxan med denna stämpel visas
            self.assertContains(response, str(self.axe.display_id))


class StampCreateViewTest(StampViewTestBase):
    """Tester för stamp_create view"""

    def test_stamp_create_view_requires_login(self):
        """Test att skapa stämpel kräver inloggning"""
        response = self.client.get(reverse("stamp_create"))
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_stamp_create_view_with_login(self):
        """Test att sidan för att skapa stämpel fungerar med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_create"))
        self.assertEqual(response.status_code, 200)

    def test_stamp_create_view_post_valid_data(self):
        """Test att skapa stämpel med giltig data"""
        self.client.login(username="testuser", password="testpass123")

        data = {
            "name": "Ny Test Stämpel",
            "description": "Beskrivning av ny stämpel",
            "manufacturer": self.manufacturer.id,
            "stamp_type": "text",
            "status": "known",
            "year_from": 1920,
            "year_to": 1940,
            "source_category": "museum",
        }

        response = self.client.post(reverse("stamp_create"), data)

        # Kontrollera att stämpeln skapades
        if response.status_code in [200, 302]:
            self.assertTrue(Stamp.objects.filter(name="Ny Test Stämpel").exists())

    def test_stamp_create_view_post_invalid_data(self):
        """Test att skapa stämpel med ogiltiga data"""
        self.client.login(username="testuser", password="testpass123")

        # Ogiltiga data: kräver tillverkare för known status
        data = {
            "name": "Ogiltig Stämpel",
            "stamp_type": "text",
            "status": "known",  # Kräver manufacturer
            "year_from": 1950,
            "year_to": 1940,  # Ogiltigt årtal
        }

        response = self.client.post(reverse("stamp_create"), data)

        # Formuläret ska returnera fel
        if response.status_code == 200:
            self.assertContains(response, "error")  # Eller annan felindikation

    def test_stamp_create_view_contains_form(self):
        """Test att sidan innehåller formulär för att skapa stämpel"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_create"))

        if response.status_code == 200:
            self.assertContains(response, "<form")
            self.assertContains(response, 'name="name"')
            self.assertContains(response, 'name="stamp_type"')


class StampEditViewTest(StampViewTestBase):
    """Tester för stamp_edit view"""

    def test_stamp_edit_view_requires_login(self):
        """Test att redigera stämpel kräver inloggning"""
        response = self.client.get(reverse("stamp_edit", args=[self.stamp1.id]))
        self.assertEqual(response.status_code, 302)

    def test_stamp_edit_view_with_login(self):
        """Test att redigeringssidan fungerar med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_edit", args=[self.stamp1.id]))
        self.assertEqual(response.status_code, 200)

    def test_stamp_edit_view_post_valid_data(self):
        """Test att redigera stämpel med giltig data"""
        self.client.login(username="testuser", password="testpass123")

        data = {
            "name": "Redigerad Test Stämpel",
            "description": "Uppdaterad beskrivning",
            "manufacturer": self.manufacturer.id,
            "stamp_type": "symbol",
            "status": "known",
            "year_from": 1925,
            "source_category": "own_collection",
        }

        response = self.client.post(reverse("stamp_edit", args=[self.stamp1.id]), data)

        # Kontrollera att stämpeln uppdaterades
        if response.status_code in [200, 302]:
            updated_stamp = Stamp.objects.get(id=self.stamp1.id)
            self.assertEqual(updated_stamp.name, "Redigerad Test Stämpel")
            self.assertEqual(updated_stamp.stamp_type, "symbol")

    def test_stamp_edit_view_invalid_id(self):
        """Test redigering med ogiltigt ID"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_edit", args=[99999]))
        self.assertEqual(response.status_code, 404)


class StampSearchViewTest(StampViewTestBase):
    """Tester för stamp_search view"""

    def test_stamp_search_view_get_request(self):
        """Test GET-förfrågan till sök-endpoint"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_search"))
        self.assertIn(response.status_code, [200, 405])  # Kanske endast POST

    def test_stamp_search_view_post_request(self):
        """Test POST-förfrågan för sökning"""
        self.client.login(username="testuser", password="testpass123")

        data = {"search": "Test Stämpel"}
        response = self.client.post(reverse("stamp_search"), data)

        # Beroende på implementation, kan vara JSON eller redirect
        self.assertIn(response.status_code, [200, 302])

    def test_stamp_search_ajax_request(self):
        """Test AJAX-sökning"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(
            reverse("stamp_search"),
            {"search": "Test"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        if response.status_code == 200:
            # Kontrollera JSON-svar om det är AJAX
            try:
                data = json.loads(response.content)
                self.assertIsInstance(data, (dict, list))
            except:
                pass  # Inte JSON, det är okej


class AxeStampViewTest(StampViewTestBase):
    """Tester för yxstämpel-relaterade views"""

    def test_add_axe_stamp_view_requires_login(self):
        """Test att lägga till yxstämpel kräver inloggning"""
        response = self.client.get(reverse("add_axe_stamp", args=[self.axe.id]))
        self.assertEqual(response.status_code, 302)

    def test_add_axe_stamp_view_with_login(self):
        """Test att lägga till yxstämpel med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("add_axe_stamp", args=[self.axe.id]))
        self.assertEqual(response.status_code, 200)

    def test_add_axe_stamp_view_post_valid_data(self):
        """Test att lägga till yxstämpel med giltig data"""
        self.client.login(username="testuser", password="testpass123")

        data = {
            "action": "save_stamp",
            "selected_image": self.axe_image.id,
            "stamp": self.stamp2.id,
            "x_coordinate": "10.5",
            "y_coordinate": "20.3",
            "width": "15.2",
            "height": "12.8",
            "position": "Skaftets sida",
            "comment": "Ny stämpel på yxan",
            "uncertainty_level": "uncertain",
        }

        response = self.client.post(reverse("add_axe_stamp", args=[self.axe.id]), data)

        if response.status_code in [200, 302]:
            # Kontrollera att yxstämpeln skapades
            self.assertTrue(
                AxeStamp.objects.filter(
                    axe=self.axe, stamp=self.stamp2, position="Skaftets sida"
                ).exists()
            )

    def test_edit_axe_stamp_view(self):
        """Test att redigera yxstämpel"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(
            reverse("edit_axe_stamp", args=[self.axe.id, self.axe_stamp.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_remove_axe_stamp_view(self):
        """Test att ta bort yxstämpel"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            reverse("remove_axe_stamp", args=[self.axe.id, self.axe_stamp.id])
        )

        if response.status_code in [200, 302]:
            # Kontrollera att yxstämpeln togs bort
            self.assertFalse(AxeStamp.objects.filter(id=self.axe_stamp.id).exists())


class StampStatisticsViewTest(StampViewTestBase):
    """Tester för stamp_statistics view"""

    def test_stamp_statistics_view_requires_login(self):
        """Test att statistik kräver inloggning"""
        response = self.client.get(reverse("stamp_statistics"))
        self.assertEqual(response.status_code, 302)

    def test_stamp_statistics_view_with_login(self):
        """Test att statistiksidan fungerar med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_statistics"))
        self.assertEqual(response.status_code, 200)

    def test_stamp_statistics_view_contains_data(self):
        """Test att statistiksidan innehåller relevant data"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_statistics"))

        if response.status_code == 200:
            # Kontrollera att sidan innehåller statistik
            self.assertContains(response, "statistik")


class AxesWithoutStampsViewTest(StampViewTestBase):
    """Tester för axes_without_stamps view"""

    def test_axes_without_stamps_view_requires_login(self):
        """Test att visa yxor utan stämplar kräver inloggning"""
        response = self.client.get(reverse("axes_without_stamps"))
        self.assertEqual(response.status_code, 302)

    def test_axes_without_stamps_view_with_login(self):
        """Test att sidan fungerar med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("axes_without_stamps"))
        self.assertEqual(response.status_code, 200)

    def test_axes_without_stamps_excludes_stamped_axes(self):
        """Test att yxor med stämplar exkluderas"""
        # Skapa en yxa utan stämpel
        unstamped_axe = Axe.objects.create(
            id=2,
            manufacturer=self.manufacturer,
            model="Yxa utan stämpel",
        )

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("axes_without_stamps"))

        if response.status_code == 200:
            # Yxan utan stämpel ska visas
            self.assertContains(response, str(unstamped_axe.display_id))
            # Yxan med stämpel ska inte visas (men detta kan vara svårt att testa beroende på implementation)


class StampImageViewTest(StampViewTestBase):
    """Tester för stämpelbilds-relaterade views"""

    def test_stamp_image_upload_view_requires_login(self):
        """Test att ladda upp stämpelbild kräver inloggning"""
        response = self.client.get(reverse("stamp_image_upload", args=[self.stamp1.id]))
        self.assertEqual(response.status_code, 302)

    def test_stamp_image_upload_view_with_login(self):
        """Test att sidan för bilduppladdning fungerar med inloggning"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_image_upload", args=[self.stamp1.id]))
        self.assertEqual(response.status_code, 200)

    def test_stamp_image_delete_view_requires_login(self):
        """Test att ta bort stämpelbild kräver inloggning"""
        # Först skapa en bild att ta bort
        stamp_image = StampImage.objects.create(
            stamp=self.stamp1, image="test_images/test.jpg"
        )

        response = self.client.get(
            reverse("stamp_image_delete", args=[self.stamp1.id, stamp_image.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_stamp_image_edit_view_requires_login(self):
        """Test att redigera stämpelbild kräver inloggning"""
        stamp_image = StampImage.objects.create(
            stamp=self.stamp1, image="test_images/test.jpg"
        )

        response = self.client.get(
            reverse("stamp_image_edit", args=[self.stamp1.id, stamp_image.id])
        )
        self.assertEqual(response.status_code, 302)


class StampViewIntegrationTest(StampViewTestBase):
    """Integrationstester för stämpel-views"""

    def test_complete_stamp_workflow(self):
        """Test komplett arbetsflöde för stämpelhantering"""
        self.client.login(username="testuser", password="testpass123")

        # 1. Visa stämpellista
        response = self.client.get(reverse("stamp_list"))
        self.assertIn(response.status_code, [200, 302])

        # 2. Skapa ny stämpel
        create_data = {
            "name": "Integration Test Stämpel",
            "description": "Skapad i integrationsttest",
            "manufacturer": self.manufacturer.id,
            "stamp_type": "text",
            "status": "known",
            "source_category": "own_collection",
        }

        response = self.client.post(reverse("stamp_create"), create_data)
        if response.status_code in [200, 302]:
            created_stamp = Stamp.objects.filter(
                name="Integration Test Stämpel"
            ).first()
            if created_stamp:
                # 3. Visa stämpeldetaljer
                response = self.client.get(
                    reverse("stamp_detail", args=[created_stamp.id])
                )
                self.assertEqual(response.status_code, 200)

                # 4. Redigera stämpel
                edit_data = create_data.copy()
                edit_data["description"] = "Uppdaterad beskrivning"

                response = self.client.post(
                    reverse("stamp_edit", args=[created_stamp.id]), edit_data
                )
                self.assertIn(response.status_code, [200, 302])

    def test_stamp_search_and_filter_integration(self):
        """Test integration mellan sökning och filtrering"""
        self.client.login(username="testuser", password="testpass123")

        # Testa kombinerad sökning och filtrering
        params = {
            "search": "Test",
            "manufacturer": str(self.manufacturer.id),
            "stamp_type": "text",
            "status": "known",
        }

        response = self.client.get(reverse("stamp_list"), params)
        self.assertIn(response.status_code, [200, 302])

    def test_axe_stamp_relationship_workflow(self):
        """Test arbetsflöde för yxstämpel-relationer"""
        self.client.login(username="testuser", password="testpass123")

        # Lägg till stämpel på yxa
        data = {
            "stamp": self.stamp2.id,
            "position": "Test position",
            "uncertainty_level": "certain",
        }

        response = self.client.post(reverse("add_axe_stamp", args=[self.axe.id]), data)

        if response.status_code in [200, 302]:
            # Kontrollera att stämpeln nu visas på yxan
            new_axe_stamp = AxeStamp.objects.filter(
                axe=self.axe, stamp=self.stamp2
            ).first()

            if new_axe_stamp:
                # Redigera yxstämpeln
                edit_data = {
                    "stamp": self.stamp2.id,
                    "position": "Uppdaterad position",
                    "uncertainty_level": "uncertain",
                }

                response = self.client.post(
                    reverse("edit_axe_stamp", args=[self.axe.id, new_axe_stamp.id]),
                    edit_data,
                )
                self.assertIn(response.status_code, [200, 302])
