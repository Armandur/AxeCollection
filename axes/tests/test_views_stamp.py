from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from axes.models import (
    Stamp,
    StampTranscription,
    StampTag,
    StampImage,
    AxeStamp,
    StampVariant,
    StampUncertaintyGroup,
    Axe,
    Manufacturer,
    AxeImage,
    StampSymbol,
)
from axes.forms import (
    StampForm,
    StampTranscriptionForm,
    AxeStampForm,
    StampImageForm,
    StampImageMarkForm,
)


class StampViewsTest(TestCase):
    """Tester för stamp views"""

    def setUp(self):
        """Skapa testdata"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # Skapa testdata
        self.manufacturer = Manufacturer.objects.create(
            name="Test Tillverkare", information="Test information"
        )

        self.stamp = Stamp.objects.create(
            name="Test Stämpel",
            manufacturer=self.manufacturer,
            description="Test beskrivning",
            stamp_type="text",
            status="known",
            source_category="own_collection",
        )

        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Yxa",
            comment="Test beskrivning",
        )

        self.axe_stamp = AxeStamp.objects.create(
            axe=self.axe, stamp=self.stamp, uncertainty_level="certain"
        )

        self.stamp_image = StampImage.objects.create(
            stamp=self.stamp, image="test_image.jpg", order=1, is_primary=True
        )

        self.stamp_symbol = StampSymbol.objects.create(
            name="Test Symbol", description="Test symbol beskrivning"
        )

        self.transcription = StampTranscription.objects.create(
            stamp=self.stamp, text="TEST STÄMPEL", quality="high"
        )

    def test_stamp_list_view(self):
        """Testa stamp_list view"""
        response = self.client.get(reverse("stamp_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Stämpel")

    def test_stamp_list_with_search(self):
        """Testa stamp_list med sökning"""
        response = self.client.get(reverse("stamp_list"), {"search": "Test"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Stämpel")

    def test_stamp_list_with_manufacturer_filter(self):
        """Testa stamp_list med tillverkarfilter"""
        response = self.client.get(
            reverse("stamp_list"), {"manufacturer": self.manufacturer.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Stämpel")

    def test_stamp_list_with_symbols_filter(self):
        """Testa stamp_list med symbolfilter"""
        # Koppla symbol till transkription
        self.transcription.symbols.add(self.stamp_symbol)

        response = self.client.get(
            reverse("stamp_list"), {"symbols": [self.stamp_symbol.id]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Stämpel")

    def test_stamp_detail_view(self):
        """Testa stamp_detail view"""
        response = self.client.get(reverse("stamp_detail", args=[self.stamp.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Stämpel")

    def test_stamp_detail_view_not_found(self):
        """Testa stamp_detail med ogiltigt ID"""
        response = self.client.get(reverse("stamp_detail", args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_stamp_create_view_requires_login(self):
        """Testa att stamp_create kräver inloggning"""
        response = self.client.get(reverse("stamp_create"))
        self.assertEqual(response.status_code, 302)  # Redirect till login

    def test_stamp_create_view_logged_in(self):
        """Testa stamp_create när inloggad"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_create"))
        self.assertEqual(response.status_code, 200)

    def test_stamp_create_post(self):
        """Testa POST till stamp_create"""
        self.client.login(username="testuser", password="testpass123")

        data = {
            "name": "Ny Stämpel",
            "manufacturer": self.manufacturer.id,
            "description": "Ny beskrivning",
            "stamp_type": "standard",
            "status": "active",
            "source_category": "auction",
        }

        response = self.client.post(reverse("stamp_create"), data)
        self.assertEqual(response.status_code, 302)  # Redirect efter skapande

        # Kontrollera att stämpeln skapades
        self.assertTrue(Stamp.objects.filter(name="Ny Stämpel").exists())

    def test_stamp_edit_view_requires_login(self):
        """Testa att stamp_edit kräver inloggning"""
        response = self.client.get(reverse("stamp_edit", args=[self.stamp.id]))
        self.assertEqual(response.status_code, 302)

    def test_stamp_edit_view_logged_in(self):
        """Testa stamp_edit när inloggad"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_edit", args=[self.stamp.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Stämpel")

    def test_stamp_edit_post(self):
        """Testa POST till stamp_edit"""
        self.client.login(username="testuser", password="testpass123")

        data = {
            "name": "Uppdaterad Stämpel",
            "manufacturer": self.manufacturer.id,
            "description": "Uppdaterad beskrivning",
            "stamp_type": "standard",
            "status": "active",
            "source_category": "auction",
        }

        response = self.client.post(reverse("stamp_edit", args=[self.stamp.id]), data)
        self.assertEqual(response.status_code, 302)

        # Kontrollera att stämpeln uppdaterades
        self.stamp.refresh_from_db()
        self.assertEqual(self.stamp.name, "Uppdaterad Stämpel")

    def test_axes_without_stamps_view_requires_login(self):
        """Testa att axes_without_stamps kräver inloggning"""
        response = self.client.get(reverse("axes_without_stamps"))
        self.assertEqual(response.status_code, 302)

    def test_axes_without_stamps_view_logged_in(self):
        """Testa axes_without_stamps när inloggad"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("axes_without_stamps"))
        self.assertEqual(response.status_code, 200)

    def test_stamp_search_view(self):
        """Testa stamp_search view"""
        response = self.client.get(reverse("stamp_search"))
        self.assertEqual(response.status_code, 200)

    def test_stamp_search_with_query(self):
        """Testa stamp_search med sökfråga"""
        response = self.client.get(reverse("stamp_search"), {"q": "Test"})
        self.assertEqual(response.status_code, 200)

    def test_stamp_image_upload_requires_login(self):
        """Testa att stamp_image_upload kräver inloggning"""
        response = self.client.get(reverse("stamp_image_upload", args=[self.stamp.id]))
        self.assertEqual(response.status_code, 302)

    def test_stamp_image_upload_logged_in(self):
        """Testa stamp_image_upload när inloggad"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stamp_image_upload", args=[self.stamp.id]))
        self.assertEqual(response.status_code, 200)

    def test_stamp_image_delete_requires_login(self):
        """Testa att stamp_image_delete kräver inloggning"""
        response = self.client.get(
            reverse("stamp_image_delete", args=[self.stamp.id, self.stamp_image.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_stamp_image_edit_requires_login(self):
        """Testa att stamp_image_edit kräver inloggning"""
        response = self.client.get(
            reverse("stamp_image_edit", args=[self.stamp.id, self.stamp_image.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_add_axe_stamp_requires_login(self):
        """Testa att add_axe_stamp kräver inloggning"""
        response = self.client.get(reverse("add_axe_stamp", args=[self.axe.id]))
        self.assertEqual(response.status_code, 302)

    def test_add_axe_stamp_logged_in(self):
        """Testa add_axe_stamp när inloggad"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("add_axe_stamp", args=[self.axe.id]))
        self.assertEqual(response.status_code, 200)

    def test_remove_axe_stamp_requires_login(self):
        """Testa att remove_axe_stamp kräver inloggning"""
        response = self.client.get(
            reverse("remove_axe_stamp", args=[self.axe.id, self.axe_stamp.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_stamp_statistics_view(self):
        """Testa stamp_statistics view"""
        response = self.client.get(reverse("stamp_statistics"))
        self.assertEqual(response.status_code, 200)

    def test_mark_axe_image_as_stamp_requires_login(self):
        """Testa att mark_axe_image_as_stamp kräver inloggning"""
        response = self.client.get(
            reverse("mark_axe_image_as_stamp", args=[self.axe.id, 1])
        )
        self.assertEqual(response.status_code, 302)

    def test_unmark_axe_image_stamp_requires_login(self):
        """Testa att unmark_axe_image_stamp kräver inloggning"""
        response = self.client.get(
            reverse("unmark_axe_image_stamp", args=[self.axe.id, 1])
        )
        self.assertEqual(response.status_code, 302)

    def test_edit_axe_image_stamp_requires_login(self):
        """Testa att edit_axe_image_stamp kräver inloggning"""
        response = self.client.get(
            reverse("edit_axe_image_stamp", args=[self.axe.id, 1])
        )
        self.assertEqual(response.status_code, 302)

    def test_stamp_image_crop_requires_login(self):
        """Testa att stamp_image_crop kräver inloggning"""
        response = self.client.get(reverse("stamp_image_crop", args=[self.stamp.id]))
        self.assertEqual(response.status_code, 302)

    def test_set_primary_stamp_image_requires_login(self):
        """Testa att set_primary_stamp_image kräver inloggning"""
        response = self.client.get(
            reverse(
                "set_primary_stamp_image", args=[self.stamp.id, self.stamp_image.id]
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_update_axe_image_stamp_show_full_requires_login(self):
        """Testa att update_axe_image_stamp_show_full kräver inloggning"""
        response = self.client.get(
            reverse("update_axe_image_stamp_show_full", args=[1])
        )
        self.assertEqual(response.status_code, 302)

    def test_edit_axe_stamp_requires_login(self):
        """Testa att edit_axe_stamp kräver inloggning"""
        response = self.client.get(
            reverse("edit_axe_stamp", args=[self.axe.id, self.axe_stamp.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_edit_axe_image_stamp_via_axe_stamp_requires_login(self):
        """Testa att edit_axe_image_stamp_via_axe_stamp kräver inloggning"""
        response = self.client.get(
            reverse("edit_axe_image_stamp_via_axe_stamp", args=[self.axe.id, 1])
        )
        self.assertEqual(response.status_code, 302)

    def test_remove_axe_image_stamp_requires_login(self):
        """Testa att remove_axe_image_stamp kräver inloggning"""
        response = self.client.get(
            reverse("remove_axe_image_stamp", args=[self.axe.id, 1])
        )
        self.assertEqual(response.status_code, 302)

    def test_transcription_create_requires_login(self):
        """Testa att transcription_create kräver inloggning"""
        response = self.client.get(reverse("transcription_create"))
        self.assertEqual(response.status_code, 302)

    def test_transcription_edit_requires_login(self):
        """Testa att transcription_edit kräver inloggning"""
        response = self.client.get(
            reverse("transcription_edit", args=[self.stamp.id, self.transcription.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_transcription_delete_requires_login(self):
        """Testa att transcription_delete kräver inloggning"""
        response = self.client.get(
            reverse("transcription_delete", args=[self.stamp.id, self.transcription.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_stamp_transcriptions_view(self):
        """Testa stamp_transcriptions view"""
        response = self.client.get(
            reverse("stamp_transcriptions", args=[self.stamp.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TEST STÄMPEL")

    def test_stamp_symbols_api_requires_login(self):
        """API:t är publikt: ska svara 200 även utan inloggning"""
        response = self.client.get(reverse("stamp_symbols_api"))
        self.assertEqual(response.status_code, 200)

    def test_stamp_symbol_update_requires_login(self):
        """Testa att stamp_symbol_update kräver inloggning"""
        response = self.client.get(
            reverse("stamp_symbol_update", args=[self.stamp_symbol.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_stamp_symbol_delete_requires_login(self):
        """Testa att stamp_symbol_delete kräver inloggning"""
        response = self.client.get(
            reverse("stamp_symbol_delete", args=[self.stamp_symbol.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_stamp_symbols_manage_requires_login(self):
        """Testa att stamp_symbols_manage kräver inloggning"""
        response = self.client.get(reverse("stamp_symbols_manage"))
        self.assertEqual(response.status_code, 302)
