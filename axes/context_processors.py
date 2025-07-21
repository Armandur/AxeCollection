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
            }
        }
    except:
        # Fallback om Settings-modellen inte finns ännu
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
            }
        } 