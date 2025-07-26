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
    MANUFACTURER_TYPE_CHOICES = [
        ('TILLVERKARE', 'Tillverkare'),
        ('SMED', 'Smed'),
    ]
    
    name = models.CharField(max_length=200)
    information = models.TextField(blank=True, null=True, verbose_name="Information")
    manufacturer_type = models.CharField(
        max_length=15,
        choices=MANUFACTURER_TYPE_CHOICES,
        default='TILLVERKARE',
        verbose_name="Typ av tillverkare",
        help_text="Är detta en fabrik, smedja, bruk eller annan tillverkare - eller en enskild smed?"
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='sub_manufacturers',
        verbose_name="Överordnad tillverkare",
        help_text="Välj en överordnad tillverkare om detta är en undertillverkare/smed"
    )

    def __str__(self):
        return self.name

    @property
    def is_sub_manufacturer(self):
        """Returnerar True om detta är en undertillverkare"""
        return self.parent is not None

    @property
    def is_main_manufacturer(self):
        """Returnerar True om detta är en huvudtillverkare (ingen parent)"""
        return self.parent is None

    @property
    def hierarchy_level(self):
        """Returnerar hierarkinivån för tillverkaren (0 för huvudtillverkare, 1+ för undertillverkare)"""
        level = 0
        current = self
        while current.parent:
            level += 1
            current = current.parent
        return level

    @property
    def full_name(self):
        """Returnerar fullständigt namn med hierarki"""
        if self.parent:
            return f"{self.parent.name} - {self.name}"
        return self.name

    @property
    def all_sub_manufacturers(self):
        """Returnerar alla undertillverkare (rekursivt)"""
        sub_manufacturers = list(self.sub_manufacturers.all())
        for sub in self.sub_manufacturers.all():
            sub_manufacturers.extend(sub.all_sub_manufacturers)
        return sub_manufacturers

    @property
    def all_axes_including_sub_manufacturers(self):
        """Returnerar alla yxor från denna tillverkare och alla undertillverkare"""
        axes = list(self.axe_set.all())
        for sub_manufacturer in self.all_sub_manufacturers:
            axes.extend(sub_manufacturer.axe_set.all())
        return axes

    @property
    def axes(self):
        return self.axe_set.all()

    class Meta:
        ordering = ['name']
        verbose_name = "Tillverkare"
        verbose_name_plural = "Tillverkare"

    @property
    def axe_count(self):
        return self.axes.count()

    @property
    def axe_count_including_sub_manufacturers(self):
        """Antal yxor inklusive undertillverkare"""
        return len(self.all_axes_including_sub_manufacturers)

    @property
    def transactions(self):
        from axes.models import Transaction
        return Transaction.objects.filter(axe__manufacturer=self)

    @property
    def transactions_including_sub_manufacturers(self):
        """Transaktioner inklusive undertillverkare"""
        from axes.models import Transaction
        all_axes = self.all_axes_including_sub_manufacturers
        axe_ids = [axe.id for axe in all_axes]
        return Transaction.objects.filter(axe_id__in=axe_ids)

    @property
    def buy_count(self):
        return self.transactions.filter(type='KÖP').count()

    @property
    def buy_count_including_sub_manufacturers(self):
        """Antal köp inklusive undertillverkare"""
        return self.transactions_including_sub_manufacturers.filter(type='KÖP').count()

    @property
    def sale_count(self):
        return self.transactions.filter(type='SÄLJ').count()

    @property
    def sale_count_including_sub_manufacturers(self):
        """Antal försäljningar inklusive undertillverkare"""
        return self.transactions_including_sub_manufacturers.filter(type='SÄLJ').count()

    @property
    def total_buy_value(self):
        return self.transactions.filter(type='KÖP').aggregate(total=Sum('price'))['total'] or 0

    @property
    def total_buy_value_including_sub_manufacturers(self):
        """Total köpvärde inklusive undertillverkare"""
        return self.transactions_including_sub_manufacturers.filter(type='KÖP').aggregate(total=Sum('price'))['total'] or 0

    @property
    def total_sale_value(self):
        return self.transactions.filter(type='SÄLJ').aggregate(total=Sum('price'))['total'] or 0

    @property
    def total_sale_value_including_sub_manufacturers(self):
        """Total försäljningsvärde inklusive undertillverkare"""
        return self.transactions_including_sub_manufacturers.filter(type='SÄLJ').aggregate(total=Sum('price'))['total'] or 0

    @property
    def net_value(self):
        return self.total_sale_value - self.total_buy_value

    @property
    def net_value_including_sub_manufacturers(self):
        """Netto-värde inklusive undertillverkare"""
        return self.total_sale_value_including_sub_manufacturers - self.total_buy_value_including_sub_manufacturers

    @property
    def average_profit_per_axe(self):
        return self.net_value / self.axe_count if self.axe_count > 0 else 0

    @property
    def average_profit_per_axe_including_sub_manufacturers(self):
        """Genomsnittlig vinst per yxa inklusive undertillverkare"""
        total_axes = self.axe_count_including_sub_manufacturers
        return self.net_value_including_sub_manufacturers / total_axes if total_axes > 0 else 0

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
    cache_busting_timestamp = models.DateTimeField(auto_now=True) # För att nollställa cachning när bildordning ändras
    
    class Meta:
        ordering = ['order']

    @property
    def webp_url(self):
        if self.image and self.image.name:
            webp_path = os.path.splitext(self.image.path)[0] + '.webp'
            if os.path.exists(webp_path):
                rel_path = os.path.relpath(webp_path, settings.MEDIA_ROOT)
                base_url = settings.MEDIA_URL + rel_path.replace('\\', '/')
                # Lägg till cache-busting parameter
                timestamp = int(self.cache_busting_timestamp.timestamp())
                return f"{base_url}?v={timestamp}"
        return None

    @property
    def image_url_with_cache_busting(self):
        """Returnerar bildens URL med cache-busting parameter"""
        if self.image and self.image.name:
            base_url = self.image.url
            timestamp = int(self.cache_busting_timestamp.timestamp())
            return f"{base_url}?v={timestamp}"
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
    cache_busting_timestamp = models.DateTimeField(auto_now=True) # För att nollställa cachning när bildordning ändras
    
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
                base_url = settings.MEDIA_URL + rel_path.replace('\\', '/')
                # Lägg till cache-busting parameter
                timestamp = int(self.cache_busting_timestamp.timestamp())
                return f"{base_url}?v={timestamp}"
        return None

    @property
    def image_url_with_cache_busting(self):
        """Returnerar bildens URL med cache-busting parameter"""
        if self.image and self.image.name:
            base_url = self.image.url
            timestamp = int(self.cache_busting_timestamp.timestamp())
            return f"{base_url}?v={timestamp}"
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
    country_code = models.CharField(max_length=2, blank=True, null=True, help_text="ISO 3166-1 alpha-2 landskod, t.ex. 'SE' för Sverige")
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
    COLOR_CHOICES = [
        # Bootstrap 5.2 standardfärger
        ('bg-primary', 'Blå (Primary)'),
        ('bg-secondary', 'Grå (Secondary)'),
        ('bg-success', 'Grön (Success)'),
        ('bg-danger', 'Röd (Danger)'),
        ('bg-warning', 'Gul/Orange (Warning)'),
        ('bg-info', 'Cyan (Info)'),
        ('bg-light', 'Ljusgrå (Light)'),
        ('bg-dark', 'Mörkgrå (Dark)'),
        
        # Ljusare versioner (subtle)
        ('bg-primary-subtle', 'Ljusare blå'),
        ('bg-secondary-subtle', 'Ljusare grå'),
        ('bg-success-subtle', 'Ljusare grön'),
        ('bg-danger-subtle', 'Ljusare röd'),
        ('bg-warning-subtle', 'Ljusare gul'),
        ('bg-info-subtle', 'Ljusare cyan'),
        ('bg-light-subtle', 'Ännu ljusare grå'),
        ('bg-dark-subtle', 'Ljusare mörkgrå'),
        
        # Text-färger som bakgrund (för variation)
        ('bg-body', 'Bakgrundsfärg'),
        ('bg-muted', 'Dämpad'),
        ('bg-white', 'Vit'),
        ('bg-black', 'Svart'),
        
        # Kombinationer och variationer
        ('bg-primary bg-opacity-75', 'Blå 75% opacity'),
        ('bg-secondary bg-opacity-75', 'Grå 75% opacity'),
        ('bg-success bg-opacity-75', 'Grön 75% opacity'),
        ('bg-danger bg-opacity-75', 'Röd 75% opacity'),
        ('bg-warning bg-opacity-75', 'Gul 75% opacity'),
        ('bg-info bg-opacity-75', 'Cyan 75% opacity'),
        ('bg-light bg-opacity-75', 'Ljusgrå 75% opacity'),
        ('bg-dark bg-opacity-75', 'Mörkgrå 75% opacity'),
        
        # Med text-färger för kontrast
        ('bg-primary text-white', 'Blå med vit text'),
        ('bg-secondary text-white', 'Grå med vit text'),
        ('bg-success text-white', 'Grön med vit text'),
        ('bg-danger text-white', 'Röd med vit text'),
        ('bg-warning text-dark', 'Gul med mörk text'),
        ('bg-info text-dark', 'Cyan med mörk text'),
        ('bg-light text-dark', 'Ljusgrå med mörk text'),
        ('bg-dark text-white', 'Mörkgrå med vit text'),
    ]
    
    name = models.CharField(max_length=100)
    color_class = models.CharField(
        max_length=30,
        choices=COLOR_CHOICES,
        default='bg-primary',
        verbose_name="Färg för badge",
        help_text="Välj färg för plattformens badge"
    )

    def __str__(self):
        return self.name

    def get_color_class(self):
        """Returnera den valda färgen eller fallback till automatisk färg"""
        if self.color_class:
            return self.color_class

        # Fallback till automatisk färg om ingen valts
        platform_colors = [
            # Bootstrap 5.2 standardfärger
            'bg-primary',           # Blå
            'bg-secondary',         # Grå
            'bg-success',           # Grön
            'bg-danger',            # Röd
            'bg-warning',           # Gul/Orange
            'bg-info',              # Cyan
            'bg-light',             # Ljusgrå
            'bg-dark',              # Mörkgrå
            
            # Ljusare versioner (subtle)
            'bg-primary-subtle',    # Ljusare blå
            'bg-secondary-subtle',  # Ljusare grå
            'bg-success-subtle',    # Ljusare grön
            'bg-danger-subtle',     # Ljusare röd
            'bg-warning-subtle',    # Ljusare gul
            'bg-info-subtle',       # Ljusare cyan
            'bg-light-subtle',      # Ännu ljusare grå
            'bg-dark-subtle',       # Ljusare mörkgrå
            
            # Text-färger som bakgrund
            'bg-body',              # Bakgrundsfärg
            'bg-muted',             # Dämpad
            'bg-white',             # Vit
            'bg-black',             # Svart
        ]

        # Använd modulo för att få en färg baserat på ID
        color_index = self.id % len(platform_colors)
        return platform_colors[color_index]

    def get_total_buy_value(self):
        """Total köpvärde för plattformen"""
        from decimal import Decimal
        return sum(
            transaction.price 
            for transaction in self.transaction_set.filter(type='KÖP')
        ) or Decimal('0.00')

    def get_total_sale_value(self):
        """Total försäljningsvärde för plattformen"""
        from decimal import Decimal
        return sum(
            transaction.price 
            for transaction in self.transaction_set.filter(type='SÄLJ')
        ) or Decimal('0.00')

    def get_profit_loss(self):
        """Vinst/förlust för plattformen"""
        return self.get_total_sale_value() - self.get_total_buy_value()

    def get_transaction_count(self):
        """Antal transaktioner på plattformen"""
        return self.transaction_set.count()

    def get_buy_count(self):
        """Antal köp på plattformen"""
        return self.transaction_set.filter(type='KÖP').count()

    def get_sale_count(self):
        """Antal försäljningar på plattformen"""
        return self.transaction_set.filter(type='SÄLJ').count()

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

