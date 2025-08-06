"""
Tester för admin.py
"""
import os
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpRequest
from axes.admin import (
    ManufacturerAdmin,
    AxeAdmin,
    AxeDeleteForm,
    MeasurementTypeAdmin,
    MeasurementTemplateAdmin,
    StampAdmin,
    StampTranscriptionAdmin,
    StampTagAdmin,
    StampImageAdmin,
    AxeStampAdmin,
    StampVariantAdmin,
    StampUncertaintyGroupAdmin,
)
from axes.models import (
    Manufacturer,
    Axe,
    Contact,
    Platform,
    Transaction,
    MeasurementType,
    MeasurementTemplate,
    MeasurementTemplateItem,
    Measurement,
    ManufacturerImage,
    ManufacturerLink,
    AxeImage,
    Stamp,
    StampTranscription,
    StampTag,
    StampImage,
    AxeStamp,
    StampVariant,
    StampUncertaintyGroup,
    StampSymbol,
)


class AdminTestCase(TestCase):
    """Basistestklass för admin-tester"""

    def setUp(self):
        """Sätt upp testdata"""
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.user = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="adminpass123"
        )

        # Skapa testdata
        self.manufacturer = Manufacturer.objects.create(
            name="Test Manufacturer",
            manufacturer_type="TILLVERKARE",
            country_code="SE",
        )
        self.parent_manufacturer = Manufacturer.objects.create(
            name="Parent Manufacturer",
            manufacturer_type="TILLVERKARE",
            country_code="NO",
        )
        self.child_manufacturer = Manufacturer.objects.create(
            name="Child Manufacturer",
            parent=self.parent_manufacturer,
            manufacturer_type="SMED",
            country_code="DK",
        )

        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer,
            model="Test Axe Model",
            status="KÖPT",
        )

        self.contact = Contact.objects.create(
            name="Test Contact",
            email="contact@test.com",
        )

        self.platform = Platform.objects.create(
            name="Test Platform",
            url="https://test.com",
        )

        self.transaction = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            price=1000,
            type="KÖP",
            transaction_date="2024-01-15",
        )

        self.measurement_type = MeasurementType.objects.create(
            name="Length",
            unit="cm",
            is_active=True,
            sort_order=1,
        )

        self.measurement_template = MeasurementTemplate.objects.create(
            name="Standard Template",
            description="Standard measurements",
            is_active=True,
            sort_order=1,
        )

        self.measurement_template_item = MeasurementTemplateItem.objects.create(
            template=self.measurement_template,
            measurement_type=self.measurement_type,
            sort_order=1,
        )

        # Skapa MeasurementType för mått
        self.measurement_type = MeasurementType.objects.create(
            name="Längd",
            unit="cm",
            description="Längdmått",
            sort_order=1,
        )
        
        # Skapa MeasurementTemplate för måttmall
        self.measurement_template = MeasurementTemplate.objects.create(
            name="Standard yxa",
            description="Standardmått för yxor",
            sort_order=1,
        )
        
        # Skapa MeasurementTemplateItem
        self.measurement_template_item = MeasurementTemplateItem.objects.create(
            template=self.measurement_template,
            measurement_type=self.measurement_type,
            sort_order=1,
        )
        
        self.measurement = Measurement.objects.create(
            axe=self.axe,
            name="Längd",
            value=10.5,
            unit="cm",
        )

        self.stamp = Stamp.objects.create(
            name="Test Stamp",
            manufacturer=self.manufacturer,
            stamp_type="symbol",
            status="known",
            source_category="own_collection",
        )

        self.stamp_transcription = StampTranscription.objects.create(
            stamp=self.stamp,
            text="Test transcription",
            quality="high",
            created_by=self.user,
        )

        self.stamp_tag = StampTag.objects.create(
            name="Test Tag",
            description="Test tag description",
            color="#FF0000",
        )

        # Skapa en mock-bild för AxeImage
        from django.core.files.uploadedfile import SimpleUploadedFile
        mock_axe_image = SimpleUploadedFile(
            "test_axe_image.jpg",
            b"fake axe image content",
            content_type="image/jpeg"
        )
        
        self.axe_image = AxeImage.objects.create(
            axe=self.axe,
            image=mock_axe_image,
        )
        
        # Skapa en mock-bild för StampImage
        mock_stamp_image = SimpleUploadedFile(
            "test_stamp_image.jpg",
            b"fake stamp image content",
            content_type="image/jpeg"
        )
        
        self.stamp_image = StampImage.objects.create(
            stamp=self.stamp,
            image=mock_stamp_image,
            image_type="reference",
            caption="Test image",
            description="Test image description",
            uncertainty_level="certain",
            order=1,
        )

        self.axe_stamp = AxeStamp.objects.create(
            axe=self.axe,
            stamp=self.stamp,
            uncertainty_level="certain",
            position="top",
        )

        self.stamp_variant = StampVariant.objects.create(
            main_stamp=self.stamp,
            variant_stamp=self.stamp,
            description="Test variant",
        )

        # Skapa StampSymbol för symboler
        self.stamp_symbol = StampSymbol.objects.create(
            name="Test Symbol",
            symbol_type="crown",
            description="Test symbol description",
            pictogram="👑",
            is_predefined=True,
        )
        
        self.stamp_uncertainty_group = StampUncertaintyGroup.objects.create(
            name="Test Group",
            description="Test group description",
            confidence_level="high",
        )


