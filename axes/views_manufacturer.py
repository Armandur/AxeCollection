from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Manufacturer, ManufacturerImage, ManufacturerLink, Axe, Transaction
from django.db.models import Sum, Max
import json
import os
import shutil
from django.conf import settings


def get_available_parents(current_manufacturer=None):
    """
    Hämta alla tillgängliga föräldrar för en tillverkare.
    Exkluderar den aktuella tillverkaren och alla dess undertillverkare (rekursivt).
    """
    if current_manufacturer is None:
        # För nya tillverkare, alla tillverkare är tillgängliga
        all_manufacturers = Manufacturer.objects.all()
    else:
        # För befintliga tillverkare, exkludera sig själv och alla undertillverkare
        excluded_ids = {current_manufacturer.id}

        # Rekursivt hitta alla undertillverkare
        def get_all_sub_manufacturer_ids(manufacturer):
            for sub in manufacturer.sub_manufacturers.all():
                excluded_ids.add(sub.id)
                get_all_sub_manufacturer_ids(sub)

        get_all_sub_manufacturer_ids(current_manufacturer)
        all_manufacturers = Manufacturer.objects.exclude(id__in=excluded_ids)

    # Sortera hierarkiskt istället för alfabetiskt
    def _is_descendant(manufacturer, ancestor):
        """Kontrollera om manufacturer är en efterkommande till ancestor"""
        current = manufacturer
        while current.parent:
            if current.parent == ancestor:
                return True
            current = current.parent
        return False

    def sort_hierarchically(manufacturers):
        """Sorterar tillverkare hierarkiskt: huvudtillverkare först, sedan undertillverkare i korrekt ordning"""
        main_manufacturers = [m for m in manufacturers if m.hierarchy_level == 0]
        sorted_list = []

        for main in main_manufacturers:
            sorted_list.append(main)
            # Sortera undertillverkare hierarkiskt

            def sort_children_recursive(parent=None):
                """Sorterar barn rekursivt under en förälder"""
                children = [m for m in manufacturers if m.parent == parent]
                children.sort(key=lambda x: x.name)  # Sortera barn alfabetiskt
                result = []
                for child in children:
                    result.append(child)
                    # Lägg till alla barn till detta barn rekursivt
                    result.extend(sort_children_recursive(child))
                return result

            # Sortera alla undertillverkare rekursivt
            sorted_subs = sort_children_recursive(main)
            sorted_list.extend(sorted_subs)

        return sorted_list

    return sort_hierarchically(all_manufacturers)


def manufacturer_list(request):
    # Hämta alla tillverkare och sortera dem hierarkiskt
    all_manufacturers = Manufacturer.objects.all()

    # Sortera hierarkiskt istället för alfabetiskt
    def _is_descendant(manufacturer, ancestor):
        """Kontrollera om manufacturer är en efterkommande till ancestor"""
        current = manufacturer
        while current.parent:
            if current.parent == ancestor:
                return True
            current = current.parent
        return False

    def sort_hierarchically(manufacturers):
        """Sorterar tillverkare hierarkiskt: huvudtillverkare först, sedan undertillverkare i korrekt ordning"""
        main_manufacturers = [m for m in manufacturers if m.hierarchy_level == 0]
        sorted_list = []

        for main in main_manufacturers:
            sorted_list.append(main)
            # Hitta alla undertillverkare för denna huvudtillverkare
            [
                m
                for m in manufacturers
                if m.hierarchy_level > 0 and _is_descendant(m, main)
            ]

            # Sortera undertillverkare hierarkiskt
            def sort_children_recursive(parent=None):
                """Sorterar barn rekursivt under en förälder"""
                children = [m for m in manufacturers if m.parent == parent]
                children.sort(key=lambda x: x.name)  # Sortera barn alfabetiskt
                result = []
                for child in children:
                    result.append(child)
                    # Lägg till alla barn till detta barn rekursivt
                    result.extend(sort_children_recursive(child))
                return result

            # Sortera alla undertillverkare rekursivt
            sorted_subs = sort_children_recursive(main)
            sorted_list.extend(sorted_subs)

        return sorted_list

    manufacturers = sort_hierarchically(all_manufacturers)

    # Ta bort all tilldelning av statistikfält, använd properties direkt i template/context
    total_manufacturers = len(manufacturers)
    total_axes = Axe.objects.count()
    total_transactions = Transaction.objects.count()
    average_axes_per_manufacturer = (
        total_axes / total_manufacturers if total_manufacturers > 0 else 0
    )
    # Hämta inställningar för DataTables
    from .models import Settings

    settings = Settings.get_settings()
    if request.user.is_authenticated:
        default_page_length = int(settings.default_manufacturers_rows_private)
    else:
        default_page_length = int(settings.default_manufacturers_rows_public)

    context = {
        "manufacturers": manufacturers,
        "total_manufacturers": total_manufacturers,
        "total_axes": total_axes,
        "total_transactions": total_transactions,
        "average_axes_per_manufacturer": average_axes_per_manufacturer,
        "default_page_length": default_page_length,
    }
    return render(request, "axes/manufacturer_list.html", context)


