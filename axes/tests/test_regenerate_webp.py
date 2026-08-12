"""Tester för management-kommandot regenerate_webp.

Bevisar att kommandot faktiskt tillämpar EXIF-rotation retroaktivt på
befintliga webp-filer (inte bara att det kör utan att krascha), och att
cache_busting_timestamp bumpas så webbläsare inte visar en gammal,
felvänd bild ur cachen.
"""

import io
import os
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from axes.models import AxeImage, Axe, Manufacturer, ManufacturerImage, StampImage
from axes.tests.factories import make_stamp


def _make_rotated_jpeg_bytes(width=40, height=20):
    """Skapar en JPEG bredare än hög med EXIF-orientering 6 (90 grader).

    Rättvänd (dvs. med exif_transpose tillämpad) ska bilden bli
    height x width - motsatta dimensioner mot originalets råpixlar.
    """
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), "blue")
    exif = img.getexif()
    exif[0x0112] = 6  # Orientation
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


def _write_unrotated_webp(webp_path, width=40, height=20):
    """Skriver en webp med originalets (felvända) dimensioner, som om den
    genererats innan exif_transpose fanns med."""
    img = Image.new("RGB", (width, height), "blue")
    img.save(webp_path, "WEBP", quality=85)


class RegenerateWebpAxeImageTest(TestCase):
    def setUp(self):
        self.media_root_ctx = tempfile.TemporaryDirectory()
        self.media_root = self.media_root_ctx.name
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()

        manufacturer = Manufacturer.objects.create(name="Test")
        axe = Axe.objects.create(manufacturer=manufacturer, model="Test Axe")
        self.axe_image = AxeImage.objects.create(
            axe=axe,
            image=SimpleUploadedFile(
                "axe_exif.jpg",
                _make_rotated_jpeg_bytes(),
                content_type="image/jpeg",
            ),
        )

        # Skriv över den korrekt genererade webp:en med en felvänd variant,
        # så utgångsläget matchar produktionsdata (webp med originalets
        # dimensioner, inte de roterade).
        self.webp_path = os.path.splitext(self.axe_image.image.path)[0] + ".webp"
        _write_unrotated_webp(self.webp_path)
        self.old_timestamp = AxeImage.objects.get(
            pk=self.axe_image.pk
        ).cache_busting_timestamp

    def tearDown(self):
        self.override.disable()
        self.media_root_ctx.cleanup()

    def test_regenerate_applies_exif_rotation(self):
        assert os.path.exists(self.webp_path), "utgångs-webp måste finnas"
        # Utgångsläge: webp har originalets (felvända) dimensioner
        self.assertEqual(Image.open(self.webp_path).size, (40, 20))

        call_command("regenerate_webp", "--model", "axe")

        self.assertTrue(os.path.exists(self.webp_path))
        with Image.open(self.webp_path) as img:
            self.assertEqual(img.size, (20, 40))

        self.axe_image.refresh_from_db()
        self.assertGreater(self.axe_image.cache_busting_timestamp, self.old_timestamp)

    def test_dry_run_does_not_write(self):
        assert os.path.exists(self.webp_path)
        mtime_before = os.path.getmtime(self.webp_path)

        call_command("regenerate_webp", "--model", "axe", "--dry-run")

        mtime_after = os.path.getmtime(self.webp_path)
        self.assertEqual(mtime_before, mtime_after)
        with Image.open(self.webp_path) as img:
            self.assertEqual(img.size, (40, 20))

        self.axe_image.refresh_from_db()
        self.assertEqual(self.axe_image.cache_busting_timestamp, self.old_timestamp)


class RegenerateWebpManufacturerImageTest(TestCase):
    def setUp(self):
        self.media_root_ctx = tempfile.TemporaryDirectory()
        self.media_root = self.media_root_ctx.name
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()

        manufacturer = Manufacturer.objects.create(name="Test tillverkare")
        self.manufacturer_image = ManufacturerImage.objects.create(
            manufacturer=manufacturer,
            image=SimpleUploadedFile(
                "manufacturer_exif.jpg",
                _make_rotated_jpeg_bytes(),
                content_type="image/jpeg",
            ),
        )

        self.webp_path = (
            os.path.splitext(self.manufacturer_image.image.path)[0] + ".webp"
        )
        _write_unrotated_webp(self.webp_path)
        self.old_timestamp = ManufacturerImage.objects.get(
            pk=self.manufacturer_image.pk
        ).cache_busting_timestamp

    def tearDown(self):
        self.override.disable()
        self.media_root_ctx.cleanup()

    def test_regenerate_applies_exif_rotation(self):
        assert os.path.exists(self.webp_path), "utgångs-webp måste finnas"
        self.assertEqual(Image.open(self.webp_path).size, (40, 20))

        call_command("regenerate_webp", "--model", "manufacturer")

        with Image.open(self.webp_path) as img:
            self.assertEqual(img.size, (20, 40))

        self.manufacturer_image.refresh_from_db()
        self.assertGreater(
            self.manufacturer_image.cache_busting_timestamp, self.old_timestamp
        )


