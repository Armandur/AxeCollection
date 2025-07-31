from django.core.management.base import BaseCommand
from axes.models import AxeStamp, Axe


class Command(BaseCommand):
    help = (
        "Kontrollera AxeStamp-värden för att identifiera problem med uncertainty_level"
    )

    def handle(self, *args, **options):
        self.stdout.write("Kontrollerar AxeStamp-värden...")

        # Hämta alla AxeStamp-objekt
        axe_stamps = AxeStamp.objects.all().select_related("axe", "stamp")

        self.stdout.write(f"Hittade {axe_stamps.count()} AxeStamp-objekt")

        for axe_stamp in axe_stamps:
            self.stdout.write(
                f"\nYxa {axe_stamp.axe.display_id} - Stämpel: {axe_stamp.stamp.name}"
            )
            self.stdout.write(
                f"  uncertainty_level (raw): '{axe_stamp.uncertainty_level}'"
            )
            self.stdout.write(
                f"  get_uncertainty_level_display(): '{axe_stamp.get_uncertainty_level_display()}'"
            )

            # Kontrollera om värdet är giltigt
            valid_choices = [choice[0] for choice in AxeStamp.UNCERTAINTY_CHOICES]
            if axe_stamp.uncertainty_level not in valid_choices:
                self.stdout.write(
                    f"  VARNING: Ogiltigt värde! Giltiga värden: {valid_choices}"
                )
            else:
                self.stdout.write(f"  ✓ Giltigt värde")

        # Kontrollera specifikt för yxor 52 och 53
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("SPECIFIKT FÖR YXOR 52 OCH 53:")

        for axe_id in [52, 53]:
            try:
                axe = Axe.objects.get(id=axe_id)
                axe_stamps = AxeStamp.objects.filter(axe=axe).select_related("stamp")

                self.stdout.write(f"\nYxa {axe.display_id}:")
                for axe_stamp in axe_stamps:
                    self.stdout.write(f"  Stämpel: {axe_stamp.stamp.name}")
                    self.stdout.write(
                        f"  uncertainty_level: '{axe_stamp.uncertainty_level}'"
                    )
                    self.stdout.write(
                        f"  display: '{axe_stamp.get_uncertainty_level_display()}'"
                    )

            except Axe.DoesNotExist:
                self.stdout.write(f"Yxa {axe_id} finns inte")

        self.stdout.write("\nKontroll slutförd!")
