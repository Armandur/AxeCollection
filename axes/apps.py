from django.apps import AppConfig


class AxesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'axes'

    def ready(self):
        """Run when the app is ready"""
        # Import here to avoid circular imports
        from django.core.management import call_command
        from django.db import connection
        
        try:
            # Check if we're in a management command (to avoid running during migrations)
            import sys
            if 'manage.py' in sys.argv and any(cmd in sys.argv for cmd in ['migrate', 'makemigrations', 'collectstatic']):
                return
                
            # Only run if we have a database connection and the table exists
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='axes_axeimage'")
                if cursor.fetchone():
                    # Run the fix command automatically
                    call_command('fix_image_paths', verbosity=0)
        except Exception as e:
            # Silently fail if there are any issues (e.g., during initial setup)
            pass
