from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from .models import (
    Stamp,
    StampTranscription,
    StampTag,
    StampImage,
    AxeStamp,
    StampVariant,
    StampUncertaintyGroup,
    Axe,
    Manufacturer,
    AxeImage,
)
from .forms import StampForm, StampTranscriptionForm, AxeStampForm, StampImageForm, StampImageMarkForm
import json


@login_required
def stamp_list(request):
    """Lista alla stämplar med sökning och filtrering"""

    # Hämta filterparametrar
    search_query = request.GET.get("search", "")
    manufacturer_filter = request.GET.get("manufacturer", "")
    stamp_type_filter = request.GET.get("stamp_type", "")
    status_filter = request.GET.get("status", "")
    source_filter = request.GET.get("source", "")

    # Basqueryset med optimerad prestanda
    stamps = Stamp.objects.select_related("manufacturer").prefetch_related(
        "transcriptions",
        Prefetch(
            "images",
            queryset=StampImage.objects.order_by(
                "-is_primary", "order", "-uploaded_at"
            ),
        ),
        Prefetch("axes", queryset=AxeStamp.objects.select_related("axe__manufacturer")),
    )

    # Applicera filter
    if search_query:
        stamps = stamps.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(transcriptions__text__icontains=search_query)
            | Q(manufacturer__name__icontains=search_query)
        ).distinct()

    if manufacturer_filter:
        stamps = stamps.filter(manufacturer_id=manufacturer_filter)

    if stamp_type_filter:
        stamps = stamps.filter(stamp_type=stamp_type_filter)

    if status_filter:
        stamps = stamps.filter(status=status_filter)

    if source_filter:
        stamps = stamps.filter(source_category=source_filter)

    # Sortering
    sort_by = request.GET.get("sort", "name")
    if sort_by == "name":
        stamps = stamps.order_by("name")
    elif sort_by == "manufacturer":
        stamps = stamps.order_by("manufacturer__name", "name")
    elif sort_by == "created":
        stamps = stamps.order_by("-created_at")
    elif sort_by == "axes_count":
        stamps = stamps.annotate(axes_count=Count("axes")).order_by("-axes_count")
    elif sort_by == "images_count":
        stamps = stamps.annotate(images_count=Count("images")).order_by("-images_count")

    # Paginering
    paginator = Paginator(stamps, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Förbehandla data för att hitta primära bilder och räkna objekt
    for stamp in page_obj:
        # Hitta primär StampImage
        stamp_images = list(stamp.images.all())
        primary_stamp_image = next(
            (img for img in stamp_images if img.is_primary), None
        )
        if primary_stamp_image:
            stamp._primary_image = primary_stamp_image
        elif stamp_images:
            # Annars ta första StampImage
            stamp._primary_image = stamp_images[0]
        else:
            # Om ingen bild finns alls, sätt till None
            stamp._primary_image = None

        # Beräkna antal bilder och yxor
        stamp.total_images = len(stamp_images)
        stamp.total_axes = stamp.axes.count()

    # Context för filter
    manufacturers = Manufacturer.objects.all().order_by("name")

    context = {
        "page_obj": page_obj,
        "stamps": page_obj,
        "manufacturers": manufacturers,
        "stamp_types": Stamp.STAMP_TYPE_CHOICES,
        "status_choices": Stamp.STATUS_CHOICES,
        "source_choices": Stamp.SOURCE_CATEGORY_CHOICES,
        "search_query": search_query,
        "manufacturer_filter": manufacturer_filter,
        "stamp_type_filter": stamp_type_filter,
        "status_filter": status_filter,
        "source_filter": source_filter,
        "sort_by": sort_by,
    }

    return render(request, "axes/stamp_list.html", context)


@login_required
def stamp_detail(request, stamp_id):
    """Detaljvy för en stämpel"""

    stamp = get_object_or_404(
        Stamp.objects.select_related("manufacturer").prefetch_related(
            "transcriptions", "images", "axes"
        ),
        id=stamp_id,
    )

    # Hämta relaterade stämplar (varianter, osäkerhetsgrupper)
    related_stamps = Stamp.objects.filter(
        Q(variants__main_stamp=stamp)
        | Q(main_stamp__variant_stamp=stamp)
        | Q(uncertainty_groups__stamps=stamp)
    ).distinct()

    # Hämta alla StampImage-kopplingar för denna stämpel
    stamp_images = (
        StampImage.objects.filter(stamp=stamp)
        .select_related("axe_image__axe")
        .order_by("-is_primary", "order", "-uploaded_at")
    )

    context = {
        "stamp": stamp,
        "related_stamps": related_stamps,
        "stamp_images": stamp_images,
    }

    return render(request, "axes/stamp_detail.html", context)


@login_required
def stamp_create(request):
    """Skapa ny stämpel"""

    # Hämta manufacturer från URL-parametern
    manufacturer_id = request.GET.get("manufacturer")
    initial_data = {}

    if manufacturer_id:
        try:
            manufacturer = Manufacturer.objects.get(id=manufacturer_id)
            initial_data["manufacturer"] = manufacturer
        except Manufacturer.DoesNotExist:
            pass

    if request.method == "POST":
        form = StampForm(request.POST)
        if form.is_valid():
            stamp = form.save()
            messages.success(request, f'Stämpel "{stamp.name}" skapades framgångsrikt.')
            return redirect("stamp_detail", stamp_id=stamp.id)
    else:
        form = StampForm(initial=initial_data)

    context = {
        "form": form,
        "title": "Skapa ny stämpel",
    }

    return render(request, "axes/stamp_form.html", context)


@login_required
def stamp_edit(request, stamp_id):
    """Redigera stämpel"""

    stamp = get_object_or_404(Stamp, id=stamp_id)

    if request.method == "POST":
        form = StampForm(request.POST, instance=stamp)
        if form.is_valid():
            stamp = form.save()
            messages.success(
                request, f'Stämpel "{stamp.name}" uppdaterades framgångsrikt.'
            )
            return redirect("stamp_detail", stamp_id=stamp.id)
    else:
        form = StampForm(instance=stamp)

    context = {
        "form": form,
        "stamp": stamp,
        "title": f"Redigera stämpel: {stamp.name}",
    }

    return render(request, "axes/stamp_form.html", context)


@login_required
def axes_without_stamps(request):
    """Lista yxor som inte har stämplar definierade"""

    # Hämta yxor som inte har några stämplar
    axes_without_stamps = Axe.objects.filter(stamps__isnull=True).select_related(
        "manufacturer"
    )

    # Filtrering
    manufacturer_filter = request.GET.get("manufacturer", "")
    if manufacturer_filter:
        axes_without_stamps = axes_without_stamps.filter(
            manufacturer_id=manufacturer_filter
        )

    # Sortering
    sort_by = request.GET.get("sort", "manufacturer")
    if sort_by == "manufacturer":
        axes_without_stamps = axes_without_stamps.order_by(
            "manufacturer__name", "model"
        )
    elif sort_by == "created":
        axes_without_stamps = axes_without_stamps.order_by("-id")
    elif sort_by == "model":
        axes_without_stamps = axes_without_stamps.order_by("model")

    # Paginering
    paginator = Paginator(axes_without_stamps, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Statistik
    total_axes = Axe.objects.count()
    axes_with_stamps = Axe.objects.filter(stamps__isnull=False).distinct().count()
    axes_without_stamps_count = total_axes - axes_with_stamps

    context = {
        "page_obj": page_obj,
        "axes": page_obj,
        "total_axes": total_axes,
        "axes_with_stamps": axes_with_stamps,
        "axes_without_stamps_count": axes_without_stamps_count,
        "manufacturers": Manufacturer.objects.all().order_by("name"),
        "filters": {
            "manufacturer": manufacturer_filter,
            "sort": sort_by,
        },
    }

    return render(request, "axes/axes_without_stamps.html", context)


@login_required
def stamp_search(request):
    """AJAX-sökning för stämplar"""

    query = request.GET.get("q", "")
    manufacturer_filter = request.GET.get("manufacturer", "")
    stamp_type_filter = request.GET.get("stamp_type", "")

    if not query and not manufacturer_filter and not stamp_type_filter:
        return JsonResponse({"results": []})

    stamps = Stamp.objects.select_related("manufacturer").prefetch_related(
        "transcriptions"
    )

    # Sökning
    if query:
        stamps = stamps.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(transcriptions__text__icontains=query)
            | Q(manufacturer__name__icontains=query)
        ).distinct()

    # Filtrering
    if manufacturer_filter:
        stamps = stamps.filter(manufacturer_id=manufacturer_filter)

    if stamp_type_filter:
        stamps = stamps.filter(stamp_type=stamp_type_filter)

    # Begränsa resultat
    stamps = stamps[:20]

    results = []
    for stamp in stamps:
        # Hitta bästa matchande transkription
        best_transcription = ""
        if query:
            transcriptions = stamp.transcriptions.all()
            for transcription in transcriptions:
                if query.lower() in transcription.text.lower():
                    best_transcription = transcription.text
                    break
            if not best_transcription and transcriptions.exists():
                best_transcription = transcriptions.first().text

        results.append(
            {
                "id": stamp.id,
                "name": stamp.name,
                "manufacturer": (
                    stamp.manufacturer.name if stamp.manufacturer else "Okänd"
                ),
                "type": stamp.get_stamp_type_display(),
                "status": stamp.get_status_display(),
                "description": (
                    stamp.description[:100] + "..."
                    if stamp.description and len(stamp.description) > 100
                    else stamp.description
                ),
                "transcription": (
                    best_transcription[:100] + "..."
                    if best_transcription and len(best_transcription) > 100
                    else best_transcription
                ),
                "url": f"/stamplar/{stamp.id}/",
            }
        )

    return JsonResponse({"results": results})


@login_required
def stamp_image_upload(request, stamp_id):
    """Ladda upp bild för stämpel"""

    stamp = get_object_or_404(Stamp, id=stamp_id)

    if request.method == "POST":
        form = StampImageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                stamp_image = form.save(commit=False)
                stamp_image.stamp = stamp
                
                # Sätt image_type automatiskt till standalone för nya bilder
                stamp_image.image_type = "standalone"
                
                # Hantera koordinater från formuläret
                x_coord = request.POST.get("x_coordinate")
                y_coord = request.POST.get("y_coordinate")
                width = request.POST.get("width")
                height = request.POST.get("height")

                if x_coord and y_coord and width and height:
                    from decimal import Decimal
                    stamp_image.x_coordinate = Decimal(x_coord)
                    stamp_image.y_coordinate = Decimal(y_coord)
                    stamp_image.width = Decimal(width)
                    stamp_image.height = Decimal(height)

                # De nya fälten hanteras automatiskt av form.save() eftersom de finns i Meta.fields
                stamp_image.save()

                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Bild laddades upp framgångsrikt.",
                            "image_id": stamp_image.id,
                            "image_url": stamp_image.image_url_with_cache_busting,
                            "webp_url": stamp_image.webp_url,
                        }
                    )

                messages.success(request, "Bild laddades upp framgångsrikt.")
                return redirect("stamp_detail", stamp_id=stamp.id)
            except Exception as e:
                messages.error(request, f"Fel vid uppladdning av bild: {e}")
                # Rendera formuläret igen med fel
                context = {
                    "stamp": stamp,
                    "stamp_image": None,
                    "form": form,
                    "title": f"Ladda upp bild för {stamp.name}",
                }
                return render(request, "axes/stamp_image_form.html", context)
        else:
            messages.error(request, "Formuläret innehåller fel. Kontrollera dina indata.")
            # Rendera formuläret igen med fel
            context = {
                "stamp": stamp,
                "stamp_image": None,
                "form": form,
                "title": f"Ladda upp bild för {stamp.name}",
            }
            return render(request, "axes/stamp_image_form.html", context)
    else:
        form = StampImageForm()

    context = {
        "stamp": stamp,
        "stamp_image": None,  # För nya bilder finns ingen stamp_image än
        "form": form,
        "title": f"Ladda upp bild för {stamp.name}",
    }

    return render(request, "axes/stamp_image_form.html", context)


