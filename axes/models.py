from django.db import models
from PIL import Image
import os
from django.conf import settings
from django.db.models import Sum, Max
from django.core.exceptions import ValidationError

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
        obj, created = cls.objects.get_or_create(id=1, defaults={"next_id": 1})
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
            obj, created = cls.objects.get_or_create(id=1, defaults={"next_id": 1})
            obj.next_id = deleted_id
            obj.save()

    @classmethod
    def peek_next_id(cls):
        obj, created = cls.objects.get_or_create(id=1, defaults={"next_id": 1})
        return obj.next_id


class Manufacturer(models.Model):
    MANUFACTURER_TYPE_CHOICES = [
        ("TILLVERKARE", "Tillverkare"),
        ("SMED", "Smed"),
    ]

    name = models.CharField(max_length=200)
    information = models.TextField(blank=True, null=True, verbose_name="Information")
    manufacturer_type = models.CharField(
        max_length=15,
        choices=MANUFACTURER_TYPE_CHOICES,
        default="TILLVERKARE",
        verbose_name="Typ av tillverkare",
        help_text="Är detta en fabrik, smedja, bruk eller annan tillverkare - eller en enskild smed?",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sub_manufacturers",
        verbose_name="Överordnad tillverkare",
        help_text="Välj en överordnad tillverkare om detta är en undertillverkare/smed",
    )
    country_code = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="ISO 3166-1 alpha-2 landskod, t.ex. 'SE' för Sverige",
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
        ordering = ["name"]
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
        return self.transactions.filter(type="KÖP").count()

    @property
    def buy_count_including_sub_manufacturers(self):
        """Antal köp inklusive undertillverkare"""
        return self.transactions_including_sub_manufacturers.filter(type="KÖP").count()

    @property
    def sale_count(self):
        return self.transactions.filter(type="SÄLJ").count()

    @property
    def sale_count_including_sub_manufacturers(self):
        """Antal försäljningar inklusive undertillverkare"""
        return self.transactions_including_sub_manufacturers.filter(type="SÄLJ").count()

    @property
    def total_buy_value(self):
        from decimal import Decimal

        result = self.transactions.filter(type="KÖP").aggregate(total=Sum("price"))[
            "total"
        ]
        return result if result is not None else Decimal("0")

    @property
    def total_buy_value_including_sub_manufacturers(self):
        """Total köpvärde inklusive undertillverkare"""
        from decimal import Decimal

        result = self.transactions_including_sub_manufacturers.filter(
            type="KÖP"
        ).aggregate(total=Sum("price"))["total"]
        return result if result is not None else Decimal("0")

    @property
    def total_sale_value(self):
        from decimal import Decimal

        result = self.transactions.filter(type="SÄLJ").aggregate(total=Sum("price"))[
            "total"
        ]
        return result if result is not None else Decimal("0")

    @property
    def total_sale_value_including_sub_manufacturers(self):
        """Total försäljningsvärde inklusive undertillverkare"""
        from decimal import Decimal

        result = self.transactions_including_sub_manufacturers.filter(
            type="SÄLJ"
        ).aggregate(total=Sum("price"))["total"]
        return result if result is not None else Decimal("0")

    @property
    def net_value(self):
        return self.total_sale_value - self.total_buy_value

    @property
    def net_value_including_sub_manufacturers(self):
        """Netto-värde inklusive undertillverkare"""
        return (
            self.total_sale_value_including_sub_manufacturers
            - self.total_buy_value_including_sub_manufacturers
        )

    @property
    def average_profit_per_axe(self):
        return self.net_value / self.axe_count if self.axe_count > 0 else 0

    @property
    def average_profit_per_axe_including_sub_manufacturers(self):
        """Genomsnittlig vinst per yxa inklusive undertillverkare"""
        total_axes = self.axe_count_including_sub_manufacturers
        return (
            self.net_value_including_sub_manufacturers / total_axes
            if total_axes > 0
            else 0
        )


class Axe(models.Model):
    STATUS_CHOICES = [
        ("KÖPT", "Köpt"),
        ("MOTTAGEN", "Mottagen/Ägd"),
    ]

    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.PROTECT
    )  # Skyddar mot att radera tillverkare som har yxor kopplade
    model = models.CharField(max_length=200)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="KÖPT")

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
        from decimal import Decimal

        result = self.transactions.filter(type="KÖP").aggregate(total=Sum("price"))[
            "total"
        ]
        return result if result is not None else Decimal("0")

    @property
    def total_buy_shipping(self):
        from decimal import Decimal

        result = self.transactions.filter(type="KÖP").aggregate(
            total=Sum("shipping_cost")
        )["total"]
        return result if result is not None else Decimal("0")

    @property
    def total_sale_value(self):
        from decimal import Decimal

        result = self.transactions.filter(type="SÄLJ").aggregate(total=Sum("price"))[
            "total"
        ]
        return result if result is not None else Decimal("0")

    @property
    def total_sale_shipping(self):
        from decimal import Decimal

        result = self.transactions.filter(type="SÄLJ").aggregate(
            total=Sum("shipping_cost")
        )["total"]
        return result if result is not None else Decimal("0")

    @property
    def net_value(self):
        return self.total_sale_value - self.total_buy_value

    @property
    def profit_loss(self):
        return (self.total_sale_value + self.total_sale_shipping) - (
            self.total_buy_value + self.total_buy_shipping
        )

    @property
    def measurement_count(self):
        """Returnerar antalet registrerade mått för yxan"""
        return self.measurements.count()

    @property
    def is_latest(self):
        """Kontrollerar om denna yxa är den senaste (högsta ID)"""
        return self.id == Axe.objects.aggregate(Max("id"))["id__max"]


