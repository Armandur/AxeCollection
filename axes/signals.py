"""Signal-handlers för ändringsloggen (AuditLog).

Fångar skapande, ändring och borttagning av de åtta kärnmodellerna via
pre_save/post_save/post_delete, oavsett om ändringen görs via vyer, admin
eller Django-shell. AuditLog självt registreras aldrig, för att undvika
oändlig loop.

En bugg i loggningen får aldrig hindra den riktiga spara/ta bort-operationen,
så varje handler är helt inkapslad i try/except.
"""

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db.models.signals import post_delete, post_save, pre_save

from .middleware import get_current_user
from .models import (
    Axe,
    AuditLog,
    Contact,
    Manufacturer,
    Measurement,
    Platform,
    Settings,
    Stamp,
    Transaction,
)

logger = logging.getLogger(__name__)

AUDITED_MODELS = [
    Axe,
    Manufacturer,
    Contact,
    Transaction,
    Stamp,
    Settings,
    Platform,
    Measurement,
]


def _serialize_value(value):
    """Gör ett fältvärde JSON-säkert för lagring i AuditLog.changes."""
    try:
        if value is None:
            return None
        if isinstance(value, (Decimal, date, UUID)):
            return str(value)
        if isinstance(value, (str, int, float, bool)):
            return value
        return str(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return None


def _build_field_diff(old_instance, new_instance):
    """Jämför konkreta fält mellan gammal och ny instans, returnerar en
    diff-dict {fältnamn: [gammalt, nytt]} för endast de fält som ändrats."""
    diff = {}
    for field in new_instance._meta.concrete_fields:
        if getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False):
            continue
        attname = field.attname  # ger FK:s _id-fält istället för related-objektet
        old_value = getattr(old_instance, attname, None)
        new_value = getattr(new_instance, attname, None)
        if old_value != new_value:
            diff[field.name] = [
                _serialize_value(old_value),
                _serialize_value(new_value),
            ]
    return diff


def _safe_repr(sender, instance):
    try:
        return str(instance)[:255]
    except Exception:
        return f"{sender.__name__} #{instance.pk}"


def _resolve_user():
    """Hämtar aktuell användare från thread-local, men bara om det är en
    faktisk inloggad User-instans (inte AnonymousUser eller None)."""
    user = get_current_user()
    if user is not None and getattr(user, "is_authenticated", False) and user.pk:
        return user
    return None


def audit_pre_save(sender, instance, **kwargs):
    try:
        if not instance.pk:
            instance._audit_is_create = True
            instance._audit_changes = {}
            return
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._audit_is_create = True
            instance._audit_changes = {}
            return
        instance._audit_is_create = False
        instance._audit_changes = _build_field_diff(old_instance, instance)
    except Exception:
        logger.exception(
            "Fel vid audit pre_save-hantering för %s",
            getattr(sender, "__name__", sender),
        )


def audit_post_save(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        # Fixtures/loaddata - logga inte
        return
    try:
        is_create = created or getattr(instance, "_audit_is_create", False)
        action = "CREATE" if is_create else "UPDATE"
        changes = {} if is_create else getattr(instance, "_audit_changes", {})
        AuditLog.objects.create(
            user=_resolve_user(),
            action=action,
            model_name=sender.__name__,
            object_id=str(instance.pk),
            object_repr=_safe_repr(sender, instance),
            changes=changes,
        )
    except Exception:
        logger.exception(
            "Fel vid audit post_save-hantering för %s",
            getattr(sender, "__name__", sender),
        )
    finally:
        # Städa upp temporära attribut oavsett utfall
        if hasattr(instance, "_audit_changes"):
            del instance._audit_changes
        if hasattr(instance, "_audit_is_create"):
            del instance._audit_is_create


def audit_post_delete(sender, instance, **kwargs):
    try:
        AuditLog.objects.create(
            user=_resolve_user(),
            action="DELETE",
            model_name=sender.__name__,
            object_id=str(instance.pk),
            object_repr=_safe_repr(sender, instance),
            changes={},
        )
    except Exception:
        logger.exception(
            "Fel vid audit post_delete-hantering för %s",
            getattr(sender, "__name__", sender),
        )


def _register_audit_signals():
    for model in AUDITED_MODELS:
        name = model.__name__
        pre_save.connect(
            audit_pre_save, sender=model, dispatch_uid=f"audit_pre_save_{name}"
        )
        post_save.connect(
            audit_post_save, sender=model, dispatch_uid=f"audit_post_save_{name}"
        )
        post_delete.connect(
            audit_post_delete, sender=model, dispatch_uid=f"audit_post_delete_{name}"
        )


_register_audit_signals()
