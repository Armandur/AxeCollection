from django.apps import AppConfig


class AxesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'axes'

    def ready(self):
        """Run when the app is ready"""
        # No automatic image path fixing - only done during backup restore
        pass
