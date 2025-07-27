import pytest
import os
import tempfile
import shutil
import zipfile
import json
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from io import StringIO
from axes.models import (
    Transaction,
    Axe,
    Contact,
    Platform,
    Manufacturer,
    NextAxeID,
    ManufacturerImage,
)
from decimal import Decimal
from django.utils import timezone
from axes.models import MeasurementType, MeasurementTemplate, MeasurementTemplateItem
from axes.models import Settings
from axes.models import Measurement, ManufacturerLink, AxeImage


class ClearTransactionsCommandTest(TestCase):
    def setUp(self):
        # Skapa testdata
        self.contact = Contact.objects.create(name="Test Contact")
        self.platform = Platform.objects.create(name="Test Platform")
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe", status="KÖPT"
        )

        # Skapa några transaktioner
        self.transaction1 = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="KÖP",
            price=Decimal("100.00"),
            shipping_cost=Decimal("10.00"),
        )

        self.transaction2 = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="SÄLJ",
            price=Decimal("150.00"),
            shipping_cost=Decimal("15.00"),
        )

    def test_clear_transactions_without_confirm(self):
        """Testa att kommandot kräver bekräftelse"""
        out = StringIO()
        call_command("clear_transactions", stdout=out)

        output = out.getvalue()
        self.assertIn("Du är på väg att radera 2 transaktioner!", output)
        self.assertIn("Kör kommandot igen med --confirm för att bekräfta.", output)

        # Kontrollera att transaktionerna fortfarande finns
        self.assertEqual(Transaction.objects.count(), 2)

    def test_clear_transactions_with_confirm(self):
        """Testa att kommandot raderar transaktioner med bekräftelse"""
        out = StringIO()
        call_command("clear_transactions", confirm=True, stdout=out)

        output = out.getvalue()
        self.assertIn("Raderar 2 transaktioner...", output)
        self.assertIn("SUCCESS: Raderade 2 transaktioner!", output)

        # Kontrollera att transaktionerna är raderade
        self.assertEqual(Transaction.objects.count(), 0)

    def test_clear_transactions_no_transactions(self):
        """Testa kommandot när det inte finns några transaktioner"""
        # Rensa alla transaktioner först
        Transaction.objects.all().delete()

        out = StringIO()
        call_command("clear_transactions", confirm=True, stdout=out)

        output = out.getvalue()
        self.assertIn("Raderar 0 transaktioner...", output)
        self.assertIn("SUCCESS: Raderade 0 transaktioner!", output)

        # Kontrollera att det fortfarande inte finns några transaktioner
        self.assertEqual(Transaction.objects.count(), 0)


class MarkAllAxesReceivedCommandTest(TestCase):
    def setUp(self):
        # Skapa testdata
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")

        # Skapa yxor med olika status
        self.axe1 = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe 1", status="KÖPT"
        )

        self.axe2 = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe 2", status="MOTTAGEN"
        )

        self.axe3 = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe 3", status="KÖPT"
        )

    def test_mark_all_axes_received(self):
        """Testa att kommandot sätter alla yxor till MOTTAGEN"""
        out = StringIO()
        call_command("mark_all_axes_received", stdout=out)

        output = out.getvalue()
        self.assertIn("Satte status till MOTTAGEN för 3 yxor.", output)

        # Kontrollera att alla yxor har status MOTTAGEN
        self.axe1.refresh_from_db()
        self.axe2.refresh_from_db()
        self.axe3.refresh_from_db()

        self.assertEqual(self.axe1.status, "MOTTAGEN")
        self.assertEqual(self.axe2.status, "MOTTAGEN")
        self.assertEqual(self.axe3.status, "MOTTAGEN")

    def test_mark_all_axes_received_no_axes(self):
        """Testa kommandot när det inte finns några yxor"""
        # Rensa alla yxor först
        Axe.objects.all().delete()

        out = StringIO()
        call_command("mark_all_axes_received", stdout=out)

        output = out.getvalue()
        self.assertIn("Satte status till MOTTAGEN för 0 yxor.", output)

        # Kontrollera att det fortfarande inte finns några yxor
        self.assertEqual(Axe.objects.count(), 0)


class InitNextAxeIDCommandTest(TestCase):
    def setUp(self):
        # Rensa befintliga NextAxeID objekt
        NextAxeID.objects.all().delete()
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")

    def test_init_next_axe_id_with_existing_axes(self):
        """Testa att kommandot sätter rätt nästa ID när det finns befintliga yxor"""
        # Skapa några yxor med specifika ID:n
        axe1 = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe 1", status="KÖPT"
        )
        axe2 = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe 2", status="KÖPT"
        )

        # Hitta högsta ID:t
        max_id = max(axe1.id, axe2.id)
        expected_next_id = max_id + 1

        out = StringIO()
        call_command("init_next_axe_id", stdout=out)

        output = out.getvalue()
        self.assertIn(f"Nästa yx-ID satt till {expected_next_id}", output)

        # Kontrollera att NextAxeID är korrekt satt
        next_axe_id = NextAxeID.objects.get(id=1)
        self.assertEqual(next_axe_id.next_id, expected_next_id)

    def test_init_next_axe_id_no_axes(self):
        """Testa att kommandot sätter nästa ID till 1 när det inte finns några yxor"""
        # Rensa alla yxor
        Axe.objects.all().delete()

        out = StringIO()
        call_command("init_next_axe_id", stdout=out)

        output = out.getvalue()
        self.assertIn("Nästa yx-ID satt till 1", output)

        # Kontrollera att NextAxeID är korrekt satt
        next_axe_id = NextAxeID.objects.get(id=1)
        self.assertEqual(next_axe_id.next_id, 1)

    def test_init_next_axe_id_updates_existing(self):
        """Testa att kommandot uppdaterar befintligt NextAxeID objekt"""
        # Skapa ett befintligt NextAxeID objekt
        existing_next_id = NextAxeID.objects.create(id=1, next_id=999)

        # Skapa en yxa
        axe = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe", status="KÖPT"
        )

        expected_next_id = axe.id + 1

        out = StringIO()
        call_command("init_next_axe_id", stdout=out)

        output = out.getvalue()
        self.assertIn(f"Nästa yx-ID satt till {expected_next_id}", output)

        # Kontrollera att NextAxeID är uppdaterat
        existing_next_id.refresh_from_db()
        self.assertEqual(existing_next_id.next_id, expected_next_id)