class RegenerateWebpStampImageTest(TestCase):
    def setUp(self):
        self.media_root_ctx = tempfile.TemporaryDirectory()
        self.media_root = self.media_root_ctx.name
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()

        stamp = make_stamp()
        self.stamp_image = StampImage.objects.create(
            stamp=stamp,
            image_type="standalone",
            image=SimpleUploadedFile(
                "stamp_exif.jpg",
                _make_rotated_jpeg_bytes(),
                content_type="image/jpeg",
            ),
        )

        self.webp_path = os.path.splitext(self.stamp_image.image.path)[0] + ".webp"
        # StampImage._create_webp_version() skapar bara webp om filen saknas
        # sedan innan - eftersom den redan finns (skapad utan rotation-fix
        # historiskt sett) simulerar vi det genom att skriva över den.
        _write_unrotated_webp(self.webp_path)
        self.old_timestamp = StampImage.objects.get(
            pk=self.stamp_image.pk
        ).cache_busting_timestamp

    def tearDown(self):
        self.override.disable()
        self.media_root_ctx.cleanup()

    def test_regenerate_applies_exif_rotation(self):
        assert os.path.exists(self.webp_path), "utgångs-webp måste finnas"
        self.assertEqual(Image.open(self.webp_path).size, (40, 20))

        call_command("regenerate_webp", "--model", "stamp")

        with Image.open(self.webp_path) as img:
            self.assertEqual(img.size, (20, 40))

        self.stamp_image.refresh_from_db()
        self.assertGreater(self.stamp_image.cache_busting_timestamp, self.old_timestamp)

    def test_dry_run_does_not_write(self):
        assert os.path.exists(self.webp_path)
        mtime_before = os.path.getmtime(self.webp_path)

        call_command("regenerate_webp", "--model", "stamp", "--dry-run")

        mtime_after = os.path.getmtime(self.webp_path)
        self.assertEqual(mtime_before, mtime_after)
        with Image.open(self.webp_path) as img:
            self.assertEqual(img.size, (40, 20))

        self.stamp_image.refresh_from_db()
        self.assertEqual(self.stamp_image.cache_busting_timestamp, self.old_timestamp)


class RegenerateWebpMissingOriginalTest(TestCase):
    """Bilder utan originalfil på disk ska hoppas över, inte krascha körningen."""

    def setUp(self):
        self.media_root_ctx = tempfile.TemporaryDirectory()
        self.media_root = self.media_root_ctx.name
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()

        manufacturer = Manufacturer.objects.create(name="Test")
        axe = Axe.objects.create(manufacturer=manufacturer, model="Test Axe")
        self.axe_image = AxeImage.objects.create(
            axe=axe,
            image=SimpleUploadedFile(
                "will_be_deleted.jpg",
                _make_rotated_jpeg_bytes(),
                content_type="image/jpeg",
            ),
        )
        # Ta bort originalfilen från disk för att simulera äldre, saknad data
        os.remove(self.axe_image.image.path)

    def tearDown(self):
        self.override.disable()
        self.media_root_ctx.cleanup()

    def test_missing_original_is_skipped_without_crash(self):
        out = io.StringIO()
        call_command("regenerate_webp", "--model", "axe", stdout=out)
        self.assertIn("1 hoppade över", out.getvalue())


class RegenerateWebpCorruptOriginalTest(TestCase):
    """En oläsbar originalfil ska räknas som FEL, inte som regenererad.

    Modellernas save() sväljer webp-fel tyst, så ett kommando som räknar
    lyckade regenereringar utifrån att save() returnerade skulle rapportera
    "1 regenererade, 0 fel" här - för en bild där ingen webp skrevs.
    """

    def setUp(self):
        self.media_root_ctx = tempfile.TemporaryDirectory()
        self.media_root = self.media_root_ctx.name
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()

        manufacturer = Manufacturer.objects.create(name="Test")
        axe = Axe.objects.create(manufacturer=manufacturer, model="Test Axe")
        self.axe_image = AxeImage.objects.create(
            axe=axe,
            image=SimpleUploadedFile(
                "corrupt.jpg",
                _make_rotated_jpeg_bytes(),
                content_type="image/jpeg",
            ),
        )
        # Originalfilen finns kvar på disk men går inte att avkoda
        with open(self.axe_image.image.path, "wb") as fh:
            fh.write(b"inte en bild")
        self.old_timestamp = AxeImage.objects.get(
            pk=self.axe_image.pk
        ).cache_busting_timestamp

    def tearDown(self):
        self.override.disable()
        self.media_root_ctx.cleanup()

    def test_unreadable_original_counts_as_error(self):
        assert os.path.exists(self.axe_image.image.path), "originalet måste finnas"
        out, err = io.StringIO(), io.StringIO()

        call_command("regenerate_webp", "--model", "axe", stdout=out, stderr=err)

        self.assertIn("0 regenererade", out.getvalue())
        self.assertIn("1 fel", out.getvalue())
        self.assertIn(str(self.axe_image.pk), err.getvalue())

        # Cache-busting ska inte bumpas för en bild som inte regenererades
        self.axe_image.refresh_from_db()
        self.assertEqual(self.axe_image.cache_busting_timestamp, self.old_timestamp)
