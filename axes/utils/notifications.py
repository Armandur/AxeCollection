"""
Push-notiser via ntfy.sh, t.ex. när en publik kommentar hamnar i moderering.
"""

import logging

import requests

from django.urls import reverse

from ..models import Settings

logger = logging.getLogger(__name__)


def send_pending_comment_notification(comment, request):
    """Skicka en push-notis via ntfy.sh om en ny kommentar väntar på granskning.

    Läser topic-URL:en från Settings. Om den är tom skickas ingen notis.
    Fel vid anropet loggas men höjs aldrig vidare - ett notis-fel ska
    aldrig påverka att kommentaren redan sparats.
    """
    topic_url = Settings.get_settings().ntfy_topic_url
    if not topic_url:
        return

    moderation_url = request.build_absolute_uri(reverse("comment_moderation"))
    target = comment.axe or comment.manufacturer or comment.stamp
    body = f'Ny kommentar väntar på granskning: "{comment.body[:200]}"'
    if target is not None:
        body = f"Ny kommentar på {target} väntar på granskning."

    try:
        requests.post(
            topic_url,
            data=body.encode("utf-8"),
            headers={
                "Title": "Ny kommentar väntar",
                "Click": moderation_url,
                "Tags": "speech_balloon",
            },
            timeout=5,
        )
    except Exception:
        logger.exception("Kunde inte skicka ntfy-notis för ny kommentar")
