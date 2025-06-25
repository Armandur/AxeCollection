from django.contrib import admin
from .models import Manufacturer, Axe, AxeImage, ManufacturerImage, ManufacturerLink, Measurement, Contact, Platform, Transaction
from django.utils.safestring import mark_safe

class ManufacturerImageInline(admin.TabularInline):
    model = ManufacturerImage
    extra = 1
    fields = ('image', 'caption', 'description')

class ManufacturerLinkInline(admin.TabularInline):
    model = ManufacturerLink
    extra = 1
    fields = ('title', 'url', 'link_type', 'description', 'is_active')

class ManufacturerImageAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'caption', 'description')
    list_filter = ('manufacturer',)
    search_fields = ('manufacturer__name', 'caption', 'description')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 100px;" />')
        return "-"
    image_preview.short_description = 'Förhandsvisning'
    image_preview.allow_tags = True

class ManufacturerLinkAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'title', 'link_type', 'is_active', 'created_at')
    list_filter = ('manufacturer', 'link_type', 'is_active', 'created_at')
    search_fields = ('manufacturer__name', 'title', 'description', 'url')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)

class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment')
    search_fields = ('name', 'comment')
    inlines = [ManufacturerImageInline, ManufacturerLinkInline]

# "Registrera" dina modeller så de dyker upp i admin-gränssnittet
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Axe)
admin.site.register(AxeImage)
admin.site.register(ManufacturerImage, ManufacturerImageAdmin)
admin.site.register(ManufacturerLink, ManufacturerLinkAdmin)
admin.site.register(Measurement)
admin.site.register(Contact)
admin.site.register(Platform)
admin.site.register(Transaction)
