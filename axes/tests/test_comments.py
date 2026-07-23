from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from axes.models import Comment, Settings
from axes.tests.factories import make_axe, make_manufacturer, make_stamp


class CommentModelTest(TestCase):
    def test_clean_requires_exactly_one_target(self):
        axe = make_axe()
        manufacturer = make_manufacturer()

        with self.assertRaises(ValidationError):
            Comment(body="Test").full_clean()

        with self.assertRaises(ValidationError):
            Comment(axe=axe, manufacturer=manufacturer, body="Test").full_clean()

        # Exakt en satt (axe) ska passera clean() utan att höja ValidationError
        Comment(axe=axe, body="Test").full_clean()


class SubmitAxeCommentTest(TestCase):
    def setUp(self):
        cache.clear()
        self.axe = make_axe()
        self.url = reverse("submit_axe_comment", args=[self.axe.pk])

    def tearDown(self):
        cache.clear()

    def test_submit_creates_pending_comment(self):
        response = self.client.post(
            self.url, {"author_name": "Kalle", "body": "Fin yxa!", "website": ""}
        )
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(axe=self.axe)
        self.assertEqual(comment.status, "PENDING")
        self.assertEqual(comment.body, "Fin yxa!")

    def test_pending_comment_not_visible_on_axe_detail(self):
        self.client.post(
            self.url,
            {"author_name": "Kalle", "body": "Väntande kommentar", "website": ""},
        )
        response = self.client.get(reverse("axe_detail", args=[self.axe.pk]))
        self.assertNotIn(b"V\xc3\xa4ntande kommentar", response.content)

    def test_approved_comment_visible_on_axe_detail(self):
        Comment.objects.create(
            axe=self.axe, body="Godkänd kommentar", status="APPROVED"
        )
        response = self.client.get(reverse("axe_detail", args=[self.axe.pk]))
        self.assertIn("Godkänd kommentar".encode(), response.content)

    def test_rejected_and_spam_comments_not_visible(self):
        Comment.objects.create(axe=self.axe, body="Avvisad text", status="REJECTED")
        Comment.objects.create(axe=self.axe, body="Skräptext", status="SPAM")
        response = self.client.get(reverse("axe_detail", args=[self.axe.pk]))
        self.assertNotIn("Avvisad text".encode(), response.content)
        self.assertNotIn("Skräptext".encode(), response.content)

    def test_honeypot_filled_marks_spam_but_returns_success(self):
        response = self.client.post(
            self.url,
            {
                "author_name": "Bot",
                "body": "Köp billiga skor",
                "website": "http://spam.com",
            },
        )
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(axe=self.axe)
        self.assertEqual(comment.status, "SPAM")

    def test_honeypot_ajax_returns_same_success_response_as_normal(self):
        normal = self.client.post(
            self.url,
            {"author_name": "A", "body": "Normal kommentar", "website": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        cache.clear()
        honeypot = self.client.post(
            self.url,
            {"author_name": "B", "body": "Bot-kommentar", "website": "spam"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(normal.status_code, 200)
        self.assertEqual(honeypot.status_code, 200)
        self.assertEqual(normal.json(), honeypot.json())

    def test_rate_limit_blocks_after_max_submits(self):
        for i in range(5):
            self.client.post(
                self.url, {"author_name": "X", "body": f"Kommentar {i}", "website": ""}
            )
        self.assertEqual(Comment.objects.filter(axe=self.axe).count(), 5)

        self.client.post(
            self.url, {"author_name": "X", "body": "Sjätte kommentaren", "website": ""}
        )
        self.assertEqual(Comment.objects.filter(axe=self.axe).count(), 5)

    def test_comments_disabled_rejects_submission(self):
        settings = Settings.get_settings()
        settings.comments_enabled_public = False
        settings.save()

        self.client.post(
            self.url, {"author_name": "X", "body": "Ska inte sparas", "website": ""}
        )
        self.assertEqual(Comment.objects.filter(axe=self.axe).count(), 0)

    def test_xss_in_comment_body_is_escaped(self):
        Comment.objects.create(
            axe=self.axe, body="<script>alert(1)</script>", status="APPROVED"
        )
        response = self.client.get(reverse("axe_detail", args=[self.axe.pk]))
        content = response.content.decode()
        self.assertNotIn("<script>alert(1)</script>", content)
        self.assertIn("&lt;script&gt;", content)


class SubmitManufacturerCommentTest(TestCase):
    def setUp(self):
        cache.clear()
        self.manufacturer = make_manufacturer()

    def tearDown(self):
        cache.clear()

    def test_approved_comment_visible_on_manufacturer_detail(self):
        Comment.objects.create(
            manufacturer=self.manufacturer,
            body="Godkänd tillverkarkommentar",
            status="APPROVED",
        )
        response = self.client.get(
            reverse("manufacturer_detail", args=[self.manufacturer.pk])
        )
        self.assertIn("Godkänd tillverkarkommentar".encode(), response.content)

    def test_submit_creates_pending_manufacturer_comment(self):
        url = reverse("submit_manufacturer_comment", args=[self.manufacturer.pk])
        response = self.client.post(
            url, {"author_name": "Kalle", "body": "Fin tillverkare!", "website": ""}
        )
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(manufacturer=self.manufacturer)
        self.assertEqual(comment.status, "PENDING")


class SubmitStampCommentTest(TestCase):
    def setUp(self):
        cache.clear()
        self.stamp = make_stamp()
        self.url = reverse("submit_stamp_comment", args=[self.stamp.pk])

    def tearDown(self):
        cache.clear()

    def test_submit_creates_pending_comment_not_visible_on_stamp_detail(self):
        response = self.client.post(
            self.url,
            {
                "author_name": "Kalle",
                "body": "Väntande stämpelkommentar",
                "website": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(stamp=self.stamp)
        self.assertEqual(comment.status, "PENDING")

        detail_response = self.client.get(reverse("stamp_detail", args=[self.stamp.pk]))
        self.assertNotIn("Väntande stämpelkommentar".encode(), detail_response.content)

    def test_approved_comment_visible_on_stamp_detail(self):
        Comment.objects.create(
            stamp=self.stamp, body="Godkänd stämpelkommentar", status="APPROVED"
        )
        response = self.client.get(reverse("stamp_detail", args=[self.stamp.pk]))
        self.assertIn("Godkänd stämpelkommentar".encode(), response.content)


class CommentModerationViewTest(TestCase):
    def setUp(self):
        cache.clear()
        self.axe = make_axe()

    def tearDown(self):
        cache.clear()

    def test_moderation_view_requires_login(self):
        response = self.client.get(reverse("comment_moderation"))
        self.assertEqual(response.status_code, 302)

    def test_moderate_comment_approve(self):
        user = User.objects.create_user(username="admin", password="pass1234")
        self.client.force_login(user)
        comment = Comment.objects.create(axe=self.axe, body="Väntar på beslut")

        response = self.client.post(
            reverse("moderate_comment", args=[comment.pk]), {"action": "approve"}
        )
        self.assertEqual(response.status_code, 200)

        comment.refresh_from_db()
        self.assertEqual(comment.status, "APPROVED")
        self.assertEqual(comment.moderated_by, user)
        self.assertIsNotNone(comment.moderated_at)
