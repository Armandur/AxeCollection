from django.core.management.base import BaseCommand
from axes.utils.tradera_parser import parse_tradera_url
import json


class Command(BaseCommand):
    help = 'Testa Tradera URL-parser'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='Tradera-auktions-URL att testa')

    def handle(self, *args, **options):
        url = options['url']
        
        self.stdout.write(f"Testar Tradera-parser med URL: {url}")
        
        try:
            result = parse_tradera_url(url)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Parsning lyckades!')
            )
            
            # Skriv ut resultatet i JSON-format
            self.stdout.write("\nExtraherad data:")
            self.stdout.write(json.dumps(result, indent=2, ensure_ascii=False))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Fel vid parsning: {e}')
            ) 