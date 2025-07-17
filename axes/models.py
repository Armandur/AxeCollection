from django.db import models
from PIL import Image
import os
from django.conf import settings
from django.db.models import Sum, Max

# Create your models here.

class NextAxeID(models.Model):
    """Håller reda på nästa ID som ska användas för nya yxor"""
    next_id = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = "Nästa yx-ID"
        verbose_name_plural = "Nästa yx-ID"
    
    @classmethod
    def get_next_id(cls):
        """Hämta nästa ID och öka räknaren"""
        obj, created = cls.objects.get_or_create(id=1, defaults={'next_id': 1})
        next_id = obj.next_id
        obj.next_id += 1
        obj.save()
        return next_id
    
    @classmethod
    def reset_if_last_axe_deleted(cls, deleted_id):
        """Återställ nästa ID om den senaste yxan togs bort"""
        # Kontrollera om det finns några yxor med högre ID
        if not Axe.objects.filter(id__gt=deleted_id).exists():
            # Det var den senaste yxan, återställ nästa ID
            obj, created = cls.objects.get_or_create(id=1, defaults={'next_id': 1})
            obj.next_id = deleted_id
            obj.save()

    @classmethod
    def peek_next_id(cls):
        obj, created = cls.objects.get_or_create(id=1, defaults={'next_id': 1})
        return obj.next_id

class Manufacturer(models.Model):
    name = models.CharField(max_length=200)
    information = models.TextField(blank=True, null=True, verbose_name="Information")

    def __str__(self):
        return self.name

    @property
    def axes(self):
        return self.axe_set.all()

    @property
    def axe_count(self):
        return self.axes.count()

    @property
    def transactions(self):
        from axes.models import Transaction
        return Transaction.objects.filter(axe__manufacturer=self)

    @property
    def buy_count(self):
        return self.transactions.filter(type='KÖP').count()

    @property
    def sale_count(self):
        return self.transactions.filter(type='SÄLJ').count()

    @property
    def total_buy_value(self):
        return self.transactions.filter(type='KÖP').aggregate(total=Sum('price'))['total'] or 0

    @property
    def total_sale_value(self):
        return self.transactions.filter(type='SÄLJ').aggregate(total=Sum('price'))['total'] or 0

    @property
    def net_value(self):
        return self.total_sale_value - self.total_buy_value

    @property
    def average_profit_per_axe(self):
        return self.net_value / self.axe_count if self.axe_count > 0 else 0

class Axe(models.Model):
    STATUS_CHOICES = [
        ('KÖPT', 'Köpt'),
        ('MOTTAGEN', 'Mottagen/Ägd'),
    ]
    
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT) # Skyddar mot att radera tillverkare som har yxor kopplade
    model = models.CharField(max_length=200)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='KÖPT')

    def save(self, *args, **kwargs):
        # Om det är en ny yxa (ingen ID än), använd nästa ID
        if not self.pk:
            self.id = NextAxeID.get_next_id()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Spara ID:t innan radering för att kunna återställa nästa ID
        deleted_id = self.id
        result = super().delete(*args, **kwargs)
        # Återställ nästa ID om det var den senaste yxan
        NextAxeID.reset_if_last_axe_deleted(deleted_id)
        return result

    @property
    def display_id(self):
        """Returnerar ID:t (samma som visnings-ID)"""
        return self.id

    def __str__(self):
        return f"{self.manufacturer.name} - {self.model}"

    @property
    def transactions(self):
        return self.transaction_set.all()

    @property
    def total_buy_value(self):
        return self.transactions.filter(type='KÖP').aggregate(total=Sum('price'))['total'] or 0

    @property
    def total_buy_shipping(self):
        return self.transactions.filter(type='KÖP').aggregate(total=Sum('shipping_cost'))['total'] or 0

    @property
    def total_sale_value(self):
        return self.transactions.filter(type='SÄLJ').aggregate(total=Sum('price'))['total'] or 0

    @property
    def total_sale_shipping(self):
        return self.transactions.filter(type='SÄLJ').aggregate(total=Sum('shipping_cost'))['total'] or 0

    @property
    def net_value(self):
        return self.total_sale_value - self.total_buy_value

    @property
    def profit_loss(self):
        return (self.total_sale_value + self.total_sale_shipping) - (self.total_buy_value + self.total_buy_shipping)

    @property
    def measurement_count(self):
        """Returnerar antalet registrerade mått för yxan"""
        return self.measurements.count()

    @property
    def is_latest(self):
        """Kontrollerar om denna yxa är den senaste (högsta ID)"""
        return self.id == Axe.objects.aggregate(Max('id'))['id__max']

class AxeImage(models.Model):
    axe = models.ForeignKey(Axe, related_name='images', on_delete=models.CASCADE) # Raderas bilden om yxan raderas
    image = models.ImageField(upload_to='axe_images/') # Django hanterar filuppladdning
    description = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0) # Ordning för bilderna (a=1, b=2, c=3, etc.)
    
    class Meta:
        ordering = ['order']

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

    def delete(self, *args, **kwargs):
        # Ta bort både originalfilen och .webp-filen
        if self.image and self.image.name:
            # Ta bort originalfilen
            if os.path.exists(self.image.path):
                try:
                    os.remove(self.image.path)
                except Exception as e:
                    pass  # Kan logga fel om så önskas
            
            # Ta bort .webp-filen om den finns
            webp_path = os.path.splitext(self.image.path)[0] + '.webp'
            if os.path.exists(webp_path):
                try:
                    os.remove(webp_path)
                except Exception as e:
                    pass  # Kan logga fel om så önskas
        super().delete(*args, **kwargs)