@login_required
def manufacturer_create(request):
    """Skapa en ny tillverkare"""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        information = request.POST.get("information", "").strip()
        parent_id = request.POST.get("parent", "").strip()
        manufacturer_type = request.POST.get("manufacturer_type", "TILLVERKARE")

        if not name:
            messages.error(request, "Tillverkarnamn är obligatoriskt")
            available_parents = get_available_parents()
            return render(
                request,
                "axes/manufacturer_form.html",
                {
                    "name": name,
                    "information": information,
                    "parent": parent_id,
                    "manufacturer_type": manufacturer_type,
                    "available_parents": available_parents,
                    "manufacturers": available_parents,  # Lägg till för hierarchy_prefix filtren
                },
            )

        # Kontrollera om tillverkaren redan finns
        existing_manufacturer = Manufacturer.objects.filter(name__iexact=name).first()
        if existing_manufacturer:
            messages.error(request, f'Tillverkaren "{name}" finns redan')
            available_parents = get_available_parents()
            return render(
                request,
                "axes/manufacturer_form.html",
                {
                    "name": name,
                    "information": information,
                    "parent": parent_id,
                    "manufacturer_type": manufacturer_type,
                    "existing_manufacturer": existing_manufacturer,
                    "available_parents": available_parents,
                    "manufacturers": available_parents,  # Lägg till för hierarchy_prefix filtren
                },
            )

        # Hämta parent om vald
        parent = None
        if parent_id:
            try:
                parent = Manufacturer.objects.get(id=parent_id)
            except Manufacturer.DoesNotExist:
                messages.error(request, "Vald överordnad tillverkare finns inte")
                available_parents = get_available_parents()
                return render(
                    request,
                    "axes/manufacturer_form.html",
                    {
                        "name": name,
                        "information": information,
                        "parent": parent_id,
                        "manufacturer_type": manufacturer_type,
                        "available_parents": available_parents,
                        "manufacturers": available_parents,  # Lägg till för hierarchy_prefix filtren
                    },
                )

        # Behåll användarens val av manufacturer_type, oavsett om det är en undertillverkare eller inte

        # Skapa tillverkaren
        manufacturer = Manufacturer.objects.create(
            name=name,
            information=information if information else None,
            parent=parent,
            manufacturer_type=manufacturer_type,
        )

        messages.success(request, f'Tillverkaren "{manufacturer.name}" har skapats')
        return redirect("manufacturer_detail", pk=manufacturer.pk)

    # Hämta parent från URL-parametern om den finns
    parent_id = request.GET.get("parent", "")

    # Konvertera till heltal om det finns, annars None
    parent_int = None
    if parent_id:
        try:
            parent_int = int(parent_id)
        except ValueError:
            parent_int = None

    available_parents = get_available_parents()
    return render(
        request,
        "axes/manufacturer_form.html",
        {
            "parent": parent_int,
            "available_parents": available_parents,
            "manufacturers": available_parents,  # Lägg till för hierarchy_prefix filtren
        },
    )


