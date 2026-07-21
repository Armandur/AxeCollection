"""Lätta objekt-factories för tester.

Ersätter tunga `generate_test_data`-anrop i setUp. Varje funktion skapar
ETT minimalt giltigt objekt och tar **kwargs för att override:a fält.
Skapa bara det testet faktiskt behöver - inte en hel genererad datamängd.
"""

from datetime import date
from decimal import Decimal

from axes.models import (
    Axe,
    Contact,
    Manufacturer,
    Measurement,
    MeasurementType,
    Platform,
    Stamp,
    Transaction,
)

_counter = {"n": 0}


def _next():
    _counter["n"] += 1
    return _counter["n"]


def make_manufacturer(**kwargs):
    kwargs.setdefault("name", f"Tillverkare {_next()}")
    return Manufacturer.objects.create(**kwargs)


def make_axe(manufacturer=None, **kwargs):
    if manufacturer is None:
        manufacturer = make_manufacturer()
    kwargs.setdefault("model", f"Modell {_next()}")
    return Axe.objects.create(manufacturer=manufacturer, **kwargs)


def make_contact(**kwargs):
    kwargs.setdefault("name", f"Kontakt {_next()}")
    return Contact.objects.create(**kwargs)


def make_platform(**kwargs):
    kwargs.setdefault("name", f"Plattform {_next()}")
    return Platform.objects.create(**kwargs)


def make_measurement_type(**kwargs):
    kwargs.setdefault("name", f"Måtttyp {_next()}")
    kwargs.setdefault("unit", "mm")
    return MeasurementType.objects.create(**kwargs)


def make_measurement(axe=None, **kwargs):
    if axe is None:
        axe = make_axe()
    kwargs.setdefault("name", "Längd")
    kwargs.setdefault("value", Decimal("100"))
    kwargs.setdefault("unit", "mm")
    return Measurement.objects.create(axe=axe, **kwargs)


def make_transaction(axe=None, **kwargs):
    if axe is None:
        axe = make_axe()
    kwargs.setdefault("transaction_date", date(2024, 1, 15))
    kwargs.setdefault("type", "KÖP")
    kwargs.setdefault("price", Decimal("500"))
    return Transaction.objects.create(axe=axe, **kwargs)


def make_stamp(manufacturer=None, **kwargs):
    if manufacturer is None:
        manufacturer = make_manufacturer()
    kwargs.setdefault("name", f"Stämpel {_next()}")
    return Stamp.objects.create(manufacturer=manufacturer, **kwargs)
