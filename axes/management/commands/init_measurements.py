from django.core.management.base import BaseCommand
from axes.models import MeasurementType, MeasurementTemplate, MeasurementTemplateItem

class Command(BaseCommand):
    help = 'Initiera standardmåtttyper och måttmallar'

    def handle(self, *args, **options):
        self.stdout.write('Skapar måtttyper...')
        
        # Skapa måtttyper
        measurement_types = [
            {'name': 'Bladlängd', 'unit': 'mm', 'sort_order': 1},
            {'name': 'Bladbredd', 'unit': 'mm', 'sort_order': 2},
            {'name': 'Skaftlängd', 'unit': 'mm', 'sort_order': 3},
            {'name': 'Skaftbredd', 'unit': 'mm', 'sort_order': 4},
            {'name': 'Total längd', 'unit': 'mm', 'sort_order': 5},
            {'name': 'Vikt', 'unit': 'gram', 'sort_order': 6},
            {'name': 'Bladvikt', 'unit': 'gram', 'sort_order': 7},
            {'name': 'Skaftvikt', 'unit': 'gram', 'sort_order': 8},
            {'name': 'Handtag', 'unit': 'mm', 'sort_order': 9},
            {'name': 'Bladtjocklek', 'unit': 'mm', 'sort_order': 10},
            {'name': 'Öga', 'unit': 'mm', 'sort_order': 11},
        ]
        
        created_types = {}
        for mt_data in measurement_types:
            mt, created = MeasurementType.objects.get_or_create(
                name=mt_data['name'],
                defaults={
                    'unit': mt_data['unit'],
                    'sort_order': mt_data['sort_order'],
                    'description': f'Standard måtttyp för {mt_data["name"].lower()}'
                }
            )
            created_types[mt.name] = mt
            if created:
                self.stdout.write(f'  Skapade måtttyp: {mt.name} ({mt.unit})')
            else:
                self.stdout.write(f'  Måtttyp finns redan: {mt.name} ({mt.unit})')
        
        self.stdout.write('\nSkapar måttmallar...')
        
        # Skapa måttmallar
        templates_data = [
            {
                'name': 'Standard yxa',
                'description': 'Grundläggande mått för de flesta yxor',
                'sort_order': 1,
                'measurements': ['Bladlängd', 'Bladbredd', 'Skaftlängd', 'Total längd', 'Vikt']
            },
            {
                'name': 'Fällkniv',
                'description': 'Mått för fällknivar',
                'sort_order': 2,
                'measurements': ['Bladlängd', 'Bladbredd', 'Handtag', 'Vikt']
            },
            {
                'name': 'Köksyxa',
                'description': 'Mått för köksyxor',
                'sort_order': 3,
                'measurements': ['Bladlängd', 'Bladbredd', 'Skaftlängd', 'Vikt']
            },
            {
                'name': 'Detaljerad yxa',
                'description': 'Omfattande mått för detaljerad dokumentation',
                'sort_order': 4,
                'measurements': ['Bladlängd', 'Bladbredd', 'Bladtjocklek', 'Skaftlängd', 'Skaftbredd', 'Total längd', 'Vikt', 'Bladvikt', 'Skaftvikt', 'Öga']
            }
        ]
        
        for template_data in templates_data:
            template, created = MeasurementTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'sort_order': template_data['sort_order']
                }
            )
            
            if created:
                self.stdout.write(f'  Skapade mall: {template.name}')
                
                # Lägg till mått i mallen
                for i, measurement_name in enumerate(template_data['measurements']):
                    if measurement_name in created_types:
                        MeasurementTemplateItem.objects.create(
                            template=template,
                            measurement_type=created_types[measurement_name],
                            sort_order=i + 1
                        )
                        self.stdout.write(f'    - Lade till: {measurement_name}')
            else:
                self.stdout.write(f'  Mall finns redan: {template.name}')
        
        self.stdout.write(self.style.SUCCESS('\nInitiering av måtttyper och mallar slutförd!')) 