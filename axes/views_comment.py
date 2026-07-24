import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CommentForm
from .models import Axe, Comment, Manufacturer, Settings, Stamp
from .utils.notifications import send_pending_comment_notification

logger = logging.getLogger(__name__)

RATE_LIMIT_MAX = 5
RATE_LIMIT_WINDOW = 3600


def _is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _bad_request(request, redirect_url, message):
    """Gemensam 400-respons (AJAX-JSON eller redirect+messages)."""
    if _is_ajax(request):
        return JsonResponse({"success": False, "error": message}, status=400)
    messages.error(request, message)
    return redirect(redirect_url)


def _submit_comment(request, target, target_field, redirect_url):
    """Delad logik för att ta emot en kommentar på en yxa eller tillverkare."""
    settings = Settings.get_settings()
    if not settings.comments_enabled_public:
        message = "Kommentarer är avstängda just nu."
        if _is_ajax(request):
            return JsonResponse({"success": False, "error": message}, status=403)
        messages.error(request, message)
        return redirect(redirect_url)

    if not request.session.session_key:
        request.session.create()
    rate_limit_key = f"comment_rl_{request.session.session_key}"
    submit_count = cache.get(rate_limit_key, 0)
    if submit_count >= RATE_LIMIT_MAX:
        message = "Du har skickat in för många kommentarer. Försök igen senare."
        if _is_ajax(request):
            return JsonResponse({"success": False, "error": message}, status=429)
        messages.error(request, message)
        return redirect(redirect_url)

    form = CommentForm(request.POST)
    if not form.is_valid():
        if _is_ajax(request):
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        messages.error(request, "Kommentaren kunde inte skickas. Kontrollera fälten.")
        return redirect(redirect_url)

    if form.is_honeypot_filled:
        status = "SPAM"
    elif request.user.is_authenticated:
        status = "APPROVED"
    else:
        status = "PENDING"

    parent = None
    parent_id = form.cleaned_data.get("parent_id")
    if parent_id:
        try:
            parent = Comment.objects.get(pk=parent_id)
        except Comment.DoesNotExist:
            return _bad_request(
                request, redirect_url, "Kommentaren att svara på finns inte."
            )

        if parent.target != target:
            return _bad_request(
                request, redirect_url, "Kommentaren att svara på finns inte."
            )

        if not request.user.is_authenticated and (
            parent.status != "APPROVED" or parent.is_removed
        ):
            return _bad_request(
                request, redirect_url, "Kommentaren att svara på finns inte."
            )

    comment = Comment(
        author_name=form.cleaned_data["author_name"],
        body=form.cleaned_data["body"],
        status=status,
        parent=parent,
    )
    if status == "APPROVED":
        comment.moderated_by = request.user
        comment.moderated_at = timezone.now()
    setattr(comment, target_field, target)
    try:
        comment.full_clean()
    except Exception:
        logger.exception("Kunde inte validera ny kommentar")
        message = "Kommentaren kunde inte sparas. Försök igen."
        if _is_ajax(request):
            return JsonResponse({"success": False, "error": message}, status=400)
        messages.error(request, message)
        return redirect(redirect_url)
    comment.save()

    if status == "PENDING":
        send_pending_comment_notification(comment, request)

    cache.set(rate_limit_key, submit_count + 1, RATE_LIMIT_WINDOW)

    success_message = "Tack, din kommentar väntar på granskning."
    if _is_ajax(request):
        return JsonResponse({"success": True, "message": success_message})
    messages.success(request, success_message)
    return redirect(redirect_url)


@require_POST
def submit_axe_comment(request, pk):
    axe = get_object_or_404(Axe, pk=pk)
    return _submit_comment(request, axe, "axe", reverse("axe_detail", args=[axe.pk]))


@require_POST
def submit_manufacturer_comment(request, pk):
    manufacturer = get_object_or_404(Manufacturer, pk=pk)
    return _submit_comment(
        request,
        manufacturer,
        "manufacturer",
        reverse("manufacturer_detail", args=[manufacturer.pk]),
    )


@require_POST
def submit_stamp_comment(request, pk):
    stamp = get_object_or_404(Stamp, pk=pk)
    return _submit_comment(
        request, stamp, "stamp", reverse("stamp_detail", args=[stamp.pk])
    )


@login_required
def comment_moderation(request):
    """Admin-vy för att godkänna/avvisa/markera kommentarer som skräp."""
    status = request.GET.get("status", "PENDING")
    comments = Comment.objects.select_related(
        "axe", "manufacturer", "stamp", "moderated_by", "parent"
    )

    if status and status != "ALL":
        comments = comments.filter(status=status)

    paginator = Paginator(comments, 50)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "status_choices": Comment.STATUS_CHOICES,
        "selected_status": status,
        "pending_count": Comment.objects.filter(status="PENDING").count(),
    }
    return render(request, "axes/comment_moderation.html", context)


@login_required
@require_POST
def moderate_comment(request, pk):
    """AJAX-vy: godkänn/avvisa/markera en kommentar som skräp."""
    comment = get_object_or_404(Comment, pk=pk)
    action = request.POST.get("action")

    if action == "delete":
        if comment.replies.exists():
            comment.is_removed = True
            comment.moderated_by = request.user
            comment.moderated_at = timezone.now()
            comment.save()
            return JsonResponse({"success": True, "removed": True})
        comment.delete()
        return JsonResponse({"success": True, "deleted": True})

    action_to_status = {
        "approve": "APPROVED",
        "reject": "REJECTED",
        "spam": "SPAM",
    }
    new_status = action_to_status.get(action)
    if new_status is None:
        return JsonResponse({"success": False, "error": "Okänd åtgärd."}, status=400)

    comment.status = new_status
    comment.moderated_at = timezone.now()
    comment.moderated_by = request.user
    comment.save()

    return JsonResponse(
        {
            "success": True,
            "status": comment.status,
            "status_display": comment.get_status_display(),
        }
    )