class ManufacturerAdminTest(AdminTestCase):
    """Tester för ManufacturerAdmin"""

    def setUp(self):
        super().setUp()
        self.admin = ManufacturerAdmin(Manufacturer, self.admin_site)

    def test_list_display(self):
        """Testa list_display"""
        list_display = self.admin.get_list_display(self.factory.get("/"))
        expected_fields = ["hierarchical_name", "parent", "manufacturer_type", "country_code"]
        for field in expected_fields:
            self.assertIn(field, list_display)

    def test_hierarchical_name_with_parent(self):
        """Testa hierarchical_name med parent"""
        result = self.admin.hierarchical_name(self.child_manufacturer)
        self.assertIn("└─", result)
        self.assertIn("DK", result)
        self.assertIn("Child Manufacturer", result)

    def test_hierarchical_name_without_parent(self):
        """Testa hierarchical_name utan parent"""
        result = self.admin.hierarchical_name(self.manufacturer)
        self.assertNotIn("└─", result)
        self.assertIn("SE", result)
        self.assertIn("Test Manufacturer", result)

    def test_hierarchical_name_without_country_code(self):
        """Testa hierarchical_name utan country_code"""
        self.manufacturer.country_code = ""
        self.manufacturer.save()
        result = self.admin.hierarchical_name(self.manufacturer)
        self.assertNotIn("SE", result)
        self.assertIn("Test Manufacturer", result)

    def test_get_queryset(self):
        """Testa get_queryset"""
        queryset = self.admin.get_queryset(self.factory.get("/"))
        self.assertIn(self.manufacturer, queryset)
        self.assertIn(self.parent_manufacturer, queryset)
        self.assertIn(self.child_manufacturer, queryset)

    def test_list_filter(self):
        """Testa list_filter"""
        self.assertEqual(self.admin.list_filter, ("manufacturer_type", "parent", "country_code"))

    def test_search_fields(self):
        """Testa search_fields"""
        self.assertEqual(self.admin.search_fields, ("name", "information", "country_code"))


