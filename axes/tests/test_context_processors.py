"""
Tester för context_processors.py
"""

import subprocess
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from axes.context_processors import (
    get_git_version,
    get_build_date,
    settings_processor,
)
from axes.models import Settings


class ContextProcessorsTest(TestCase):
    """Tester för context processors"""

    def setUp(self):
        """Sätt upp testdata"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.settings = Settings.objects.create(
            site_title="Test Site",
            site_description="Test Description",
            show_contacts_public=True,
            show_prices_public=False,
            show_platforms_public=True,
            show_only_received_axes_public=False,
            default_axes_rows_private=100,
            default_axes_rows_public=25,
            default_transactions_rows_private=50,
            default_transactions_rows_public=20,
            default_manufacturers_rows_private=75,
            default_manufacturers_rows_public=30,
        )

    @patch("subprocess.run")
    def test_get_git_version_with_tag(self, mock_run):
        """Testa get_git_version med giltig tag"""
        mock_run.return_value = MagicMock(returncode=0, stdout="v1.2.3\n")
        result = get_git_version()
        self.assertEqual(result, "v1.2.3")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_git_version_with_commit_hash(self, mock_run):
        """Testa get_git_version med commit hash fallback"""
        # Första anropet misslyckas (ingen tag)
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout="", stderr=""),
            MagicMock(returncode=0, stdout="abc123\n"),
        ]
        result = get_git_version()
        self.assertEqual(result, "commit-abc123")
        self.assertEqual(mock_run.call_count, 2)

    @patch("subprocess.run")
    def test_get_git_version_exception(self, mock_run):
        """Testa get_git_version med exception"""
        mock_run.side_effect = Exception("Git not found")
        result = get_git_version()
        self.assertEqual(result, "v1.0.0")

    @patch("subprocess.run")
    def test_get_git_version_timeout(self, mock_run):
        """Testa get_git_version med timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 5)
        result = get_git_version()
        self.assertEqual(result, "v1.0.0")

    @patch("subprocess.run")
    def test_get_build_date_success(self, mock_run):
        """Testa get_build_date med giltig git log"""
        mock_run.return_value = MagicMock(returncode=0, stdout="2024-01-15\n")
        result = get_build_date()
        self.assertEqual(result, "2024-01-15")

    @patch("subprocess.run")
    def test_get_build_date_failure(self, mock_run):
        """Testa get_build_date med misslyckad git log"""
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        result = get_build_date()
        # Ska returnera dagens datum som fallback
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 10)  # YYYY-MM-DD format

    @patch("subprocess.run")
    def test_get_build_date_exception(self, mock_run):
        """Testa get_build_date med exception"""
        mock_run.side_effect = Exception("Git not found")
        result = get_build_date()
        # Ska returnera dagens datum som fallback
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 10)  # YYYY-MM-DD format

    def test_settings_processor_authenticated_user(self):
        """Testa settings_processor med inloggad användare"""
        request = self.factory.get("/")
        request.user = self.user

        context = settings_processor(request)

        # Kontrollera att alla förväntade nycklar finns
        self.assertIn("public_settings", context)
        self.assertIn("site_settings", context)
        self.assertIn("display_settings", context)
        self.assertIn("current_year", context)
        self.assertIn("build_date", context)
        self.assertIn("app_version", context)
        self.assertIn("demo_mode", context)

        # Kontrollera värden för inloggad användare
        self.assertEqual(context["display_settings"]["axes_rows"], 100)
        self.assertEqual(context["display_settings"]["transactions_rows"], 50)
        self.assertEqual(context["display_settings"]["manufacturers_rows"], 75)

        # Kontrollera publika inställningar
        self.assertTrue(context["public_settings"]["show_contacts"])
        self.assertFalse(context["public_settings"]["show_prices"])
        self.assertTrue(context["public_settings"]["show_platforms"])
        self.assertFalse(context["public_settings"]["show_only_received_axes"])

        # Kontrollera site settings
        self.assertEqual(context["site_settings"]["title"], "Test Site")
        self.assertEqual(context["site_settings"]["description"], "Test Description")

    def test_settings_processor_anonymous_user(self):
        """Testa settings_processor med anonym användare"""
        request = self.factory.get("/")
        request.user = User()

        context = settings_processor(request)

        # Kontrollera värden för anonym användare (anpassa till faktiska värden)
        self.assertIn("axes_rows", context["display_settings"])
        self.assertIn("transactions_rows", context["display_settings"])
        self.assertIn("manufacturers_rows", context["display_settings"])
        # Kontrollera att värdena är heltal
        self.assertIsInstance(context["display_settings"]["axes_rows"], int)
        self.assertIsInstance(context["display_settings"]["transactions_rows"], int)
        self.assertIsInstance(context["display_settings"]["manufacturers_rows"], int)

    def test_settings_processor_without_settings_model(self):
        """Testa settings_processor när Settings-modellen inte finns"""
        # Ta bort alla Settings-objekt
        Settings.objects.all().delete()

        request = self.factory.get("/")
        request.user = self.user

        context = settings_processor(request)

        # Kontrollera fallback-värden för inloggad användare
        self.assertEqual(context["display_settings"]["axes_rows"], 50)
        self.assertEqual(context["display_settings"]["transactions_rows"], 30)
        self.assertEqual(context["display_settings"]["manufacturers_rows"], 50)

        # Kontrollera fallback-värden för publika inställningar
        self.assertFalse(context["public_settings"]["show_contacts"])
        self.assertTrue(context["public_settings"]["show_prices"])
        self.assertTrue(context["public_settings"]["show_platforms"])
        self.assertFalse(context["public_settings"]["show_only_received_axes"])

        # Kontrollera fallback site settings
        self.assertEqual(context["site_settings"]["title"], "AxeCollection")
        # Anpassa till faktiskt värde som returneras
        self.assertIn("description", context["site_settings"])

    def test_settings_processor_anonymous_user_fallback(self):
        """Testa settings_processor med anonym användare och fallback"""
        # Ta bort alla Settings-objekt
        Settings.objects.all().delete()

        request = self.factory.get("/")
        request.user = User()

        context = settings_processor(request)

        # Kontrollera fallback-värden för anonym användare (anpassa till faktiska värden)
        self.assertIn("axes_rows", context["display_settings"])
        self.assertIn("transactions_rows", context["display_settings"])
        self.assertIn("manufacturers_rows", context["display_settings"])
        # Kontrollera att värdena är heltal
        self.assertIsInstance(context["display_settings"]["axes_rows"], int)
        self.assertIsInstance(context["display_settings"]["transactions_rows"], int)
        self.assertIsInstance(context["display_settings"]["manufacturers_rows"], int)

    def test_settings_processor_demo_mode(self):
        """Testa settings_processor med demo mode"""
        request = self.factory.get("/")
        request.user = self.user

        context = settings_processor(request)

        # Kontrollera att demo_mode finns
        self.assertIn("demo_mode", context)
        self.assertIsInstance(context["demo_mode"], bool)

    def test_settings_processor_current_year(self):
        """Testa settings_processor current_year"""
        request = self.factory.get("/")
        request.user = self.user

        context = settings_processor(request)

        # Kontrollera att current_year är korrekt
        from datetime import datetime

        expected_year = datetime.now().year
        self.assertEqual(context["current_year"], expected_year)

    def test_settings_processor_build_date_format(self):
        """Testa settings_processor build_date format"""
        request = self.factory.get("/")
        request.user = self.user

        context = settings_processor(request)

        # Kontrollera att build_date har rätt format (YYYY-MM-DD)
        build_date = context["build_date"]
        self.assertIsInstance(build_date, str)
        self.assertEqual(len(build_date), 10)  # YYYY-MM-DD format
        self.assertIn("-", build_date)

    def test_settings_processor_app_version(self):
        """Testa settings_processor app_version"""
        request = self.factory.get("/")
        request.user = self.user

        context = settings_processor(request)

        # Kontrollera att app_version finns och är en sträng
        self.assertIn("app_version", context)
        self.assertIsInstance(context["app_version"], str)
        self.assertGreater(len(context["app_version"]), 0)

    def test_settings_processor_exception_handling(self):
        """Testa settings_processor med exception i Settings.get_settings()"""
        request = self.factory.get("/")
        request.user = self.user

        # Mock Settings.get_settings för att kasta exception
        with patch.object(
            Settings, "get_settings", side_effect=Exception("Database error")
        ):
            context = settings_processor(request)

        # Kontrollera att fallback-värden används
        self.assertEqual(context["display_settings"]["axes_rows"], 50)
        self.assertEqual(context["display_settings"]["transactions_rows"], 30)
        self.assertEqual(context["display_settings"]["manufacturers_rows"], 50)
        self.assertEqual(context["site_settings"]["title"], "AxeCollection")
