from django import template
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

register = template.Library()

@register.filter(name='format_decimal')
def format_decimal(value):
    """
    Formaterar ett Decimal-värde.
    - Visar inga decimaler om det är ett heltal.
    - Visar två decimaler om det finns decimaler.
    - Använder mellanslag som tusentalsavgränsare (svensk standard).
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

    # Formatera med tusentalsavgränsare (mellanslag)
    def format_sv(num, decimals=0):
        if decimals == 0:
            return f"{int(num):,}".replace(",", " ")
        else:
            s = f"{num:,.2f}".replace(",", " ")
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