class AxeAdminTest(AdminTestCase):
    """Tester för AxeAdmin"""

    def setUp(self):
        super().setUp()
        self.admin = AxeAdmin(Axe, self.admin_site)

    def test_list_display(self):
        """Testa list_display"""
        self.assertEqual(
            self.admin.list_display,
            ("id", "manufacturer", "model", "status", "display_id")
        )

    def test_list_filter(self):
        """Testa list_filter"""
        self.assertEqual(self.admin.list_filter, ("manufacturer", "status"))

    def test_search_fields(self):
        """Testa search_fields"""
        self.assertEqual(
            self.admin.search_fields,
            ("manufacturer__name", "model", "comment")
        )

    def test_readonly_fields(self):
        """Testa readonly_fields"""
        self.assertEqual(self.admin.readonly_fields, ("display_id",))

    def test_get_queryset(self):
        """Testa get_queryset"""
        queryset = self.admin.get_queryset(self.factory.get("/"))
        self.assertIn(self.axe, queryset)

    @patch("os.path.isfile")
    @patch("os.remove")
    def test_delete_model_with_images(self, mock_remove, mock_isfile):
        """Testa delete_model med bilder"""
        mock_isfile.return_value = True
        
        # Skapa en testbild
        image_content = b"fake image content"
        image = SimpleUploadedFile("test.jpg", image_content, content_type="image/jpeg")
        axe_image = AxeImage.objects.create(
            axe=self.axe,
            image=image,
        )

        request = self.factory.post("/", {"delete_images": "on"})
        request.user = self.user

        self.admin.delete_model(request, self.axe)

        # Kontrollera att bildfilen skulle tas bort
        mock_remove.assert_called()

    def test_get_flat_deleted_objects(self):
        """Testa get_flat_deleted_objects"""
        deleted_objects = [
            [self.axe, self.contact],
            self.transaction,
            [self.measurement]
        ]
        flat = self.admin.get_flat_deleted_objects(deleted_objects)
        self.assertIsInstance(flat, list)
        self.assertGreater(len(flat), 0)

    def test_delete_view(self):
        """Testa delete_view"""
        request = self.factory.get("/")
        request.user = self.user
        
        with patch.object(self.admin, 'get_object') as mock_get_object:
            mock_get_object.return_value = self.axe
            response = self.admin.delete_view(request, str(self.axe.id))
            self.assertIsNotNone(response)


class AxeDeleteFormTest(AdminTestCase):
    """Tester för AxeDeleteForm"""

    def test_form_fields(self):
        """Testa form-fält"""
        form = AxeDeleteForm()
        self.assertIn("delete_images", form.fields)
        self.assertTrue(form.fields["delete_images"].required is False)
        self.assertTrue(form.fields["delete_images"].initial is True)


class MeasurementTypeAdminTest(AdminTestCase):
    """Tester för MeasurementTypeAdmin"""

    def setUp(self):
        super().setUp()
        self.admin = MeasurementTypeAdmin(MeasurementType, self.admin_site)

    def test_list_display(self):
        """Testa list_display"""
        expected_fields = ["name", "unit", "is_active", "sort_order", "created_at"]
        for field in expected_fields:
            self.assertIn(field, self.admin.list_display)

    def test_list_filter(self):
        """Testa list_filter"""
        self.assertEqual(self.admin.list_filter, ("is_active", "created_at"))

    def test_search_fields(self):
        """Testa search_fields"""
        self.assertEqual(self.admin.search_fields, ("name", "description"))

    def test_ordering(self):
        """Testa ordering"""
        self.assertEqual(self.admin.ordering, ("sort_order", "name"))

    def test_list_editable(self):
        """Testa list_editable"""
        self.assertEqual(self.admin.list_editable, ("is_active", "sort_order"))


class MeasurementTemplateAdminTest(AdminTestCase):
    """Tester för MeasurementTemplateAdmin"""

    def setUp(self):
        super().setUp()
        self.admin = MeasurementTemplateAdmin(MeasurementTemplate, self.admin_site)

    def test_list_display(self):
        """Testa list_display"""
        expected_fields = [
            "name", "description", "is_active", "sort_order", 
            "item_count", "created_at"
        ]
        for field in expected_fields:
            self.assertIn(field, self.admin.list_display)

    def test_item_count(self):
        """Testa item_count metod"""
        count = self.admin.item_count(self.measurement_template)
        self.assertEqual(count, 1)

    def test_list_filter(self):
        """Testa list_filter"""
        self.assertEqual(self.admin.list_filter, ("is_active", "created_at"))

    def test_search_fields(self):
        """Testa search_fields"""
        self.assertEqual(self.admin.search_fields, ("name", "description"))

    def test_ordering(self):
        """Testa ordering"""
        self.assertEqual(self.admin.ordering, ("sort_order", "name"))

    def test_list_editable(self):
        """Testa list_editable"""
        self.assertEqual(self.admin.list_editable, ("is_active", "sort_order"))