class ManufacturerImage(models.Model):
    IMAGE_TYPES = [
        ('STAMP', 'Stämpel'),
        ('OTHER', 'Övrig bild'),
    ]
    
    manufacturer = models.ForeignKey(Manufacturer, related_name='images', on_delete=models.CASCADE) # Raderas bilden om tillverkaren raderas
    image = models.ImageField(upload_to='manufacturer_images/') # Django hanterar filuppladdning
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES, default='STAMP', help_text="Typ av bild")
    caption = models.CharField(max_length=255, blank=True, null=True) # Bildtext
    description = models.TextField(blank=True, null=True) # Mer detaljerad beskrivning
    order = models.PositiveIntegerField(default=0, help_text="Sorteringsordning inom samma typ")
    
    class Meta:
        ordering = ['image_type', 'order']
        verbose_name = "Tillverkarbild"
        verbose_name_plural = "Tillverkarbilder"

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
    order = models.PositiveIntegerField(default=0, help_text="Sorteringsordning inom samma typ")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['link_type', 'order']
    
    def __str__(self):
        return f"{self.manufacturer.name} - {self.title}"

class MeasurementType(models.Model):
    """Dynamisk måtttyp som kan konfigureras av administratörer"""
    name = models.CharField(max_length=100, unique=True, help_text="Namn på måtttypen, t.ex. 'Bladlängd'")
    unit = models.CharField(max_length=50, help_text="Standardenhet för måtttypen, t.ex. 'mm'")
    description = models.TextField(blank=True, null=True, help_text="Beskrivning av måtttypen")
    is_active = models.BooleanField(default=True, help_text="Om måtttypen ska vara tillgänglig")
    sort_order = models.IntegerField(default=0, help_text="Sorteringsordning i listor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.unit})"


class MeasurementTemplate(models.Model):
    """Mall för att snabbt lägga till flera mått på en gång"""
    name = models.CharField(max_length=100, unique=True, help_text="Namn på mallen, t.ex. 'Standard yxa'")
    description = models.TextField(blank=True, null=True, help_text="Beskrivning av mallen")
    is_active = models.BooleanField(default=True, help_text="Om mallen ska vara tillgänglig")
    sort_order = models.IntegerField(default=0, help_text="Sorteringsordning i listor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class MeasurementTemplateItem(models.Model):
    """Individuellt mått i en måttmall"""
    template = models.ForeignKey(MeasurementTemplate, on_delete=models.CASCADE, related_name='items')
    measurement_type = models.ForeignKey(MeasurementType, on_delete=models.CASCADE)
    sort_order = models.IntegerField(default=0, help_text="Sorteringsordning inom mallen")
    
    class Meta:
        ordering = ['sort_order']
        unique_together = ['template', 'measurement_type']

    def __str__(self):
        return f"{self.template.name} - {self.measurement_type.name}"


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

    @property
    def transactions(self):
        from axes.models import Transaction
        return Transaction.objects.filter(contact=self)

    @property
    def total_transactions(self):
        return self.transactions.count()

    @property
    def buy_count(self):
        return self.transactions.filter(type='KÖP').count()

    @property
    def sale_count(self):
        return self.transactions.filter(type='SÄLJ').count()

    @property
    def total_buy_value(self):
        return self.transactions.filter(type='KÖP').aggregate(total=Sum('price'))['total'] or 0

    @property
    def total_sale_value(self):
        return self.transactions.filter(type='SÄLJ').aggregate(total=Sum('price'))['total'] or 0

    @property
    def net_value(self):
        return self.total_sale_value - self.total_buy_value

    @property
    def latest_transaction_date(self):
        """Returnerar datum för senaste transaktionen"""
        latest_transaction = self.transactions.order_by('-transaction_date').first()
        return latest_transaction.transaction_date if latest_transaction else None

    @property
    def unique_axes_count(self):
        """Returnerar antalet unika yxor som kontakten är kopplad till"""
        return self.transactions.values('axe').distinct().count()

class Platform(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @property
    def color_class(self):
        """Generera en unik pastellfärg baserat på plattformens ID"""
        # Lista med färger som inte krockar med status/ekonomi (undvik grön/röd)
        platform_colors = [
            'bg-primary',           # Blå
            'bg-info',              # Ljusblå
            'bg-warning',           # Gul/Orange
            'bg-secondary',         # Grå
            'bg-dark',              # Mörkgrå
            'bg-light',             # Ljusgrå
            'bg-primary-subtle',    # Ljusare blå
            'bg-info-subtle',       # Ljusare ljusblå
            'bg-warning-subtle',    # Ljusare gul
            'bg-secondary-subtle',  # Ljusare grå
            'bg-dark-subtle',       # Ljusare mörkgrå
            'bg-light-subtle',      # Ännu ljusare grå
        ]
        
        # Använd modulo för att få en färg baserat på ID
        color_index = self.id % len(platform_colors)
        return platform_colors[color_index]

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('KÖP', 'Köp'),
        ('SÄLJ', 'Sälj'),
    ]
    axe = models.ForeignKey(Axe, on_delete=models.CASCADE, related_name='transactions')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, blank=True, null=True)
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, blank=True, null=True)
    transaction_date = models.DateField()
    type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.type} av {self.axe} på {self.transaction_date}"
