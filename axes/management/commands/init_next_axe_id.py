from django.core.management.base import BaseCommand
from axes.models import Axe, NextAxeID
from django.db import models


class Command(BaseCommand):
    help = "Initiera nästa yx-ID baserat på befintliga yxor."

    def handle(self, *args, **options):
        # Hitta högsta befintliga ID:t
        max_id = Axe.objects.all().aggregate(max_id=models.Max("id"))["max_id"]

        if max_id is None:
            next_id = 1
        else:
            next_id = max_id + 1

        # Sätt nästa ID
        obj, created = NextAxeID.objects.get_or_create(
            id=1, defaults={"next_id": next_id}
        )
        if not created:
            obj.next_id = next_id
            obj.save()

        self.stdout.write(self.style.SUCCESS(f"Nästa yx-ID satt till {next_id}"))
