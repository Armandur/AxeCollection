import pytest
from django import forms
from axes.forms import AxeForm, ContactForm, PlatformForm
from axes.models import Manufacturer, Axe, Contact, Platform
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
    assert not hasattr(axe, 'id') or axe.id is None

@pytest.mark.django_db
def test_axeform_with_comment():
    m = Manufacturer.objects.create(name="Testtillverkare")
    form = AxeForm(data={
        "manufacturer": m.id, 
        "model": "Testmodell", 
        "status": "KÖPT",
        "comment": "En testkommentar"
    })
    assert form.is_valid()
    axe = form.save(commit=False)
    assert axe.comment == "En testkommentar"

@pytest.mark.django_db
def test_axeform_edit_existing_axe():
    m = Manufacturer.objects.create(name="Testtillverkare")
    axe = Axe.objects.create(manufacturer=m, model="Gammal modell", status="KÖPT")
    form = AxeForm(instance=axe, data={
        "manufacturer": m.id,
        "model": "Ny modell",
        "status": "MOTTAGEN"
    })
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
    form = ContactForm(data={
        "name": "Test Person",
        "email": "test@example.com"
    })
    assert form.is_valid()
    contact = form.save(commit=False)
    assert contact.name == "Test Person"
    assert contact.email == "test@example.com"

@pytest.mark.django_db
def test_contactform_with_country_code():
    form = ContactForm(data={
        "name": "Test Person",
        "country_code": "SE"
    })
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
    form = PlatformForm(data={
        "name": "Test Platform",
        "color_class": "bg-success"
    })
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