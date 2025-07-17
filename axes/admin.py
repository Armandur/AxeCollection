from django.contrib import admin
from .models import Manufacturer, Axe, AxeImage, ManufacturerImage, ManufacturerLink, Measurement, Contact, Platform, Transaction, NextAxeID, MeasurementType, MeasurementTemplate, MeasurementTemplateItem
from django.utils.safestring import mark_safe
from django import forms
from django.utils.translation import gettext_lazy as _
import os
import zipfile
import json
import subprocess
from django.conf import settings

from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

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
    list_display = ('name', 'information')
    search_fields = ('name', 'information')
    inlines = [ManufacturerImageInline, ManufacturerLinkInline]

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


class BackupAdminView(View):
    """Admin-vy för backup-hantering"""
    
    def get(self, request):
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        backups = []
        
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                file_path = os.path.join(backup_dir, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    backup_info = {
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'path': file_path,
                        'stats': self.get_backup_stats(file_path)
                    }
                    backups.append(backup_info)
        
        # Sortera efter senast modifierad
        backups.sort(key=lambda x: x['modified'], reverse=True)
        
        # Hämta output från session om det finns
        restore_output = request.session.pop('restore_output', None)
        backup_output = request.session.pop('backup_output', None)
        
        context = {
            'backups': backups,
            'backup_dir': backup_dir,
            'title': 'Backup-hantering',
            'restore_output': restore_output,
            'backup_output': backup_output,
        }
        
        return render(request, 'admin/backup_management.html', context)
    
    def get_backup_stats(self, backup_path):
        """Hämta statistik från backup-fil"""
        try:
            if backup_path.endswith('.zip'):
                # Läs statistik från komprimerad backup
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    if 'backup_stats.json' in zipf.namelist():
                        stats_content = zipf.read('backup_stats.json').decode('utf-8')
                        return json.loads(stats_content)
            elif backup_path.endswith('.sqlite3'):
                # För icke-komprimerade backuper, leta efter motsvarande stats-fil
                stats_path = backup_path.replace('.sqlite3', '_stats.json')
                if os.path.exists(stats_path):
                    with open(stats_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
        except Exception as e:
            # Returnera None om statistik inte kan läsas
            pass
        return None
    
    def post(self, request):
        action = request.POST.get('action')
        
        if action == 'create_backup':
            return self.create_backup(request)
        elif action == 'delete_backup':
            return self.delete_backup(request)
        elif action == 'restore_backup':
            return self.restore_backup(request)
        else:
            messages.error(request, 'Ogiltig åtgärd')
            return redirect('admin:backup_management')
    
    def create_backup(self, request):
        """Skapa ny backup"""
        try:
            include_media = request.POST.get('include_media') == 'on'
            compress = request.POST.get('compress') == 'on'
            
            cmd = ['python', 'manage.py', 'backup_database']
            if include_media:
                cmd.append('--include-media')
            if compress:
                cmd.append('--compress')
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=settings.BASE_DIR)
            
            if result.returncode == 0:
                messages.success(request, 'Backup skapad framgångsrikt!')
                # Lägg till output i session för visning
                request.session['backup_output'] = result.stdout
            else:
                messages.error(request, f'Fel vid backup: {result.stderr}')
                # Lägg till feloutput i session för visning
                request.session['backup_output'] = result.stderr
                
        except Exception as e:
            messages.error(request, f'Fel vid backup: {str(e)}')
            request.session['backup_output'] = str(e)
        
        return redirect('admin:backup_management')
    
    def delete_backup(self, request):
        """Ta bort backup"""
        filename = request.POST.get('filename')
        if filename:
            backup_path = os.path.join(settings.BASE_DIR, 'backups', filename)
            try:
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    messages.success(request, f'Backup {filename} raderad')
                else:
                    messages.error(request, 'Backup-filen finns inte')
            except Exception as e:
                messages.error(request, f'Fel vid radering: {str(e)}')
        
        return redirect('admin:backup_management')
    
    def restore_backup(self, request):
        """Återställ från backup"""
        filename = request.POST.get('filename')
        if not filename:
            messages.error(request, 'Ingen backup-fil vald')
            return redirect('admin:backup_management')
        
        backup_path = os.path.join(settings.BASE_DIR, 'backups', filename)
        if not os.path.exists(backup_path):
            messages.error(request, 'Backup-filen finns inte')
            return redirect('admin:backup_management')
        
        try:
            # Kör återställningskommandot
            cmd = ['python', 'manage.py', 'restore_backup', backup_path, '--confirm', '--include-media']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=settings.BASE_DIR)
            
            if result.returncode == 0:
                messages.success(request, f'Backup {filename} återställd framgångsrikt!')
                # Lägg till output i session för visning
                request.session['restore_output'] = result.stdout
            else:
                messages.error(request, f'Fel vid återställning: {result.stderr}')
                # Lägg till feloutput i session för visning
                request.session['restore_output'] = result.stderr
                
        except Exception as e:
            messages.error(request, f'Fel vid återställning: {str(e)}')
            request.session['restore_output'] = str(e)
        
        return redirect('admin:backup_management')

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

# Lägg till backup-vy till admin på korrekt sätt
from django.urls import re_path

def get_admin_urls(urls):
    def get_urls():
        my_urls = [
            path('backup/', admin.site.admin_view(BackupAdminView.as_view()), name='backup_management'),
        ]
        return my_urls + urls
    return get_urls

admin.site.get_urls = get_admin_urls(admin.site.get_urls())