@login_required
def stamp_image_delete(request, stamp_id, image_id):
    """Ta bort stämpelbild"""

    stamp = get_object_or_404(Stamp, id=stamp_id)
    stamp_image = get_object_or_404(StampImage, id=image_id, stamp=stamp)

    if request.method == "POST":
        image_name = stamp_image.caption or "Bild"
        stamp_image.delete()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "message": f'Bild "{image_name}" togs bort.'}
            )

        messages.success(request, f'Bild "{image_name}" togs bort.')
        return redirect("stamp_detail", stamp_id=stamp.id)

    context = {
        "stamp": stamp,
        "stamp_image": stamp_image,
        "title": f"Ta bort bild från {stamp.name}",
    }

    return render(request, "axes/stamp_image_delete.html", context)


@login_required
def stamp_image_edit(request, stamp_id, image_id):
    """Redigera stämpelbild"""

    stamp = get_object_or_404(Stamp, id=stamp_id)
    stamp_image = get_object_or_404(StampImage, id=image_id, stamp=stamp)

    # Om det är en axe_mark-bild, omdirigera till edit_axe_image_stamp
    if stamp_image.image_type == "axe_mark" and stamp_image.axe_image:
        return redirect("edit_axe_image_stamp", axe_id=stamp_image.axe_image.axe.id, mark_id=stamp_image.id)

    if request.method == "POST":
        form = StampImageForm(request.POST, request.FILES, instance=stamp_image)
        if form.is_valid():
            # Hantera koordinater från formuläret
            x_coord = request.POST.get("x_coordinate")
            y_coord = request.POST.get("y_coordinate")
            width = request.POST.get("width")
            height = request.POST.get("height")

            stamp_image = form.save(commit=False)
            stamp_image.stamp = stamp
            
            # Behåll befintlig image_type för redigering
            # (formuläret innehåller inte image_type längre, så vi behåller det befintliga)

            # Uppdatera koordinater om de finns
            if x_coord and y_coord and width and height:
                from decimal import Decimal
                stamp_image.x_coordinate = Decimal(x_coord)
                stamp_image.y_coordinate = Decimal(y_coord)
                stamp_image.width = Decimal(width)
                stamp_image.height = Decimal(height)

            stamp_image.save()

            # Om det är en AJAX-request, returnera JSON
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Bild uppdaterades framgångsrikt.",
                        "image_id": stamp_image.id,
                        "image_url": stamp_image.image_url_with_cache_busting,
                        "webp_url": stamp_image.webp_url,
                    }
                )

            messages.success(request, "Bild uppdaterades framgångsrikt.")
            return redirect("stamp_detail", stamp_id=stamp.id)
    else:
        form = StampImageForm(instance=stamp_image)

    context = {
        "stamp": stamp,
        "stamp_image": stamp_image,
        "form": form,
        "title": f"Redigera bild för {stamp.name}",
    }

    return render(request, "axes/stamp_image_form.html", context)


