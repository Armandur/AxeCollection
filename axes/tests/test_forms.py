import pytest
from django import forms
from django.test import TestCase
from axes.forms import (
    AxeForm,
    ContactForm,
    PlatformForm,
    TransactionForm,
    MeasurementForm,
    BackupUploadForm,
)
from axes.models import (
    Manufacturer,
    Axe,
    Contact,
    Platform,
    Transaction,
    MeasurementType,
)
from django.utils import timezone

import datetime


@pytest.mark.django_db
def test_axeform_requires_manufacturer():
    form = AxeForm(data={"model": "Testmodell", "status": "KÖPT"})
    assert not form.is_valid()
    assert "manufacturer" in form.errors
    # Django default: "This field is required."
    assert form.errors["manufacturer"] == ["This field is required."]


@pytest.mark.django_db
def test_axeform_invalid_manufacturer():
    form = AxeForm(data={"manufacturer": 9999, "model": "Testmodell", "status": "KÖPT"})
    assert not form.is_valid()
    assert "manufacturer" in form.errors
    # Django default: "Select a valid choice. 9999 is not one of the available choices."
    assert "Select a valid choice" in form.errors["manufacturer"][0]


@pytest.mark.django_db
def test_axeform_valid_minimal(monkeypatch):
    m = Manufacturer.objects.create(name="Testtillverkare")
    form = AxeForm(data={"manufacturer": m.id, "model": "Testmodell", "status": "KÖPT"})
    assert form.is_valid()
    axe = form.save(commit=False)
    assert axe.manufacturer == m
    assert axe.model == "Testmodell"
    assert axe.status == "KÖPT"


@pytest.mark.django_db
def test_axeform_hierarchical_choices():
    parent = Manufacturer.objects.create(name="Parent")
    child = Manufacturer.objects.create(name="Child", parent=parent)
    form = AxeForm()
    choices = form.fields["manufacturer"].choices
    # Första valet är tomt
    assert choices[0][1] == "Välj tillverkare..."
    # Parent och child finns med
    labels = [c[1] for c in choices]
    assert any("Parent" in label for label in labels)
    assert any("Child" in label for label in labels)
    # Child ska ha prefix (indentering)
    child_label = [c[1] for c in choices if c[0] == child.id][0]
    assert "Child" in child_label and child_label != "Child"


@pytest.mark.django_db
def test_axeform_clean_manufacturer_valid():
    m = Manufacturer.objects.create(name="Testtillverkare")
    form = AxeForm()
    form.cleaned_data = {"manufacturer": m.id}
    result = form.clean_manufacturer()
    assert result == m


@pytest.mark.django_db
def test_axeform_clean_manufacturer_invalid():
    form = AxeForm()
    form.cleaned_data = {"manufacturer": 9999}
    with pytest.raises(forms.ValidationError, match="Vald tillverkare finns inte."):
        form.clean_manufacturer()


@pytest.mark.django_db
def test_axeform_clean_manufacturer_empty():
    form = AxeForm()
    form.cleaned_data = {"manufacturer": ""}
    with pytest.raises(forms.ValidationError, match="Tillverkare måste väljas."):
        form.clean_manufacturer()


@pytest.mark.django_db
def test_axeform_save_creates_axe():
    m = Manufacturer.objects.create(name="Testtillverkare")
    form = AxeForm(data={"manufacturer": m.id, "model": "Testmodell", "status": "KÖPT"})
    assert form.is_valid()
    axe = form.save()
    assert isinstance(axe, Axe)
    assert axe.manufacturer == m
    assert axe.model == "Testmodell"
    assert axe.status == "KÖPT"
    assert axe.id is not None


@pytest.mark.django_db
def test_axeform_save_commit_false():
    m = Manufacturer.objects.create(name="Testtillverkare")
    form = AxeForm(data={"manufacturer": m.id, "model": "Testmodell", "status": "KÖPT"})
    assert form.is_valid()
    axe = form.save(commit=False)
    assert isinstance(axe, Axe)
    assert axe.manufacturer == m
    assert axe.model == "Testmodell"
    assert axe.status == "KÖPT"
    # Axe ska inte ha sparat till databasen än
    assert not hasattr(axe, "id") or axe.id is None


@pytest.mark.django_db
def test_axeform_with_comment():
    m = Manufacturer.objects.create(name="Testtillverkare")
    form = AxeForm(
        data={
            "manufacturer": m.id,
            "model": "Testmodell",
            "status": "KÖPT",
            "comment": "En testkommentar",
        }
    )
    assert form.is_valid()
    axe = form.save(commit=False)
    assert axe.comment == "En testkommentar"


