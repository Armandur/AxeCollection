from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Fix image paths for different environments (Windows/Linux)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force fix even if no issues detected',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        cursor = connection.cursor()
        
        # Check for backslashes in image paths
        cursor.execute("SELECT COUNT(*) FROM axes_axeimage WHERE image LIKE '%\\\\%'")
        count_with_backslashes = cursor.fetchone()[0]
        
        # Check for missing /app/media/ prefix in Docker environment
        cursor.execute("SELECT COUNT(*) FROM axes_axeimage WHERE image NOT LIKE '/app/media/%'")
        count_without_prefix = cursor.fetchone()[0]
        

        
        if options['dry_run']:
            self.stdout.write(f"Would fix {count_with_backslashes} paths with backslashes")
            self.stdout.write(f"Would fix {count_without_prefix} paths without /app/media/ prefix")
            return
        
        fixes_made = 0
        
        # Fix backslashes
        if count_with_backslashes > 0:
            cursor.execute("UPDATE axes_axeimage SET image = REPLACE(image, '\\\\', '/')")
            self.stdout.write(f"Fixed {count_with_backslashes} paths with backslashes")
            fixes_made += count_with_backslashes
        
        # Fix missing /app/media/ prefix in Docker environment
        if count_without_prefix > 0:
            cursor.execute("UPDATE axes_axeimage SET image = '/app/media/' || image WHERE image NOT LIKE '/app/media/%'")
            self.stdout.write(f"Added /app/media/ prefix to {count_without_prefix} paths")
            fixes_made += count_without_prefix
        
        # Fix paths that have /app/media/ prefix but shouldn't (Django handles this automatically)
        cursor.execute("SELECT COUNT(*) FROM axes_axeimage WHERE image LIKE '/app/media/%'")
        count_with_app_media = cursor.fetchone()[0]
        
        if count_with_app_media > 0:
            cursor.execute("UPDATE axes_axeimage SET image = REPLACE(image, '/app/media/', '')")
            self.stdout.write(f"Removed /app/media/ prefix from {count_with_app_media} paths")
            fixes_made += count_with_app_media
        
        # Fix paths that have media/ prefix but shouldn't (Django adds this automatically)
        cursor.execute("SELECT COUNT(*) FROM axes_axeimage WHERE image LIKE 'media/%'")
        count_with_media_prefix = cursor.fetchone()[0]
        
        if count_with_media_prefix > 0:
            cursor.execute("UPDATE axes_axeimage SET image = REPLACE(image, 'media/', '')")
            self.stdout.write(f"Removed media/ prefix from {count_with_media_prefix} paths")
            fixes_made += count_with_media_prefix
        
        if fixes_made > 0:
            connection.commit()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully fixed {fixes_made} image paths')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No image path issues found')
            )