@login_required
def add_axe_stamp(request, axe_id):
    """Lägg till stämpel på yxa - integrerat flöde med bildval och markering"""

    axe = get_object_or_404(Axe, id=axe_id)
    existing_images = axe.images.all()

    # Om inga bilder finns, omdirigera till redigera-sidan
    if not existing_images.exists():
        messages.warning(
            request,
            "Denna yxa har inga bilder än. Lägg till bilder först via redigera-sidan.",
        )
        return redirect("axe_edit", pk=axe.id)

    if request.method == "POST":
        # Hantera olika typer av POST-requests
        action = request.POST.get("action", "")

        if action == "select_image":
            # Användaren har valt en bild - visa markering
            selected_image_id = request.POST.get("selected_image")
            if selected_image_id:
                selected_image = get_object_or_404(
                    AxeImage, id=selected_image_id, axe=axe
                )
                context = {
                    "axe": axe,
                    "existing_images": existing_images,
                    "selected_image": selected_image,
                    "available_stamps": Stamp.objects.select_related(
                        "manufacturer"
                    ).order_by("manufacturer__name", "name"),
                    "title": f"Markera stämpel på bild - {axe}",
                }
                return render(request, "axes/axe_stamp_form.html", context)

        elif action == "save_stamp":
            # Användaren har markerat en bild och vill spara stämpeln
            selected_image_id = request.POST.get("selected_image")
            stamp_id = request.POST.get("stamp")
            x_coord = request.POST.get("x_coordinate")
            y_coord = request.POST.get("y_coordinate")
            width = request.POST.get("width")
            height = request.POST.get("height")
            position = request.POST.get("position", "")
            uncertainty_level = request.POST.get("uncertainty_level", "")
            comment = request.POST.get("comment", "")

            if selected_image_id and stamp_id:
                selected_image = get_object_or_404(
                    AxeImage, id=selected_image_id, axe=axe
                )
                stamp = get_object_or_404(Stamp, id=stamp_id)

                # Konvertera koordinater till Decimal om de finns
                from decimal import Decimal
                x_coord_decimal = Decimal(x_coord) if x_coord else None
                y_coord_decimal = Decimal(y_coord) if y_coord else None
                width_decimal = Decimal(width) if width else None
                height_decimal = Decimal(height) if height else None

                # Skapa StampImage med image_type='axe_mark'
                stamp_image = StampImage.objects.create(
                    axe_image=selected_image,
                    stamp=stamp,
                    image_type="axe_mark",
                    x_coordinate=x_coord_decimal,
                    y_coordinate=y_coord_decimal,
                    width=width_decimal,
                    height=height_decimal,
                    show_full_image=False,
                    is_primary=False,
                    comment=comment,
                )

                # Skapa även AxeStamp för att koppla stämpeln till yxan
                axe_stamp = AxeStamp.objects.create(
                    axe=axe,
                    stamp=stamp,
                    position=position,
                    uncertainty_level=uncertainty_level,
                    comment=comment,
                )

                messages.success(
                    request,
                    f'Stämpel "{stamp.name}" markerades på bilden och kopplades till yxan.',
                )
                return redirect("axe_detail", pk=axe.id)
            else:
                messages.error(request, "Bild och stämpel måste väljas.")

    # GET-request - visa bildval
    context = {
        "axe": axe,
        "existing_images": existing_images,
        "title": f"Välj bild för stämpelmarkering - {axe}",
    }

    return render(request, "axes/axe_stamp_form.html", context)


