from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from axes.middleware import _thread_locals
from axes.models import Axe, AuditLog, Contact, Manufacturer
from axes.signals import audit_post_save


class AuditLogSignalTest(TestCase):
    """Tester för att AuditLog fylls i korrekt av signal-handlers i
    axes/signals.py vid skapande, ändring och borttagning."""

    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(name="Testtillverkare")

    def test_create_axe_logs_create(self):
        axe = Axe.objects.create(manufacturer=self.manufacturer, model="Testmodell")

        logs = AuditLog.objects.filter(model_name="Axe", object_id=str(axe.pk))
        self.assertEqual(logs.count(), 1)
        log = logs.first()
        self.assertEqual(log.action, "CREATE")
        self.assertEqual(log.changes, {})

    def test_update_axe_logs_update_with_diff(self):
        axe = Axe.objects.create(manufacturer=self.manufacturer, model="Testmodell")

        axe.model = "Nytt modellnamn"
        axe.save()

        logs = AuditLog.objects.filter(
            model_name="Axe", object_id=str(axe.pk), action="UPDATE"
        )
        self.assertEqual(logs.count(), 1)
        log = logs.first()
        self.assertIn("model", log.changes)
        self.assertEqual(log.changes["model"], ["Testmodell", "Nytt modellnamn"])
        # Endast det ändrade fältet ska finnas med
        self.assertEqual(len(log.changes), 1)

    def test_delete_axe_logs_delete(self):
        axe = Axe.objects.create(manufacturer=self.manufacturer, model="Testmodell")
        axe_id = axe.pk
        axe_repr = str(axe)

        axe.delete()

        logs = AuditLog.objects.filter(
            model_name="Axe", object_id=str(axe_id), action="DELETE"
        )
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().object_repr, axe_repr)

    def test_user_captured_via_thread_local(self):
        user = User.objects.create_user(username="testare", password="pass1234")
        _thread_locals.user = user
        try:
            axe = Axe.objects.create(
                manufacturer=self.manufacturer, model="Med användare"
            )
        finally:
            _thread_locals.user = None

        log = AuditLog.objects.get(
            model_name="Axe", object_id=str(axe.pk), action="CREATE"
        )
        self.assertEqual(log.user, user)

    def test_user_captured_via_real_view_request(self):
        """End-to-end: en inloggad användare skapar en kontakt via en
        riktig vy, och AuditLog ska fånga rätt användare via
        CurrentUserMiddleware."""
        user = User.objects.create_user(username="klientanvandare", password="pass1234")
        self.client.force_login(user)

        response = self.client.post(
            reverse("contact_create"),
            {
                "name": "Ny kontakt",
                "email": "",
                "phone": "",
                "alias": "",
                "street": "",
                "postal_code": "",
                "city": "",
                "country": "",
                "country_code": "",
                "comment": "",
            },
        )
        self.assertEqual(response.status_code, 302)

        contact = Contact.objects.get(name="Ny kontakt")
        log = AuditLog.objects.get(
            model_name="Contact", object_id=str(contact.pk), action="CREATE"
        )
        self.assertEqual(log.user, user)

    def test_raw_save_is_not_logged(self):
        """Sparningar med raw=True (t.ex. loaddata/fixtures) ska inte loggas."""
        axe = Axe(manufacturer=self.manufacturer, model="Fixture-yxa")
        # Sätt pk manuellt så create-flaggan inte styr utfallet
        axe.save()
        count_before = AuditLog.objects.count()

        audit_post_save(sender=Axe, instance=axe, created=False, raw=True)

        self.assertEqual(AuditLog.objects.count(), count_before)