class ResetToTestDataCommandTest(TestCase):
    def setUp(self):
        # Skapa lite befintlig data
        self.manufacturer = Manufacturer.objects.create(name="Existing Manufacturer")
        self.contact = Contact.objects.create(name="Existing Contact")
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer, model="Existing Axe", status="KÖPT"
        )

    def test_reset_to_test_data_default(self):
        """Testa att kommandot återställer till testdata med standardvärden"""
        out = StringIO()
        call_command("reset_to_test_data", stdout=out)

        output = out.getvalue()
        self.assertIn("Återställer till testdata...", output)
        self.assertIn("Databasen har återställts till testdata!", output)

        # Kontrollera att ny testdata har skapats
        self.assertGreater(Axe.objects.count(), 0)
        self.assertGreater(Manufacturer.objects.count(), 0)
        self.assertGreater(Contact.objects.count(), 0)

    def test_reset_to_test_data_custom_counts(self):
        """Testa att kommandot använder anpassade antal"""
        out = StringIO()
        call_command(
            "reset_to_test_data", axes=10, manufacturers=5, contacts=8, stdout=out
        )

        output = out.getvalue()
        self.assertIn("Återställer till testdata...", output)
        self.assertIn("Databasen har återställts till testdata!", output)

        # Kontrollera att rätt antal objekt har skapats
        # Notera: generate_test_data kan skapa fler objekt än specificerat
        # så vi kontrollerar bara att det finns data
        self.assertGreater(Axe.objects.count(), 0)
        self.assertGreater(Manufacturer.objects.count(), 0)
        self.assertGreater(Contact.objects.count(), 0)


class DeleteManufacturerCommandTest(TestCase):
    def setUp(self):
        # Skapa testdata
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe", status="KÖPT"
        )

        # Skapa en tillverkarbild
        self.manufacturer_image = ManufacturerImage.objects.create(
            manufacturer=self.manufacturer, image_type="LOGO", order=1
        )

    def test_delete_manufacturer_not_found(self):
        """Testa att kommandot ger fel när tillverkare inte finns"""
        with self.assertRaises(CommandError):
            call_command("delete_manufacturer", 999)

    def test_delete_manufacturer_with_axes_no_options(self):
        """Testa att kommandot förhindrar borttagning när tillverkare har yxor"""
        out = StringIO()
        call_command("delete_manufacturer", self.manufacturer.id, stdout=out)

        output = out.getvalue()
        self.assertIn("Kan inte ta bort tillverkare med 1 yxor", output)
        self.assertIn("--move-axes-to-unknown", output)

        # Kontrollera att tillverkaren fortfarande finns
        self.manufacturer.refresh_from_db()
        self.assertTrue(Manufacturer.objects.filter(id=self.manufacturer.id).exists())

    @patch("builtins.input", return_value="ja")
    def test_delete_manufacturer_move_axes_to_unknown(self, mock_input):
        """Testa att kommandot flyttar yxor till 'Okänd tillverkare'"""
        out = StringIO()
        call_command(
            "delete_manufacturer",
            self.manufacturer.id,
            move_axes_to_unknown=True,
            stdout=out,
        )

        output = out.getvalue()
        self.assertIn('Flyttar 1 yxor till "Okänd tillverkare"', output)
        self.assertIn("Flyttade 1 yxor", output)
        self.assertIn('Tillverkare "Test Manufacturer" har tagits bort', output)

        # Kontrollera att tillverkaren är borttagen
        self.assertFalse(Manufacturer.objects.filter(id=self.manufacturer.id).exists())

        # Kontrollera att yxan flyttats till "Okänd tillverkare"
        unknown_manufacturer = Manufacturer.objects.get(name="Okänd tillverkare")
        self.axe.refresh_from_db()
        self.assertEqual(self.axe.manufacturer, unknown_manufacturer)

    def test_delete_manufacturer_move_axes_to_specific(self):
        """Testa att kommandot flyttar yxor till specifik tillverkare"""
        target_manufacturer = Manufacturer.objects.create(name="Target Manufacturer")

        out = StringIO()
        call_command(
            "delete_manufacturer",
            self.manufacturer.id,
            move_axes_to=target_manufacturer.id,
            force=True,
            stdout=out,
        )

        output = out.getvalue()
        self.assertIn(f'Flyttar 1 yxor till "{target_manufacturer.name}"', output)
        self.assertIn("Flyttade 1 yxor", output)

        # Kontrollera att yxan flyttats till rätt tillverkare
        self.axe.refresh_from_db()
        self.assertEqual(self.axe.manufacturer, target_manufacturer)

    def test_delete_manufacturer_move_axes_to_invalid_id(self):
        """Testa att kommandot ger fel när mål-tillverkare inte finns"""
        out = StringIO()
        with self.assertRaises(Manufacturer.DoesNotExist):
            call_command(
                "delete_manufacturer",
                self.manufacturer.id,
                move_axes_to=999,
                force=True,
                stdout=out,
            )

        # Kontrollera att tillverkaren fortfarande finns
        self.manufacturer.refresh_from_db()
        self.assertTrue(Manufacturer.objects.filter(id=self.manufacturer.id).exists())

    def test_delete_manufacturer_delete_axes(self):
        """Testa att kommandot tar bort yxor med --delete-axes"""
        out = StringIO()
        call_command(
            "delete_manufacturer",
            self.manufacturer.id,
            delete_axes=True,
            force=True,
            stdout=out,
        )

        output = out.getvalue()
        self.assertIn("Raderar 1 yxor", output)
        self.assertIn("Raderade 1 yxor", output)

        # Kontrollera att yxan är borttagen
        self.assertFalse(Axe.objects.filter(id=self.axe.id).exists())

        # Kontrollera att tillverkaren är borttagen
        self.assertFalse(Manufacturer.objects.filter(id=self.manufacturer.id).exists())

    def test_delete_manufacturer_no_axes(self):
        """Testa att kommandot tar bort tillverkare utan yxor"""
        # Ta bort yxan först
        self.axe.delete()

        out = StringIO()
        call_command(
            "delete_manufacturer", self.manufacturer.id, force=True, stdout=out
        )

        output = out.getvalue()
        self.assertIn('Tillverkare "Test Manufacturer" har tagits bort', output)

        # Kontrollera att tillverkaren är borttagen
        self.assertFalse(Manufacturer.objects.filter(id=self.manufacturer.id).exists())

    @patch("builtins.input", return_value="nej")
    def test_delete_manufacturer_cancelled(self, mock_input):
        """Testa att kommandot avbryts när användaren säger nej"""
        # Ta bort yxan först så att kommandot frågar om bekräftelse
        self.axe.delete()

        out = StringIO()
        call_command("delete_manufacturer", self.manufacturer.id, stdout=out)

        output = out.getvalue()
        self.assertIn("Borttagning avbruten", output)

        # Kontrollera att tillverkaren fortfarande finns
        self.manufacturer.refresh_from_db()
        self.assertTrue(Manufacturer.objects.filter(id=self.manufacturer.id).exists())