@login_required
def remove_axe_stamp(request, axe_id, axe_stamp_id):
    """Ta bort stämpel från yxa"""

    axe_stamp = get_object_or_404(AxeStamp, id=axe_stamp_id, axe_id=axe_id)
    stamp_name = axe_stamp.stamp.name

    if request.method == "POST":
        # Ta bort alla stämpelmarkeringar för denna stämpel på denna yxa
        StampImage.objects.filter(
            axe_image__axe_id=axe_id, stamp_id=axe_stamp.stamp_id, image_type="axe_mark"
        ).delete()

        # Ta bort själva stämpelkopplingen
        axe_stamp.delete()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "message": f'Stämpel "{stamp_name}" togs bort från yxan.',
                }
            )

        messages.success(request, f'Stämpel "{stamp_name}" togs bort från yxan.')
        return redirect("axe_detail", pk=axe_id)

    # För AJAX GET-anrop, returnera modal-innehåll
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        context = {
            "axe_stamp": axe_stamp,
            "axe": axe_stamp.axe,
            "stamp": axe_stamp.stamp,
        }
        return render(request, "axes/axe_stamp_confirm_delete_modal.html", context)

    context = {
        "axe_stamp": axe_stamp,
        "axe": axe_stamp.axe,
        "stamp": axe_stamp.stamp,
    }

    return render(request, "axes/axe_stamp_confirm_delete.html", context)