class Settings(models.Model):
    """Globala inställningar för systemet"""
    # Publika inställningar
    show_contacts_public = models.BooleanField(
        default=False, 
        verbose_name="Visa kontakter publikt",
        help_text="Om kontaktinformation ska visas för icke-inloggade användare"
    )
    show_prices_public = models.BooleanField(
        default=True, 
        verbose_name="Visa priser publikt",
        help_text="Om priser ska visas för icke-inloggade användare"
    )
    show_platforms_public = models.BooleanField(
        default=True, 
        verbose_name="Visa plattformar publikt",
        help_text="Om plattformar ska visas för icke-inloggade användare"
    )
    show_only_received_axes_public = models.BooleanField(
        default=False, 
        verbose_name="Visa endast mottagna yxor publikt",
        help_text="Om endast mottagna yxor ska visas i publika listor"
    )
    
    # Standardantal rader för publika användare
    default_axes_rows_public = models.CharField(
        max_length=10,
        choices=[
            ('10', '10 rader'),
            ('25', '25 rader'),
            ('50', '50 rader'),
            ('100', '100 rader'),
            ('-1', 'Alla rader'),
        ],
        default='20',
        verbose_name="Standardantal yxor (publik)",
        help_text="Antal yxor som visas per sida för icke-inloggade användare"
    )
    default_transactions_rows_public = models.CharField(
        max_length=10,
        choices=[
            ('10', '10 rader'),
            ('25', '25 rader'),
            ('50', '50 rader'),
            ('100', '100 rader'),
            ('-1', 'Alla rader'),
        ],
        default='15',
        verbose_name="Standardantal transaktioner (publik)",
        help_text="Antal transaktioner som visas per sida för icke-inloggade användare"
    )
    default_manufacturers_rows_public = models.CharField(
        max_length=10,
        choices=[
            ('10', '10 rader'),
            ('25', '25 rader'),
            ('50', '50 rader'),
            ('100', '100 rader'),
            ('-1', 'Alla rader'),
        ],
        default='25',
        verbose_name="Standardantal tillverkare (publik)",
        help_text="Antal tillverkare som visas per sida för icke-inloggade användare"
    )
    
    # Standardantal rader för inloggade användare
    default_axes_rows_private = models.CharField(
        max_length=10,
        choices=[
            ('10', '10 rader'),
            ('25', '25 rader'),
            ('50', '50 rader'),
            ('100', '100 rader'),
            ('-1', 'Alla rader'),
        ],
        default='50',
        verbose_name="Standardantal yxor (privat)",
        help_text="Antal yxor som visas per sida för inloggade användare"
    )
    default_transactions_rows_private = models.CharField(
        max_length=10,
        choices=[
            ('10', '10 rader'),
            ('25', '25 rader'),
            ('50', '50 rader'),
            ('100', '100 rader'),
            ('-1', 'Alla rader'),
        ],
        default='30',
        verbose_name="Standardantal transaktioner (privat)",
        help_text="Antal transaktioner som visas per sida för inloggade användare"
    )
    default_manufacturers_rows_private = models.CharField(
        max_length=10,
        choices=[
            ('10', '10 rader'),
            ('25', '25 rader'),
            ('50', '50 rader'),
            ('100', '100 rader'),
            ('-1', 'Alla rader'),
        ],
        default='50',
        verbose_name="Standardantal tillverkare (privat)",
        help_text="Antal tillverkare som visas per sida för inloggade användare"
    )
    
    # Systeminställningar
    site_title = models.CharField(
        max_length=100, 
        default="AxeCollection",
        verbose_name="Sajttitel",
        help_text="Titel som visas i webbläsaren och på sidor"
    )
    site_description = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Sajtbeskrivning",
        help_text="Beskrivning av sajten för sökmotorer"
    )
    
    # Extern host-konfiguration
    external_hosts = models.TextField(
        blank=True,
        null=True,
        verbose_name="Externa hosts",
        help_text="Komma-separerad lista av externa hosts (t.ex. demo.domain.com,192.168.1.100)"
    )
    external_csrf_origins = models.TextField(
        blank=True,
        null=True,
        verbose_name="CSRF-tillåtna origins",
        help_text="Komma-separerad lista av CSRF-tillåtna origins med protokoll (t.ex. https://demo.domain.com,http://192.168.1.100)"
    )
    
    class Meta:
        verbose_name = "Inställning"
        verbose_name_plural = "Inställningar"
    
    def __str__(self):
        return "Systeminställningar"
    
    @classmethod
    def get_settings(cls):
        """Hämta eller skapa inställningar"""
        obj, created = cls.objects.get_or_create(id=1)
        return obj
