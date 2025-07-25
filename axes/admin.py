from django.contrib import admin
from .models import Manufacturer, Axe, AxeImage, ManufacturerImage, ManufacturerLink, Measurement, Contact, Platform, Transaction, NextAxeID, MeasurementType, MeasurementTemplate, MeasurementTemplateItem
from django.utils.safestring import mark_safe
from django import forms
from django.utils.translation import gettext_lazy as _
import os

class ManufacturerImageInline(admin.TabularInline):
    model = ManufacturerImage
    extra = 1
    fields = ('image', 'image_type', 'caption', 'description', 'order')
    ordering = ('image_type', 'order')

class ManufacturerLinkInline(admin.TabularInline):
    model = ManufacturerLink
    extra = 1
    fields = ('title', 'url', 'link_type', 'description', 'is_active')

class ManufacturerImageAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'image_type', 'caption', 'order')
    list_filter = ('image_type', 'manufacturer')
    search_fields = ('manufacturer__name', 'caption', 'description')
    ordering = ('manufacturer', 'image_type', 'order')

class ManufacturerLinkAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'title', 'link_type', 'is_active', 'order')
    list_filter = ('link_type', 'is_active', 'manufacturer')
    search_fields = ('manufacturer__name', 'title', 'url')
    ordering = ('manufacturer', 'order')

class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'manufacturer_type', 'information')
    list_filter = ('manufacturer_type', 'parent')
    search_fields = ('name', 'information')
    inlines = [ManufacturerImageInline, ManufacturerLinkInline]
    
    def get_queryset(self, request):
        # Visa huvudtillverkare först, sedan undertillverkare
        return super().get_queryset(request).select_related('parent').order_by('parent__name', 'name')
    
    def get_list_display(self, request):
        # Lägg till hierarki-visning
        list_display = list(super().get_list_display(request))
        if 'hierarchical_name' not in list_display:
            list_display.insert(0, 'hierarchical_name')
        return list_display
    
    def hierarchical_name(self, obj):
        if obj.parent:
            return f"└─ {obj.name}"
        return obj.name
    hierarchical_name.short_description = 'Namn'
    hierarchical_name.admin_order_field = 'name'

class AxeDeleteForm(forms.Form):
    delete_images = forms.BooleanField(
        label=_('Ta bort bildfiler från disken vid radering'),
        required=False,
        initial=True,
        help_text=_('Om ibockad tas både original- och webp-bilder bort permanent från filsystemet.')
    )

class AxeAdmin(admin.ModelAdmin):
    list_display = ('id', 'manufacturer', 'model', 'status', 'display_id')
    list_filter = ('manufacturer', 'status')
    search_fields = ('manufacturer__name', 'model', 'comment')
    readonly_fields = ('display_id',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('manufacturer')
    
    def delete_model(self, request, obj):
        # Hantera bockruta för att ta bort bilder
        delete_images = True
        if request.method == 'POST':
            delete_images = request.POST.get('delete_images', 'on') == 'on'
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
                webp_path = os.path.splitext(img.image.path)[0] + '.webp'
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
        if hasattr(response, 'context_data') and 'deleted_objects' in response.context_data:
            flat = self.get_flat_deleted_objects(response.context_data['deleted_objects'])
            response.context_data['deleted_objects_flat'] = flat
        return response

class MeasurementTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'is_active', 'sort_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'name')
    list_editable = ('is_active', 'sort_order')


class MeasurementTemplateItemInline(admin.TabularInline):
    model = MeasurementTemplateItem
    extra = 1
    ordering = ('sort_order',)


class MeasurementTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'sort_order', 'item_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'name')
    list_editable = ('is_active', 'sort_order')
    inlines = [MeasurementTemplateItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Antal mått'




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