@login_required
def stamp_statistics(request):
    """Statistik för stämplar"""

    # Grundläggande statistik
    total_stamps = Stamp.objects.count()
    known_stamps = Stamp.objects.filter(status="known").count()
    unknown_stamps = Stamp.objects.filter(status="unknown").count()

    # Stämplar per tillverkare
    stamps_by_manufacturer = (
        Stamp.objects.values("manufacturer__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    # Stämplar per typ
    stamps_by_type = (
        Stamp.objects.values("stamp_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Yxor med stämplar vs utan
    total_axes = Axe.objects.count()
    axes_with_stamps = Axe.objects.filter(stamps__isnull=False).distinct().count()
    axes_without_stamps = total_axes - axes_with_stamps

    context = {
        "total_stamps": total_stamps,
        "known_stamps": known_stamps,
        "unknown_stamps": unknown_stamps,
        "stamps_by_manufacturer": stamps_by_manufacturer,
        "stamps_by_type": stamps_by_type,
        "total_axes": total_axes,
        "axes_with_stamps": axes_with_stamps,
        "axes_without_stamps": axes_without_stamps,
    }

    return render(request, "axes/stamp_statistics.html", context)


@login_required
def mark_axe_image_as_stamp(request, axe_id, image_id):
    """Markera en AxeImage som innehåller en stämpel"""

    axe_image = get_object_or_404(AxeImage, id=image_id, axe_id=axe_id)

    if request.method == "POST":
        stamp_id = request.POST.get("stamp")
        x_coord = request.POST.get("x_coordinate")
        y_coord = request.POST.get("y_coordinate")
        width = request.POST.get("width")
        height = request.POST.get("height")
        comment = request.POST.get("comment", "")

        if stamp_id:
            stamp = get_object_or_404(Stamp, id=stamp_id)

            # Konvertera koordinater till Decimal om de finns
            from decimal import Decimal
            x_coord_decimal = Decimal(x_coord) if x_coord else None
            y_coord_decimal = Decimal(y_coord) if y_coord else None
            width_decimal = Decimal(width) if width else None
            height_decimal = Decimal(height) if height else None

            # Skapa eller uppdatera StampImage med image_type='axe_mark'
            stamp_image, created = StampImage.objects.get_or_create(
                axe_image=axe_image,
                stamp=stamp,
                image_type="axe_mark",
                defaults={
                    "x_coordinate": x_coord_decimal,
                    "y_coordinate": y_coord_decimal,
                    "width": width_decimal,
                    "height": height_decimal,
                    "show_full_image": False,  # Standardvärde
                    "is_primary": False,  # Standardvärde
                    "comment": comment,
                },
            )

            if not created:
                # Uppdatera befintlig
                stamp_image.x_coordinate = x_coord_decimal
                stamp_image.y_coordinate = y_coord_decimal
                stamp_image.width = width_decimal
                stamp_image.height = height_decimal
                stamp_image.comment = comment
                stamp_image.save()

            messages.success(request, f"Bild markerad som stämpel: {stamp.name}")
            return redirect("axe_detail", pk=axe_id)

    # Hämta tillgängliga stämplar (prioritera tillverkarens stämplar)
    available_stamps = Stamp.objects.select_related("manufacturer").order_by(
        "manufacturer__name", "name"
    )

    # Befintlig markering
    existing_mark = StampImage.objects.filter(
        axe_image=axe_image, image_type="axe_mark"
    ).first()

    context = {
        "axe_image": axe_image,
        "axe": axe_image.axe,
        "available_stamps": available_stamps,
        "existing_mark": existing_mark,
    }

    return render(request, "axes/mark_axe_image_as_stamp.html", context)


@login_required
def unmark_axe_image_stamp(request, axe_id, image_id):
    """Ta bort markering av stämpel från AxeImage"""

    axe_image = get_object_or_404(AxeImage, id=image_id, axe_id=axe_id)
    stamp_mark = get_object_or_404(
        StampImage, axe_image=axe_image, image_type="axe_mark"
    )

    if request.method == "POST":
        stamp_name = stamp_mark.stamp.name
        stamp_mark.delete()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "message": f"Stämpelmarkering borttagen: {stamp_name}",
                }
            )

        messages.success(request, f"Stämpelmarkering borttagen: {stamp_name}")
        return redirect("axe_detail", pk=axe_id)

    # För AJAX GET-anrop, returnera modal-innehåll
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        context = {
            "axe_image": axe_image,
            "axe": axe_image.axe,
            "stamp_mark": stamp_mark,
        }
        return render(request, "axes/unmark_axe_image_stamp_modal.html", context)

    context = {
        "axe_image": axe_image,
        "axe": axe_image.axe,
        "stamp_mark": stamp_mark,
    }

    return render(request, "axes/unmark_axe_image_stamp.html", context)


@login_required
def edit_axe_image_stamp(request, axe_id, mark_id):
    """Redigera stämpelmarkering på AxeImage med samma funktionalitet som axe_stamp_form"""

    stamp_mark = get_object_or_404(
        StampImage, id=mark_id, axe_image__axe_id=axe_id, image_type="axe_mark"
    )
    axe_image = stamp_mark.axe_image
    axe = axe_image.axe

    if request.method == "POST":
        # Hantera olika typer av POST-requests
        action = request.POST.get("action", "")

        if action == "save_stamp":
            # Användaren har markerat en bild och vill spara stämpeln
            stamp_id = request.POST.get("stamp")
            x_coord = request.POST.get("x_coordinate")
            y_coord = request.POST.get("y_coordinate")
            width = request.POST.get("width")
            height = request.POST.get("height")
            position = request.POST.get("position", "")
            uncertainty_level = request.POST.get("uncertainty_level", "")
            comment = request.POST.get("comment", "")

            if stamp_id:
                stamp = get_object_or_404(Stamp, id=stamp_id)

                # Konvertera koordinater till Decimal
                from decimal import Decimal
                x_coord_decimal = Decimal(x_coord) if x_coord else None
                y_coord_decimal = Decimal(y_coord) if y_coord else None
                width_decimal = Decimal(width) if width else None
                height_decimal = Decimal(height) if height else None

                # Uppdatera AxeImageStamp
                stamp_mark.stamp = stamp
                stamp_mark.x_coordinate = x_coord_decimal
                stamp_mark.y_coordinate = y_coord_decimal
                stamp_mark.width = width_decimal
                stamp_mark.height = height_decimal
                stamp_mark.position = position
                stamp_mark.uncertainty_level = uncertainty_level
                stamp_mark.comment = comment
                stamp_mark.save()

                messages.success(
                    request, f"Stämpelmarkering uppdaterades framgångsrikt."
                )
                return redirect("axe_detail", pk=axe_id)
            else:
                messages.error(request, "Stämpel måste väljas.")
        else:
            # Hantera vanlig form submission
            form = StampImageMarkForm(request.POST, instance=stamp_mark)
            if form.is_valid():
                # Hantera koordinater från formuläret
                x_coord = request.POST.get("x_coordinate")
                y_coord = request.POST.get("y_coordinate")
                width = request.POST.get("width")
                height = request.POST.get("height")

                stamp_mark = form.save(commit=False)

                # Uppdatera koordinater om de finns
                if x_coord and y_coord and width and height:
                    from decimal import Decimal
                    stamp_mark.x_coordinate = Decimal(x_coord)
                    stamp_mark.y_coordinate = Decimal(y_coord)
                    stamp_mark.width = Decimal(width)
                    stamp_mark.height = Decimal(height)

                stamp_mark.save()

                # Om det är en AJAX-request, returnera JSON
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Stämpelmarkering uppdaterades framgångsrikt.",
                            "mark_id": stamp_mark.id,
                        }
                    )

                messages.success(
                    request, "Stämpelmarkering uppdaterades framgångsrikt."
                )
                return redirect("axe_detail", pk=axe_id)
    else:
        form = StampImageMarkForm(instance=stamp_mark)

    # Skapa en kontext för den nya stamp_image_mark_form.html template
    context = {
        "axe": axe,
        "selected_image": axe_image,
        "title": f"Redigera stämpelmarkering - {axe.display_id}",
        "form": form,
    }

    return render(request, "axes/stamp_image_mark_form.html", context)


