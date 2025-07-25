from .models import Settings
from datetime import datetime
import subprocess
import os
from django.conf import settings as django_settings

def get_git_version():
    """Hämta Git version/commit hash"""
    try:
        # Försök hämta senaste tag
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
        
        # Fallback: hämta kort commit hash
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return f"commit-{result.stdout.strip()}"
    except:
        pass
    return "v1.0.0"

def get_build_date():
    """Hämta senaste commit-datum eller nuvarande datum"""
    try:
        result = subprocess.run(['git', 'log', '-1', '--format=%cd', '--date=short'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return datetime.now().strftime('%Y-%m-%d')

def settings_processor(request):
    """Context processor som gör inställningar tillgängliga i alla templates"""
    try:
        settings = Settings.get_settings()
        return {
            'public_settings': {
                'show_contacts': settings.show_contacts_public,
                'show_prices': settings.show_prices_public,
                'show_platforms': settings.show_platforms_public,
                'show_only_received_axes': settings.show_only_received_axes_public,
            },
            'site_settings': {
                'title': settings.site_title,
                'description': settings.site_description,
            },
            'display_settings': {
                'axes_rows': int(settings.default_axes_rows_private) if request.user.is_authenticated else int(settings.default_axes_rows_public),
                'transactions_rows': int(settings.default_transactions_rows_private) if request.user.is_authenticated else int(settings.default_transactions_rows_public),
                'manufacturers_rows': int(settings.default_manufacturers_rows_private) if request.user.is_authenticated else int(settings.default_manufacturers_rows_public),
            },
            # Footer information
            'current_year': datetime.now().year,
            'build_date': get_build_date(),
            'app_version': get_git_version(),
            # Demo mode
            'demo_mode': getattr(django_settings, 'DEMO_MODE', False),
        }
    except Exception as e:
        # Fallback om Settings-modellen inte finns ännu
        print(f"Settings processor error: {e}")
        return {
            'public_settings': {
                'show_contacts': False,
                'show_prices': True,
                'show_platforms': True,
                'show_only_received_axes': False,
            },
            'site_settings': {
                'title': 'AxeCollection',
                'description': '',
            },
            'display_settings': {
                'axes_rows': 50 if request.user.is_authenticated else 20,
                'transactions_rows': 30 if request.user.is_authenticated else 15,
                'manufacturers_rows': 50 if request.user.is_authenticated else 25,
            },
            # Footer information (fallback values)
            'current_year': datetime.now().year,
            'build_date': datetime.now().strftime('%Y-%m-%d'),
            'app_version': 'v1.0.0',
            # Demo mode (fallback)
            'demo_mode': getattr(django_settings, 'DEMO_MODE', False),
        } 