class AxeImage(models.Model):
    axe = models.ForeignKey(
        Axe, related_name="images", on_delete=models.CASCADE
    )  # Raderas bilden om yxan raderas
    image = models.ImageField(upload_to="axe_images/")  # Django hanterar filuppladdning
    description = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(
        default=0
    )  # Ordning för bilderna (a=1, b=2, c=3, etc.)
    cache_busting_timestamp = models.DateTimeField(
        auto_now=True
    )  # För att nollställa cachning när bildordning ändras

    class Meta:
        ordering = ["order"]

    @property
    def webp_url(self):
        if self.image and self.image.name:
            webp_path = os.path.splitext(self.image.path)[0] + ".webp"
            if os.path.exists(webp_path):
                rel_path = os.path.relpath(webp_path, settings.MEDIA_ROOT)
                base_url = settings.MEDIA_URL + rel_path.replace("\\", "/")
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
            webp_path = os.path.splitext(img_path)[0] + ".webp"
            try:
                img = Image.open(img_path)
                img.save(webp_path, "WEBP", quality=85)
            except Exception:
                pass  # Kan logga fel om så önskas

    def delete(self, *args, **kwargs):
        # Ta bort både originalfilen och .webp-filen
        if self.image and self.image.name:
            # Ta bort originalfilen
            if os.path.exists(self.image.path):
                try:
                    os.remove(self.image.path)
                except Exception:
                    pass  # Kan logga fel om så önskas

            # Ta bort .webp-filen om den finns
            webp_path = os.path.splitext(self.image.path)[0] + ".webp"
            if os.path.exists(webp_path):
                try:
                    os.remove(webp_path)
                except Exception:
                    pass  # Kan logga fel om så önskas
        super().delete(*args, **kwargs)


class ManufacturerImage(models.Model):
    IMAGE_TYPES = [
        ("STAMP", "Stämpel"),
        ("OTHER", "Övrig bild"),
    ]

    manufacturer = models.ForeignKey(
        Manufacturer, related_name="images", on_delete=models.CASCADE
    )  # Raderas bilden om tillverkaren raderas
    image = models.ImageField(
        upload_to="manufacturer_images/"
    )  # Django hanterar filuppladdning
    image_type = models.CharField(
        max_length=20, choices=IMAGE_TYPES, default="STAMP", help_text="Typ av bild"
    )
    caption = models.CharField(max_length=255, blank=True, null=True)  # Bildtext
    description = models.TextField(blank=True, null=True)  # Mer detaljerad beskrivning
    order = models.PositiveIntegerField(
        default=0, help_text="Sorteringsordning inom samma typ"
    )
    cache_busting_timestamp = models.DateTimeField(
        auto_now=True
    )  # För att nollställa cachning när bildordning ändras

    class Meta:
        ordering = ["image_type", "order"]
        verbose_name = "Tillverkarbild"
        verbose_name_plural = "Tillverkarbilder"

    @property
    def webp_url(self):
        if self.image and self.image.name:
            webp_path = os.path.splitext(self.image.path)[0] + ".webp"
            if os.path.exists(webp_path):
                rel_path = os.path.relpath(webp_path, settings.MEDIA_ROOT)
                base_url = settings.MEDIA_URL + rel_path.replace("\\", "/")
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
            webp_path = os.path.splitext(img_path)[0] + ".webp"
            try:
                img = Image.open(img_path)
                img.save(webp_path, "WEBP", quality=85)
            except Exception:
                pass  # Kan logga fel om så önskas

    def __str__(self):
        return f"{self.manufacturer.name} - {self.caption or 'Bild'}"