@login_required
def manufacturer_edit(request, pk):
    """Redigera en befintlig tillverkare"""
    manufacturer = get_object_or_404(Manufacturer, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        information = request.POST.get("information", "").strip()
        parent_id = request.POST.get("parent", "").strip()
        manufacturer_type = request.POST.get("manufacturer_type", "TILLVERKARE")

        if not name:
            messages.error(request, "Tillverkarnamn är obligatoriskt")
            available_parents = get_available_parents(manufacturer)
            return render(
                request,
                "axes/manufacturer_form.html",
                {
                    "manufacturer": manufacturer,
                    "name": name,
                    "information": information,
                    "parent": parent_id,
                    "manufacturer_type": manufacturer_type,
                    "available_parents": available_parents,
                    "manufacturers": available_parents,  # Lägg till för hierarchy_prefix filtren
                    "is_edit": True,
                },
            )

        # Kontrollera om tillverkarnamn redan finns (exkludera sig själv)
        existing_manufacturer = (
            Manufacturer.objects.filter(name__iexact=name)
            .exclude(id=manufacturer.id)
            .first()
        )
        if existing_manufacturer:
            messages.error(request, f'Tillverkaren "{name}" finns redan')
            available_parents = get_available_parents(manufacturer)
            return render(
                request,
                "axes/manufacturer_form.html",
                {
                    "manufacturer": manufacturer,
                    "name": name,
                    "information": information,
                    "parent": parent_id,
                    "manufacturer_type": manufacturer_type,
                    "existing_manufacturer": existing_manufacturer,
                    "available_parents": available_parents,
                    "manufacturers": available_parents,  # Lägg till för hierarchy_prefix filtren
                    "is_edit": True,
                },
            )

        # Validera parent (förhindra cirkulära referenser)
        parent = None
        if parent_id:
            try:
                parent = Manufacturer.objects.get(id=parent_id)
                # Kontrollera att parent inte är denna tillverkare själv
                if parent.id == manufacturer.id:
                    messages.error(
                        request,
                        "En tillverkare kan inte vara sin egen överordnad tillverkare",
                    )
                    available_parents = get_available_parents(manufacturer)
                    return render(
                        request,
                        "axes/manufacturer_form.html",
                        {
                            "manufacturer": manufacturer,
                            "name": name,
                            "information": information,
                            "parent": parent_id,
                            "manufacturer_type": manufacturer_type,
                            "available_parents": available_parents,
                            "manufacturers": available_parents,  # Lägg till för hierarchy_prefix filtren
                            "is_edit": True,
                        },
                    )

                # Kontrollera att parent inte är en undertillverkare av denna tillverkare (rekursivt)
                def check_circular_reference(check_manufacturer, target_id):
                    if check_manufacturer.parent_id == target_id:
                        return True
                    if check_manufacturer.parent:
                        return check_circular_reference(
                            check_manufacturer.parent, target_id
                        )
                    return False

                if check_circular_reference(parent, manufacturer.id):
                    messages.error(
                        request,
                        "En tillverkare kan inte vara överordnad tillverkare till sin egen överordnad tillverkare",
                    )
                    available_parents = get_available_parents(manufacturer)
                    return render(
                        request,
                        "axes/manufacturer_form.html",
                        {
                            "manufacturer": manufacturer,
                            "name": name,
                            "information": information,
                            "parent": parent_id,
                            "manufacturer_type": manufacturer_type,
                            "available_parents": available_parents,
                            "manufacturers": available_parents,  # Lägg till för hierarchy_prefix filtren
                            "is_edit": True,
                        },
                    )

            except Manufacturer.DoesNotExist:
                messages.error(request, "Vald överordnad tillverkare finns inte")
                available_parents = get_available_parents(manufacturer)
                return render(
                    request,
                    "axes/manufacturer_form.html",
                    {
                        "manufacturer": manufacturer,
                        "name": name,
                        "information": information,
                        "parent": parent_id,
                        "manufacturer_type": manufacturer_type,
                        "available_parents": available_parents,
                        "manufacturers": available_parents,  # Lägg till för hierarchy_prefix filtren
                        "is_edit": True,
                    },
                )

        # Behåll användarens val av manufacturer_type, oavsett om det är en undertillverkare eller inte

        # Uppdatera tillverkaren
        manufacturer.name = name
        manufacturer.information = information if information else None
        manufacturer.parent = parent
        manufacturer.manufacturer_type = manufacturer_type
        manufacturer.save()

        messages.success(request, f'Tillverkaren "{manufacturer.name}" har uppdaterats')
        return redirect("manufacturer_detail", pk=manufacturer.pk)

    available_parents = get_available_parents(manufacturer)
    return render(
        request,
        "axes/manufacturer_form.html",
        {
            "manufacturer": manufacturer,
            "name": manufacturer.name,
            "information": manufacturer.information or "",
            "parent": manufacturer.parent.id if manufacturer.parent else "",
            "manufacturer_type": manufacturer.manufacturer_type,
            "available_parents": available_parents,
            "manufacturers": available_parents,  # Lägg till för hierarchy_prefix filtren
            "is_edit": True,
        },
    )


def manufacturer_detail(request, pk):
    manufacturer = get_object_or_404(Manufacturer, pk=pk)
    axes = Axe.objects.filter(manufacturer=manufacturer).order_by("-id")
    images = ManufacturerImage.objects.filter(manufacturer=manufacturer).order_by(
        "image_type", "order"
    )
    links = ManufacturerLink.objects.filter(manufacturer=manufacturer).order_by(
        "link_type", "order"
    )

    # Hämta yxor från undertillverkare
    sub_manufacturer_axes = []
    for sub_manufacturer in manufacturer.all_sub_manufacturers:
        sub_axes = Axe.objects.filter(manufacturer=sub_manufacturer).order_by("-id")
        for axe in sub_axes:
            axe.sub_manufacturer_name = sub_manufacturer.name
            axe.sub_manufacturer_id = sub_manufacturer.id
            # Beräkna status_class för undertillverkare också
            if axe.status == "MOTTAGEN":
                axe.status_class = "bg-success"
            elif axe.status == "KÖPT":
                axe.status_class = "bg-warning"
            elif axe.status == "SÅLD":
                axe.status_class = "bg-secondary"
            else:
                # Om statusfältet är tomt eller okänt, bestäm utifrån senaste transaktion
                last_transaction = (
                    Transaction.objects.filter(axe=axe)
                    .order_by("-transaction_date")
                    .first()
                )
                if last_transaction:
                    if last_transaction.type == "SÄLJ":
                        axe.status = "SÅLD"
                        axe.status_class = "bg-secondary"
                    elif last_transaction.type == "KÖP":
                        axe.status = "KÖPT"
                        axe.status_class = "bg-warning"
                    else:
                        axe.status = "OKÄND"
                        axe.status_class = "bg-light"
                else:
                    axe.status = "OKÄND"
                    axe.status_class = "bg-light"
        sub_manufacturer_axes.extend(sub_axes)

    # Statistik för direkt kopplade yxor
    total_axes = axes.count()
    transactions = Transaction.objects.filter(axe__manufacturer=manufacturer)
    total_transactions = transactions.count()
    buy_transactions = transactions.filter(type="KÖP")
    sale_transactions = transactions.filter(type="SÄLJ")
    total_buy_value = buy_transactions.aggregate(total=Sum("price"))["total"] or 0
    total_sale_value = sale_transactions.aggregate(total=Sum("price"))["total"] or 0
    total_profit = total_sale_value - total_buy_value
    average_profit_per_axe = total_profit / total_axes if total_axes > 0 else 0
    # Köp/sälj-antal
    buy_count = buy_transactions.count()
    sale_count = sale_transactions.count()

    # Statistik inklusive undertillverkare
    total_axes_including_sub = manufacturer.axe_count_including_sub_manufacturers
    total_buy_value_including_sub = (
        manufacturer.total_buy_value_including_sub_manufacturers
    )
    total_sale_value_including_sub = (
        manufacturer.total_sale_value_including_sub_manufacturers
    )
    total_profit_including_sub = manufacturer.net_value_including_sub_manufacturers
    buy_count_including_sub = manufacturer.buy_count_including_sub_manufacturers
    sale_count_including_sub = manufacturer.sale_count_including_sub_manufacturers
    # Status för varje yxa
    for axe in axes:
        # Prioritera statusfältet
        if axe.status == "MOTTAGEN":
            axe.status_class = "bg-success"
        elif axe.status == "KÖPT":
            axe.status_class = "bg-warning"
        elif axe.status == "SÅLD":
            axe.status_class = "bg-secondary"
        else:
            # Om statusfältet är tomt eller okänt, bestäm utifrån senaste transaktion
            last_transaction = (
                Transaction.objects.filter(axe=axe)
                .order_by("-transaction_date")
                .first()
            )
            if last_transaction:
                if last_transaction.type == "SÄLJ":
                    axe.status = "SÅLD"
                    axe.status_class = "bg-secondary"
                elif last_transaction.type == "KÖP":
                    axe.status = "KÖPT"
                    axe.status_class = "bg-warning"
                else:
                    axe.status = "OKÄND"
                    axe.status_class = "bg-light"
            else:
                axe.status = "OKÄND"
                axe.status_class = "bg-light"
    # Gruppera bilder efter typ
    images_by_type = {}
    for image in images:
        if image.image_type not in images_by_type:
            images_by_type[image.image_type] = []
        images_by_type[image.image_type].append(image)

    # Gruppera länkar efter typ
    links_by_type = {}
    for link in links:
        if link.link_type not in links_by_type:
            links_by_type[link.link_type] = []
        links_by_type[link.link_type].append(link)
    # Alla transaktioner
    transactions = (
        Transaction.objects.filter(axe__manufacturer=manufacturer)
        .select_related("axe", "contact", "platform")
        .order_by("-transaction_date")
    )
    # Unika kontakter
    unique_contacts = set()
    for transaction in transactions:
        if transaction.contact:
            unique_contacts.add(transaction.contact)

    # Skapa breadcrumbs som visar hierarki
    breadcrumbs = [
        {"text": "Hem", "url": "/yxor/"},
        {"text": "Tillverkare", "url": "/tillverkare/"},
    ]

    # Lägg till överordnad tillverkare om det finns
    if manufacturer.parent:
        breadcrumbs.append(
            {
                "text": manufacturer.parent.name,
                "url": f"/tillverkare/{manufacturer.parent.id}/",
            }
        )

    # Lägg till aktuell tillverkare
    breadcrumbs.append({"text": manufacturer.name, "url": None})

    # Förbereda separata listor för undertillverkare och smeder
    sub_manufacturers = manufacturer.sub_manufacturers.all().order_by("name")
    sub_tillverkare = [
        m for m in sub_manufacturers if m.manufacturer_type == "TILLVERKARE"
    ]
    sub_smeder = [m for m in sub_manufacturers if m.manufacturer_type == "SMED"]

    context = {
        "manufacturer": manufacturer,
        "axes": axes,
        "sub_manufacturer_axes": sub_manufacturer_axes,
        "images": images,
        "links": links,
        "images_by_type": images_by_type,
        "links_by_type": links_by_type,
        "transactions": transactions,
        "unique_contacts": unique_contacts,
        "total_axes": total_axes,
        "total_transactions": total_transactions,
        "total_buy_value": total_buy_value,
        "total_sale_value": total_sale_value,
        "total_profit": total_profit,
        "average_profit_per_axe": average_profit_per_axe,
        "buy_count": buy_count,
        "sale_count": sale_count,
        "total_axes_including_sub": total_axes_including_sub,
        "total_buy_value_including_sub": total_buy_value_including_sub,
        "total_sale_value_including_sub": total_sale_value_including_sub,
        "total_profit_including_sub": total_profit_including_sub,
        "buy_count_including_sub": buy_count_including_sub,
        "sale_count_including_sub": sale_count_including_sub,
        "breadcrumbs": breadcrumbs,
        "sub_tillverkare": sub_tillverkare,
        "sub_smeder": sub_smeder,
    }
    return render(request, "axes/manufacturer_detail.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def edit_manufacturer_information(request, pk):
    """AJAX-vy för att redigera tillverkarinformation"""
    try:
        manufacturer = get_object_or_404(Manufacturer, pk=pk)
        data = json.loads(request.body)
        new_information = data.get("information", "").strip()

        # Validering
        if len(new_information) > 10000:  # Max 10KB
            return JsonResponse(
                {
                    "success": False,
                    "error": "Informationen är för lång (max 10 000 tecken)",
                },
                status=400,
            )

        manufacturer.information = new_information
        manufacturer.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Information uppdaterad",
                "information": manufacturer.information,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Ogiltig JSON-data"}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Ett fel uppstod: {str(e)}"}, status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def edit_manufacturer_name(request, pk):
    """AJAX-vy för att redigera tillverkarnamn"""
    try:
        manufacturer = get_object_or_404(Manufacturer, pk=pk)
        data = json.loads(request.body)
        new_name = data.get("name", "").strip()
        if not new_name:
            return JsonResponse(
                {"success": False, "error": "Namnet får inte vara tomt."}, status=400
            )
        if len(new_name) > 200:
            return JsonResponse(
                {"success": False, "error": "Namnet får vara max 200 tecken."},
                status=400,
            )
        manufacturer.name = new_name
        manufacturer.save()
        return JsonResponse({"success": True, "name": manufacturer.name})
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Ogiltig JSON-data"}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Ett fel uppstod: {str(e)}"}, status=500
        )


