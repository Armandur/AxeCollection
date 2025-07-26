import os
import shutil
import zipfile
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Skapa automatisk backup av databasen och media-filer"

    def add_arguments(self, parser):
        parser.add_argument(
            "--include-media",
            action="store_true",
            help="Inkludera media-filer i backup",
        )
        parser.add_argument(
            "--compress",
            action="store_true",
            help="Komprimera backup-filen",
        )
        parser.add_argument(
            "--keep-days",
            type=int,
            default=30,
            help="Antal dagar att behålla gamla backuper (standard: 30)",
        )

    def handle(self, *args, **options):
        self.stdout.write("Startar automatisk backup...")

        # Skapa backup-mapp
        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Generera timestamp för backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Skapa backup av databasen
        db_backup_path = self.backup_database(backup_dir, timestamp)

        # Skapa statistik för backup
        stats = self.create_backup_stats()

        # Skapa backup av media-filer om begärt
        media_backup_path = None
        if options["include_media"]:
            media_backup_path = self.backup_media_files(backup_dir, timestamp)
            stats["media_files"] = self.count_media_files()

        # Skapa komprimerad backup om begärt
        if options["compress"]:
            self.create_compressed_backup(
                backup_dir, timestamp, db_backup_path, media_backup_path, stats
            )
        else:
            # Spara statistik-fil för icke-komprimerade backuper
            stats_path = os.path.join(backup_dir, f"stats_{timestamp}.json")
            with open(stats_path, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)

        # Rensa gamla backuper
        self.cleanup_old_backups(backup_dir, options["keep_days"])

        self.stdout.write(
            self.style.SUCCESS(f"Backup slutförd! Timestamp: {timestamp}")
        )

    def create_backup_stats(self):
        """Skapa statistik över databas-innehåll"""
        from axes.models import (
            Axe,
            Contact,
            Manufacturer,
            Transaction,
            Measurement,
            AxeImage,
            ManufacturerImage,
            ManufacturerLink,
        )

        stats = {
            "timestamp": datetime.now().isoformat(),
            "database": {
                "axes": Axe.objects.count(),
                "contacts": Contact.objects.count(),
                "manufacturers": Manufacturer.objects.count(),
                "transactions": Transaction.objects.count(),
                "measurements": Measurement.objects.count(),
                "axe_images": AxeImage.objects.count(),
                "manufacturer_images": ManufacturerImage.objects.count(),
                "manufacturer_links": ManufacturerLink.objects.count(),
            },
        }

        # Lägg till ekonomisk statistik
        total_buy_value = sum(
            t.price for t in Transaction.objects.filter(type="KÖP") if t.price
        )
        total_sell_value = sum(
            t.price for t in Transaction.objects.filter(type="SÄLJ") if t.price
        )

        stats["financial"] = {
            "total_buy_value": float(total_buy_value) if total_buy_value else 0,
            "total_sell_value": float(total_sell_value) if total_sell_value else 0,
            "net_value": (
                float(total_sell_value - total_buy_value)
                if total_sell_value and total_buy_value
                else 0
            ),
        }

        return stats

    def count_media_files(self):
        """Räkna media-filer"""
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            return 0

        count = 0
        for root, dirs, files in os.walk(media_root):
            count += len(files)
        return count

    def backup_database(self, backup_dir, timestamp):
        """Skapa backup av databasen"""
        db_name = settings.DATABASES["default"]["NAME"]
        db_backup_name = f"db_backup_{timestamp}.sqlite3"
        db_backup_path = os.path.join(backup_dir, db_backup_name)

        # Kopiera databasfilen
        shutil.copy2(db_name, db_backup_path)

        self.stdout.write(f"  Databas backup: {db_backup_name}")
        return db_backup_path

    def backup_media_files(self, backup_dir, timestamp):
        """Skapa backup av media-filer"""
        media_backup_name = f"media_backup_{timestamp}"
        media_backup_path = os.path.join(backup_dir, media_backup_name)

        # Kopiera media-mappen
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.copytree(settings.MEDIA_ROOT, media_backup_path)
            self.stdout.write(f"  Media backup: {media_backup_name}")
        else:
            self.stdout.write("  Media-mapp finns inte, hoppar över media-backup")
            return None

        return media_backup_path

    def create_compressed_backup(
        self, backup_dir, timestamp, db_backup_path, media_backup_path, stats
    ):
        """Skapa komprimerad backup-fil"""
        zip_name = f"full_backup_{timestamp}.zip"
        zip_path = os.path.join(backup_dir, zip_name)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Lägg till databas-backup
            if db_backup_path and os.path.exists(db_backup_path):
                zipf.write(db_backup_path, os.path.basename(db_backup_path))

            # Lägg till media-backup
            if media_backup_path and os.path.exists(media_backup_path):
                for root, dirs, files in os.walk(media_backup_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, media_backup_path)
                        zipf.write(file_path, f"media/{arc_name}")

            # Lägg till statistik-fil
            stats_content = json.dumps(stats, indent=2, ensure_ascii=False)
            zipf.writestr("backup_stats.json", stats_content)

        # Ta bort individuella backup-filer efter komprimering
        if db_backup_path and os.path.exists(db_backup_path):
            os.remove(db_backup_path)
        if media_backup_path and os.path.exists(media_backup_path):
            shutil.rmtree(media_backup_path)

        self.stdout.write(f"  Komprimerad backup: {zip_name}")

    def cleanup_old_backups(self, backup_dir, keep_days):
        """Rensa gamla backup-filer"""
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        removed_count = 0

        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        removed_count += 1
                        self.stdout.write(f"  Raderade gammal backup: {filename}")
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f"  Kunde inte radera {filename}: {e}")
                        )

        if removed_count > 0:
            self.stdout.write(f"  Raderade {removed_count} gamla backup-filer")