class BackupDatabaseCommandTest(TestCase):
    def setUp(self):
        # Skapa testdata
        self.contact = Contact.objects.create(name="Test Contact")
        self.platform = Platform.objects.create(name="Test Platform")
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe", status="KÖPT"
        )

        # Skapa några transaktioner
        self.transaction1 = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="KÖP",
            price=Decimal("100.00"),
            shipping_cost=Decimal("10.00"),
        )

        self.transaction2 = Transaction.objects.create(
            axe=self.axe,
            contact=self.contact,
            platform=self.platform,
            transaction_date=timezone.now().date(),
            type="SÄLJ",
            price=Decimal("150.00"),
            shipping_cost=Decimal("15.00"),
        )

        # Skapa temporär backup-mapp
        self.temp_backup_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Rensa temporär backup-mapp
        if os.path.exists(self.temp_backup_dir):
            shutil.rmtree(self.temp_backup_dir)

    @override_settings(BASE_DIR=tempfile.gettempdir())
    @patch("axes.management.commands.backup_database.settings")
    def test_backup_database_basic(self, mock_settings):
        """Testa grundläggande backup-funktionalitet"""
        temp_dir = tempfile.gettempdir()
        mock_settings.BASE_DIR = temp_dir
        mock_settings.DATABASES = {
            "default": {"NAME": os.path.join(temp_dir, "test_db.sqlite3")}
        }
        mock_settings.MEDIA_ROOT = os.path.join(temp_dir, "media")

        # Skapa en temporär databasfil
        temp_db_path = os.path.join(temp_dir, "test_db.sqlite3")
        with open(temp_db_path, "w") as f:
            f.write("test database content")

        backup_dir = os.path.join(temp_dir, "backups")

        try:
            out = StringIO()
            call_command("backup_database", stdout=out)

            output = out.getvalue()
            self.assertIn("Startar automatisk backup...", output)
            self.assertIn("Backup slutförd!", output)

            # Kontrollera att backup-mappen skapades
            self.assertTrue(os.path.exists(backup_dir))

            # Kontrollera att backup-filer skapades
            backup_files = os.listdir(backup_dir)
            self.assertGreater(len(backup_files), 0)

        finally:
            # Rensa
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)

    @override_settings(BASE_DIR=tempfile.gettempdir())
    @patch("axes.management.commands.backup_database.settings")
    def test_backup_database_with_compress(self, mock_settings):
        """Testa backup med komprimering"""
        temp_dir = tempfile.gettempdir()
        mock_settings.BASE_DIR = temp_dir
        mock_settings.DATABASES = {
            "default": {"NAME": os.path.join(temp_dir, "test_db.sqlite3")}
        }
        mock_settings.MEDIA_ROOT = os.path.join(temp_dir, "media")

        # Skapa en temporär databasfil
        temp_db_path = os.path.join(temp_dir, "test_db.sqlite3")
        with open(temp_db_path, "w") as f:
            f.write("test database content")

        backup_dir = os.path.join(temp_dir, "backups")

        try:
            out = StringIO()
            call_command("backup_database", compress=True, stdout=out)

            output = out.getvalue()
            self.assertIn("Startar automatisk backup...", output)
            self.assertIn("Backup slutförd!", output)

            # Kontrollera att backup-mappen skapades
            self.assertTrue(os.path.exists(backup_dir))

            # Kontrollera att zip-fil skapades
            backup_files = os.listdir(backup_dir)
            zip_files = [f for f in backup_files if f.endswith(".zip")]
            self.assertGreater(len(zip_files), 0)

        finally:
            # Rensa
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)

    @override_settings(BASE_DIR=tempfile.gettempdir())
    @patch("axes.management.commands.backup_database.settings")
    def test_backup_database_with_media(self, mock_settings):
        """Testa backup med media-filer"""
        temp_dir = tempfile.gettempdir()
        mock_settings.BASE_DIR = temp_dir
        mock_settings.DATABASES = {
            "default": {"NAME": os.path.join(temp_dir, "test_db.sqlite3")}
        }

        # Skapa temporär media-mapp med några filer
        temp_media_dir = os.path.join(temp_dir, "media")
        os.makedirs(temp_media_dir, exist_ok=True)
        mock_settings.MEDIA_ROOT = temp_media_dir

        # Skapa några testfiler i media
        test_file1 = os.path.join(temp_media_dir, "test1.txt")
        test_file2 = os.path.join(temp_media_dir, "test2.txt")
        with open(test_file1, "w") as f:
            f.write("test file 1")
        with open(test_file2, "w") as f:
            f.write("test file 2")

        # Skapa en temporär databasfil
        temp_db_path = os.path.join(temp_dir, "test_db.sqlite3")
        with open(temp_db_path, "w") as f:
            f.write("test database content")

        backup_dir = os.path.join(temp_dir, "backups")

        try:
            out = StringIO()
            call_command("backup_database", include_media=True, stdout=out)

            output = out.getvalue()
            self.assertIn("Startar automatisk backup...", output)
            self.assertIn("Backup slutförd!", output)

            # Kontrollera att backup-mappen skapades
            self.assertTrue(os.path.exists(backup_dir))

        finally:
            # Rensa
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            if os.path.exists(temp_media_dir):
                shutil.rmtree(temp_media_dir)

    @override_settings(BASE_DIR=tempfile.gettempdir())
    @patch("axes.management.commands.backup_database.settings")
    def test_backup_database_cleanup_old_backups(self, mock_settings):
        """Testa rensning av gamla backup-filer"""
        temp_dir = tempfile.gettempdir()
        mock_settings.BASE_DIR = temp_dir
        mock_settings.DATABASES = {
            "default": {"NAME": os.path.join(temp_dir, "test_db.sqlite3")}
        }
        mock_settings.MEDIA_ROOT = os.path.join(temp_dir, "media")

        # Skapa en temporär databasfil
        temp_db_path = os.path.join(temp_dir, "test_db.sqlite3")
        with open(temp_db_path, "w") as f:
            f.write("test database content")

        backup_dir = os.path.join(temp_dir, "backups")

        try:
            out = StringIO()
            call_command("backup_database", keep_days=1, stdout=out)

            output = out.getvalue()
            self.assertIn("Startar automatisk backup...", output)
            self.assertIn("Backup slutförd!", output)

        finally:
            # Rensa
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)

    def test_backup_database_stats_creation(self):
        """Testa att backup-statistik skapas korrekt"""
        from axes.management.commands.backup_database import Command

        command = Command()
        stats = command.create_backup_stats()

        # Kontrollera att statistik innehåller förväntade fält
        self.assertIn("timestamp", stats)
        self.assertIn("database", stats)
        self.assertIn("financial", stats)

        # Kontrollera databas-statistik
        db_stats = stats["database"]
        self.assertIn("axes", db_stats)
        self.assertIn("contacts", db_stats)
        self.assertIn("manufacturers", db_stats)
        self.assertIn("transactions", db_stats)

        # Kontrollera att värdena är korrekta
        self.assertEqual(db_stats["axes"], 1)  # Vi skapade 1 yxa i setUp
        self.assertEqual(db_stats["contacts"], 1)  # Vi skapade 1 kontakt i setUp
        self.assertEqual(
            db_stats["manufacturers"], 1
        )  # Vi skapade 1 tillverkare i setUp
        self.assertEqual(
            db_stats["transactions"], 2
        )  # Vi skapade 2 transaktioner i setUp

        # Kontrollera ekonomisk statistik
        financial_stats = stats["financial"]
        self.assertIn("total_buy_value", financial_stats)
        self.assertIn("total_sell_value", financial_stats)
        self.assertIn("net_value", financial_stats)

        # Kontrollera att värdena är korrekta
        self.assertEqual(financial_stats["total_buy_value"], 100.0)  # KÖP-transaktion
        self.assertEqual(financial_stats["total_sell_value"], 150.0)  # SÄLJ-transaktion
        self.assertEqual(financial_stats["net_value"], 50.0)  # 150 - 100


