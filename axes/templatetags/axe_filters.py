from django import template
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='format_decimal')
def format_decimal(value):
    """
    Formaterar ett Decimal-värde.
    - Visar inga decimaler om det är ett heltal.
    - Visar två decimaler om det finns decimaler.
    - Använder Unicode non-breaking space som tusentalsavgränsare.
    """
    if value is None:
        return ""
    
    # Säkerställ att värdet är ett Decimal
    if not isinstance(value, Decimal):
        try:
            # Hantera olika typer av värden
            if isinstance(value, (int, float)):
                value = Decimal(str(value))
            elif isinstance(value, str):
                # Rensa strängen från onödiga tecken
                cleaned = value.strip().replace(',', '.')
                if cleaned:
                    value = Decimal(cleaned)
                else:
                    return "0"
            else:
                return str(value)
        except (ValueError, TypeError, InvalidOperation):
            return str(value)

    # Formatera med tusentalsavgränsare (Unicode non-breaking space)
    def format_sv(num, decimals=0):
        if decimals == 0:
            return f"{int(num):,}".replace(",", "\u00A0")
        else:
            s = f"{num:,.2f}".replace(",", "\u00A0")
            # Ta bort onödiga decimaler om .00
            if s.endswith(".00"):
                s = s[:-3]
            return s

    try:
        if value == value.to_integral_value():
            return format_sv(value, 0)
        else:
            return format_sv(value, 2)
    except (ValueError, TypeError, InvalidOperation):
        return str(value)

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
    return f"{formatted_value}\u00A0{currency}"

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