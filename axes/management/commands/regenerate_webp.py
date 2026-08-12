import os

from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageOps

from axes.models import AxeImage, ManufacturerImage, StampImage


class Command(BaseCommand):
    help = (
        "Regenererar .webp-versioner av befintliga bilder så att EXIF-rotation "
        "(telefonbilder) tillämpas retroaktivt. Skriver alltid över befintlig "
        "webp och bumpar cache_busting_timestamp så webbläsare inte visar "
        "gamla, felvända bilder ur cachen."
    )

    # convert_rgb speglar respektive modells egen webp-generering, så
    # kommandot producerar samma filer som en vanlig omsparning skulle göra.
    MODEL_CHOICES = {
        "axe": (AxeImage, False),
        "manufacturer": (ManufacturerImage, False),
        "stamp": (StampImage, True),
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Visa vad som skulle göras utan att skriva några filer",
        )
        parser.add_argument(
            "--model",
            choices=sorted(self.MODEL_CHOICES.keys()),
            help="Begränsa till en bildmodell (axe, manufacturer eller stamp)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        model_filter = options.get("model")

        if model_filter:
            models_to_run = {model_filter: self.MODEL_CHOICES[model_filter]}
        else:
            models_to_run = self.MODEL_CHOICES

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run - inget skrivs till disk"))

        for name, (model, convert_rgb) in models_to_run.items():
            self._regenerate(name, model, convert_rgb, dry_run)

    def _regenerate(self, name, model, convert_rgb, dry_run):
        """Skriver om webp:en explicit i stället för att gå via instansens
        save(). Modellernas save() sväljer fel i webp-genereringen
        (except Exception: pass), så en ren retur därifrån skulle inte bevisa
        att filen faktiskt skrevs - då hade sammanfattningen rapporterat
        lyckade regenereringar för bilder som aldrig rörts."""
        regenerated = 0
        skipped = 0
        errors = 0

        for instance in model.objects.all().iterator():
            if not instance.image or not instance.image.name:
                skipped += 1
                continue

            image_path = instance.image.path
            if not os.path.exists(image_path):
                self.stdout.write(
                    self.style.WARNING(
                        f"{name}: hoppar över {model.__name__} (id={instance.pk}) "
                        f"- originalfilen saknas: {image_path}"
                    )
                )
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(f"{name}: skulle regenerera (id={instance.pk})")
                regenerated += 1
                continue

            webp_path = os.path.splitext(image_path)[0] + ".webp"
            try:
                with Image.open(image_path) as img:
                    # Rotera enligt EXIF-orientering (telefonbilder) så webp:en
                    # visas rättvänd - webbläsare auto-roterar JPEG men inte webp
                    img = ImageOps.exif_transpose(img)
                    if convert_rgb and img.mode in ("RGBA", "LA", "P"):
                        img = img.convert("RGB")
                    img.save(webp_path, "WEBP", quality=85)

                # Bumpa cache-busting utan att gå via save(): webp_url:en
                # returnerar ?v=<timestamp>, så en oförändrad timestamp gör att
                # besökaren fortsätter få den gamla, felvända bilden ur cachen.
                model.objects.filter(pk=instance.pk).update(
                    cache_busting_timestamp=timezone.now()
                )
                regenerated += 1
            except Exception as exc:
                errors += 1
                self.stderr.write(
                    self.style.ERROR(
                        f"{name}: fel vid regenerering av {model.__name__} "
                        f"(id={instance.pk}, path={image_path}): {exc}"
                    )
                )

        self._write_summary(name, regenerated, skipped, errors, dry_run)

    def _write_summary(self, name, regenerated, skipped, errors, dry_run):
        verb = "skulle regenereras" if dry_run else "regenererade"
        style = self.style.ERROR if errors else self.style.SUCCESS
        self.stdout.write(
            style(
                f"{name}: {regenerated} {verb}, {skipped} hoppade över, "
                f"{errors} fel."
            )
        )
