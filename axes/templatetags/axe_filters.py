from django import template
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.utils.safestring import mark_safe
import re
import os
from django.template.defaultfilters import floatformat

register = template.Library()

# Landskod till flagg-emoji mapping
COUNTRY_FLAGS = {
    'SE': '🇸🇪',
    'FI': '🇫🇮',
    'NO': '🇳🇴',
    'DK': '🇩🇰',
    'DE': '🇩🇪',
    'GB': '🇬🇧',
    'US': '🇺🇸',
    'FR': '🇫🇷',
    'IT': '🇮🇹',
    'ES': '🇪🇸',
    'PL': '🇵🇱',
    'EE': '🇪🇪',
    'LV': '🇱🇻',
    'LT': '🇱🇹',
    'RU': '🇷🇺',
    'NL': '🇳🇱',
    'BE': '🇧🇪',
    'CH': '🇨🇭',
    'AT': '🇦🇹',
    'IE': '🇮🇪',
    'IS': '🇮🇸',
    'CZ': '🇨🇿',
    'SK': '🇸🇰',
    'HU': '🇭🇺',
    'UA': '🇺🇦',
    'RO': '🇷🇴',
    'BG': '🇧🇬',
    'HR': '🇭🇷',
    'SI': '🇸🇮',
    'PT': '🇵🇹',
    'GR': '🇬🇷',
    'TR': '🇹🇷',
    'CA': '🇨🇦',
    'AU': '🇦🇺',
    'NZ': '🇳🇿',
}

@register.filter
def format_decimal(value):
    """Formatera decimaltal med svenska format (komma som decimalseparator, non-breaking space som tusentalsavgränsare)"""
    if value is None:
        return "0"
    
    try:
        # Konvertera till Decimal för exakt hantering
        decimal_value = Decimal(str(value))
        
        # Kontrollera om det är ett heltal
        if decimal_value == decimal_value.to_integral():
            # Heltal - formatera utan decimaler
            integer_str = str(int(decimal_value))
        else:
            # Decimaltal - formatera med 2 decimaler
            integer_str = str(int(decimal_value))
            decimal_str = str(decimal_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)).split('.')[1]
        
        # Lägg till tusentalsavgränsare med non-breaking space
        formatted_integer = ""
        for i, digit in enumerate(reversed(integer_str)):
            if i > 0 and i % 3 == 0:
                formatted_integer = "\u00A0" + formatted_integer  # Non-breaking space
            formatted_integer = digit + formatted_integer
        
        # Lägg till decimaler om de finns
        if decimal_value != decimal_value.to_integral():
            return mark_safe(f"{formatted_integer},{decimal_str}")
        else:
            return mark_safe(formatted_integer)
            
    except (ValueError, InvalidOperation):
        # Fallback till gammal formatering om något går fel
        return mark_safe(floatformat(value, 2).replace('.', ','))

@register.filter(name='format_currency')
def format_currency(value, currency="kr"):
    """
    Formaterar ett belopp med valuta och förhindrar radbrytning.
    - Använder format_decimal för talformatering
    - Lägger till valuta med non-breaking space
    """
    if value is None:
        return ""
    
    formatted_value = format_decimal(value)
    if formatted_value == "":
        return ""
    
    # Använd non-breaking space mellan tal och valuta
    return mark_safe(f"{formatted_value}\u00A0{currency}")

@register.filter(name='status_badge')
def status_badge(status):
    """
    Returnerar Bootstrap badge-klass för olika status.
    """
    status_classes = {
        'KÖPT': 'bg-warning text-dark',
        'MOTTAGEN': 'bg-success',
        'SÅLD': 'bg-secondary',
    }
    return status_classes.get(status, 'bg-secondary')

@register.filter(name='transaction_badge')
def transaction_badge(transaction_type):
    """
    Returnerar Bootstrap badge-klass för transaktionstyper.
    """
    if transaction_type == 'KÖP':
        return 'bg-danger'
    elif transaction_type == 'SÄLJ':
        return 'bg-success'
    else:
        return 'bg-secondary'

@register.filter(name='transaction_icon')
def transaction_icon(transaction_type):
    """
    Returnerar Bootstrap ikon för transaktionstyper.
    """
    if transaction_type == 'KÖP':
        return 'bi-arrow-down-circle'
    elif transaction_type == 'SÄLJ':
        return 'bi-arrow-up-circle'
    else:
        return 'bi-question-circle'

@register.filter(name='default_if_empty')
def default_if_empty(value, default="-"):
    """
    Returnerar default-värde om värdet är tomt eller None.
    """
    if value is None or value == "":
        return default
    return value