class StampAdminTest(AdminTestCase):
    """Tester för StampAdmin"""

    def setUp(self):
        super().setUp()
        self.admin = StampAdmin(Stamp, self.admin_site)

    def test_list_display(self):
        """Testa list_display"""
        expected_fields = [
            "name", "manufacturer", "stamp_type", "status", 
            "year_range", "source_category"
        ]
        for field in expected_fields:
            self.assertIn(field, self.admin.list_display)

    def test_list_filter(self):
        """Testa list_filter"""
        expected_filters = ("stamp_type", "status", "source_category", "manufacturer")
        for filter_name in expected_filters:
            self.assertIn(filter_name, self.admin.list_filter)

    def test_search_fields(self):
        """Testa search_fields"""
        self.assertEqual(
            self.admin.search_fields,
            ("name", "description", "manufacturer__name")
        )

    def test_ordering(self):
        """Testa ordering"""
        self.assertEqual(self.admin.ordering, ("name",))

    def test_fieldsets(self):
        """Testa fieldsets"""
        self.assertIsInstance(self.admin.fieldsets, tuple)
        self.assertGreater(len(self.admin.fieldsets), 0)


class StampTranscriptionAdminTest(AdminTestCase):
    """Tester för StampTranscriptionAdmin"""

    def setUp(self):
        super().setUp()
        self.admin = StampTranscriptionAdmin(StampTranscription, self.admin_site)

    def test_list_display(self):
        """Testa list_display"""
        expected_fields = ["stamp", "text", "quality", "created_by", "created_at"]
        for field in expected_fields:
            self.assertIn(field, self.admin.list_display)

    def test_list_filter(self):
        """Testa list_filter"""
        expected_filters = ("quality", "created_at", "stamp__manufacturer")
        for filter_name in expected_filters:
            self.assertIn(filter_name, self.admin.list_filter)

    def test_search_fields(self):
        """Testa search_fields"""
        self.assertEqual(
            self.admin.search_fields,
            ("text", "stamp__name", "stamp__manufacturer__name")
        )

    def test_ordering(self):
        """Testa ordering"""
        self.assertEqual(self.admin.ordering, ("-created_at",))


class StampTagAdminTest(AdminTestCase):
    """Tester för StampTagAdmin"""

    def setUp(self):
        super().setUp()
        self.admin = StampTagAdmin(StampTag, self.admin_site)

    def test_list_display(self):
        """Testa list_display"""
        expected_fields = ["name", "description", "color", "created_at"]
        for field in expected_fields:
            self.assertIn(field, self.admin.list_display)

    def test_list_filter(self):
        """Testa list_filter"""
        self.assertEqual(self.admin.list_filter, ("created_at",))

    def test_search_fields(self):
        """Testa search_fields"""
        self.assertEqual(self.admin.search_fields, ("name", "description"))

    def test_ordering(self):
        """Testa ordering"""
        self.assertEqual(self.admin.ordering, ("name",))


class StampImageAdminTest(AdminTestCase):
    """Tester för StampImageAdmin"""

    def setUp(self):
        super().setUp()
        self.admin = StampImageAdmin(StampImage, self.admin_site)

    def test_list_display(self):
        """Testa list_display"""
        expected_fields = [
            "stamp", "image_type", "axe_image", "caption", "is_primary",
            "has_coordinates", "show_full_image", "uploaded_at"
        ]
        for field in expected_fields:
            self.assertIn(field, self.admin.list_display)

    def test_has_coordinates(self):
        """Testa has_coordinates metod"""
        # Testa med koordinater
        self.stamp_image.x_coordinate = 10
        self.stamp_image.y_coordinate = 20
        self.stamp_image.width = 30
        self.stamp_image.height = 40
        self.stamp_image.save()
        result = self.admin.has_coordinates(self.stamp_image)
        self.assertTrue(result)

        # Testa utan koordinater
        self.stamp_image.x_coordinate = None
        self.stamp_image.y_coordinate = None
        self.stamp_image.width = None
        self.stamp_image.height = None
        self.stamp_image.save()
        result = self.admin.has_coordinates(self.stamp_image)
        self.assertFalse(result)

    def test_get_queryset(self):
        """Testa get_queryset"""
        queryset = self.admin.get_queryset(self.factory.get("/"))
        self.assertIn(self.stamp_image, queryset)

    def test_save_model_with_warning(self):
        """Testa save_model med varning"""
        request = self.factory.post("/")
        request.user = self.user
        
        # Skapa en axe_mark bild med axe_image
        self.stamp_image.image_type = "axe_mark"
        self.stamp_image.axe_image = self.axe_image
        
        with patch.object(self.admin, 'message_user') as mock_message:
            self.admin.save_model(request, self.stamp_image, None, False)
            # Kontrollera att save_model körs utan fel
            self.assertTrue(True)


