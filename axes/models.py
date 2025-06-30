from django.db import models
from PIL import Image
import os
from django.conf import settings

# Create your models here.

class Manufacturer(models.Model):
    name = models.CharField(max_length=200)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Axe(models.Model):
    STATUS_CHOICES = [
        ('KÖPT', 'Köpt'),
        ('MOTTAGEN', 'Mottagen/Ägd'),
    ]
    
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT) # Skyddar mot att radera tillverkare som har yxor kopplade
    model = models.CharField(max_length=200)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='KÖPT')

    def __str__(self):
        return f"{self.manufacturer.name} - {self.model}"

class AxeImage(models.Model):
    axe = models.ForeignKey(Axe, related_name='images', on_delete=models.CASCADE) # Raderas bilden om yxan raderas
    image = models.ImageField(upload_to='axe_images/') # Django hanterar filuppladdning
    description = models.CharField(max_length=255, blank=True, null=True)

    @property
    def webp_url(self):
        if self.image and self.image.name:
            webp_path = os.path.splitext(self.image.path)[0] + '.webp'
            if os.path.exists(webp_path):
                rel_path = os.path.relpath(webp_path, settings.MEDIA_ROOT)
                return settings.MEDIA_URL + rel_path.replace('\\', '/')
        return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and self.image.name:
            img_path = self.image.path
            webp_path = os.path.splitext(img_path)[0] + '.webp'
            try:
                img = Image.open(img_path)
                img.save(webp_path, 'WEBP', quality=85)
            except Exception as e:
                pass  # Kan logga fel om så önskas

class ManufacturerImage(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, related_name='images', on_delete=models.CASCADE) # Raderas bilden om tillverkaren raderas
    image = models.ImageField(upload_to='manufacturer_images/') # Django hanterar filuppladdning
    caption = models.CharField(max_length=255, blank=True, null=True) # Bildtext för stämplar
    description = models.TextField(blank=True, null=True) # Mer detaljerad beskrivning

    @property
    def webp_url(self):
        if self.image and self.image.name:
            webp_path = os.path.splitext(self.image.path)[0] + '.webp'
            if os.path.exists(webp_path):
                rel_path = os.path.relpath(webp_path, settings.MEDIA_ROOT)
                return settings.MEDIA_URL + rel_path.replace('\\', '/')
        return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and self.image.name:
            img_path = self.image.path
            webp_path = os.path.splitext(img_path)[0] + '.webp'
            try:
                img = Image.open(img_path)
                img.save(webp_path, 'WEBP', quality=85)
            except Exception as e:
                pass  # Kan logga fel om så önskas

    def __str__(self):
        return f"{self.manufacturer.name} - {self.caption or 'Bild'}"

    class Meta:
        verbose_name = "Tillverkarbild"
        verbose_name_plural = "Tillverkarbilder"

class ManufacturerLink(models.Model):
    LINK_TYPES = [
        ('WEBSITE', 'Hemsida'),
        ('CATALOG', 'Katalog'),
        ('VIDEO', 'Video/Film'),
        ('ARTICLE', 'Artikel'),
        ('DOCUMENT', 'Dokument'),
        ('OTHER', 'Övrigt'),
    ]
    
    manufacturer = models.ForeignKey(Manufacturer, related_name='links', on_delete=models.CASCADE)
    title = models.CharField(max_length=255) # Titel på länken
    url = models.URLField() # Länken
    link_type = models.CharField(max_length=20, choices=LINK_TYPES, default='OTHER')
    description = models.TextField(blank=True, null=True) # Beskrivning av innehållet
    is_active = models.BooleanField(default=True) # Om länken fortfarande fungerar
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['link_type', 'title']
    
    def __str__(self):
        return f"{self.manufacturer.name} - {self.title}"

class Measurement(models.Model):
    axe = models.ForeignKey(Axe, related_name='measurements', on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # t.ex. "Vikt"
    value = models.DecimalField(max_digits=10, decimal_places=2) # t.ex. 1800.00
    unit = models.CharField(max_length=50) # t.ex. "gram"

    def __str__(self):
        return f"{self.axe}: {self.name} är {self.value} {self.unit}"

class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    alias = models.CharField(max_length=100, blank=True, null=True)  # Gemensamt alias
    street = models.CharField(max_length=200, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    is_naj_member = models.BooleanField("Medlem i Nordic Axe Junkies", default=False)

    def __str__(self):
        return self.name

class Platform(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('KÖP', 'Köp'),
        ('SÄLJ', 'Sälj'),
    ]
    axe = models.ForeignKey(Axe, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, blank=True, null=True)
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, blank=True, null=True)
    transaction_date = models.DateField()
    type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.type} av {self.axe} på {self.transaction_date}"