@login_required
def stamp_image_crop(request, stamp_id):
    """Visa och hantera beskärning av stämpelbilder"""

    stamp = get_object_or_404(Stamp.objects.select_related("manufacturer"), id=stamp_id)

    # Hämta alla StampImage-kopplingar för denna stämpel
    stamp_images = (
        StampImage.objects.filter(stamp=stamp)
        .select_related("axe_image__axe")
        .order_by("-is_primary", "-created_at")
    )

    context = {
        "stamp": stamp,
        "axe_image_marks": stamp_images,
    }

    return render(request, "axes/stamp_image_crop.html", context)


@login_required
def set_primary_stamp_image(request, stamp_id, mark_id):
    """Sätt en AxeImageStamp som huvudbild för stämpeln"""

    stamp = get_object_or_404(Stamp, id=stamp_id)
    mark = get_object_or_404(StampImage, id=mark_id, stamp=stamp)

    if request.method == "POST":
        # Hantera JSON-data från AJAX-anrop
        if (
            request.headers.get("Content-Type") == "application/json"
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        ):
            try:
                import json

                data = json.loads(request.body)
                is_primary = data.get("is_primary", True)

                if is_primary:
                    # Ta bort tidigare huvudbild
                    StampImage.objects.filter(stamp=stamp, is_primary=True).update(
                        is_primary=False
                    )
                    # Sätt ny huvudbild
                    mark.is_primary = True
                    mark.save()
                else:
                    # Ta bort huvudbildsmarkering
                    mark.is_primary = False
                    mark.save()

                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Huvudbild uppdaterad för stämpel: {stamp.name}",
                    }
                )
            except json.JSONDecodeError:
                return JsonResponse(
                    {"success": False, "error": "Ogiltig JSON-data"}, status=400
                )
        else:
            # Hantera vanligt POST-anrop (icke-AJAX)
            # Ta bort tidigare huvudbild
            StampImage.objects.filter(stamp=stamp, is_primary=True).update(
                is_primary=False
            )
            # Sätt ny huvudbild
            mark.is_primary = True
            mark.save()

            messages.success(request, f"Huvudbild satt för stämpel: {stamp.name}")
            return redirect("stamp_detail", stamp_id=stamp_id)

    return redirect("stamp_detail", stamp_id=stamp_id)


