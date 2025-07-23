from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Återställ databasen till testdata'

    def add_arguments(self, parser):
        parser.add_argument(
            '--axes',
            type=int,
            default=50,
            help='Antal yxor att generera (default: 50)',
        )
        parser.add_argument(
            '--manufacturers',
            type=int,
            default=15,
            help='Antal tillverkare att generera (default: 15)',
        )
        parser.add_argument(
            '--contacts',
            type=int,
            default=25,
            help='Antal kontakter att generera (default: 25)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Återställer till testdata...')
        
        # Rensa all data och generera ny testdata
        call_command(
            'generate_test_data',
            clear=True,
            axes=options['axes'],
            manufacturers=options['manufacturers'],
            contacts=options['contacts']
        )
        
        self.stdout.write(
            self.style.SUCCESS('Databasen har återställts till testdata!')
        ) 