import os
import csv
from django.core.management.base import BaseCommand
from axes.models import (
    Axe,
    Manufacturer,
    Contact,
    Platform,
    Transaction,
    Measurement,
    AxeImage,
    ManufacturerLink,
)
from django.conf import settings

EXPORT_DIR = os.path.join(settings.BASE_DIR, "exported_csv")


class Command(BaseCommand):
    help = "Exportera data till CSV-filer för enklare samarbete och backup."

    def clean_text(self, text):
        """Rensa text från radbrytningar och extra whitespace för säker CSV-export"""
        if text is None:
            return ""
        # Ersätt radbrytningar med mellanslag och rensa extra whitespace
        return " ".join(str(text).replace("\n", " ").replace("\r", " ").split())

    def handle(self, *args, **options):
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)
        self.export_manufacturers()
        self.export_contacts()
        self.export_platforms()
        self.export_axes()
        self.export_transactions()
        self.export_measurements()
        self.export_axeimages()
        self.export_manufacturerlinks()
        self.export_manufacturerimages()
        self.stdout.write(
            self.style.SUCCESS("Export klar! Filer finns i exported_csv/")
        )

    def export_manufacturers(self):
        with open(
            os.path.join(EXPORT_DIR, "Manufacturer.csv"),
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "comment"])
            for m in Manufacturer.objects.all():
                writer.writerow([m.id, m.name, self.clean_text(m.information)])

    def export_contacts(self):
        with open(
            os.path.join(EXPORT_DIR, "Kontakt.csv"), "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "id",
                    "name",
                    "email",
                    "phone",
                    "alias",
                    "street",
                    "postal_code",
                    "city",
                    "country",
                    "comment",
                    "is_naj_member",
                ]
            )
            for c in Contact.objects.all():
                writer.writerow(
                    [
                        c.id,
                        c.name,
                        c.email or "",
                        c.phone or "",
                        c.alias or "",
                        c.street or "",
                        c.postal_code or "",
                        c.city or "",
                        c.country or "",
                        self.clean_text(c.comment),
                        int(c.is_naj_member),
                    ]
                )

    def export_platforms(self):
        with open(
            os.path.join(EXPORT_DIR, "Platform.csv"), "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name"])
            for p in Platform.objects.all():
                writer.writerow([p.id, p.name])

    def export_axes(self):
        with open(
            os.path.join(EXPORT_DIR, "Axe.csv"), "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow(
                ["id", "manufacturer_id", "manufacturer_name", "model", "comment"]
            )
            for a in Axe.objects.select_related("manufacturer").all():
                writer.writerow(
                    [
                        a.id,
                        a.manufacturer.id if a.manufacturer else "",
                        a.manufacturer.name if a.manufacturer else "",
                        a.model,
                        self.clean_text(a.comment),
                    ]
                )

    def export_transactions(self):
        with open(
            os.path.join(EXPORT_DIR, "Transaction.csv"),
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "id",
                    "axe_id",
                    "axe_model",
                    "contact_id",
                    "contact_name",
                    "platform_id",
                    "platform_name",
                    "transaction_date",
                    "type",
                    "price",
                    "shipping_cost",
                    "comment",
                ]
            )
            for t in Transaction.objects.select_related(
                "axe", "contact", "platform"
            ).all():
                writer.writerow(
                    [
                        t.id,
                        t.axe.id if t.axe else "",
                        t.axe.model if t.axe else "",
                        t.contact.id if t.contact else "",
                        t.contact.name if t.contact else "",
                        t.platform.id if t.platform else "",
                        t.platform.name if t.platform else "",
                        t.transaction_date,
                        t.type,
                        t.price,
                        t.shipping_cost,
                        self.clean_text(t.comment),
                    ]
                )

    def export_measurements(self):
        with open(
            os.path.join(EXPORT_DIR, "Measurement.csv"),
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)
            writer.writerow(["id", "axe_id", "axe_model", "name", "value", "unit"])
            for m in Measurement.objects.select_related("axe").all():
                writer.writerow(
                    [
                        m.id,
                        m.axe.id if m.axe else "",
                        m.axe.model if m.axe else "",
                        m.name,
                        m.value,
                        m.unit,
                    ]
                )

    def export_axeimages(self):
        with open(
            os.path.join(EXPORT_DIR, "AxeImage.csv"), "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow(["id", "axe_id", "axe_model", "image", "description"])
            for img in AxeImage.objects.select_related("axe").all():
                writer.writerow(
                    [
                        img.id,
                        img.axe.id if img.axe else "",
                        img.axe.model if img.axe else "",
                        os.path.basename(img.image.name) if img.image else "",
                        self.clean_text(img.description),
                    ]
                )

    def export_manufacturerlinks(self):
        with open(
            os.path.join(EXPORT_DIR, "ManufacturerLink.csv"),
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "id",
                    "manufacturer_id",
                    "manufacturer_name",
                    "title",
                    "url",
                    "link_type",
                    "description",
                    "is_active",
                    "created_at",
                    "updated_at",
                ]
            )
            for link in ManufacturerLink.objects.select_related("manufacturer").all():
                writer.writerow(
                    [
                        link.id,
                        link.manufacturer.id if link.manufacturer else "",
                        link.manufacturer.name if link.manufacturer else "",
                        link.title,
                        link.url,
                        link.link_type,
                        self.clean_text(link.description),
                        int(link.is_active),
                        link.created_at,
                        link.updated_at,
                    ]
                )

    def export_manufacturerimages(self):
        from axes.models import ManufacturerImage

        with open(
            os.path.join(EXPORT_DIR, "ManufacturerImage.csv"),
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "id",
                    "manufacturer_id",
                    "manufacturer_name",
                    "image",
                    "caption",
                    "description",
                ]
            )
            for img in ManufacturerImage.objects.select_related("manufacturer").all():
                writer.writerow(
                    [
                        img.id,
                        img.manufacturer.id if img.manufacturer else "",
                        img.manufacturer.name if img.manufacturer else "",
                        os.path.basename(img.image.name) if img.image else "",
                        self.clean_text(img.caption),
                        self.clean_text(img.description),
                    ]
                )