@login_required
def update_axe_image_stamp_show_full(request, mark_id):
    """Uppdatera show_full_image för en AxeImageStamp"""

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Endast POST-anrop tillåtet"})

    try:
        mark = get_object_or_404(StampImage, id=mark_id)

        # Läs JSON-data från request body
        import json

        data = json.loads(request.body)
        show_full_image = data.get("show_full_image", False)

        mark.show_full_image = show_full_image
        mark.save()

        return JsonResponse(
            {"success": True, "message": "Inställning uppdaterad framgångsrikt"}
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def edit_axe_stamp(request, axe_id, axe_stamp_id):
    """Redigera en befintlig yxstämpel med bildmarkering"""

    axe = get_object_or_404(Axe, id=axe_id)
    axe_stamp = get_object_or_404(AxeStamp, id=axe_stamp_id, axe=axe)

    # Hämta befintliga bilder för yxan
    existing_images = axe.images.all().order_by("order")

    # Hämta befintlig StampImage för denna stämpel
    existing_stamp_image = StampImage.objects.filter(
        stamp=axe_stamp.stamp, axe_image__axe=axe, image_type="axe_mark"
    ).first()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "select_image":
            # Steg 1: Välj bild
            selected_image_id = request.POST.get("selected_image_id")
            if selected_image_id:
                selected_image = get_object_or_404(
                    AxeImage, id=selected_image_id, axe=axe
                )
                available_stamps = Stamp.objects.all().order_by("name")

                # Hämta befintlig StampImage för den valda bilden
                selected_image_stamp = StampImage.objects.filter(
                    stamp=axe_stamp.stamp,
                    axe_image=selected_image,
                    image_type="axe_mark",
                ).first()

                context = {
                    "axe": axe,
                    "axe_stamp": axe_stamp,
                    "selected_image": selected_image,
                    "available_stamps": available_stamps,
                    "existing_stamp_image": selected_image_stamp,
                    "title": f"Redigera stämpel - {axe.display_id}",
                }
                return render(request, "axes/axe_stamp_edit.html", context)

        elif action == "save_stamp":
            # Steg 2: Spara stämpel med bildmarkering
            form = AxeStampForm(request.POST, instance=axe_stamp)
            if form.is_valid():
                # Spara AxeStamp
                axe_stamp = form.save()

                # Hantera AxeImageStamp
                selected_image_id = request.POST.get("selected_image_id")
                if selected_image_id:
                    selected_image = get_object_or_404(
                        AxeImage, id=selected_image_id, axe=axe
                    )

                    # Ta bort befintlig StampImage för samma stämpel på samma bild
                    StampImage.objects.filter(
                        stamp=axe_stamp.stamp,
                        axe_image=selected_image,
                        image_type="axe_mark",
                    ).delete()

                    # Skapa ny StampImage
                    x_coord = request.POST.get("x_coordinate")
                    y_coord = request.POST.get("y_coordinate")
                    width = request.POST.get("width")
                    height = request.POST.get("height")

                    if x_coord and y_coord and width and height:
                        # Konvertera koordinater till Decimal
                        from decimal import Decimal
                        StampImage.objects.create(
                            axe_image=selected_image,
                            stamp=axe_stamp.stamp,
                            image_type="axe_mark",
                            x_coordinate=Decimal(x_coord),
                            y_coordinate=Decimal(y_coord),
                            width=Decimal(width),
                            height=Decimal(height),
                            comment=request.POST.get("image_comment", ""),
                        )
                    else:
                        # Om inga koordinater finns, ta bort alla StampImage för denna stämpel
                        StampImage.objects.filter(
                            stamp=axe_stamp.stamp,
                            axe_image__axe=axe,
                            image_type="axe_mark",
                        ).delete()

                messages.success(
                    request, f'Stämpel "{axe_stamp.stamp.name}" uppdaterades.'
                )
                return redirect("axe_detail", pk=axe.id)
        else:
            # Vanlig formulärhantering (utan bildmarkering)
            form = AxeStampForm(request.POST, instance=axe_stamp)
            if form.is_valid():
                form.save()
                messages.success(
                    request, f'Stämpel "{axe_stamp.stamp.name}" uppdaterades.'
                )
                return redirect("axe_detail", pk=axe.id)
    else:
        form = AxeStampForm(instance=axe_stamp)

    context = {
        "axe": axe,
        "axe_stamp": axe_stamp,
        "existing_images": existing_images,
        "existing_stamp_image": existing_stamp_image,
        "form": form,
        "title": f"Redigera stämpel - {axe.display_id}",
    }

    # Om det finns en befintlig StampImage, förvalda den aktuella bilden
    if existing_stamp_image:
        context["selected_image"] = existing_stamp_image.axe_image
        context["available_stamps"] = Stamp.objects.all().order_by("name")

    return render(request, "axes/axe_stamp_edit.html", context)


@login_required
def edit_axe_image_stamp_via_axe_stamp(request, axe_id, image_id):
    """Redigera stämpelmarkering via AxeStamp-formuläret"""

    axe_image = get_object_or_404(AxeImage, id=image_id, axe_id=axe_id)
    stamp_mark = get_object_or_404(
        StampImage, axe_image=axe_image, image_type="axe_mark"
    )

    # Omdirigera till edit_axe_image_stamp med rätt parametrar
    return redirect("edit_axe_image_stamp", axe_id=axe_id, mark_id=stamp_mark.id)


@login_required
def remove_axe_image_stamp(request, axe_id, mark_id):
    """Ta bort specifik stämpelmarkering från AxeImageStamp"""

    stamp_mark = get_object_or_404(
        StampImage, id=mark_id, axe_image__axe_id=axe_id, image_type="axe_mark"
    )

    if request.method == "POST":
        stamp_name = stamp_mark.stamp.name
        stamp_mark.delete()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "message": f"Stämpelmarkering borttagen: {stamp_name}",
                }
            )

        messages.success(request, f"Stämpelmarkering borttagen: {stamp_name}")
        return redirect("axe_detail", pk=axe_id)

    # För AJAX GET-anrop, returnera modal-innehåll
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        context = {
            "axe_image": stamp_mark.axe_image,
            "axe": stamp_mark.axe_image.axe,
            "stamp_mark": stamp_mark,
        }
        return render(request, "axes/unmark_axe_image_stamp_modal.html", context)

    context = {
        "axe_image": stamp_mark.axe_image,
        "axe": stamp_mark.axe_image.axe,
        "stamp_mark": stamp_mark,
    }

    return render(request, "axes/unmark_axe_image_stamp.html", context)
