import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from axes.models import (
    Manufacturer, Axe, Contact, Platform, Transaction, 
    MeasurementType, MeasurementTemplate, Measurement,
    ManufacturerImage, ManufacturerLink, Settings
)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')


class ManufacturerFactory(DjangoModelFactory):
    class Meta:
        model = Manufacturer
    
    name = factory.Sequence(lambda n: f'Tillverkare {n}')
    information = factory.Faker('text', max_nb_chars=200)
    manufacturer_type = 'TILLVERKARE'


class SubManufacturerFactory(DjangoModelFactory):
    class Meta:
        model = Manufacturer
    
    name = factory.Sequence(lambda n: f'Undertillverkare {n}')
    information = factory.Faker('text', max_nb_chars=200)
    manufacturer_type = 'SMED'
    parent = factory.SubFactory(ManufacturerFactory)


class ContactFactory(DjangoModelFactory):
    class Meta:
        model = Contact
    
    name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    city = factory.Faker('city')
    country = factory.Faker('country')
    country_code = factory.Faker('country_code', representation='alpha-2')


class PlatformFactory(DjangoModelFactory):
    class Meta:
        model = Platform
    
    name = factory.Sequence(lambda n: f'Plattform {n}')
    color_class = 'bg-primary'


class AxeFactory(DjangoModelFactory):
    class Meta:
        model = Axe
    
    manufacturer = factory.SubFactory(ManufacturerFactory)
    model = factory.Sequence(lambda n: f'Modell {n}')
    comment = factory.Faker('text', max_nb_chars=100)
    status = 'KÖPT'


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = Transaction
    
    axe = factory.SubFactory(AxeFactory)
    contact = factory.SubFactory(ContactFactory)
    platform = factory.SubFactory(PlatformFactory)
    transaction_date = factory.Faker('date')
    type = 'KÖP'
    price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    shipping_cost = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)


class MeasurementTypeFactory(DjangoModelFactory):
    class Meta:
        model = MeasurementType
    
    name = factory.Sequence(lambda n: f'Måtttyp {n}')
    unit = factory.Iterator(['mm', 'gram', 'cm', 'kg'])
    description = factory.Faker('text', max_nb_chars=100)


class MeasurementTemplateFactory(DjangoModelFactory):
    class Meta:
        model = MeasurementTemplate
    
    name = factory.Sequence(lambda n: f'Mall {n}')
    description = factory.Faker('text', max_nb_chars=100)


class MeasurementFactory(DjangoModelFactory):
    class Meta:
        model = Measurement
    
    axe = factory.SubFactory(AxeFactory)
    name = factory.Sequence(lambda n: f'Mått {n}')
    value = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    unit = factory.Iterator(['mm', 'gram', 'cm', 'kg'])


class SettingsFactory(DjangoModelFactory):
    class Meta:
        model = Settings
    
    show_contacts_public = False
    show_prices_public = True
    show_platforms_public = True
    show_only_received_axes_public = False
    site_title = "AxeCollection Test" 