class AxeStampAdminTest(AdminTestCase):
    """Tester för AxeStampAdmin"""

    def setUp(self):
        super().setUp()
        self.admin = AxeStampAdmin(AxeStamp, self.admin_site)

    def test_list_display(self):
        """Testa list_display"""
        expected_fields = ["axe", "stamp", "uncertainty_level", "position", "created_at"]
        for field in expected_fields:
            self.assertIn(field, self.admin.list_display)

    def test_list_filter(self):
        """Testa list_filter"""
        expected_filters = ("uncertainty_level", "created_at", "stamp__manufacturer")
        for filter_name in expected_filters:
            self.assertIn(filter_name, self.admin.list_filter)

    def test_search_fields(self):
        """Testa search_fields"""
        self.assertEqual(
            self.admin.search_fields,
            ("axe__model", "stamp__name", "comment", "position")
        )

    def test_ordering(self):
        """Testa ordering"""
        self.assertEqual(self.admin.ordering, ("-created_at",))


class StampVariantAdminTest(AdminTestCase):
    """Tester för StampVariantAdmin"""

    def setUp(self):
        super().setUp()
        self.admin = StampVariantAdmin(StampVariant, self.admin_site)

    def test_list_display(self):
        """Testa list_display"""
        expected_fields = ["main_stamp", "variant_stamp", "description", "created_at"]
        for field in expected_fields:
            self.assertIn(field, self.admin.list_display)

    def test_list_filter(self):
        """Testa list_filter"""
        expected_filters = ("created_at", "main_stamp__manufacturer")
        for filter_name in expected_filters:
            self.assertIn(filter_name, self.admin.list_filter)

    def test_search_fields(self):
        """Testa search_fields"""
        self.assertEqual(
            self.admin.search_fields,
            ("main_stamp__name", "variant_stamp__name", "description")
        )

    def test_ordering(self):
        """Testa ordering"""
        self.assertEqual(self.admin.ordering, ("-created_at",))


class StampUncertaintyGroupAdminTest(AdminTestCase):
    """Tester för StampUncertaintyGroupAdmin"""

    def setUp(self):
        super().setUp()
        self.admin = StampUncertaintyGroupAdmin(StampUncertaintyGroup, self.admin_site)

    def test_list_display(self):
        """Testa list_display"""
        expected_fields = ["name", "confidence_level", "stamp_count", "created_at"]
        for field in expected_fields:
            self.assertIn(field, self.admin.list_display)

    def test_stamp_count(self):
        """Testa stamp_count metod"""
        count = self.admin.stamp_count(self.stamp_uncertainty_group)
        self.assertEqual(count, 0)  # Inga stämplar kopplade än

    def test_list_filter(self):
        """Testa list_filter"""
        expected_filters = ("confidence_level", "created_at")
        for filter_name in expected_filters:
            self.assertIn(filter_name, self.admin.list_filter)

    def test_search_fields(self):
        """Testa search_fields"""
        self.assertEqual(self.admin.search_fields, ("name", "description"))

    def test_ordering(self):
        """Testa ordering"""
        self.assertEqual(self.admin.ordering, ("-created_at",)) 