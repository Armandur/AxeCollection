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
            
            # Ta bort befintlig backup om den finns
            if os.path.exists(current_media_backup):
                shutil.rmtree(current_media_backup)
                self.stdout.write(f'  Tog bort befintlig backup: {current_media_backup}')
            
            shutil.copytree(settings.MEDIA_ROOT, current_media_backup)
            self.stdout.write(f'  Skapade backup av nuvarande media: {current_media_backup}')
            
            # I Docker-miljö kan vi inte ta bort volym-mappade mappar
            # Istället rensar vi innehållet och kopierar över
            try:
                # Försök ta bort mappen (fungerar i utvecklingsmiljö)
                shutil.rmtree(settings.MEDIA_ROOT)
            except OSError:
                # I Docker-miljö: rensa innehållet istället
                self.stdout.write('  Rensar befintlig media-mapp (Docker-volym)')
                for item in os.listdir(settings.MEDIA_ROOT):
                    item_path = os.path.join(settings.MEDIA_ROOT, item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
        
        # Kopiera media från backup
        # Använd copy2 istället för copytree eftersom mappen redan finns
        self._copy_directory_contents(media_backup_dir, settings.MEDIA_ROOT)
        self.stdout.write('  Återställde media-filer')
    
    def fix_image_paths(self):
        """Fix image paths after restore to handle Windows/Linux differences and environment-specific needs"""
        from django.db import connection
        from django.conf import settings
        
        cursor = connection.cursor()
        
        fixes_made = 0
        
        # Fix backslashes using Python approach (more reliable than SQL)
        cursor.execute("SELECT id, image FROM axes_axeimage")
        rows = cursor.fetchall()
        
        backslash_fixes = 0
        for row_id, image_path in rows:
            if '\\' in image_path:
                # Fixa backslashes
                new_path = image_path.replace('\\', '/')
                cursor.execute("UPDATE axes_axeimage SET image = %s WHERE id = %s", [new_path, row_id])
                backslash_fixes += 1
        
        if backslash_fixes > 0:
            self.stdout.write(f'  Fixade {backslash_fixes} sökvägar med backslashes')
            fixes_made += backslash_fixes
        
        # Check for incorrect /app/media/ prefix (should be removed)
        cursor.execute("SELECT COUNT(*) FROM axes_axeimage WHERE image LIKE '/app/media/%'")
        count_with_app_media = cursor.fetchone()[0]
        
        # Remove incorrect /app/media/ prefix (always needed)
        if count_with_app_media > 0:
            cursor.execute("UPDATE axes_axeimage SET image = REPLACE(image, '/app/media/', '')")
            self.stdout.write(f'  Tog bort /app/media/ prefix från {count_with_app_media} sökvägar')
            fixes_made += count_with_app_media
        
        # Handle media/ prefix based on environment
        if getattr(settings, 'DEBUG', True):
            # Development environment: remove media/ prefix (Django adds it automatically)
            cursor.execute("SELECT COUNT(*) FROM axes_axeimage WHERE image LIKE 'media/%'")
            count_with_media_prefix = cursor.fetchone()[0]
            
            if count_with_media_prefix > 0:
                cursor.execute("UPDATE axes_axeimage SET image = REPLACE(image, 'media/', '')")
                self.stdout.write(f'  Tog bort media/ prefix från {count_with_media_prefix} sökvägar (utvecklingsmiljö)')
                fixes_made += count_with_media_prefix
        else:
            # Production environment: remove media/ prefix (Nginx handles /media/ URL directly)
            cursor.execute("SELECT COUNT(*) FROM axes_axeimage WHERE image LIKE 'media/%'")
            count_with_media_prefix = cursor.fetchone()[0]
            
            if count_with_media_prefix > 0:
                cursor.execute("UPDATE axes_axeimage SET image = REPLACE(image, 'media/', '')")
                self.stdout.write(f'  Tog bort media/ prefix från {count_with_media_prefix} sökvägar (produktionsmiljö)')
                fixes_made += count_with_media_prefix
        
        if fixes_made > 0:
            connection.commit()
            self.stdout.write(f'  Fixade totalt {fixes_made} bildsökvägar')
        else:
            self.stdout.write('  Inga sökvägsproblem hittades')
    
    def _copy_directory_contents(self, src_dir, dst_dir):
        """Kopiera innehållet från en mapp till en annan"""
        for item in os.listdir(src_dir):
            src_path = os.path.join(src_dir, item)
            dst_path = os.path.join(dst_dir, item)
            
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dst_path)
            elif os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    # Om mappen redan finns, kopiera innehållet rekursivt
                    self._copy_directory_contents(src_path, dst_path)
                else:
                    # Om mappen inte finns, skapa den och kopiera
                    shutil.copytree(src_path, dst_path) 