@register.simple_tag
def breadcrumb_item(text, url=None, is_active=False):
    """
    Skapar en breadcrumb-item med rätt CSS-klasser.
    """
    if is_active:
        return mark_safe(f'<li class="breadcrumb-item active" aria-current="page">{text}</li>')
    elif url:
        return mark_safe(f'<li class="breadcrumb-item"><a href="{url}">{text}</a></li>')
    else:
        return mark_safe(f'<li class="breadcrumb-item">{text}</li>')

@register.filter(name='markdown')
def markdown(value):
    """
    Konverterar markdown-text till HTML.
    """
    if not value:
        return ""
    
    # Escape HTML först
    html = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Rubriker
    html = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*$)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Fet och kursiv text
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Länkar
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)
    
    # Listor
    html = re.sub(r'^\* (.*$)', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^- (.*$)', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^(\d+)\. (.*$)', r'<li>\2</li>', html, flags=re.MULTILINE)
    
    # Radbrytningar
    html = re.sub(r'\n\n', '</p><p>', html)
    html = re.sub(r'\n', '<br>', html)
    
    # Wrappa i p-taggar
    html = '<p>' + html + '</p>'
    
    # Fixa listor
    html = re.sub(r'<p><li>', '<ul><li>', html)
    html = re.sub(r'</li></p>', '</li></ul>', html)
    
    return mark_safe(html)

@register.filter(name='strip_markdown_and_truncate')
def strip_markdown_and_truncate(value, max_length=100):
    """
    Strippar markdown-formatering och begränsar texten till max_length tecken.
    Lägger till "..." om texten är längre.
    """
    if not value:
        return ""
    
    # Strippa markdown-formatering
    # Ta bort rubriker
    text = re.sub(r'^#{1,6}\s+', '', value, flags=re.MULTILINE)
    
    # Ta bort fet och kursiv text (behåll innehållet)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    # Ta bort länkar (behåll texten)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Ta bort listmarkeringar
    text = re.sub(r'^[\*\-]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Ta bort kodblock
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Rensa whitespace
    text = re.sub(r'\n+', ' ', text)  # Ersätt radbrytningar med mellanslag
    text = re.sub(r'\s+', ' ', text)  # Ersätt flera whitespace med ett mellanslag
    text = text.strip()
    
    # Begränsa längden
    if len(text) > max_length:
        # Försök att klippa vid ett mellanslag
        truncated = text[:max_length-3]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:  # Om vi hittar ett mellanslag i slutet av texten
            truncated = truncated[:last_space]
        return truncated + "..."
    
    return text

@register.filter
def times(value):
    """Upprepa text ett visst antal gånger"""
    try:
        count = int(value)
        return range(count)
    except (ValueError, TypeError):
        return range(0)

@register.filter
def basename(value):
    """Returnerar filnamnet utan sökväg."""
    return os.path.basename(value)

@register.filter
def country_flag(country_code):
    """Returnera flagg-emoji för landskod"""
    if not country_code:
        return ""
    return COUNTRY_FLAGS.get(country_code.upper(), "")

@register.filter
def country_name(country_code):
    """Returnera landsnamn för landskod"""
    if not country_code:
        return ""
    
    # Landskod till namn mapping
    COUNTRY_NAMES = {
        'SE': 'Sverige',
        'FI': 'Finland',
        'NO': 'Norge',
        'DK': 'Danmark',
        'DE': 'Tyskland',
        'GB': 'Storbritannien',
        'US': 'USA',
        'FR': 'Frankrike',
        'IT': 'Italien',
        'ES': 'Spanien',
        'PL': 'Polen',
        'EE': 'Estland',
        'LV': 'Lettland',
        'LT': 'Litauen',
        'RU': 'Ryssland',
        'NL': 'Nederländerna',
        'BE': 'Belgien',
        'CH': 'Schweiz',
        'AT': 'Österrike',
        'IE': 'Irland',
        'IS': 'Island',
        'CZ': 'Tjeckien',
        'SK': 'Slovakien',
        'HU': 'Ungern',
        'UA': 'Ukraina',
        'RO': 'Rumänien',
        'BG': 'Bulgarien',
        'HR': 'Kroatien',
        'SI': 'Slovenien',
        'PT': 'Portugal',
        'GR': 'Grekland',
        'TR': 'Turkiet',
        'CA': 'Kanada',
        'AU': 'Australien',
        'NZ': 'Nya Zeeland',
    }
    
    return COUNTRY_NAMES.get(country_code.upper(), country_code)