import os
import zipfile
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Återställ databas och media från backup'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            type=str,
            help='Sökväg till backup-filen (zip eller sqlite3)',
        )
        parser.add_argument(
            '--include-media',
            action='store_true',
            help='Återställ även media-filer',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Bekräfta att du vill återställa (detta kommer att skriva över befintlig data)',
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        
        if not os.path.exists(backup_file):
            self.stdout.write(
                self.style.ERROR(f'Backup-filen {backup_file} finns inte!')
            )
            return
        
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'VARNING: Detta kommer att skriva över befintlig data!'
                )
            )
            self.stdout.write(
                'Kör kommandot igen med --confirm för att bekräfta.'
            )
            return
        
        self.stdout.write('Startar återställning från backup...')
        
        # Kontrollera om det är en zip-fil eller sqlite3-fil
        if backup_file.endswith('.zip'):
            self.restore_from_zip(backup_file, options['include_media'])
        elif backup_file.endswith('.sqlite3'):
            self.restore_database(backup_file)
        else:
            self.stdout.write(
                self.style.ERROR('Backup-filen måste vara .zip eller .sqlite3')
            )
        
        # Fixa sökvägar efter återställning
        self.fix_image_paths()
        
        self.stdout.write(
            self.style.SUCCESS('Återställning slutförd!')
        )

    def restore_from_zip(self, zip_path, include_media):
        """Återställ från komprimerad backup"""
        backup_dir = os.path.join(settings.BASE_DIR, 'temp_restore')
        
        try:
            # Skapa temporär mapp för utpackning
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            os.makedirs(backup_dir)
            
            # Packa upp zip-filen
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(backup_dir)
            
            # Hitta databas-filen
            db_files = [f for f in os.listdir(backup_dir) if f.endswith('.sqlite3')]
            if db_files:
                db_backup_path = os.path.join(backup_dir, db_files[0])
                self.restore_database(db_backup_path)
            
            # Återställ media om begärt
            if include_media:
                media_backup_dir = os.path.join(backup_dir, 'media')
                if os.path.exists(media_backup_dir):
                    self.restore_media_files(media_backup_dir)
                else:
                    self.stdout.write('  Media-mapp finns inte i backup')
            
        finally:
            # Rensa temporär mapp
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)

    def restore_database(self, db_backup_path):
        """Återställ databas"""
        db_name = settings.DATABASES['default']['NAME']
        
        # Skapa backup av nuvarande databas
        current_backup = f'{db_name}.backup'
        if os.path.exists(db_name):
            shutil.copy2(db_name, current_backup)
            self.stdout.write(f'  Skapade backup av nuvarande databas: {current_backup}')
        
        # Kopiera backup-databasen
        shutil.copy2(db_backup_path, db_name)
        self.stdout.write(f'  Återställde databas från: {os.path.basename(db_backup_path)}')

    def restore_media_files(self, media_backup_dir):
        """Återställ media-filer"""
        if os.path.exists(settings.MEDIA_ROOT):
            # Skapa backup av nuvarande media
            current_media_backup = f'{settings.MEDIA_ROOT}.backup'
            shutil.copytree(settings.MEDIA_ROOT, current_media_backup)
            self.stdout.write(f'  Skapade backup av nuvarande media: {current_media_backup}')
            
            # Ta bort nuvarande media och kopiera från backup
            shutil.rmtree(settings.MEDIA_ROOT)
        
        # Kopiera media från backup
        shutil.copytree(media_backup_dir, settings.MEDIA_ROOT)
        self.stdout.write('  Återställde media-filer')
    
    def fix_image_paths(self):
        """Fix image paths after restore to handle Windows/Linux differences"""
        from django.db import connection
        
        cursor = connection.cursor()
        
        # Check for backslashes in image paths (Windows to Linux)
        cursor.execute("SELECT COUNT(*) FROM axes_axeimage WHERE image LIKE '%\\\\%'")
        count_with_backslashes = cursor.fetchone()[0]
        
        # Check for incorrect /app/media/ prefix (should be removed)
        cursor.execute("SELECT COUNT(*) FROM axes_axeimage WHERE image LIKE '/app/media/%'")
        count_with_app_media = cursor.fetchone()[0]
        
        # Check for incorrect media/ prefix (should be removed)
        cursor.execute("SELECT COUNT(*) FROM axes_axeimage WHERE image LIKE 'media/%'")
        count_with_media_prefix = cursor.fetchone()[0]
        
        fixes_made = 0
        
        # Fix backslashes
        if count_with_backslashes > 0:
            cursor.execute("UPDATE axes_axeimage SET image = REPLACE(image, '\\\\', '/')")
            self.stdout.write(f'  Fixade {count_with_backslashes} sökvägar med backslashes')
            fixes_made += count_with_backslashes
        
        # Remove incorrect /app/media/ prefix
        if count_with_app_media > 0:
            cursor.execute("UPDATE axes_axeimage SET image = REPLACE(image, '/app/media/', '')")
            self.stdout.write(f'  Tog bort /app/media/ prefix från {count_with_app_media} sökvägar')
            fixes_made += count_with_app_media
        
        # Remove incorrect media/ prefix
        if count_with_media_prefix > 0:
            cursor.execute("UPDATE axes_axeimage SET image = REPLACE(image, 'media/', '')")
            self.stdout.write(f'  Tog bort media/ prefix från {count_with_media_prefix} sökvägar')
            fixes_made += count_with_media_prefix
        
        if fixes_made > 0:
            connection.commit()
            self.stdout.write(f'  Fixade totalt {fixes_made} bildsökvägar')
        else:
            self.stdout.write('  Inga sökvägsproblem hittades') 