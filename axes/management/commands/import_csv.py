import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from axes.models import Manufacturer, Axe, Contact, Platform, Transaction, Measurement
from decimal import Decimal
from datetime import datetime
import re
import shutil


class Command(BaseCommand):
    help = "Importera data från CSV-filer med ID-referenser"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_dir", type=str, help="Sökväg till mappen med CSV-filer"
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Rensa all data (Yxor, Kontakter, Transaktioner, etc.) innan import",
        )

    def handle(self, *args, **options):
        csv_dir = options["csv_dir"]
        reset = options.get("reset", False)

        if not os.path.exists(csv_dir):
            self.stdout.write(f"FEL: Mappen {csv_dir} finns inte!")
            return

        if reset:
            self.stdout.write("Rensar gammal data...")
            Transaction.objects.all().delete()
            Measurement.objects.all().delete()
            Axe.objects.all().delete()
            Contact.objects.all().delete()
            Platform.objects.all().delete()
            Manufacturer.objects.all().delete()
            self.stdout.write("All data från CSV-importer har raderats!")

        with transaction.atomic():
            # Skapa mappningar för ID -> objekt
            self.manufacturer_map = {}
            self.contact_map = {}
            self.platform_map = {}
            self.axe_map = {}

            # Importera i rätt ordning
            self.import_manufacturers(csv_dir)
            self.import_contacts(csv_dir)
            self.import_platforms(csv_dir)
            self.import_axes(csv_dir)
            self.import_transactions(csv_dir)
            self.import_measurements(csv_dir)
            self.import_manufacturerlinks(csv_dir)
            self.import_axeimages(csv_dir)
            self.import_manufacturerimages(csv_dir)

        self.stdout.write("SUCCESS: Import slutförd!")

    def clean_price(self, price_str):
        """Rensar prissträng från 'kr' och andra tecken"""
        if not price_str:
            return "0"
        # Ta bort 'kr', mellanslag och andra tecken, behåll bara siffror och punkt
        cleaned = re.sub(r"[^\d.-]", "", str(price_str))
        return cleaned if cleaned else "0"

    def read_csv_file(self, csv_file):
        """Läser CSV-fil med rätt kodning"""
        if not os.path.exists(csv_file):
            return None

        encodings = ["utf-8-sig", "cp1252", "latin-1", "utf-8"]

        for encoding in encodings:
            try:
                with open(csv_file, "r", encoding=encoding) as file:
                    file_content = file.read()
                return file_content.splitlines()
            except UnicodeDecodeError:
                continue

        self.stdout.write(f"Kunde inte läsa {csv_file} med någon kodning")
        return None

    def import_manufacturers(self, csv_dir):
        csv_file = os.path.join(csv_dir, "Tillverkare.csv")
        lines = self.read_csv_file(csv_file)
        if not lines:
            return

        reader = csv.reader(lines)
        next(reader, None)  # Hoppa över header
        for row in reader:
            if len(row) >= 2:
                manufacturer_id = int(row[0])
                name = row[1].strip('"')
                comment = row[2].strip('"') if len(row) > 2 and row[2] else ""

                manufacturer = Manufacturer.objects.create(
                    id=manufacturer_id, name=name, comment=comment
                )
                self.manufacturer_map[manufacturer_id] = manufacturer

                self.stdout.write(f"Skapade tillverkare: {manufacturer.name}")

    def import_contacts(self, csv_dir):
        csv_file = os.path.join(csv_dir, "Kontakt.csv")
        lines = self.read_csv_file(csv_file)
        if not lines:
            self.stdout.write("Ingen kontaktfil hittades eller kunde läsas!")
            return

        reader = csv.reader(lines)
        next(reader, None)  # Hoppa över header
        for i, row in enumerate(reader):
            if len(row) >= 11:
                contact_id = int(row[0])
                name = row[1].strip('"') if row[1] else ""
                email = row[2].strip('"') if row[2] else ""
                phone = row[3].strip('"') if row[3] else ""
                alias = row[4].strip('"') if row[4] else ""
                # street, postal_code, city, country = row[5:9] (ignoreras)
                comment = row[9].strip('"') if row[9] else ""
                is_member = row[10].strip('"') if row[10] else "0"
                contact = Contact.objects.create(
                    id=contact_id,
                    name=name,
                    email=email,
                    phone=phone,
                    alias=alias,
                    comment=comment,
                    is_naj_member=is_member == "1",
                )
                self.contact_map[contact_id] = contact
                self.stdout.write(f"Skapade kontakt: {contact.name}")
            else:
                self.stdout.write(f"Hoppar över rad {i+1} (för få kolumner)")

    def import_platforms(self, csv_dir):
        csv_file = os.path.join(csv_dir, "Plattform.csv")
        lines = self.read_csv_file(csv_file)
        if not lines:
            return

        reader = csv.reader(lines)
        next(reader, None)  # Hoppa över header
        for row in reader:
            if len(row) >= 2:
                platform_id = int(row[0])
                name = row[1].strip('"')

                platform = Platform.objects.create(id=platform_id, name=name)
                self.platform_map[platform_id] = platform

                self.stdout.write(f"Skapade plattform: {platform.name}")

    def import_axes(self, csv_dir):
        csv_file = os.path.join(csv_dir, "Yxa.csv")
        lines = self.read_csv_file(csv_file)
        if not lines:
            return

        reader = csv.reader(lines)
        next(reader, None)  # Hoppa över header
        for row in reader:
            if len(row) >= 5:
                axe_id = int(row[0])
                manufacturer_id = int(row[1]) if row[1] else None
                # row[2] = manufacturer_name, ignoreras
                model = row[3].strip('"') if row[3] else ""
                comment = row[4].strip('"') if row[4] else ""
                # Bildimport: sista kolumnen
                image_filenames = []
                if len(row) > 5:
                    image_col = row[-1].strip('"')
                    if image_col:
                        image_filenames = [
                            img.strip() for img in image_col.split(";") if img.strip()
                        ]

                if manufacturer_id and manufacturer_id in self.manufacturer_map:
                    manufacturer = self.manufacturer_map[manufacturer_id]

                    axe = Axe.objects.create(
                        id=axe_id,
                        manufacturer=manufacturer,
                        model=model,
                        comment=comment,
                    )
                    self.axe_map[axe_id] = axe

                    self.stdout.write(f"Skapade yxa: {axe}")

                    # Skapa AxeImage-objekt för varje bild
                    from axes.models import (
                        AxeImage,
                    )  # Importera här för att undvika cirkulärt beroende

                    media_axe_dir = os.path.join("media", "axe_images")
                    if not os.path.exists(media_axe_dir):
                        os.makedirs(media_axe_dir)
                    for img_filename in image_filenames:
                        # Korrekt prefix utifrån förskjutningspunkter
                        if axe_id < 77:
                            prefix_id = axe_id
                        elif 77 <= axe_id < 146:
                            prefix_id = axe_id + 1
                        else:
                            prefix_id = axe_id + 2
                        prefixed_filename = f"{prefix_id}_{img_filename}"
                        src_path = os.path.join("exported_images", prefixed_filename)
                        dest_path = os.path.join(media_axe_dir, prefixed_filename)
                        image_field_path = os.path.join("axe_images", prefixed_filename)
                        # Kopiera bara om filen inte redan finns
                        if os.path.exists(src_path) and not os.path.exists(dest_path):
                            shutil.copy2(src_path, dest_path)
                            self.stdout.write(
                                f"  Kopierade bild: {src_path} -> {dest_path}"
                            )
                        elif not os.path.exists(src_path):
                            self.stdout.write(f"  Bild saknas: {src_path}")
                        AxeImage.objects.create(axe=axe, image=image_field_path)
                        self.stdout.write(f"  Länkade bild: {image_field_path}")
                else:
                    self.stdout.write(
                        f"Kunde inte hitta tillverkare med ID {manufacturer_id} för yxa {model}"
                    )

    def import_transactions(self, csv_dir):
        csv_file = os.path.join(csv_dir, "Transaktioner.csv")
        lines = self.read_csv_file(csv_file)
        if not lines:
            return

        reader = csv.reader(lines)
        next(reader, None)  # Hoppa över header
        for row in reader:
            if len(row) >= 8:
                transaction_id = int(row[0])
                axe_id = int(row[1]) if row[1] else None
                contact_id = int(row[2]) if len(row) > 2 and row[2] else None
                date_str = row[3] if len(row) > 3 else ""
                price_str = row[4] if len(row) > 4 else "0"
                shipping_str = row[5] if len(row) > 5 else "0"
                total_str = row[6] if len(row) > 6 else "0"
                comment = row[7].strip('"') if len(row) > 7 and row[7] else ""
                platform_id = int(row[8]) if len(row) > 8 and row[8] else None
                transaction_type = (
                    row[9].strip('"') if len(row) > 9 and row[9] else "KÖP"
                )

                try:
                    # Hitta yxa
                    if axe_id and axe_id in self.axe_map:
                        axe = self.axe_map[axe_id]
                    else:
                        self.stdout.write(f"Kunde inte hitta yxa med ID {axe_id}")
                        continue

                    # Hitta kontakt
                    contact = None
                    if contact_id and contact_id in self.contact_map:
                        contact = self.contact_map[contact_id]

                    # Hitta plattform
                    platform = None
                    if platform_id and platform_id in self.platform_map:
                        platform = self.platform_map[platform_id]

                    # Konvertera datum
                    if date_str:
                        # Hantera olika datumformat
                        date_str = date_str.split()[0]  # Ta bara datumdelen
                        transaction_date = datetime.strptime(
                            date_str, "%Y-%m-%d"
                        ).date()
                    else:
                        transaction_date = datetime.now().date()

                    # Konvertera priser
                    price = Decimal(self.clean_price(price_str))
                    shipping_cost = Decimal(self.clean_price(shipping_str))

                    # Bestäm transaktionstyp
                    if "Försäljning" in transaction_type or "SÄLJ" in transaction_type:
                        trans_type = "SÄLJ"
                    else:
                        trans_type = "KÖP"

                    # Skapa transaktion
                    transaction = Transaction.objects.create(
                        id=transaction_id,
                        axe=axe,
                        contact=contact,
                        platform=platform,
                        transaction_date=transaction_date,
                        type=trans_type,
                        price=abs(price),  # Ta absolutvärde
                        shipping_cost=abs(shipping_cost),
                        comment=comment,
                    )
                    self.stdout.write(f"Skapade transaktion: {transaction}")

                except Exception as e:
                    self.stdout.write(
                        f"Fel vid import av transaktion {transaction_id}: {e}"
                    )

    def import_measurements(self, csv_dir):
        csv_file = os.path.join(csv_dir, "Mått.csv")
        lines = self.read_csv_file(csv_file)
        if not lines:
            return

        reader = csv.reader(lines)
        next(reader, None)  # Hoppa över header
        for row in reader:
            if len(row) >= 5:
                measurement_id = int(row[0])
                axe_id = int(row[1]) if row[1] else None
                value_str = row[2] if len(row) > 2 else "0"
                name = row[3].strip('"') if len(row) > 3 and row[3] else ""
                unit = row[4].strip('"') if len(row) > 4 and row[4] else ""

                try:
                    # Hitta yxa
                    if axe_id and axe_id in self.axe_map:
                        axe = self.axe_map[axe_id]
                    else:
                        self.stdout.write(
                            f"Kunde inte hitta yxa med ID {axe_id} för mätning"
                        )
                        continue

                    # Konvertera värde
                    value = (
                        Decimal(value_str.replace(",", "."))
                        if value_str
                        else Decimal("0")
                    )

                    measurement = Measurement.objects.create(
                        id=measurement_id, axe=axe, name=name, value=value, unit=unit
                    )
                    self.stdout.write(f"Skapade mätning: {measurement}")

                except Exception as e:
                    self.stdout.write(
                        f"Fel vid import av mätning {measurement_id}: {e}"
                    )

    def import_manufacturerlinks(self, csv_dir):
        from axes.models import ManufacturerLink

        csv_file = os.path.join(csv_dir, "ManufacturerLink.csv")
        lines = self.read_csv_file(csv_file)
        if not lines:
            return
        reader = csv.reader(lines)
        next(reader, None)  # Hoppa över header
        for row in reader:
            if len(row) >= 3:
                link_id = int(row[0])
                manufacturer_id = int(row[1]) if row[1] else None
                title = row[2].strip('"') if len(row) > 2 and row[2] else ""
                url = row[3].strip('"') if len(row) > 3 and row[3] else ""
                link_type = row[4].strip('"') if len(row) > 4 and row[4] else ""
                description = row[5].strip('"') if len(row) > 5 and row[5] else ""
                is_active = bool(int(row[6])) if len(row) > 6 and row[6] else True
                # created_at och updated_at kan hoppas över eller sättas till nu
                manufacturer = self.manufacturer_map.get(manufacturer_id)
                if manufacturer:
                    ManufacturerLink.objects.create(
                        id=link_id,
                        manufacturer=manufacturer,
                        title=title,
                        url=url,
                        link_type=link_type,
                        description=description,
                        is_active=is_active,
                    )
                    self.stdout.write(f"Skapade ManufacturerLink: {title}")

    def import_axeimages(self, csv_dir):
        from axes.models import AxeImage

        csv_file = os.path.join(csv_dir, "AxeImage.csv")
        lines = self.read_csv_file(csv_file)
        if not lines:
            return
        reader = csv.reader(lines)
        next(reader, None)  # Hoppa över header
        media_axe_dir = os.path.join("media", "axe_images")
        if not os.path.exists(media_axe_dir):
            os.makedirs(media_axe_dir)
        for row in reader:
            if len(row) >= 3:
                img_id = int(row[0])
                axe_id = int(row[1]) if row[1] else None
                img_filename = row[2].strip('"') if len(row) > 2 and row[2] else ""
                if axe_id and axe_id in self.axe_map and img_filename:
                    axe = self.axe_map[axe_id]
                    src_path = os.path.join(csv_dir, "axe_images", img_filename)
                    dest_path = os.path.join(media_axe_dir, img_filename)
                    image_field_path = os.path.join("axe_images", img_filename)
                    if os.path.exists(src_path) and not os.path.exists(dest_path):
                        shutil.copy2(src_path, dest_path)
                        self.stdout.write(
                            f"  Kopierade bild: {src_path} -> {dest_path}"
                        )
                    elif not os.path.exists(src_path):
                        self.stdout.write(f"  Bild saknas: {src_path}")
                    AxeImage.objects.create(id=img_id, axe=axe, image=image_field_path)
                    self.stdout.write(f"  Länkade bild: {image_field_path}")

    def import_manufacturerimages(self, csv_dir):
        from axes.models import ManufacturerImage

        csv_file = os.path.join(csv_dir, "ManufacturerImage.csv")
        lines = self.read_csv_file(csv_file)
        if not lines:
            return
        reader = csv.reader(lines)
        next(reader, None)  # Hoppa över header
        media_manuf_dir = os.path.join("media", "manufacturer_images")
        if not os.path.exists(media_manuf_dir):
            os.makedirs(media_manuf_dir)
        for row in reader:
            if len(row) >= 4:
                img_id = int(row[0])
                manufacturer_id = int(row[1]) if row[1] else None
                img_filename = row[3].strip('"') if len(row) > 3 and row[3] else ""
                caption = row[4].strip('"') if len(row) > 4 and row[4] else ""
                description = row[5].strip('"') if len(row) > 5 and row[5] else ""
                if (
                    manufacturer_id
                    and manufacturer_id in self.manufacturer_map
                    and img_filename
                ):
                    manufacturer = self.manufacturer_map[manufacturer_id]
                    src_path = os.path.join(
                        csv_dir, "manufacturer_images", img_filename
                    )
                    dest_path = os.path.join(media_manuf_dir, img_filename)
                    image_field_path = os.path.join("manufacturer_images", img_filename)
                    if os.path.exists(src_path) and not os.path.exists(dest_path):
                        shutil.copy2(src_path, dest_path)
                        self.stdout.write(
                            f"  Kopierade tillverkarbild: {src_path} -> {dest_path}"
                        )
                    elif not os.path.exists(src_path):
                        self.stdout.write(f"  Tillverkarbild saknas: {src_path}")
                    ManufacturerImage.objects.create(
                        id=img_id,
                        manufacturer=manufacturer,
                        image=image_field_path,
                        caption=caption,
                        description=description,
                    )
                    self.stdout.write(f"  Länkade tillverkarbild: {image_field_path}")
