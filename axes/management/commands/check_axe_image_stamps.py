from django.core.management.base import BaseCommand
from axes.models import StampImage, AxeStamp, Axe


class Command(BaseCommand):
    help = "Check AxeImageStamp records in the database"

    def handle(self, *args, **options):
        count = StampImage.objects.count()
        self.stdout.write(f"Total AxeImageStamp records: {count}")

        if count > 0:
            self.stdout.write("\nSample AxeImageStamp records:")
            for si in StampImage.objects.all()[:5]:
                self.stdout.write(f"  {si}")
                if si.axe_image:
                    self.stdout.write(f"    Axe: {si.axe_image.axe.display_id}")
                self.stdout.write(f"    Stamp: {si.stamp.name}")
                if si.has_coordinates:
                    self.stdout.write(
                        f"    Coordinates: x={si.x_coordinate}, y={si.y_coordinate}, w={si.width}, h={si.height}"
                    )
                self.stdout.write(f"    Comment: {si.comment}")
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
                # Check if this AxeStamp has any StampImage records
                image_stamps = StampImage.objects.filter(
                    stamp=as_obj.stamp, axe_image__axe=as_obj.axe
                )
                self.stdout.write(
                    f"    Associated AxeImageStamp records: {image_stamps.count()}"
                )
                for si in image_stamps:
                    if si.axe_image and si.has_coordinates:
                        self.stdout.write(
                            f"      - {si.axe_image.axe.display_id} image {si.axe_image.id}: x={si.x_coordinate}, y={si.y_coordinate}"
                        )
