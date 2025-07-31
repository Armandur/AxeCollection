from django.core.management.base import BaseCommand
from axes.models import AxeImageStamp, AxeStamp, Axe


class Command(BaseCommand):
    help = "Check AxeImageStamp records in the database"

    def handle(self, *args, **options):
        count = AxeImageStamp.objects.count()
        self.stdout.write(f"Total AxeImageStamp records: {count}")

        if count > 0:
            self.stdout.write("\nSample records:")
            for ais in AxeImageStamp.objects.all()[:5]:
                self.stdout.write(f"  {ais}")
                self.stdout.write(f"    Axe: {ais.axe_image.axe.display_id}")
                self.stdout.write(f"    Stamp: {ais.stamp.name}")
                self.stdout.write(
                    f"    Coordinates: x={ais.x_coordinate}, y={ais.y_coordinate}, w={ais.width}, h={ais.height}"
                )
                self.stdout.write(f"    Comment: {ais.comment}")
                self.stdout.write("")
        else:
            self.stdout.write("No AxeImageStamp records found.")

        # Check AxeStamp records
        axe_stamp_count = AxeStamp.objects.count()
        self.stdout.write(f"Total AxeStamp records: {axe_stamp_count}")

        if axe_stamp_count > 0:
            self.stdout.write("\nSample AxeStamp records:")
            for as_obj in AxeStamp.objects.all()[:3]:
                self.stdout.write(f"  {as_obj}")
                # Check if this AxeStamp has any AxeImageStamp records
                image_stamps = AxeImageStamp.objects.filter(
                    stamp=as_obj.stamp, axe_image__axe=as_obj.axe
                )
                self.stdout.write(
                    f"    Associated AxeImageStamp records: {image_stamps.count()}"
                )
                for ais in image_stamps:
                    self.stdout.write(
                        f"      - {ais.axe_image.axe.display_id} image {ais.axe_image.id}: x={ais.x_coordinate}, y={ais.y_coordinate}"
                    )
