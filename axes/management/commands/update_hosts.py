from django.core.management.base import BaseCommand
from axes.models import Settings
import os


class Command(BaseCommand):
    help = "Uppdatera ALLOWED_HOSTS och CSRF_TRUSTED_ORIGINS från databasen"

    def handle(self, *args, **options):
        try:
            # Hämta inställningar från databasen
            settings_obj = Settings.get_settings()

            # Uppdatera ALLOWED_HOSTS
            if settings_obj.external_hosts:
                # Lägg till hosts från databasen till miljövariabeln
                current_env_hosts = os.environ.get("ALLOWED_HOSTS", "")
                db_hosts = settings_obj.external_hosts

                if current_env_hosts:
                    # Kombinera befintliga och nya hosts
                    combined_hosts = f"{current_env_hosts},{db_hosts}"
                else:
                    combined_hosts = db_hosts

                os.environ["ALLOWED_HOSTS"] = combined_hosts
                self.stdout.write(
                    self.style.SUCCESS(f"ALLOWED_HOSTS uppdaterad: {combined_hosts}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("Inga externa hosts konfigurerade i databasen")
                )

            # Uppdatera CSRF_TRUSTED_ORIGINS
            if settings_obj.external_csrf_origins:
                # Lägg till origins från databasen till miljövariabeln
                current_env_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
                db_origins = settings_obj.external_csrf_origins

                if current_env_origins:
                    # Kombinera befintliga och nya origins
                    combined_origins = f"{current_env_origins},{db_origins}"
                else:
                    combined_origins = db_origins

                os.environ["CSRF_TRUSTED_ORIGINS"] = combined_origins
                self.stdout.write(
                    self.style.SUCCESS(
                        f"CSRF_TRUSTED_ORIGINS uppdaterad: {combined_origins}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "Inga externa CSRF-origins konfigurerade i databasen"
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Fel vid uppdatering av hosts: {e}"))