@require_http_methods(["POST"])
def edit_manufacturer_image(request, image_id):
    """Redigera tillverkarbild via AJAX"""
    try:
        image = ManufacturerImage.objects.get(id=image_id)
        data = json.loads(request.body)

        # Uppdatera fält
        if "caption" in data:
            image.caption = data["caption"]
        if "description" in data:
            image.description = data["description"]
        if "image_type" in data:
            image.image_type = data["image_type"]

        image.save()

        return JsonResponse({"success": True, "message": "Bild uppdaterad"})
    except ManufacturerImage.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Bild hittades inte"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["POST"])
def delete_manufacturer_image(request, image_id):
    """Ta bort tillverkarbild via AJAX"""
    try:
        image = ManufacturerImage.objects.get(id=image_id)
        image.delete()

        return JsonResponse({"success": True, "message": "Bild borttagen"})
    except ManufacturerImage.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Bild hittades inte"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["POST"])
def add_manufacturer_image(request):
    """Lägg till ny tillverkarbild via AJAX"""
    try:
        manufacturer_id = request.POST.get("manufacturer_id")
        image_file = request.FILES.get("image")
        caption = request.POST.get("caption", "")
        description = request.POST.get("description", "")
        image_type = request.POST.get("image_type", "STAMP")

        if not manufacturer_id or not image_file:
            return JsonResponse(
                {"success": False, "error": "Tillverkare och bild krävs"}, status=400
            )

        manufacturer = Manufacturer.objects.get(id=manufacturer_id)

        # Skapa ny bild
        image = ManufacturerImage.objects.create(
            manufacturer=manufacturer,
            image=image_file,
            caption=caption,
            description=description,
            image_type=image_type,
        )

        return JsonResponse(
            {"success": True, "message": "Bild uppladdad", "image_id": image.id}
        )
    except Manufacturer.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Tillverkare hittades inte"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["POST"])