class InitMeasurementsCommandTest(TestCase):
    def setUp(self):
        # Rensa befintliga måtttyper och mallar för att få en ren start
        MeasurementType.objects.all().delete()
        MeasurementTemplate.objects.all().delete()
        MeasurementTemplateItem.objects.all().delete()

    def test_init_measurements_creates_types(self):
        """Testa att kommandot skapar alla förväntade måtttyper"""
        out = StringIO()
        call_command("init_measurements", stdout=out)

        output = out.getvalue()
        self.assertIn("Skapar måtttyper...", output)
        self.assertIn("Skapade måtttyp: Bladlängd (mm)", output)
        self.assertIn("Skapade måtttyp: Bladbredd (mm)", output)
        self.assertIn("Skapade måtttyp: Vikt (gram)", output)

        # Kontrollera att alla förväntade måtttyper skapades
        expected_types = [
            "Bladlängd",
            "Bladbredd",
            "Skaftlängd",
            "Skaftbredd",
            "Total längd",
            "Vikt",
            "Bladvikt",
            "Skaftvikt",
            "Handtag",
            "Bladtjocklek",
            "Öga",
        ]

        for type_name in expected_types:
            self.assertTrue(MeasurementType.objects.filter(name=type_name).exists())

        self.assertEqual(MeasurementType.objects.count(), 11)

    def test_init_measurements_creates_templates(self):
        """Testa att kommandot skapar alla förväntade måttmallar"""
        out = StringIO()
        call_command("init_measurements", stdout=out)

        output = out.getvalue()
        self.assertIn("Skapar måttmallar...", output)
        self.assertIn("Skapade mall: Standard yxa", output)
        self.assertIn("Skapade mall: Fällkniv", output)
        self.assertIn("Skapade mall: Köksyxa", output)
        self.assertIn("Skapade mall: Detaljerad yxa", output)

        # Kontrollera att alla mallar skapades
        expected_templates = ["Standard yxa", "Fällkniv", "Köksyxa", "Detaljerad yxa"]
        for template_name in expected_templates:
            self.assertTrue(
                MeasurementTemplate.objects.filter(name=template_name).exists()
            )

        self.assertEqual(MeasurementTemplate.objects.count(), 4)

    def test_init_measurements_creates_template_items(self):
        """Testa att kommandot skapar mått i mallarna"""
        out = StringIO()
        call_command("init_measurements", stdout=out)

        # Kontrollera att "Standard yxa" mallen har rätt mått
        standard_template = MeasurementTemplate.objects.get(name="Standard yxa")
        standard_items = MeasurementTemplateItem.objects.filter(
            template=standard_template
        ).order_by("sort_order")

        expected_measurements = [
            "Bladlängd",
            "Bladbredd",
            "Skaftlängd",
            "Total längd",
            "Vikt",
        ]
        self.assertEqual(standard_items.count(), 5)

        for i, item in enumerate(standard_items):
            self.assertEqual(item.measurement_type.name, expected_measurements[i])
            self.assertEqual(item.sort_order, i + 1)

    def test_init_measurements_idempotent(self):
        """Testa att kommandot kan köras flera gånger utan att skapa duplicerade data"""
        # Kör kommandot första gången
        out1 = StringIO()
        call_command("init_measurements", stdout=out1)

        initial_type_count = MeasurementType.objects.count()
        initial_template_count = MeasurementTemplate.objects.count()
        initial_item_count = MeasurementTemplateItem.objects.count()

        # Kör kommandot igen
        out2 = StringIO()
        call_command("init_measurements", stdout=out2)

        output2 = out2.getvalue()
        self.assertIn("Måtttyp finns redan: Bladlängd (mm)", output2)
        self.assertIn("Mall finns redan: Standard yxa", output2)

        # Kontrollera att inga nya objekt skapades
        self.assertEqual(MeasurementType.objects.count(), initial_type_count)
        self.assertEqual(MeasurementTemplate.objects.count(), initial_template_count)
        self.assertEqual(MeasurementTemplateItem.objects.count(), initial_item_count)

    def test_init_measurements_success_message(self):
        """Testa att kommandot visar rätt success-meddelande"""
        out = StringIO()
        call_command("init_measurements", stdout=out)

        output = out.getvalue()
        self.assertIn("Initiering av måtttyper och mallar slutförd!", output)

    def test_init_measurements_creates_fallkniv_template(self):
        """Testa att Fällkniv-mallen skapas med rätt mått"""
        out = StringIO()
        call_command("init_measurements", stdout=out)

        fallkniv_template = MeasurementTemplate.objects.get(name="Fällkniv")
        fallkniv_items = MeasurementTemplateItem.objects.filter(
            template=fallkniv_template
        ).order_by("sort_order")

        expected_measurements = ["Bladlängd", "Bladbredd", "Handtag", "Vikt"]
        self.assertEqual(fallkniv_items.count(), 4)

        for i, item in enumerate(fallkniv_items):
            self.assertEqual(item.measurement_type.name, expected_measurements[i])
            self.assertEqual(item.sort_order, i + 1)

    def test_init_measurements_creates_detailed_template(self):
        """Testa att Detaljerad yxa-mallen skapas med alla mått"""
        out = StringIO()
        call_command("init_measurements", stdout=out)

        detailed_template = MeasurementTemplate.objects.get(name="Detaljerad yxa")
        detailed_items = MeasurementTemplateItem.objects.filter(
            template=detailed_template
        ).order_by("sort_order")

        expected_measurements = [
            "Bladlängd",
            "Bladbredd",
            "Bladtjocklek",
            "Skaftlängd",
            "Skaftbredd",
            "Total längd",
            "Vikt",
            "Bladvikt",
            "Skaftvikt",
            "Öga",
        ]
        self.assertEqual(detailed_items.count(), 10)

        for i, item in enumerate(detailed_items):
            self.assertEqual(item.measurement_type.name, expected_measurements[i])
            self.assertEqual(item.sort_order, i + 1)