class ManufacturerLink(models.Model):
    LINK_TYPES = [
        ("WEBSITE", "Hemsida"),
        ("CATALOG", "Katalog"),
        ("VIDEO", "Video/Film"),
        ("ARTICLE", "Artikel"),
        ("DOCUMENT", "Dokument"),
        ("OTHER", "Övrigt"),
    ]

    manufacturer = models.ForeignKey(
        Manufacturer, related_name="links", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)  # Titel på länken
    url = models.URLField()  # Länken
    link_type = models.CharField(max_length=20, choices=LINK_TYPES, default="OTHER")
    description = models.TextField(blank=True, null=True)  # Beskrivning av innehållet
    is_active = models.BooleanField(default=True)  # Om länken fortfarande fungerar
    order = models.PositiveIntegerField(
        default=0, help_text="Sorteringsordning inom samma typ"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["link_type", "order"]

    def __str__(self):
        return f"{self.manufacturer.name} - {self.title}"


class MeasurementType(models.Model):
    """Dynamisk måtttyp som kan konfigureras av administratörer"""

    name = models.CharField(
        max_length=100, unique=True, help_text="Namn på måtttypen, t.ex. 'Bladlängd'"
    )
    unit = models.CharField(
        max_length=50, help_text="Standardenhet för måtttypen, t.ex. 'mm'"
    )
    description = models.TextField(
        blank=True, null=True, help_text="Beskrivning av måtttypen"
    )
    is_active = models.BooleanField(
        default=True, help_text="Om måtttypen ska vara tillgänglig"
    )
    sort_order = models.IntegerField(default=0, help_text="Sorteringsordning i listor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.name} ({self.unit})"


class MeasurementTemplate(models.Model):
    """Mall för att snabbt lägga till flera mått på en gång"""

    name = models.CharField(
        max_length=100, unique=True, help_text="Namn på mallen, t.ex. 'Standard yxa'"
    )
    description = models.TextField(
        blank=True, null=True, help_text="Beskrivning av mallen"
    )
    is_active = models.BooleanField(
        default=True, help_text="Om mallen ska vara tillgänglig"
    )
    sort_order = models.IntegerField(default=0, help_text="Sorteringsordning i listor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class MeasurementTemplateItem(models.Model):
    """Individuellt mått i en måttmall"""

    template = models.ForeignKey(
        MeasurementTemplate, on_delete=models.CASCADE, related_name="items"
    )
    measurement_type = models.ForeignKey(MeasurementType, on_delete=models.CASCADE)
    sort_order = models.IntegerField(
        default=0, help_text="Sorteringsordning inom mallen"
    )

    class Meta:
        ordering = ["sort_order"]
        unique_together = ["template", "measurement_type"]

    def __str__(self):
        return f"{self.template.name} - {self.measurement_type.name}"


class Measurement(models.Model):
    axe = models.ForeignKey(Axe, related_name="measurements", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # t.ex. "Vikt"
    value = models.DecimalField(max_digits=10, decimal_places=2)  # t.ex. 1800.00
    unit = models.CharField(max_length=50)  # t.ex. "gram"

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
    country_code = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="ISO 3166-1 alpha-2 landskod, t.ex. 'SE' för Sverige",
    )
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
        return self.transactions.filter(type="KÖP").count()

    @property
    def sale_count(self):
        return self.transactions.filter(type="SÄLJ").count()

    @property
    def total_buy_value(self):
        from decimal import Decimal

        result = self.transactions.filter(type="KÖP").aggregate(total=Sum("price"))[
            "total"
        ]
        return result if result is not None else Decimal("0")

    @property
    def total_sale_value(self):
        from decimal import Decimal

        result = self.transactions.filter(type="SÄLJ").aggregate(total=Sum("price"))[
            "total"
        ]
        return result if result is not None else Decimal("0")

    @property
    def net_value(self):
        return self.total_sale_value - self.total_buy_value

    @property
    def latest_transaction_date(self):
        """Returnerar datum för senaste transaktionen"""
        latest_transaction = self.transactions.order_by("-transaction_date").first()
        return latest_transaction.transaction_date if latest_transaction else None

    @property
    def unique_axes_count(self):
        """Returnerar antalet unika yxor som kontakten är kopplad till"""
        return self.transactions.values("axe").distinct().count()


class Platform(models.Model):
    COLOR_CHOICES = [
        # Bootstrap 5.2 standardfärger
        ("bg-primary", "Blå (Primary)"),
        ("bg-secondary", "Grå (Secondary)"),
        ("bg-success", "Grön (Success)"),
        ("bg-danger", "Röd (Danger)"),
        ("bg-warning", "Gul/Orange (Warning)"),
        ("bg-info", "Cyan (Info)"),
        ("bg-light", "Ljusgrå (Light)"),
        ("bg-dark", "Mörkgrå (Dark)"),
        # Ljusare versioner (subtle)
        ("bg-primary-subtle", "Ljusare blå"),
        ("bg-secondary-subtle", "Ljusare grå"),
        ("bg-success-subtle", "Ljusare grön"),
        ("bg-danger-subtle", "Ljusare röd"),
        ("bg-warning-subtle", "Ljusare gul"),
        ("bg-info-subtle", "Ljusare cyan"),
        ("bg-light-subtle", "Ännu ljusare grå"),
        ("bg-dark-subtle", "Ljusare mörkgrå"),
        # Text-färger som bakgrund (för variation)
        ("bg-body", "Bakgrundsfärg"),
        ("bg-muted", "Dämpad"),
        ("bg-white", "Vit"),
        ("bg-black", "Svart"),
        # Kombinationer och variationer
        ("bg-primary bg-opacity-75", "Blå 75% opacity"),
        ("bg-secondary bg-opacity-75", "Grå 75% opacity"),
        ("bg-success bg-opacity-75", "Grön 75% opacity"),
        ("bg-danger bg-opacity-75", "Röd 75% opacity"),
        ("bg-warning bg-opacity-75", "Gul 75% opacity"),
        ("bg-info bg-opacity-75", "Cyan 75% opacity"),
        ("bg-light bg-opacity-75", "Ljusgrå 75% opacity"),
        ("bg-dark bg-opacity-75", "Mörkgrå 75% opacity"),
        # Med text-färger för kontrast
        ("bg-primary text-white", "Blå med vit text"),
        ("bg-secondary text-white", "Grå med vit text"),
        ("bg-success text-white", "Grön med vit text"),
        ("bg-danger text-white", "Röd med vit text"),
        ("bg-warning text-dark", "Gul med mörk text"),
        ("bg-info text-dark", "Cyan med mörk text"),
        ("bg-light text-dark", "Ljusgrå med mörk text"),
        ("bg-dark text-white", "Mörkgrå med vit text"),
    ]

    name = models.CharField(max_length=100)
    url = models.URLField(
        blank=True, null=True, verbose_name="URL", help_text="Hemsida för plattformen"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Kommentar",
        help_text="Beskrivning av plattformen",
    )
    color_class = models.CharField(
        max_length=30,
        choices=COLOR_CHOICES,
        default="bg-primary",
        verbose_name="Färg för badge",
        help_text="Välj färg för plattformens badge",
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
            "bg-primary",  # Blå
            "bg-secondary",  # Grå
            "bg-success",  # Grön
            "bg-danger",  # Röd
            "bg-warning",  # Gul/Orange
            "bg-info",  # Cyan
            "bg-light",  # Ljusgrå
            "bg-dark",  # Mörkgrå
            # Ljusare versioner (subtle)
            "bg-primary-subtle",  # Ljusare blå
            "bg-secondary-subtle",  # Ljusare grå
            "bg-success-subtle",  # Ljusare grön
            "bg-danger-subtle",  # Ljusare röd
            "bg-warning-subtle",  # Ljusare gul
            "bg-info-subtle",  # Ljusare cyan
            "bg-light-subtle",  # Ännu ljusare grå
            "bg-dark-subtle",  # Ljusare mörkgrå
            # Text-färger som bakgrund
            "bg-body",  # Bakgrundsfärg
            "bg-muted",  # Dämpad
            "bg-white",  # Vit
            "bg-black",  # Svart
        ]

        # Använd modulo för att få en färg baserat på ID
        color_index = self.id % len(platform_colors)
        return platform_colors[color_index]

    def get_total_buy_value(self):
        """Total köpvärde för plattformen"""
        from decimal import Decimal

        return sum(
            transaction.price for transaction in self.transaction_set.filter(type="KÖP")
        ) or Decimal("0.00")

    def get_total_sale_value(self):
        """Total försäljningsvärde för plattformen"""
        from decimal import Decimal

        return sum(
            transaction.price
            for transaction in self.transaction_set.filter(type="SÄLJ")
        ) or Decimal("0.00")

    def get_profit_loss(self):
        """Vinst/förlust för plattformen"""
        return self.get_total_sale_value() - self.get_total_buy_value()

    def get_transaction_count(self):
        """Antal transaktioner på plattformen"""
        return self.transaction_set.count()

    def get_buy_count(self):
        """Antal köp på plattformen"""
        return self.transaction_set.filter(type="KÖP").count()

    def get_sale_count(self):
        """Antal försäljningar på plattformen"""
        return self.transaction_set.filter(type="SÄLJ").count()


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("KÖP", "Köp"),
        ("SÄLJ", "Sälj"),
    ]
    axe = models.ForeignKey(Axe, on_delete=models.CASCADE, related_name="transactions")
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, blank=True, null=True
    )
    platform = models.ForeignKey(
        Platform, on_delete=models.SET_NULL, blank=True, null=True
    )
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
        help_text="Om kontaktinformation ska visas för icke-inloggade användare",
    )
    show_prices_public = models.BooleanField(
        default=True,
        verbose_name="Visa priser publikt",
        help_text="Om priser ska visas för icke-inloggade användare",
    )
    show_platforms_public = models.BooleanField(
        default=True,
        verbose_name="Visa plattformar publikt",
        help_text="Om plattformar ska visas för icke-inloggade användare",
    )
    show_only_received_axes_public = models.BooleanField(
        default=False,
        verbose_name="Visa endast mottagna yxor publikt",
        help_text="Om endast mottagna yxor ska visas i publika listor",
    )

    # Standardantal rader för publika användare
    default_axes_rows_public = models.CharField(
        max_length=10,
        choices=[
            ("10", "10 rader"),
            ("25", "25 rader"),
            ("50", "50 rader"),
            ("100", "100 rader"),
            ("-1", "Alla rader"),
        ],
        default="20",
        verbose_name="Standardantal yxor (publik)",
        help_text="Antal yxor som visas per sida för icke-inloggade användare",
    )
    default_transactions_rows_public = models.CharField(
        max_length=10,
        choices=[
            ("10", "10 rader"),
            ("25", "25 rader"),
            ("50", "50 rader"),
            ("100", "100 rader"),
            ("-1", "Alla rader"),
        ],
        default="15",
        verbose_name="Standardantal transaktioner (publik)",
        help_text="Antal transaktioner som visas per sida för icke-inloggade användare",
    )
    default_manufacturers_rows_public = models.CharField(
        max_length=10,
        choices=[
            ("10", "10 rader"),
            ("25", "25 rader"),
            ("50", "50 rader"),
            ("100", "100 rader"),
            ("-1", "Alla rader"),
        ],
        default="25",
        verbose_name="Standardantal tillverkare (publik)",
        help_text="Antal tillverkare som visas per sida för icke-inloggade användare",
    )

    # Standardantal rader för inloggade användare
    default_axes_rows_private = models.CharField(
        max_length=10,
        choices=[
            ("10", "10 rader"),
            ("25", "25 rader"),
            ("50", "50 rader"),
            ("100", "100 rader"),
            ("-1", "Alla rader"),
        ],
        default="50",
        verbose_name="Standardantal yxor (privat)",
        help_text="Antal yxor som visas per sida för inloggade användare",
    )
    default_transactions_rows_private = models.CharField(
        max_length=10,
        choices=[
            ("10", "10 rader"),
            ("25", "25 rader"),
            ("50", "50 rader"),
            ("100", "100 rader"),
            ("-1", "Alla rader"),
        ],
        default="30",
        verbose_name="Standardantal transaktioner (privat)",
        help_text="Antal transaktioner som visas per sida för inloggade användare",
    )
    default_manufacturers_rows_private = models.CharField(
        max_length=10,
        choices=[
            ("10", "10 rader"),
            ("25", "25 rader"),
            ("50", "50 rader"),
            ("100", "100 rader"),
            ("-1", "Alla rader"),
        ],
        default="50",
        verbose_name="Standardantal tillverkare (privat)",
        help_text="Antal tillverkare som visas per sida för inloggade användare",
    )

    # Systeminställningar
    site_title = models.CharField(
        max_length=100,
        default="AxeCollection",
        verbose_name="Sajttitel",
        help_text="Titel som visas i webbläsaren och på sidor",
    )
    site_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Sajtbeskrivning",
        help_text="Beskrivning av sajten för sökmotorer",
    )

    # Extern host-konfiguration
    external_hosts = models.TextField(
        blank=True,
        null=True,
        verbose_name="Externa hosts",
        help_text="Komma-separerad lista av externa hosts (t.ex. demo.domain.com,192.168.1.100)",
    )
    external_csrf_origins = models.TextField(
        blank=True,
        null=True,
        verbose_name="Externa CSRF origins",
        help_text="Komma-separerad lista av externa CSRF origins (t.ex. https://demo.domain.com,https://192.168.1.100)",
    )

    class Meta:
        verbose_name = "Inställning"
        verbose_name_plural = "Inställningar"

    def __str__(self):
        return f"Inställningar - {self.site_title}"

    @classmethod
    def get_settings(cls):
        """Hämta inställningar eller skapa standardinställningar"""
        settings, created = cls.objects.get_or_create(
            id=1,
            defaults={
                "site_title": "AxeCollection",
                "show_contacts_public": False,
                "show_prices_public": True,
                "show_platforms_public": True,
                "show_only_received_axes_public": False,
            },
        )
        return settings


