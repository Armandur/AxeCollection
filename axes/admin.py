from django.contrib import admin
from .models import (
    Manufacturer,
    Axe,
    Contact,
    Platform,
    Transaction,
    MeasurementType,
    MeasurementTemplate,
    MeasurementTemplateItem,
    Measurement,
    ManufacturerImage,
    ManufacturerLink,
    AxeImage,
    # Stämpelregister-modeller
    Stamp,
    StampTranscription,
    StampTag,
    StampImage,
    AxeStamp,
    StampVariant,
    StampUncertaintyGroup,
)
from django import forms
from django.utils.translation import gettext_lazy as _
import os


class ManufacturerImageInline(admin.TabularInline):
    model = ManufacturerImage
    extra = 1
    fields = ("image", "image_type", "caption", "description", "order")
    ordering = ("image_type", "order")


class ManufacturerLinkInline(admin.TabularInline):
    model = ManufacturerLink
    extra = 1
    fields = ("title", "url", "link_type", "description", "is_active")


class ManufacturerImageAdmin(admin.ModelAdmin):
    list_display = ("manufacturer", "image_type", "caption", "order")
    list_filter = ("image_type", "manufacturer")
    search_fields = ("manufacturer__name", "caption", "description")
    ordering = ("manufacturer", "image_type", "order")


class ManufacturerLinkAdmin(admin.ModelAdmin):
    list_display = ("manufacturer", "title", "link_type", "is_active", "order")
    list_filter = ("link_type", "is_active", "manufacturer")
    search_fields = ("manufacturer__name", "title", "url")
    ordering = ("manufacturer", "order")


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("hierarchical_name", "parent", "manufacturer_type", "country_code")
    list_filter = ("manufacturer_type", "parent", "country_code")
    search_fields = ("name", "information", "country_code")
    fields = ("name", "parent", "manufacturer_type", "country_code", "information")
    list_editable = ("country_code",)
    inlines = [ManufacturerImageInline, ManufacturerLinkInline]

    def get_queryset(self, request):
        # Visa huvudtillverkare först, sedan undertillverkare
        return (
            super()
            .get_queryset(request)
            .select_related("parent")
            .order_by("parent__name", "name")
        )

    def get_list_display(self, request):
        # Lägg till hierarki-visning
        list_display = list(super().get_list_display(request))
        if "hierarchical_name" not in list_display:
            list_display.insert(0, "hierarchical_name")
        return list_display

    def hierarchical_name(self, obj):
        # Lägg till flaggemoji om country_code finns
        flag_emoji = ""
        if obj.country_code:
            flag_emoji = f"{obj.country_code} "

        if obj.parent:
            return f"└─ {flag_emoji}{obj.name}"
        return f"{flag_emoji}{obj.name}"

    hierarchical_name.short_description = "Namn"
    hierarchical_name.admin_order_field = "name"


class AxeDeleteForm(forms.Form):
    delete_images = forms.BooleanField(
        label=_("Ta bort bildfiler från disken vid radering"),
        required=False,
        initial=True,
        help_text=_(
            "Om ibockad tas både original- och webp-bilder bort permanent från filsystemet."
        ),
    )


class AxeAdmin(admin.ModelAdmin):
    list_display = ("id", "manufacturer", "model", "status", "display_id")
    list_filter = ("manufacturer", "status")
    search_fields = ("manufacturer__name", "model", "comment")
    readonly_fields = ("display_id",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("manufacturer")

    def delete_model(self, request, obj):
        # Hantera bockruta för att ta bort bilder
        delete_images = True
        if request.method == "POST":
            delete_images = request.POST.get("delete_images", "on") == "on"
        # Radera transaktioner först
        obj.transactions.all().delete()
        # Radera mått
        obj.measurements.all().delete()
        # Radera bilder (AxeImage raderas automatiskt via CASCADE)
        if delete_images:
            for img in obj.images.all():
                # Ta bort originalbild
                if img.image and os.path.isfile(img.image.path):
                    try:
                        os.remove(img.image.path)
                    except Exception:
                        pass
                # Ta bort webp-bild
                webp_path = os.path.splitext(img.image.path)[0] + ".webp"
                if os.path.isfile(webp_path):
                    try:
                        os.remove(webp_path)
                    except Exception:
                        pass
        # Radera yxan själv
        super().delete_model(request, obj)

    def get_flat_deleted_objects(self, deleted_objects):
        flat = []
        for obj in deleted_objects:
            if isinstance(obj, (list, tuple)):
                for sub in obj:
                    flat.append(str(sub))
            else:
                flat.append(str(obj))
        return flat

    def delete_view(self, request, object_id, extra_context=None):
        response = super().delete_view(request, object_id, extra_context=extra_context)
        # Förhandsgranska deleted_objects och platta ut
        if (
            hasattr(response, "context_data")
            and "deleted_objects" in response.context_data
        ):
            flat = self.get_flat_deleted_objects(
                response.context_data["deleted_objects"]
            )
            response.context_data["deleted_objects_flat"] = flat
        return response


class MeasurementTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "is_active", "sort_order", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    ordering = ("sort_order", "name")
    list_editable = ("is_active", "sort_order")


class MeasurementTemplateItemInline(admin.TabularInline):
    model = MeasurementTemplateItem
    extra = 1
    ordering = ("sort_order",)


class MeasurementTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "is_active",
        "sort_order",
        "item_count",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    ordering = ("sort_order", "name")
    list_editable = ("is_active", "sort_order")
    inlines = [MeasurementTemplateItemInline]

    def item_count(self, obj):
        return obj.items.count()

    item_count.short_description = "Antal mått"


# Stämpelregister admin-klasser
class StampTranscriptionInline(admin.TabularInline):
    model = StampTranscription
    extra = 1
    fields = ("text", "quality", "created_by")
    ordering = ("-created_at",)


class StampImageInline(admin.TabularInline):
    model = StampImage
    extra = 1
    fields = ("image", "caption", "description", "quality", "order")
    ordering = ("order", "-uploaded_at",)


class StampTagInline(admin.TabularInline):
    model = StampTag
    extra = 1
    fields = ("name", "description", "color")


class StampAdmin(admin.ModelAdmin):
    list_display = ("name", "manufacturer", "stamp_type", "status", "year_range", "source_category")
    list_filter = ("stamp_type", "status", "source_category", "manufacturer")
    search_fields = ("name", "description", "manufacturer__name")
    ordering = ("name",)
    fieldsets = (
        ("Grundinformation", {
            "fields": ("name", "description", "manufacturer", "stamp_type", "status")
        }),
        ("Årtalsinformation", {
            "fields": ("year_from", "year_to", "year_uncertainty", "year_notes"),
            "classes": ("collapse",)
        }),
        ("Källinformation", {
            "fields": ("source_category", "source_reference"),
            "classes": ("collapse",)
        }),
    )
    inlines = [StampTranscriptionInline, StampImageInline]


class StampTranscriptionAdmin(admin.ModelAdmin):
    list_display = ("stamp", "text", "quality", "created_by", "created_at")
    list_filter = ("quality", "created_at", "stamp__manufacturer")
    search_fields = ("text", "stamp__name", "stamp__manufacturer__name")
    ordering = ("-created_at",)


class StampTagAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "color", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "description")
    ordering = ("name",)