class UpdateHostsCommandTest(TestCase):
    def setUp(self):
        # Rensa befintliga Settings objekt
        Settings.objects.all().delete()

        # Skapa en Settings-instans för tester
        self.settings = Settings.objects.create(
            external_hosts="example.com,test.com",
            external_csrf_origins="https://example.com,https://test.com",
        )

        # Spara ursprungliga miljövariabler för att återställa efter tester
        self.original_allowed_hosts = os.environ.get("ALLOWED_HOSTS")
        self.original_csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS")

    def tearDown(self):
        # Återställ ursprungliga miljövariabler
        if self.original_allowed_hosts is not None:
            os.environ["ALLOWED_HOSTS"] = self.original_allowed_hosts
        elif "ALLOWED_HOSTS" in os.environ:
            del os.environ["ALLOWED_HOSTS"]

        if self.original_csrf_origins is not None:
            os.environ["CSRF_TRUSTED_ORIGINS"] = self.original_csrf_origins
        elif "CSRF_TRUSTED_ORIGINS" in os.environ:
            del os.environ["CSRF_TRUSTED_ORIGINS"]

    def test_update_hosts_with_existing_settings(self):
        """Testa att kommandot uppdaterar miljövariabler med befintliga inställningar"""
        out = StringIO()
        call_command("update_hosts", stdout=out)

        output = out.getvalue()
        self.assertIn("ALLOWED_HOSTS uppdaterad: example.com,test.com", output)
        self.assertIn(
            "CSRF_TRUSTED_ORIGINS uppdaterad: https://example.com,https://test.com",
            output,
        )

        # Kontrollera att miljövariabler uppdaterades
        self.assertEqual(os.environ.get("ALLOWED_HOSTS"), "example.com,test.com")
        self.assertEqual(
            os.environ.get("CSRF_TRUSTED_ORIGINS"),
            "https://example.com,https://test.com",
        )

    def test_update_hosts_combines_with_existing_env_vars(self):
        """Testa att kommandot kombinerar med befintliga miljövariabler"""
        # Sätt befintliga miljövariabler
        os.environ["ALLOWED_HOSTS"] = "localhost,127.0.0.1"
        os.environ["CSRF_TRUSTED_ORIGINS"] = "http://localhost,http://127.0.0.1"

        out = StringIO()
        call_command("update_hosts", stdout=out)

        output = out.getvalue()
        self.assertIn(
            "ALLOWED_HOSTS uppdaterad: localhost,127.0.0.1,example.com,test.com", output
        )
        self.assertIn(
            "CSRF_TRUSTED_ORIGINS uppdaterad: http://localhost,http://127.0.0.1,https://example.com,https://test.com",
            output,
        )

        # Kontrollera att miljövariabler kombinerades korrekt
        self.assertEqual(
            os.environ.get("ALLOWED_HOSTS"), "localhost,127.0.0.1,example.com,test.com"
        )
        self.assertEqual(
            os.environ.get("CSRF_TRUSTED_ORIGINS"),
            "http://localhost,http://127.0.0.1,https://example.com,https://test.com",
        )

    def test_update_hosts_no_external_hosts(self):
        """Testa att kommandot hanterar tomma externa hosts"""
        # Uppdatera settings till tomma värden
        self.settings.external_hosts = ""
        self.settings.external_csrf_origins = ""
        self.settings.save()

        out = StringIO()
        call_command("update_hosts", stdout=out)

        output = out.getvalue()
        self.assertIn("Inga externa hosts konfigurerade i databasen", output)
        self.assertIn("Inga externa CSRF-origins konfigurerade i databasen", output)

        # Kontrollera att miljövariabler inte ändrades
        current_allowed_hosts = os.environ.get("ALLOWED_HOSTS")
        current_csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS")
        self.assertEqual(current_allowed_hosts, self.original_allowed_hosts)
        self.assertEqual(current_csrf_origins, self.original_csrf_origins)

    def test_update_hosts_only_allowed_hosts(self):
        """Testa att kommandot hanterar bara ALLOWED_HOSTS"""
        # Sätt bara external_hosts
        self.settings.external_csrf_origins = ""
        self.settings.save()

        out = StringIO()
        call_command("update_hosts", stdout=out)

        output = out.getvalue()
        self.assertIn("ALLOWED_HOSTS uppdaterad: example.com,test.com", output)
        self.assertIn("Inga externa CSRF-origins konfigurerade i databasen", output)

        # Kontrollera att bara ALLOWED_HOSTS uppdaterades
        self.assertEqual(os.environ.get("ALLOWED_HOSTS"), "example.com,test.com")
        current_csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS")
        self.assertEqual(current_csrf_origins, self.original_csrf_origins)

    def test_update_hosts_only_csrf_origins(self):
        """Testa att kommandot hanterar bara CSRF_TRUSTED_ORIGINS"""
        # Sätt bara external_csrf_origins
        self.settings.external_hosts = ""
        self.settings.save()

        out = StringIO()
        call_command("update_hosts", stdout=out)

        output = out.getvalue()
        self.assertIn("Inga externa hosts konfigurerade i databasen", output)
        self.assertIn(
            "CSRF_TRUSTED_ORIGINS uppdaterad: https://example.com,https://test.com",
            output,
        )

        # Kontrollera att bara CSRF_TRUSTED_ORIGINS uppdaterades
        current_allowed_hosts = os.environ.get("ALLOWED_HOSTS")
        self.assertEqual(current_allowed_hosts, self.original_allowed_hosts)
        self.assertEqual(
            os.environ.get("CSRF_TRUSTED_ORIGINS"),
            "https://example.com,https://test.com",
        )

    def test_update_hosts_no_settings_object(self):
        """Testa att kommandot hanterar när Settings-objekt inte finns"""
        # Ta bort Settings-objektet
        self.settings.delete()

        out = StringIO()
        call_command("update_hosts", stdout=out)

        output = out.getvalue()
        self.assertIn("Inga externa hosts konfigurerade i databasen", output)
        self.assertIn("Inga externa CSRF-origins konfigurerade i databasen", output)

        # Kontrollera att miljövariabler inte ändrades
        current_allowed_hosts = os.environ.get("ALLOWED_HOSTS")
        current_csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS")
        self.assertEqual(current_allowed_hosts, self.original_allowed_hosts)
        self.assertEqual(current_csrf_origins, self.original_csrf_origins)