def reorder_manufacturer_images(request):
    """Ändra ordning på tillverkarbilder via AJAX"""
    try:
        data = json.loads(request.body)
        manufacturer_id = data.get("manufacturer_id")
        order_data = data.get("order_data", [])

        if not manufacturer_id or not order_data:
            return JsonResponse(
                {"success": False, "error": "Tillverkare och ordningsdata krävs"},
                status=400,
            )

        # Uppdatera ordningen för varje bild
        for item in order_data:
            image_id = item.get("image_id")
            new_order = item.get("order")

            if image_id and new_order is not None:
                try:
                    image = ManufacturerImage.objects.get(
                        id=image_id, manufacturer_id=manufacturer_id
                    )
                    image.order = new_order
                    image.save()
                except ManufacturerImage.DoesNotExist:
                    continue

        return JsonResponse({"success": True, "message": "Bildordning uppdaterad"})
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Ogiltig JSON-data"}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["POST"])
def edit_manufacturer_link(request, link_id):
    """Redigera tillverkarlänk via AJAX"""
    try:
        link = ManufacturerLink.objects.get(id=link_id)
        data = json.loads(request.body)

        # Uppdatera fält
        if "title" in data:
            link.title = data["title"]
        if "url" in data:
            link.url = data["url"]
        if "link_type" in data:
            link.link_type = data["link_type"]
        if "description" in data:
            link.description = data["description"]
        if "is_active" in data:
            link.is_active = data["is_active"]

        link.save()

        return JsonResponse({"success": True, "message": "Länk uppdaterad"})
    except ManufacturerLink.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Länk hittades inte"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["POST"])