# Stämpelregister-modeller
class Stamp(models.Model):
    """Stämpel - huvudmodell för stämplar"""

    STAMP_TYPE_CHOICES = [
        ("text", "Text"),
        ("symbol", "Symbol"),
        ("text_symbol", "Text + Symbol"),
        ("label", "Etikett"),
    ]

    STATUS_CHOICES = [
        ("known", "Känd"),
        ("unknown", "Okänd"),
    ]

    SOURCE_CATEGORY_CHOICES = [
        ("own_collection", "Egen samling"),
        ("ebay_auction", "eBay/Auktion"),
        ("museum", "Museum"),
        ("private_collector", "Privat samlare"),
        ("book_article", "Bok/Artikel"),
        ("internet", "Internet"),
        ("unknown", "Okänd"),
    ]

    name = models.CharField(max_length=200, verbose_name="Namn")
    description = models.TextField(blank=True, null=True, verbose_name="Beskrivning")
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tillverkare",
    )
    stamp_type = models.CharField(
        max_length=20, choices=STAMP_TYPE_CHOICES, default="text", verbose_name="Typ"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="unknown", verbose_name="Status"
    )

    # Årtalsinformation
    year_from = models.IntegerField(null=True, blank=True, verbose_name="Från år")
    year_to = models.IntegerField(null=True, blank=True, verbose_name="Till år")
    year_uncertainty = models.BooleanField(
        default=False, verbose_name="Osäker årtalsinformation"
    )
    year_notes = models.TextField(
        blank=True, null=True, verbose_name="Anteckningar om årtal"
    )

    # Källinformation
    source_category = models.CharField(
        max_length=20,
        choices=SOURCE_CATEGORY_CHOICES,
        default="own_collection",
        verbose_name="Källkategori",
    )
    source_reference = models.TextField(
        blank=True, null=True, verbose_name="Källhänvisning"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Stämpel"
        verbose_name_plural = "Stämplar"

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        """Visa namn med tillverkare om tillgängligt"""
        if self.manufacturer:
            return f"{self.name} ({self.manufacturer.name})"
        return self.name

    @property
    def year_range(self):
        """Formatera årtalsintervall"""
        if self.year_from and self.year_to:
            if self.year_from == self.year_to:
                return str(self.year_from)
            else:
                return f"{self.year_from}-{self.year_to}"
        elif self.year_from:
            return f"från {self.year_from}"
        elif self.year_to:
            return f"till {self.year_to}"
        return "Okänt årtal"

    @property
    def primary_image(self):
        """Hämta primär bild för stämpeln"""
        return self.images.filter(is_primary=True).first()

    @property
    def image_count(self):
        """Antal bilder kopplade till stämpeln"""
        return self.images.count()

    @property
    def axe_count(self):
        """Antal yxor med denna stämpel"""
        return self.axes.count()

    def clean(self):
        """Validera stämpeldata"""
        from django.core.exceptions import ValidationError

        # Validera årtal
        if self.year_from and self.year_to and self.year_from > self.year_to:
            raise ValidationError("Från-år kan inte vara senare än till-år")

        # Validera att kända stämplar har tillverkare
        if self.status == "known" and not self.manufacturer:
            raise ValidationError("Kända stämplar måste ha en tillverkare")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class StampTranscription(models.Model):
    """Textbaserad beskrivning av stämplar"""

    QUALITY_CHOICES = [
        ("high", "Hög"),
        ("medium", "Medium"),
        ("low", "Låg"),
    ]

    stamp = models.ForeignKey(
        Stamp,
        on_delete=models.CASCADE,
        related_name="transcriptions",
        verbose_name="Stämpel",
    )
    text = models.TextField(verbose_name="Text")
    quality = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        default="medium",
        verbose_name="Kvalitet",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Skapad av",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Koppling till symboler
    symbols = models.ManyToManyField(
        "StampSymbol",
        blank=True,
        verbose_name="Symboler",
        help_text="Symboler som förekommer i denna transkribering",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Stämpeltranskribering"
        verbose_name_plural = "Stämpeltranskriberingar"

    def __str__(self):
        return f"{self.stamp.name}: {self.text}"
    
    @property
    def symbols_display(self):
        """Returnerar en formaterad sträng av alla symboler (utan kategorier)"""
        if self.symbols.exists():
            return ", ".join([symbol.display_with_pictogram for symbol in self.symbols.all()])
        return ""
    
    @property
    def full_transcription(self):
        """Returnerar komplett transkribering med text och symboler (utan kategorier)"""
        parts = [self.text]
        if self.symbols.exists():
            # Samla bara pictogrammen, inte texten
            pictograms = []
            for symbol in self.symbols.all():
                if symbol.pictogram:
                    pictograms.append(symbol.pictogram)
                else:
                    # Om ingen pictogram finns, använd symbolnamnet
                    pictograms.append(symbol.name)
            if pictograms:
                parts.append(", ".join(pictograms))
        return ", ".join(parts)
    
    @property
    def full_transcription_for_cards(self):
        """Returnerar komplett transkribering för kortvisning med ↩️ som radbrytning"""
        # Rensa bort extra mellanslag runt radbrytningar
        cleaned_text = self.text.replace('\r\n', '\n').replace('\r', '\n')  # Normalisera radbrytningar
        cleaned_text = '\n'.join(line.strip() for line in cleaned_text.split('\n'))  # Rensa mellanslag
        cleaned_text = cleaned_text.replace('\n', '↩️')  # Ersätt med symbol
        parts = [cleaned_text]
        if self.symbols.exists():
            # Samla bara pictogrammen, inte texten
            pictograms = []
            for symbol in self.symbols.all():
                if symbol.pictogram:
                    pictograms.append(symbol.pictogram)
                else:
                    # Om ingen pictogram finns, använd symbolnamnet
                    pictograms.append(symbol.name)
            if pictograms:
                parts.append(", ".join(pictograms))
        return ", ".join(parts)


class StampTag(models.Model):
    """Kategorisering av stämplar"""

    name = models.CharField(max_length=100, verbose_name="Namn")
    description = models.TextField(blank=True, null=True, verbose_name="Beskrivning")
    color = models.CharField(
        max_length=7,
        default="#007bff",
        verbose_name="Färg (hex)",
        help_text="Hex-färg för taggen, t.ex. #007bff",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Stämpeltagg"
        verbose_name_plural = "Stämpeltaggar"

    def __str__(self):
        return self.name


class StampImage(models.Model):
    """Bilder av stämplar - konsoliderad modell för både fristående och yxbildmarkeringar"""

    IMAGE_TYPE_CHOICES = [
        ("standalone", "Fristående stämpelbild"),
        ("axe_mark", "Yxbildmarkering"),
        ("reference", "Referensbild"),
        ("documentation", "Dokumentationsbild"),
    ]

    UNCERTAINTY_CHOICES = [
        ("certain", "Säker"),
        ("uncertain", "Osäker"),
        ("tentative", "Preliminär"),
    ]

    stamp = models.ForeignKey(
        Stamp, on_delete=models.CASCADE, related_name="images", verbose_name="Stämpel"
    )

    # Bildtyp för att skilja mellan olika källor
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPE_CHOICES,
        default="standalone",
        verbose_name="Bildtyp",
    )

    # Koppling till yxbild (om det är en markering)
    axe_image = models.ForeignKey(
        AxeImage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stamp_markings",
        verbose_name="Yxbild",
        help_text="Koppling till yxbild om detta är en markering",
    )

    image = models.ImageField(upload_to="stamps/", verbose_name="Bild")
    caption = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Bildtext",
        help_text="Kort beskrivning av bilden",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Beskrivning",
        help_text="Detaljerad beskrivning av vad bilden visar",
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name="Ordning", help_text="Sorteringsordning för bilderna"
    )

    # Stämpelmarkering (koordinater) - procentuella värden för bästa visning
    x_coordinate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="X-koordinat (%)",
        help_text="X-koordinat för stämpelområdet (procent från vänster)",
    )
    y_coordinate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Y-koordinat (%)",
        help_text="Y-koordinat för stämpelområdet (procent från toppen)",
    )
    width = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Bredd (%)",
        help_text="Bredd på stämpelområdet (procent av bildbredd)",
    )
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Höjd (%)",
        help_text="Höjd på stämpelområdet (procent av bildhöjd)",
    )

    # Inställningar för visning
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Huvudbild",
        help_text="Markera som huvudbild för stämpeln",
    )

    # Metadata för stämpelmarkering
    position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Position",
        help_text="Var på bilden/yxan stämpeln finns (t.ex. 'på bladet - vänstra sidan')",
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Kommentar",
        help_text="Anteckningar om stämpelområdet",
    )
    uncertainty_level = models.CharField(
        max_length=20,
        choices=UNCERTAINTY_CHOICES,
        default="certain",
        verbose_name="Osäkerhetsnivå",
    )

    # Visningsinställningar
    show_full_image = models.BooleanField(
        default=False,
        verbose_name="Visa hela bilden",
        help_text="Visa hela yxbilden istället för bara stämpelområdet",
    )

    # Extern källinformation
    external_source = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Extern källa",
        help_text="Källa för extern bild (t.ex. 'Museum X', 'Bok Y')",
    )

    cache_busting_timestamp = models.DateTimeField(
        auto_now=True, verbose_name="Cache-busting timestamp"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-uploaded_at"]
        verbose_name = "Stämpelbild"
        verbose_name_plural = "Stämpelbilder"

    def __str__(self):
        if self.axe_image:
            return f"{self.stamp.name} på {self.axe_image.axe.display_id}"
        return f"{self.stamp.name} - {self.get_image_type_display()}"

    @property
    def webp_url(self):
        """Returnerar URL för WebP-version av bilden"""
        if self.image:
            # Skapa WebP-version om den inte finns
            image_path = self.image.path
            webp_path = image_path.rsplit(".", 1)[0] + ".webp"

            if not os.path.exists(webp_path):
                try:
                    with Image.open(image_path) as img:
                        # Konvertera till RGB om nödvändigt
                        if img.mode in ("RGBA", "LA", "P"):
                            img = img.convert("RGB")
                        img.save(webp_path, "WEBP", quality=85)
                except Exception as e:
                    # Om WebP-konvertering misslyckas, returnera original
                    return self.image.url

            # Returnera WebP-URL
            webp_url = self.image.url.rsplit(".", 1)[0] + ".webp"
            return webp_url
        return None

    @property
    def image_url_with_cache_busting(self):
        """Returnerar bild-URL med cache-busting"""
        if self.image:
            timestamp = int(self.cache_busting_timestamp.timestamp())
            return f"{self.image.url}?v={timestamp}"
        return None

    @property
    def has_coordinates(self):
        """Returnerar True om koordinater är definierade"""
        return all(
            [
                self.x_coordinate is not None,
                self.y_coordinate is not None,
                self.width is not None,
                self.height is not None,
            ]
        )

    @property
    def crop_area(self):
        """Returnerar beskärningsområdet som en tuple (x%, y%, width%, height%)"""
        if self.has_coordinates:
            return (self.x_coordinate, self.y_coordinate, self.width, self.height)
        return None

    def save(self, *args, **kwargs):
        # Säkerställ att image_type är satt
        if not self.image_type:
            self.image_type = "standalone"

        # Validering för att säkerställa att axe_image finns för axe_mark-typer
        if self.image_type == "axe_mark" and not self.axe_image:
            raise ValidationError("Axe_image måste anges för axe_mark-typer")

        # För standalone-bilder, säkerställ att axe_image är None
        if self.image_type == "standalone":
            self.axe_image = None

        # Säkerställ att stamp är satt
        if not self.stamp:
            raise ValidationError("Stamp måste anges")

        # Säkerställ att image är satt (endast för standalone, reference och documentation typer)
        if (
            self.image_type in ["standalone", "reference", "documentation"]
            and not self.image
        ):
            raise ValidationError("Bild måste anges")

        # Konvertera koordinater till Decimal om de är strängar
        from decimal import Decimal

        if isinstance(self.x_coordinate, str):
            self.x_coordinate = (
                Decimal(self.x_coordinate) if self.x_coordinate else None
            )
        if isinstance(self.y_coordinate, str):
            self.y_coordinate = (
                Decimal(self.y_coordinate) if self.y_coordinate else None
            )
        if isinstance(self.width, str):
            self.width = Decimal(self.width) if self.width else None
        if isinstance(self.height, str):
            self.height = Decimal(self.height) if self.height else None

        # Validera koordinater om de finns
        if any([self.x_coordinate, self.y_coordinate, self.width, self.height]):
            if not all([self.x_coordinate, self.y_coordinate, self.width, self.height]):
                raise ValidationError("Alla koordinater måste anges tillsammans")

            # Kontrollera att värdena är inom rimliga gränser
            if (
                self.x_coordinate < 0
                or self.y_coordinate < 0
                or self.width <= 0
                or self.height <= 0
                or self.x_coordinate + self.width > 100
                or self.y_coordinate + self.height > 100
            ):
                raise ValidationError("Koordinater måste vara inom 0-100%")

        # Om detta är den första bilden för stämpeln, gör den till primär
        if not self.pk and not self.stamp.images.exists():
            self.is_primary = True

        # Om denna bild är markerad som primär, ta bort primär från andra bilder
        if self.is_primary:
            self.stamp.images.filter(is_primary=True).exclude(pk=self.pk).update(
                is_primary=False
            )

        super().save(*args, **kwargs)

        # Skapa WebP-version om det är en ny bild
        if not hasattr(self, "_webp_created"):
            self._create_webp_version()
            self._webp_created = True

    def _create_webp_version(self):
        """Skapa WebP-version av bilden"""
        if self.image:
            try:
                image_path = self.image.path
                webp_path = image_path.rsplit(".", 1)[0] + ".webp"

                if not os.path.exists(webp_path):
                    with Image.open(image_path) as img:
                        if img.mode in ("RGBA", "LA", "P"):
                            img = img.convert("RGB")
                        img.save(webp_path, "WEBP", quality=85)
            except Exception:
                # Ignorera fel vid WebP-konvertering
                pass

    def delete(self, *args, **kwargs):
        # Ta bort både originalfilen och .webp-filen
        if self.image:
            try:
                # Ta bort originalfil
                if os.path.exists(self.image.path):
                    os.remove(self.image.path)

                # Ta bort WebP-fil
                webp_path = self.image.path.rsplit(".", 1)[0] + ".webp"
                if os.path.exists(webp_path):
                    os.remove(webp_path)
            except Exception:
                # Ignorera fel vid filborttagning
                pass

        super().delete(*args, **kwargs)


class AxeStamp(models.Model):
    """Koppling mellan yxa och stämpel"""

    UNCERTAINTY_CHOICES = [
        ("certain", "Säker"),
        ("uncertain", "Osäker"),
        ("tentative", "Preliminär"),
    ]

    axe = models.ForeignKey(
        Axe, on_delete=models.CASCADE, related_name="stamps", verbose_name="Yxa"
    )
    stamp = models.ForeignKey(
        Stamp, on_delete=models.CASCADE, related_name="axes", verbose_name="Stämpel"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="Kommentar")
    position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Position",
        help_text="Var på yxan stämpeln finns",
    )
    uncertainty_level = models.CharField(
        max_length=20,
        choices=UNCERTAINTY_CHOICES,
        default="certain",
        verbose_name="Osäkerhetsnivå",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Yxstämpel"
        verbose_name_plural = "Yxstämplar"
        # Removed unique_together constraint to allow multiple instances of the same stamp

    def __str__(self):
        return f"{self.axe.display_id} - {self.stamp.name}"


class StampVariant(models.Model):
    """Varianter av stämplar"""

    main_stamp = models.ForeignKey(
        Stamp,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name="Huvudstämpel",
    )
    variant_stamp = models.ForeignKey(
        Stamp,
        on_delete=models.CASCADE,
        related_name="main_stamp",
        verbose_name="Variantstämpel",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Beskrivning",
        help_text="Beskrivning av skillnaden",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Stämpelvariant"
        verbose_name_plural = "Stämpelvarianter"
        unique_together = ["main_stamp", "variant_stamp"]

    def __str__(self):
        return f"{self.main_stamp} - variant av {self.variant_stamp}"


class StampUncertaintyGroup(models.Model):
    """Grupper av stämplar med osäker identifiering"""

    CONFIDENCE_CHOICES = [
        ("high", "Hög"),
        ("medium", "Medium"),
        ("low", "Låg"),
    ]

    name = models.CharField(max_length=200, verbose_name="Namn")
    description = models.TextField(blank=True, null=True, verbose_name="Beskrivning")
    stamps = models.ManyToManyField(
        Stamp, related_name="uncertainty_groups", verbose_name="Stämplar"
    )
    confidence_level = models.CharField(
        max_length=20,
        choices=CONFIDENCE_CHOICES,
        default="medium",
        verbose_name="Konfidensnivå",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Osäkerhetsgrupp"
        verbose_name_plural = "Osäkerhetsgrupper"

    def __str__(self):
        return self.name


class StampSymbol(models.Model):
    """Symboler som kan förekomma i stämplar"""

    SYMBOL_TYPE_CHOICES = [
        ("crown", "Krona"),
        ("cannon", "Kanon"),
        ("star", "Stjärna"),
        ("cross", "Kors"),
        ("shield", "Sköld"),
        ("anchor", "Ankare"),
        ("flower", "Blomma"),
        ("leaf", "Löv"),
        ("arrow", "Pil"),
        ("circle", "Cirkel"),
        ("square", "Fyrkant"),
        ("triangle", "Triangel"),
        ("diamond", "Diamant"),
        ("heart", "Hjärta"),
        ("other", "Övrigt"),
    ]

    name = models.CharField(max_length=100, verbose_name="Namn")
    symbol_type = models.CharField(
        max_length=20,
        choices=SYMBOL_TYPE_CHOICES,
        default="other",
        verbose_name="Symboltyp",
    )
    description = models.TextField(
        blank=True, null=True, verbose_name="Beskrivning"
    )
    pictogram = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Piktogram",
        help_text="Unicode-piktogram för symbolen (t.ex. 👑 för Krona, ⭕ för Cirkel)",
    )
    is_predefined = models.BooleanField(
        default=False,
        verbose_name="Fördefinierad",
        help_text="Om symbolen är fördefinierad eller skapad av användare",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["symbol_type", "name"]
        verbose_name = "Stämpelsymbol"
        verbose_name_plural = "Stämpelsymboler"
        unique_together = ["name", "symbol_type"]

    def __str__(self):
        return f"{self.get_symbol_type_display()}: {self.name}"

    @property
    def display_name(self):
        """Returnerar visningsnamn för symbolen"""
        if self.symbol_type == "other":
            return self.name
        return f"{self.get_symbol_type_display()}: {self.name}"

    @property
    def display_with_pictogram(self):
        """Returnerar visningsnamn med piktogram om det finns"""
        if self.pictogram:
            return f"{self.pictogram} {self.name}"
        return self.name
