from .models import Settings

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
            }
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
            }
        } 