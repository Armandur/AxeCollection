from django.core.management.base import BaseCommand
from axes.models import AxeImageStamp


class Command(BaseCommand):
    help = 'Ta bort alla AxeImageStamp-poster från databasen'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Bekräfta att du vill ta bort alla stämpelmarkeringar',
        )

    def handle(self, *args, **options):
        # Räkna antal poster
        count = AxeImageStamp.objects.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('Inga AxeImageStamp-poster finns i databasen.')
            )
            return
        
        self.stdout.write(
            f'Det finns {count} AxeImageStamp-poster i databasen.'
        )
        
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'Använd --confirm för att bekräfta att du vill ta bort alla stämpelmarkeringar.'
                )
            )
            return
        
        # Ta bort alla poster
        deleted_count = AxeImageStamp.objects.all().delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Framgångsrikt tog bort {deleted_count} AxeImageStamp-poster från databasen.'
            )
        ) 