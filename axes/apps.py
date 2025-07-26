from django.apps import AppConfig


class AxesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'axes'

    def ready(self):
        """Run when the app is ready"""
        # Aktivera WAL-mode för SQLite
        from django.db import connection
        if connection.vendor == 'sqlite':
            try:
                with connection.cursor() as cursor:
                    cursor.execute('PRAGMA journal_mode=WAL;')
            except Exception:
                # Logga eller ignorera om det inte går (t.ex. under migrationer)
                pass