def delete_manufacturer_link(request, link_id):
    """Ta bort tillverkarlänk via AJAX"""
    try:
        link = ManufacturerLink.objects.get(id=link_id)
        link.delete()

        return JsonResponse({"success": True, "message": "Länk borttagen"})
    except ManufacturerLink.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Länk hittades inte"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_manufacturer(request, pk):
    """Ta bort tillverkare och hantera deras bilder och yxor"""
    try:
        manufacturer = get_object_or_404(Manufacturer, pk=pk)
        axe_action = request.POST.get("axe_action", "move")
        target_manufacturer_id = request.POST.get("target_manufacturer_id")

        axe_count = manufacturer.axe_count
        image_count = manufacturer.images.count()
        target_manufacturer_name = None  # Initiera variabeln

        # Hantera yxor
        if axe_count > 0:
            if axe_action == "delete":
                # Ta bort alla yxor (och deras bilder flyttas automatiskt till unlinked_images)
                for axe in manufacturer.axes:
                    axe.delete()
                target_manufacturer_name = None
            elif axe_action == "move_to_specific" and target_manufacturer_id:
                # Flytta yxor till specifik tillverkare
                try:
                    target_manufacturer = Manufacturer.objects.get(
                        id=target_manufacturer_id
                    )
                    manufacturer.axe_set.update(manufacturer=target_manufacturer)
                    target_manufacturer_name = target_manufacturer.name
                except Manufacturer.DoesNotExist:
                    return JsonResponse(
                        {
                            "success": False,
                            "error": f"Tillverkare med ID {target_manufacturer_id} finns inte",
                        }
                    )
            else:
                # Flytta yxor till "Okänd tillverkare"
                unknown_manufacturer, created = Manufacturer.objects.get_or_create(
                    name="Okänd tillverkare"
                )
                manufacturer.axe_set.update(manufacturer=unknown_manufacturer)
                target_manufacturer_name = unknown_manufacturer.name

        # Hantera tillverkarbilder
        delete_images = request.POST.get("delete_images", "false").lower() == "true"
        if image_count > 0:
            if delete_images:
                # Ta bort bilderna permanent
                for image in manufacturer.images.all():
                    image.delete()
                images_moved = 0
            else:
                # Flytta bilderna till okopplade bilder
                move_manufacturer_images_to_unlinked(manufacturer)
                images_moved = image_count

        # Ta bort tillverkaren
        manufacturer_name = manufacturer.name
        manufacturer.delete()

        return JsonResponse(
            {
                "success": True,
                "message": f'Tillverkare "{manufacturer_name}" har tagits bort',
                "axes_moved": axe_count if axe_action != "delete" else 0,
                "axes_deleted": axe_count if axe_action == "delete" else 0,
                "images_moved": images_moved if "images_moved" in locals() else 0,
                "images_deleted": image_count if delete_images else 0,
                "target_manufacturer_name": target_manufacturer_name,
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_http_methods(["GET"])
def get_manufacturers_for_dropdown(request):
    """Hämta tillverkare för dropdown-menyn (exkluderar den som ska tas bort)"""
    exclude_id = request.GET.get("exclude_id")
    all_manufacturers = Manufacturer.objects.exclude(id=exclude_id)

    # Sortera hierarkiskt istället för alfabetiskt
    def _is_descendant(manufacturer, ancestor):
        """Kontrollera om manufacturer är en efterkommande till ancestor"""
        current = manufacturer
        while current.parent:
            if current.parent == ancestor:
                return True
            current = current.parent
        return False

    def sort_hierarchically(manufacturers):
        """Sorterar tillverkare hierarkiskt: huvudtillverkare först, sedan undertillverkare i korrekt ordning"""
        main_manufacturers = [m for m in manufacturers if m.hierarchy_level == 0]
        sorted_list = []

        for main in main_manufacturers:
            sorted_list.append(main)
            # Hitta alla undertillverkare för denna huvudtillverkare
            [
                m
                for m in manufacturers
                if m.hierarchy_level > 0 and _is_descendant(m, main)
            ]

            # Sortera undertillverkare hierarkiskt
            def sort_children_recursive(parent=None):
                """Sorterar barn rekursivt under en förälder"""
                children = [m for m in manufacturers if m.parent == parent]
                children.sort(key=lambda x: x.name)  # Sortera barn alfabetiskt
                result = []
                for child in children:
                    result.append(child)
                    # Lägg till alla barn till detta barn rekursivt
                    result.extend(sort_children_recursive(child))
                return result

            # Sortera alla undertillverkare rekursivt
            sorted_subs = sort_children_recursive(main)
            sorted_list.extend(sorted_subs)

        return sorted_list

    manufacturers = sort_hierarchically(all_manufacturers)

    return JsonResponse(
        {"manufacturers": [{"id": m.id, "name": m.name} for m in manufacturers]}
    )


@require_http_methods(["GET"])
def check_manufacturer_name(request):
    """Kontrollera om ett tillverkarnamn redan finns"""
    name = request.GET.get("name", "").strip()
    if not name:
        return JsonResponse({"exists": False, "manufacturer": None})

    existing_manufacturer = Manufacturer.objects.filter(name__iexact=name).first()
    if existing_manufacturer:
        return JsonResponse(
            {
                "exists": True,
                "manufacturer": {
                    "id": existing_manufacturer.id,
                    "name": existing_manufacturer.name,
                    "information": existing_manufacturer.information or "",
                    "axe_count": existing_manufacturer.axe_set.count(),
                },
            }
        )

    return JsonResponse({"exists": False, "manufacturer": None})


def move_manufacturer_images_to_unlinked(manufacturer):
    """Flyttar tillverkarbilder till unlinked_images-mappen med tillverkarnamn"""
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")

    # Skapa mapp för okopplade tillverkarbilder
    unlinked_folder = os.path.join(
        settings.MEDIA_ROOT, "unlinked_images", "manufacturers"
    )
    os.makedirs(unlinked_folder, exist_ok=True)

    moved_count = 0
    error_count = 0

    # Skapa ett säkert filnamn från tillverkarnamnet
    safe_manufacturer_name = "".join(
        c for c in manufacturer.name if c.isalnum() or c in (" ", "-", "_")
    ).rstrip()
    safe_manufacturer_name = safe_manufacturer_name.replace(" ", "_")

    # Sortera bilder efter typ och ordning
    sorted_images = manufacturer.images.order_by("image_type", "order")

    for index, manufacturer_image in enumerate(sorted_images):
        try:
            if manufacturer_image.image and manufacturer_image.image.name:
                # Bestäm filnamn (a, b, c, etc.)
                letter = chr(97 + index)  # 97 = 'a' i ASCII

                # Hämta filändelse från originalfilen
                original_ext = os.path.splitext(manufacturer_image.image.name)[1]
                new_filename = f"{safe_manufacturer_name}-{manufacturer.id}-{timestamp}-{letter}{original_ext}"
                new_path = os.path.join(unlinked_folder, new_filename)

                # Kopiera filen
                if os.path.exists(manufacturer_image.image.path):
                    shutil.copy2(manufacturer_image.image.path, new_path)

                    # Kopiera även .webp-filen om den finns
                    webp_path = (
                        os.path.splitext(manufacturer_image.image.path)[0] + ".webp"
                    )
                    if os.path.exists(webp_path):
                        webp_new_path = os.path.join(
                            unlinked_folder,
                            f"{safe_manufacturer_name}-{manufacturer.id}-{timestamp}-{letter}.webp",
                        )
                        shutil.copy2(webp_path, webp_new_path)

                    moved_count += 1

                # Ta bort originalbilden från databasen och filsystemet
                manufacturer_image.delete()

        except Exception:
            error_count += 1
            # Logga felet om så önskas
            pass

    return moved_count, error_count


@require_http_methods(["POST"])
def add_manufacturer_link(request):
    """Lägg till ny tillverkarlänk via AJAX"""
    try:
        data = json.loads(request.body)
        manufacturer_id = data.get("manufacturer_id")
        title = data.get("title", "").strip()
        url = data.get("url", "").strip()
        link_type = data.get("link_type", "OTHER")
        description = data.get("description", "").strip()
        is_active = data.get("is_active", True)

        # Validering
        if not manufacturer_id or not title or not url:
            return JsonResponse(
                {"success": False, "error": "Tillverkare, titel och URL krävs"},
                status=400,
            )

        if len(title) > 255:
            return JsonResponse(
                {"success": False, "error": "Titel får vara max 255 tecken"}, status=400
            )

        try:
            manufacturer = Manufacturer.objects.get(id=manufacturer_id)
        except Manufacturer.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Tillverkare hittades inte"}, status=404
            )

        # Bestäm nästa ordningsnummer för denna tillverkare och länktyp
        max_order = ManufacturerLink.objects.filter(
            manufacturer=manufacturer, link_type=link_type
        ).aggregate(max_order=Max("order"))["max_order"]
        next_order = (max_order or 0) + 1

        # Skapa ny länk
        link = ManufacturerLink.objects.create(
            manufacturer=manufacturer,
            title=title,
            url=url,
            link_type=link_type,
            description=description if description else None,
            is_active=is_active,
            order=next_order,
        )

        return JsonResponse(
            {"success": True, "message": "Länk tillagd", "link_id": link.id}
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Ogiltig JSON-data"}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["POST"])
def reorder_manufacturer_links(request):
    """Spara ny ordning för tillverkarlänkar"""
    try:
        data = json.loads(request.body)
        manufacturer_id = data.get("manufacturer_id")
        order_data = data.get("order_data", [])

        # Uppdatera ordningen för varje länk
        for item in order_data:
            link_id = item.get("link_id")
            new_order = item.get("order")

            try:
                link = ManufacturerLink.objects.get(
                    id=link_id, manufacturer_id=manufacturer_id
                )
                link.order = new_order
                link.save()
            except ManufacturerLink.DoesNotExist:
                continue

        return JsonResponse({"success": True, "message": "Länkordning uppdaterad"})
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Ogiltig JSON-data"}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
