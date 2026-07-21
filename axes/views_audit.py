from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.dateparse import parse_date

from .models import AuditLog


@login_required
def audit_log(request):
    """Vy för att visa ändringsloggen med filtreringsmöjligheter."""
    logs = AuditLog.objects.select_related("user").all()

    model_name = request.GET.get("model_name", "")
    action = request.GET.get("action", "")
    user_id = request.GET.get("user", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    if model_name:
        logs = logs.filter(model_name=model_name)
    if action:
        logs = logs.filter(action=action)
    if user_id:
        logs = logs.filter(user_id=user_id)

    parsed_date_from = parse_date(date_from) if date_from else None
    if parsed_date_from:
        logs = logs.filter(timestamp__date__gte=parsed_date_from)

    parsed_date_to = parse_date(date_to) if date_to else None
    if parsed_date_to:
        logs = logs.filter(timestamp__date__lte=parsed_date_to)

    paginator = Paginator(logs, 50)
    page_obj = paginator.get_page(request.GET.get("page"))

    model_names = (
        AuditLog.objects.values_list("model_name", flat=True)
        .distinct()
        .order_by("model_name")
    )
    log_user_ids = (
        AuditLog.objects.exclude(user__isnull=True)
        .values_list("user_id", flat=True)
        .distinct()
    )
    log_users = User.objects.filter(id__in=log_user_ids).order_by("username")

    context = {
        "page_obj": page_obj,
        "model_names": model_names,
        "log_users": log_users,
        "action_choices": AuditLog.ACTION_CHOICES,
        "selected_model_name": model_name,
        "selected_action": action,
        "selected_user": user_id,
        "date_from": date_from,
        "date_to": date_to,
    }
    return render(request, "axes/audit_log.html", context)