class StampImageAdmin(admin.ModelAdmin):
    list_display = (
        'stamp', 'image_type', 'axe_image', 'caption', 
        'is_primary', 'has_coordinates', 'show_full_image', 'uploaded_at'
    )
    list_filter = (
        'image_type', 'uploaded_at', 'stamp__manufacturer', 
        'uncertainty_level', 'is_primary', 'show_full_image'
    )
    search_fields = (
        'stamp__name', 'stamp__manufacturer__name', 
        'caption', 'description', 'comment', 'external_source'
    )
    ordering = ('order', '-uploaded_at',)
    fieldsets = (
        ('Grundinformation', {
            'fields': ('stamp', 'image_type', 'image', 'caption', 'description')
        }),
        ('Yxbildmarkering', {
            'fields': ('axe_image', 'show_full_image'),
            'classes': ('collapse',),
            'description': 'Inställningar för markering av stämplar på yxbilder'
        }),
        ('Koordinater', {
            'fields': ('x_coordinate', 'y_coordinate', 'width', 'height'),
            'classes': ('collapse',),
            'description': 'Procentuella koordinater för stämpelområdet'
        }),
        ('Metadata', {
            'fields': ('position', 'comment', 'uncertainty_level', 'external_source')
        }),
        ('Inställningar', {
            'fields': ('is_primary', 'order')
        })
    )
    
    def has_coordinates(self, obj):
        """Kontrollera om bilden har koordinater"""
        return obj.has_coordinates
    has_coordinates.boolean = True
    has_coordinates.short_description = 'Har koordinater'
    
    def get_queryset(self, request):
        """Optimera queryset med select_related"""
        return super().get_queryset(request).select_related(
            'stamp', 'stamp__manufacturer', 'axe_image', 'axe_image__axe'
        )
    
    def save_model(self, request, obj, form, change):
        """Validera data innan sparande"""
        if obj.image_type == 'axe_mark' and not obj.axe_image:
            self.message_user(request, 'Varning: Axe_image måste anges för axe_mark-typer', level='WARNING')
        super().save_model(request, obj, form, change)


class AxeStampAdmin(admin.ModelAdmin):
    list_display = ("axe", "stamp", "uncertainty_level", "position", "created_at")
    list_filter = ("uncertainty_level", "created_at", "stamp__manufacturer")
    search_fields = ("axe__model", "stamp__name", "comment", "position")
    ordering = ("-created_at",)
    fieldsets = (
        ("Koppling", {
            "fields": ("axe", "stamp")
        }),
        ("Detaljer", {
            "fields": ("comment", "position", "uncertainty_level")
        }),
    )


class StampVariantAdmin(admin.ModelAdmin):
    list_display = ("main_stamp", "variant_stamp", "description", "created_at")
    list_filter = ("created_at", "main_stamp__manufacturer")
    search_fields = ("main_stamp__name", "variant_stamp__name", "description")
    ordering = ("-created_at",)


class StampUncertaintyGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "confidence_level", "stamp_count", "created_at")
    list_filter = ("confidence_level", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)

    def stamp_count(self, obj):
        return obj.stamps.count()
    
    stamp_count.short_description = "Antal stämplar"


# Registrera admin-klasserna
admin.site.register(Stamp, StampAdmin)
admin.site.register(StampTranscription, StampTranscriptionAdmin)
admin.site.register(StampTag, StampTagAdmin)
admin.site.register(StampImage, StampImageAdmin)
admin.site.register(AxeStamp, AxeStampAdmin)
admin.site.register(StampVariant, StampVariantAdmin)
admin.site.register(StampUncertaintyGroup, StampUncertaintyGroupAdmin)


# "Registrera" dina modeller så de dyker upp i admin-gränssnittet
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Axe, AxeAdmin)
admin.site.register(AxeImage)
admin.site.register(ManufacturerImage, ManufacturerImageAdmin)
admin.site.register(ManufacturerLink, ManufacturerLinkAdmin)
admin.site.register(Measurement)
admin.site.register(Contact)
admin.site.register(Platform)
admin.site.register(Transaction)
admin.site.register(MeasurementType, MeasurementTypeAdmin)
admin.site.register(MeasurementTemplate, MeasurementTemplateAdmin)
