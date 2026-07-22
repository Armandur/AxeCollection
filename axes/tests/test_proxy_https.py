"""Tester för att Django respekterar X-Forwarded-Proto bakom proxy (TASK-312).

Utan SECURE_PROXY_SSL_HEADER litar Django inte på headern från proxyn och
request.is_secure()/build_absolute_uri() blir alltid http, vilket gjorde
att og:url/og:image renderades som http:// bakom en https-terminerande
reverse-proxy.
"""

from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from axes.models import Axe, AxeImage, Manufacturer, Settings


@override_settings(SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"))
class ProxyHttpsOgContextTest(TestCase):
    """Testar _build_og_context (via axe_detail-vyn) med X-Forwarded-Proto."""

    def setUp(self):
        self.client = Client()
        Settings.objects.create(
            show_only_received_axes_public=False,
        )
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        self.axe = Axe.objects.create(
            manufacturer=self.manufacturer, model="Test Axe", status="MOTTAGEN"
        )
        self.image = AxeImage.objects.create(
            axe=self.axe,
            image=SimpleUploadedFile("test.jpg", b"fake_image_content"),
            order=1,
        )

    def _get(self, https_header):
        kwargs = {}
        if https_header:
            kwargs["HTTP_X_FORWARDED_PROTO"] = "https"
        return self.client.get(f"/yxor/{self.axe.id}/", **kwargs)

    def test_og_url_is_https_with_forwarded_proto_header(self):
        """Med X-Forwarded-Proto: https ska og:url bli https://."""
        response = self._get(https_header=True)
        self.assertEqual(response.status_code, 200)
        og = response.context["og"]
        self.assertTrue(og["url"].startswith("https://"))

    def test_og_image_is_https_with_forwarded_proto_header(self):
        """Med X-Forwarded-Proto: https ska og:image bli https://."""
        response = self._get(https_header=True)
        og = response.context["og"]
        self.assertIsNotNone(og["image"])
        self.assertTrue(og["image"].startswith("https://"))

    def test_og_url_is_http_without_forwarded_proto_header(self):
        """Utan headern (t.ex. direktanrop) ska build_absolute_uri falla
        tillbaka på http, så vi vet att https-fallet verkligen styrs av
        headern och inte råkar bli https av andra skäl."""
        response = self._get(https_header=False)
        og = response.context["og"]
        self.assertTrue(og["url"].startswith("http://"))
