"""
Push-notiser via ntfy.sh, t.ex. när en publik kommentar hamnar i moderering.
"""

import logging

import requests

from django.urls import reverse

from ..models import Settings

logger = logging.getLogger(__name__)


def send_ntfy(topic_url, token, title, body, click=None):
    """Lågnivå: skicka en ntfy-notis. Returnerar (ok, felmeddelande).

    Delas av kommentarnotisen (som ignorerar returvärdet - ett notis-fel
    får aldrig påverka en redan sparad kommentar) och testknappen i
    inställningarna (som visar felet för användaren). Token utelämnas när
    den är tom (öppna topics). Fel loggas och sväljs; funktionen höjer
    aldrig vidare.
    """
    if not topic_url:
        return False, "Ingen topic-URL angiven."

    # ntfys JSON-publicering: topic + titel/meddelande i en UTF-8-body till
    # server-roten, i stället för i HTTP-headers. requests kodar header-värden
    # som latin-1, så å/ä/ö i en Title-header mojibaggar ("från" -> "fr�n") -
    # JSON-body undviker det helt.
    base_url, _, topic = topic_url.rstrip("/").rpartition("/")
    if not topic:
        return False, "Ogiltig topic-URL."

    payload = {
        "topic": topic,
        "title": title,
        "message": body,
        "tags": ["speech_balloon"],
    }
    if click:
        payload["click"] = click

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.post(base_url, json=payload, headers=headers, timeout=5)
        resp.raise_for_status()
        return True, None
    except Exception as exc:
        logger.exception("Kunde inte skicka ntfy-notis")
        return False, str(exc)


def send_pending_comment_notification(comment, request):
    """Skicka en push-notis via ntfy.sh om en ny kommentar väntar på granskning.

    Läser topic-URL:en från Settings. Om den är tom skickas ingen notis.
    Returvärdet ignoreras - ett notis-fel ska aldrig påverka att
    kommentaren redan sparats.
    """
    settings = Settings.get_settings()
    if not settings.ntfy_topic_url:
        return

    moderation_url = request.build_absolute_uri(reverse("comment_moderation"))
    target = comment.axe or comment.manufacturer or comment.stamp
    body = f'Ny kommentar väntar på granskning: "{comment.body[:200]}"'
    if target is not None:
        body = f"Ny kommentar på {target} väntar på granskning."

    send_ntfy(
        settings.ntfy_topic_url,
        settings.ntfy_token,
        "Ny kommentar väntar",
        body,
        click=moderation_url,
    )