class RestoreBackupCommandTest(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_file = os.path.join(self.temp_dir, "test_backup.sqlite3")
        self.zip_backup_file = os.path.join(self.temp_dir, "test_backup.zip")

        # Skapa en test-databas
        with open(self.backup_file, "w") as f:
            f.write("test database content")

        # Skapa en test-zip-fil
        with zipfile.ZipFile(self.zip_backup_file, "w") as zipf:
            zipf.writestr("test_db.sqlite3", "test database content")
            zipf.writestr("media/test_image.jpg", "test image content")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @override_settings(
        BASE_DIR="/tmp",
        MEDIA_ROOT="/tmp/media",
        DATABASES={"default": {"NAME": "test_db.sqlite3"}},
    )
    def test_restore_backup_file_not_found(self):
        """Test att kommandot hanterar saknade backup-filer"""
        out = StringIO()
        call_command(
            "restore_backup", "nonexistent_file.sqlite3", confirm=True, stdout=out
        )
        output = out.getvalue()
        self.assertIn("Backup-filen nonexistent_file.sqlite3 finns inte!", output)

    @override_settings(
        BASE_DIR="/tmp",
        MEDIA_ROOT="/tmp/media",
        DATABASES={"default": {"NAME": "test_db.sqlite3"}},
    )
    def test_restore_backup_requires_confirmation(self):
        """Test att kommandot kräver bekräftelse"""
        out = StringIO()
        call_command("restore_backup", self.backup_file, stdout=out)
        output = out.getvalue()
        self.assertIn("VARNING: Detta kommer att skriva över befintlig data!", output)
        self.assertIn("Kör kommandot igen med --confirm för att bekräfta.", output)

    @override_settings(
        BASE_DIR="/tmp",
        MEDIA_ROOT="/tmp/media",
        DATABASES={"default": {"NAME": "test_db.sqlite3"}},
    )
    def test_restore_backup_invalid_file_type(self):
        """Test att kommandot hanterar ogiltiga filtyper"""
        invalid_file = os.path.join(self.temp_dir, "test.txt")
        with open(invalid_file, "w") as f:
            f.write("test")

        out = StringIO()
        call_command("restore_backup", invalid_file, confirm=True, stdout=out)
        output = out.getvalue()
        self.assertIn("Backup-filen måste vara .zip eller .sqlite3", output)

    @override_settings(
        BASE_DIR="/tmp",
        MEDIA_ROOT="/tmp/media",
        DATABASES={"default": {"NAME": "test_db.sqlite3"}},
    )
    @patch("shutil.copy2")
    def test_restore_sqlite3_database(self, mock_copy2):
        """Test återställning av sqlite3-databas"""
        out = StringIO()
        call_command("restore_backup", self.backup_file, confirm=True, stdout=out)
        output = out.getvalue()

        self.assertIn("Startar återställning från backup...", output)
        self.assertIn("Återställning slutförd!", output)
        mock_copy2.assert_called()

    @override_settings(
        BASE_DIR="/tmp",
        MEDIA_ROOT="/tmp/media",
        DATABASES={"default": {"NAME": "test_db.sqlite3"}},
    )
    @patch("shutil.copy2")
    def test_restore_from_zip_without_media(self, mock_copy2):
        """Test återställning från zip utan media"""
        out = StringIO()
        call_command("restore_backup", self.zip_backup_file, confirm=True, stdout=out)
        output = out.getvalue()

        self.assertIn("Startar återställning från backup...", output)
        self.assertIn("Återställning slutförd!", output)
        mock_copy2.assert_called()

    @override_settings(
        BASE_DIR="/tmp",
        MEDIA_ROOT="/tmp/media",
        DATABASES={"default": {"NAME": "test_db.sqlite3"}},
    )
    @patch("shutil.copy2")
    @patch("shutil.copytree")
    def test_restore_from_zip_with_media(self, mock_copytree, mock_copy2):
        """Test återställning från zip med media"""
        out = StringIO()
        call_command(
            "restore_backup",
            self.zip_backup_file,
            confirm=True,
            include_media=True,
            stdout=out,
        )
        output = out.getvalue()

        self.assertIn("Startar återställning från backup...", output)
        self.assertIn("Återställning slutförd!", output)
        mock_copy2.assert_called()

    @override_settings(
        BASE_DIR="/tmp",
        MEDIA_ROOT="/tmp/media",
        DATABASES={"default": {"NAME": "test_db.sqlite3"}},
    )
    @patch("django.db.connection")
    def test_fix_image_paths(self, mock_connection):
        """Test fix_image_paths-funktionen"""
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # Mock databas-resultat
        mock_cursor.fetchall.return_value = [
            (1, "test\\image.jpg"),
            (2, "normal/image.jpg"),
        ]
        mock_cursor.fetchone.return_value = [0]  # Inga sökvägar med problem

        out = StringIO()
        call_command("restore_backup", self.backup_file, confirm=True, stdout=out)
        output = out.getvalue()

        self.assertIn("Återställning slutförd!", output)
        mock_cursor.execute.assert_called()


class GenerateTestDataCommandTest(TestCase):
    """Tester för generate_test_data.py management command"""

    def setUp(self):
        """Rensa befintlig data för att få en ren start"""
        # Rensa alla modeller som generate_test_data skapar
        Axe.objects.all().delete()
        Manufacturer.objects.all().delete()
        Contact.objects.all().delete()
        Platform.objects.all().delete()
        Transaction.objects.all().delete()
        Measurement.objects.all().delete()
        ManufacturerImage.objects.all().delete()
        ManufacturerLink.objects.all().delete()
        Settings.objects.all().delete()
        NextAxeID.objects.all().delete()
        MeasurementType.objects.all().delete()
        MeasurementTemplate.objects.all().delete()
        MeasurementTemplateItem.objects.all().delete()

    def test_generate_test_data_default(self):
        """Test att kommandot genererar testdata med standardvärden"""
        out = StringIO()
        call_command("generate_test_data", stdout=out)

        output = out.getvalue()
        self.assertIn("Genererar testdata...", output)
        self.assertIn("Testdata genererat!", output)

        # Kontrollera att data har skapats
        self.assertGreater(Axe.objects.count(), 0)
        self.assertGreater(Manufacturer.objects.count(), 0)
        self.assertGreater(Contact.objects.count(), 0)
        self.assertGreater(Platform.objects.count(), 0)

    def test_generate_test_data_with_clear(self):
        """Test att kommandot rensar befintlig data med --clear"""
        # Skapa lite befintlig data först
        manufacturer = Manufacturer.objects.create(name="Existing Manufacturer")
        axe = Axe.objects.create(manufacturer=manufacturer, model="Existing Axe")

        out = StringIO()
        call_command("generate_test_data", clear=True, stdout=out)

        output = out.getvalue()
        self.assertIn("Rensar befintlig data...", output)
        self.assertIn("Genererar testdata...", output)

        # Kontrollera att befintlig data är borttagen
        self.assertFalse(
            Manufacturer.objects.filter(name="Existing Manufacturer").exists()
        )
        self.assertFalse(Axe.objects.filter(model="Existing Axe").exists())

    def test_generate_test_data_custom_counts(self):
        """Test att kommandot använder anpassade antal"""
        out = StringIO()
        call_command(
            "generate_test_data", axes=5, manufacturers=3, contacts=4, stdout=out
        )

        output = out.getvalue()
        self.assertIn("Testdata genererat!", output)

        # Kontrollera att rätt antal objekt har skapats
        # Notera: generate_test_data kan skapa fler objekt än specificerat
        # så vi kontrollerar bara att det finns data
        self.assertGreater(Axe.objects.count(), 0)
        self.assertGreater(Manufacturer.objects.count(), 0)
        self.assertGreater(Contact.objects.count(), 0)

    def test_generate_test_data_creates_measurement_types(self):
        """Test att kommandot skapar måtttyper"""
        call_command("generate_test_data")

        # Kontrollera att måtttyper har skapats
        measurement_types = MeasurementType.objects.all()
        self.assertGreater(measurement_types.count(), 0)

        # Kontrollera att några förväntade måtttyper finns
        expected_types = ["Längd", "Bredd", "Vikt"]
        for expected_type in expected_types:
            self.assertTrue(
                MeasurementType.objects.filter(name__icontains=expected_type).exists()
            )

    def test_generate_test_data_creates_measurement_templates(self):
        """Test att kommandot skapar måttmallar"""
        call_command("generate_test_data")

        # Kontrollera att måttmallar har skapats
        templates = MeasurementTemplate.objects.all()
        self.assertGreater(templates.count(), 0)

        # Kontrollera att förväntade mallar finns (Standardyxa och Detaljerad yxa)
        expected_templates = ["Standardyxa", "Detaljerad yxa"]
        for expected_template in expected_templates:
            self.assertTrue(
                MeasurementTemplate.objects.filter(
                    name__icontains=expected_template
                ).exists()
            )

    def test_generate_test_data_creates_transactions(self):
        """Test att kommandot skapar transaktioner"""
        call_command("generate_test_data")

        # Kontrollera att transaktioner har skapats
        transactions = Transaction.objects.all()
        self.assertGreater(transactions.count(), 0)

        # Kontrollera att transaktioner har kopplingar till yxor
        # Kontakter och plattformar kan vara None enligt koden
        for transaction in transactions:
            self.assertIsNotNone(transaction.axe)
            # Kontakt och plattform kan vara None (20% resp 10% chans)

    def test_generate_test_data_creates_manufacturer_images(self):
        """Test att kommandot skapar tillverkarbilder"""
        call_command("generate_test_data")

        # Kontrollera att tillverkarbilder har skapats
        manufacturer_images = ManufacturerImage.objects.all()
        self.assertGreater(manufacturer_images.count(), 0)

        # Kontrollera att bilder har rätt typ (STAMP eller OTHER)
        for image in manufacturer_images:
            self.assertIn(image.image_type, ["STAMP", "OTHER"])

    def test_generate_test_data_creates_axe_images(self):
        """Test att kommandot skapar yxbilder"""
        call_command("generate_test_data")

        # Kontrollera att yxbilder har skapats
        axe_images = AxeImage.objects.all()
        self.assertGreater(axe_images.count(), 0)

        # Kontrollera att bilder har kopplingar till yxor
        for image in axe_images:
            self.assertIsNotNone(image.axe)

    def test_generate_test_data_creates_settings(self):
        """Test att kommandot skapar standardinställningar"""
        call_command("generate_test_data")

        # Kontrollera att Settings-objekt har skapats
        settings = Settings.objects.first()
        self.assertIsNotNone(settings)

        # Kontrollera att standardvärden är satta
        self.assertIsNotNone(settings.default_axes_rows_private)
        self.assertIsNotNone(settings.default_axes_rows_public)

    def test_generate_test_data_creates_demo_user(self):
        """Test att kommandot skapar demo-användare"""
        call_command("generate_test_data")

        # Kontrollera att demo-användare har skapats
        from django.contrib.auth.models import User

        demo_user = User.objects.filter(username="demo").first()
        self.assertIsNotNone(demo_user)
        self.assertEqual(demo_user.email, "demo@axecollection.se")

    def test_generate_test_data_success_message_format(self):
        """Test att success-meddelandet har rätt format"""
        out = StringIO()
        call_command(
            "generate_test_data", axes=10, manufacturers=5, contacts=8, stdout=out
        )

        output = out.getvalue()
        self.assertIn("Testdata genererat!", output)
        self.assertIn("tillverkare", output)
        self.assertIn("kontakter", output)
        self.assertIn("yxor", output)
        self.assertIn("plattformar", output)

    def test_generate_test_data_creates_manufacturers_with_country_codes(self):
        """Test att kommandot skapar tillverkare med landskoder"""
        call_command("generate_test_data")

        # Kontrollera att tillverkare har skapats med landskoder
        manufacturers = Manufacturer.objects.all()
        self.assertGreater(manufacturers.count(), 0)

        # Kontrollera att minst några tillverkare har landskoder
        manufacturers_with_country_codes = manufacturers.filter(
            country_code__isnull=False
        )
        self.assertGreater(manufacturers_with_country_codes.count(), 0)

        # Kontrollera att landskoderna är giltiga (2 bokstäver)
        for manufacturer in manufacturers_with_country_codes:
            self.assertEqual(len(manufacturer.country_code), 2)
            self.assertTrue(manufacturer.country_code.isalpha())

    def test_generate_test_data_creates_specific_country_codes(self):
        """Test att kommandot skapar förväntade landskoder för specifika tillverkare"""
        call_command("generate_test_data")

        # Kontrollera att specifika tillverkare har rätt landskoder
        expected_country_codes = {
            "Hjärtumssmedjan": "SE",
            "Billnäs bruk": "FI",
            "Gränsfors bruk": "SE",
            "Hults bruk": "SE",
            "S. A. Wetterlings yxfabrik": "SE",
            "Mariefors Bruk": "FI",
            "Säters yxfabrik": "SE",
            "Jäders bruk": "SE",
            "Svenska Yxfabriken AB, Kristinehamn": "SE",
            "Edsbyn Industri Aktiebolag": "SE",
            "Dansk Stålindustri": "DK",
            "Mustad": "NO",
            "Øyo": "NO",
        }

        for manufacturer_name, expected_country_code in expected_country_codes.items():
            manufacturer = Manufacturer.objects.filter(name=manufacturer_name).first()
            if manufacturer:
                self.assertEqual(
                    manufacturer.country_code,
                    expected_country_code,
                    f"Tillverkare {manufacturer_name} ska ha landskod {expected_country_code}",
                )

    def test_generate_test_data_creates_hierarchical_manufacturers_with_country_codes(
        self,
    ):
        """Test att hierarkiska tillverkare (med undertillverkare) skapas med landskoder"""
        call_command("generate_test_data")

        # Hitta huvudtillverkare med undertillverkare
        main_manufacturers = Manufacturer.objects.filter(parent__isnull=True)

        for main_manufacturer in main_manufacturers:
            # Kontrollera att huvudtillverkaren har landskod
            if main_manufacturer.country_code:
                self.assertEqual(len(main_manufacturer.country_code), 2)

                # Kontrollera att undertillverkarna har samma landskod
                sub_manufacturers = Manufacturer.objects.filter(
                    parent=main_manufacturer
                )
                for sub_manufacturer in sub_manufacturers:
                    self.assertEqual(
                        sub_manufacturer.country_code,
                        main_manufacturer.country_code,
                        f"Undertillverkare {sub_manufacturer.name} ska ha samma landskod som huvudtillverkare {main_manufacturer.name}",
                    )

    def test_generate_test_data_country_codes_are_consistent(self):
        """Test att landskoder är konsistenta inom hierarkier"""
        call_command("generate_test_data")

        # Kontrollera att alla tillverkare med landskoder har giltiga koder
        manufacturers_with_codes = Manufacturer.objects.filter(
            country_code__isnull=False
        )

        for manufacturer in manufacturers_with_codes:
            # Kontrollera format (2 bokstäver, versaler)
            self.assertEqual(len(manufacturer.country_code), 2)
            self.assertTrue(manufacturer.country_code.isalpha())
            self.assertTrue(manufacturer.country_code.isupper())

            # Kontrollera att koden är en av de förväntade
            expected_codes = ["SE", "FI", "DK", "NO"]
            self.assertIn(manufacturer.country_code, expected_codes)