@pytest.mark.django_db
def test_axeform_edit_existing_axe():
    m = Manufacturer.objects.create(name="Testtillverkare")
    axe = Axe.objects.create(manufacturer=m, model="Gammal modell", status="KÖPT")
    form = AxeForm(
        instance=axe,
        data={"manufacturer": m.id, "model": "Ny modell", "status": "MOTTAGEN"},
    )
    assert form.is_valid()
    updated_axe = form.save()
    assert updated_axe.model == "Ny modell"
    assert updated_axe.status == "MOTTAGEN"
    assert updated_axe.id == axe.id


# ContactForm tester
@pytest.mark.django_db
def test_contactform_requires_name():
    form = ContactForm(data={"email": "test@example.com"})
    assert not form.is_valid()
    assert "name" in form.errors


@pytest.mark.django_db
def test_contactform_valid_minimal():
    form = ContactForm(data={"name": "Test Person"})
    assert form.is_valid()
    contact = form.save(commit=False)
    assert contact.name == "Test Person"


@pytest.mark.django_db
def test_contactform_with_email():
    form = ContactForm(data={"name": "Test Person", "email": "test@example.com"})
    assert form.is_valid()
    contact = form.save(commit=False)
    assert contact.name == "Test Person"
    assert contact.email == "test@example.com"


@pytest.mark.django_db
def test_contactform_with_country_code():
    form = ContactForm(data={"name": "Test Person", "country_code": "SE"})
    assert form.is_valid()
    contact = form.save(commit=False)
    assert contact.country_code == "SE"


@pytest.mark.django_db
def test_contactform_save_creates_contact():
    form = ContactForm(data={"name": "Test Person"})
    assert form.is_valid()
    contact = form.save()
    assert isinstance(contact, Contact)
    assert contact.name == "Test Person"
    assert contact.id is not None


# PlatformForm tester
@pytest.mark.django_db
def test_platformform_requires_name():
    form = PlatformForm(data={"color_class": "bg-primary"})
    assert not form.is_valid()
    assert "name" in form.errors


@pytest.mark.django_db
def test_platformform_valid_minimal():
    form = PlatformForm(data={"name": "Test Platform", "color_class": "bg-primary"})
    assert form.is_valid()
    platform = form.save(commit=False)
    assert platform.name == "Test Platform"
    assert platform.color_class == "bg-primary"


@pytest.mark.django_db
def test_platformform_with_color_class():
    form = PlatformForm(data={"name": "Test Platform", "color_class": "bg-success"})
    assert form.is_valid()
    platform = form.save(commit=False)
    assert platform.name == "Test Platform"
    assert platform.color_class == "bg-success"


@pytest.mark.django_db
def test_platformform_save_creates_platform():
    form = PlatformForm(data={"name": "Test Platform", "color_class": "bg-primary"})
    assert form.is_valid()
    platform = form.save()
    assert isinstance(platform, Platform)
    assert platform.name == "Test Platform"
    assert platform.id is not None


class TransactionFormTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.contact = Contact.objects.create(
            name="Test Contact", email="test@example.com"
        )
        self.platform = Platform.objects.create(name="Test Platform")
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe", status="KÖPT"
        )

    def test_transaction_form_valid_data(self):
        """Testa TransactionForm med giltig data"""
        form_data = {
            "axe": self.axe.id,
            "transaction_date": timezone.now().date(),
            "type": "KÖP",
            "price": "100.00",
            "shipping_cost": "10.00",
            "contact": self.contact.id,
            "platform": self.platform.id,
            "comment": "Test transaction",
        }
        form = TransactionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_transaction_form_invalid_price(self):
        """Testa TransactionForm med ogiltigt pris"""
        form_data = {
            "axe": self.axe.id,
            "transaction_date": timezone.now().date(),
            "type": "KÖP",
            "price": "invalid_price",
            "shipping_cost": "10.00",
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_transaction_form_optional_fields(self):
        """Testa TransactionForm med valfria fält tomma"""
        form_data = {
            "axe": self.axe.id,
            "transaction_date": timezone.now().date(),
            "type": "KÖP",
            "price": "100.00",
            "shipping_cost": "0.00",
        }
        form = TransactionForm(data=form_data)
        self.assertTrue(form.is_valid())


class PlatformFormTest(TestCase):
    def test_platform_form_valid_data(self):
        """Testa PlatformForm med giltig data"""
        form_data = {"name": "Test Platform", "color_class": "bg-primary"}
        form = PlatformForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_platform_form_missing_name(self):
        """Testa PlatformForm utan namn"""
        form_data = {"color_class": "bg-primary"}
        form = PlatformForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_platform_form_empty_name(self):
        """Testa PlatformForm med tomt namn"""
        form_data = {"name": "", "color_class": "bg-primary"}
        form = PlatformForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class ContactFormTest(TestCase):
    def test_contact_form_valid_data(self):
        """Testa ContactForm med giltig data"""
        form_data = {
            "name": "Test Contact",
            "email": "test@example.com",
            "phone": "070-123 45 67",
            "alias": "testalias",
            "street": "Test Street 1",
            "postal_code": "123 45",
            "city": "Test City",
            "country_code": "SE",
            "comment": "Test comment",
            "is_naj_member": True,
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_contact_form_invalid_email(self):
        """Testa ContactForm med ogiltig e-post"""
        form_data = {
            "name": "Test Contact",
            "email": "invalid-email",
            "phone": "070-123 45 67",
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_contact_form_missing_required_fields(self):
        """Testa ContactForm utan obligatoriska fält"""
        form_data = {"email": "test@example.com"}
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_contact_form_country_code_choices(self):
        """Testa att ContactForm har rätt landskoder"""
        form = ContactForm()
        country_choices = form.fields["country_code"].choices
        # Kontrollera att vissa förväntade länder finns
        country_codes = [choice[0] for choice in country_choices]
        self.assertIn("SE", country_codes)
        self.assertIn("FI", country_codes)
        self.assertIn("NO", country_codes)
        self.assertIn("DK", country_codes)

    def test_contact_form_optional_fields(self):
        """Testa ContactForm med bara obligatoriska fält"""
        form_data = {"name": "Test Contact", "email": "test@example.com"}
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())


class MeasurementFormTest(TestCase):
    def setUp(self):
        self.measurement_type = MeasurementType.objects.create(
            name="Längd", unit="mm", is_active=True
        )
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe", status="KÖPT"
        )

    def test_measurement_form_valid_data(self):
        """Testa MeasurementForm med giltig data"""
        form_data = {
            "name": "Längd",
            "value": "100.50",
            "unit": "mm",
            "unit_option": "mm",
        }
        form = MeasurementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_measurement_form_custom_name(self):
        """Testa MeasurementForm med eget måttnamn"""
        form_data = {
            "name": "Övrigt",
            "custom_name": "Eget mått",
            "value": "50.00",
            "unit": "mm",
            "unit_option": "mm",
        }
        form = MeasurementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_measurement_form_invalid_value(self):
        """Testa MeasurementForm med ogiltigt värde"""
        form_data = {
            "name": "Längd",
            "value": "invalid_value",
            "unit": "mm",
            "unit_option": "mm",
        }
        form = MeasurementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("value", form.errors)

    def test_measurement_form_missing_value(self):
        """Testa MeasurementForm utan värde"""
        form_data = {"name": "Längd", "unit": "mm", "unit_option": "mm"}
        form = MeasurementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("value", form.errors)

    def test_measurement_form_clean_method(self):
        """Testa MeasurementForm clean-metod"""
        form_data = {
            "name": "Övrigt",
            "custom_name": "Eget mått",
            "value": "50.00",
            "unit": "mm",
            "unit_option": "mm",
        }
        form = MeasurementForm(data=form_data)
        if form.is_valid():
            cleaned_data = form.clean()
            self.assertEqual(cleaned_data["name"], "Eget mått")

    def test_measurement_form_unit_mapping(self):
        """Testa MeasurementForm enhetsmappning"""
        form_data = {"name": "Längd", "value": "100.00", "unit_option": "gram"}
        form = MeasurementForm(data=form_data)
        if form.is_valid():
            cleaned_data = form.clean()
            self.assertEqual(cleaned_data["unit"], "gram")

    def test_measurement_form_custom_unit(self):
        """Testa MeasurementForm med egen enhet"""
        form_data = {
            "name": "Längd",
            "value": "100.00",
            "unit_option": "ovrig",
            "unit": "custom_unit",
        }
        form = MeasurementForm(data=form_data)
        if form.is_valid():
            cleaned_data = form.clean()
            self.assertEqual(cleaned_data["unit"], "custom_unit")


class MultipleFileFieldTest(TestCase):
    def test_multiple_file_field_clean_empty(self):
        """Testa MultipleFileField clean med tom data"""
        from axes.forms import MultipleFileField
        from django.core.files.uploadedfile import SimpleUploadedFile

        field = MultipleFileField()
        cleaned_data = field.clean([])
        self.assertEqual(cleaned_data, [])

    def test_multiple_file_field_clean_single_file(self):
        """Testa MultipleFileField clean med en fil"""
        from axes.forms import MultipleFileField
        from django.core.files.uploadedfile import SimpleUploadedFile

        field = MultipleFileField()
        test_file = SimpleUploadedFile(
            "test.jpg", b"test content", content_type="image/jpeg"
        )
        cleaned_data = field.clean([test_file])
        self.assertEqual(len(cleaned_data), 1)
        self.assertEqual(cleaned_data[0].name, "test.jpg")

    def test_multiple_file_field_clean_multiple_files(self):
        """Testa MultipleFileField clean med flera filer"""
        from axes.forms import MultipleFileField
        from django.core.files.uploadedfile import SimpleUploadedFile

        field = MultipleFileField()
        test_file1 = SimpleUploadedFile(
            "test1.jpg", b"test content 1", content_type="image/jpeg"
        )
        test_file2 = SimpleUploadedFile(
            "test2.jpg", b"test content 2", content_type="image/jpeg"
        )
        cleaned_data = field.clean([test_file1, test_file2])
        self.assertEqual(len(cleaned_data), 2)
        self.assertEqual(cleaned_data[0].name, "test1.jpg")
        self.assertEqual(cleaned_data[1].name, "test2.jpg")


class AxeFormTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.parent_manufacturer = Manufacturer.objects.create(
            name="Parent Manufacturer"
        )
        self.child_manufacturer = Manufacturer.objects.create(
            name="Child Manufacturer", parent=self.parent_manufacturer
        )

    def test_axe_form_valid_data(self):
        """Testa AxeForm med giltig data"""
        form_data = {
            "manufacturer": str(self.manufacturer.id),
            "model": "Test Axe",
            "comment": "Test comment",
            "status": "KÖPT",
            "contact_search": "",
            "contact_name": "New Contact",
            "contact_email": "new@example.com",
            "transaction_price": "100.00",
            "transaction_date": timezone.now().date(),
            "platform_search": "",
            "platform_name": "New Platform",
        }
        form = AxeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_axe_form_missing_manufacturer(self):
        """Testa AxeForm utan tillverkare"""
        form_data = {"model": "Test Axe", "status": "KÖPT"}
        form = AxeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("manufacturer", form.errors)

    def test_axe_form_invalid_manufacturer_id(self):
        """Testa AxeForm med ogiltigt tillverkare-ID"""
        form_data = {
            "manufacturer": "99999",  # Ogiltigt ID
            "model": "Test Axe",
            "status": "KÖPT",
        }
        form = AxeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("manufacturer", form.errors)

    def test_axe_form_hierarchical_manufacturers(self):
        """Testa AxeForm med hierarkiska tillverkare"""
        form = AxeForm()
        manufacturer_choices = form.fields["manufacturer"].choices

        # Kontrollera att alla tillverkare finns i choices
        choice_values = [choice[0] for choice in manufacturer_choices]
        # Konvertera alla till strängar för jämförelse
        choice_values_str = [str(val) for val in choice_values]
        self.assertIn(str(self.manufacturer.id), choice_values_str)
        self.assertIn(str(self.parent_manufacturer.id), choice_values_str)
        self.assertIn(str(self.child_manufacturer.id), choice_values_str)

    def test_axe_form_clean_manufacturer(self):
        """Testa AxeForm clean_manufacturer-metod"""
        form_data = {
            "manufacturer": str(self.manufacturer.id),
            "model": "Test Axe",
            "status": "KÖPT",
        }
        form = AxeForm(data=form_data)
        if form.is_valid():
            # Testa clean_manufacturer-metoden direkt
            form.cleaned_data = {"manufacturer": str(self.manufacturer.id)}
            cleaned_manufacturer = form.clean_manufacturer()
            self.assertEqual(cleaned_manufacturer, self.manufacturer)

    def test_axe_form_contact_fields(self):
        """Testa AxeForm kontaktfält"""
        form_data = {
            "manufacturer": str(self.manufacturer.id),
            "model": "Test Axe",
            "status": "KÖPT",
            "contact_name": "New Contact",
            "contact_email": "new@example.com",
            "contact_phone": "070-123 45 67",
            "contact_alias": "newalias",
            "contact_comment": "Test comment",
            "is_naj_member": True,
            "contact_street": "Test Street 1",
            "contact_postal_code": "123 45",
            "contact_city": "Test City",
            "contact_country_code": "SE",
        }
        form = AxeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_axe_form_transaction_fields(self):
        """Testa AxeForm transaktionsfält"""
        form_data = {
            "manufacturer": str(self.manufacturer.id),
            "model": "Test Axe",
            "status": "KÖPT",
            "transaction_price": "100.00",
            "transaction_shipping": "10.00",
            "transaction_date": timezone.now().date(),
            "transaction_comment": "Test transaction",
        }
        form = AxeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_axe_form_platform_fields(self):
        """Testa AxeForm plattformsfält"""
        form_data = {
            "manufacturer": str(self.manufacturer.id),
            "model": "Test Axe",
            "status": "KÖPT",
            "platform_name": "New Platform",
            "platform_url": "https://www.example.com",
            "platform_comment": "Test platform",
        }
        form = AxeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_axe_form_invalid_transaction_price(self):
        """Testa AxeForm med ogiltigt transaktionspris"""
        form_data = {
            "manufacturer": str(self.manufacturer.id),
            "model": "Test Axe",
            "status": "KÖPT",
            "transaction_price": "invalid_price",
        }
        form = AxeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("transaction_price", form.errors)

    def test_axe_form_invalid_contact_email(self):
        """Testa AxeForm med ogiltig kontakt-e-post"""
        form_data = {
            "manufacturer": str(self.manufacturer.id),
            "model": "Test Axe",
            "status": "KÖPT",
            "contact_email": "invalid-email",
        }
        form = AxeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("contact_email", form.errors)


class BackupUploadFormTest(TestCase):
    def test_backup_upload_form_valid_zip(self):
        """Testa BackupUploadForm med giltig zip-fil"""
        from axes.forms import BackupUploadForm
        from django.core.files.uploadedfile import SimpleUploadedFile

        form_data = {}
        file_data = {
            "backup_file": SimpleUploadedFile(
                "test_backup.zip", b"test zip content", content_type="application/zip"
            )
        }
        form = BackupUploadForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid())

    def test_backup_upload_form_valid_sqlite3(self):
        """Testa BackupUploadForm med giltig sqlite3-fil"""
        from axes.forms import BackupUploadForm
        from django.core.files.uploadedfile import SimpleUploadedFile

        form_data = {}
        file_data = {
            "backup_file": SimpleUploadedFile(
                "test_backup.sqlite3",
                b"test database content",
                content_type="application/x-sqlite3",
            )
        }
        form = BackupUploadForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid())

    def test_backup_upload_form_invalid_file_type(self):
        """Testa BackupUploadForm med ogiltig filtyp"""
        from axes.forms import BackupUploadForm
        from django.core.files.uploadedfile import SimpleUploadedFile

        form_data = {}
        file_data = {
            "backup_file": SimpleUploadedFile(
                "test.txt", b"test content", content_type="text/plain"
            )
        }
        form = BackupUploadForm(data=form_data, files=file_data)
        self.assertFalse(form.is_valid())
        self.assertIn("backup_file", form.errors)

    def test_backup_upload_form_no_file(self):
        """Testa BackupUploadForm utan fil"""
        from axes.forms import BackupUploadForm

        form_data = {}
        file_data = {}
        form = BackupUploadForm(data=form_data, files=file_data)
        self.assertFalse(form.is_valid())
        self.assertIn("backup_file", form.errors)

    def test_backup_upload_form_large_file(self):
        """Testa BackupUploadForm med stor fil"""
        from axes.forms import BackupUploadForm
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Skapa en stor fil (över 2GB)
        large_content = b"x" * (2 * 1024 * 1024 * 1024 + 1)  # 2GB + 1 byte

        form_data = {}
        file_data = {
            "backup_file": SimpleUploadedFile(
                "large_backup.zip", large_content, content_type="application/zip"
            )
        }
        form = BackupUploadForm(data=form_data, files=file_data)
        self.assertFalse(form.is_valid())
        self.assertIn("backup_file", form.errors)
