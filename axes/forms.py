from django import forms
from django.utils import timezone
from django.utils.safestring import mark_safe
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
    Stamp,
    StampTranscription,
    StampTag,
    StampImage,
    AxeStamp,
    StampVariant,
    StampUncertaintyGroup,
    AxeImage,
)
from .templatetags.axe_filters import country_flag

# Lista med länder (ISO 3166-1 alpha-2, namn, flagg-emoji)
COUNTRIES = [
    ("", "Välj land..."),
    ("SE", "🇸🇪 Sverige"),
    ("FI", "🇫🇮 Finland"),
    ("NO", "🇳🇴 Norge"),
    ("DK", "🇩🇰 Danmark"),
    ("DE", "🇩🇪 Tyskland"),
    ("GB", "🇬🇧 Storbritannien"),
    ("US", "🇺🇸 USA"),
    ("FR", "🇫🇷 Frankrike"),
    ("IT", "🇮🇹 Italien"),
    ("ES", "🇪🇸 Spanien"),
    ("PL", "🇵🇱 Polen"),
    ("EE", "🇪🇪 Estland"),
    ("LV", "🇱🇻 Lettland"),
    ("LT", "🇱🇹 Litauen"),
    ("RU", "🇷🇺 Ryssland"),
    ("NL", "🇳🇱 Nederländerna"),
    ("BE", "🇧🇪 Belgien"),
    ("CH", "🇨🇭 Schweiz"),
    ("AT", "🇦🇹 Österrike"),
    ("IE", "🇮🇪 Irland"),
    ("IS", "🇮🇸 Island"),
    ("CZ", "🇨🇿 Tjeckien"),
    ("SK", "🇸🇰 Slovakien"),
    ("HU", "🇭🇺 Ungern"),
    ("UA", "🇺🇦 Ukraina"),
    ("RO", "🇷🇴 Rumänien"),
    ("BG", "🇧🇬 Bulgarien"),
    ("HR", "🇭🇷 Kroatien"),
    ("SI", "🇸🇮 Slovenien"),
    ("PT", "🇵🇹 Portugal"),
    ("GR", "🇬🇷 Grekland"),
    ("TR", "🇹🇷 Turkiet"),
    ("CA", "🇨🇦 Kanada"),
    ("AU", "🇦🇺 Australien"),
    ("NZ", "🇳🇿 Nya Zeeland"),
]


class TransactionForm(forms.ModelForm):
    transaction_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Transaktionsdatum",
        help_text="Datum för transaktionen",
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "0.00", "step": "0.01"}
        ),
        label="Pris (kr)",
        help_text="Pris för yxan (negativt för köp, positivt för sälj)",
    )
    shipping_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "0.00", "step": "0.01"}
        ),
        label="Fraktkostnad (kr)",
        help_text="Fraktkostnad",
    )
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Kontakt",
        help_text="Välj försäljare/köpare (eller skapa ny)",
    )
    platform = forms.ModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Plattform",
        help_text="Välj plattform (eller skapa ny)",
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Lägg till kommentar om transaktionen...",
            }
        ),
        label="Kommentar",
        help_text="Kommentar om transaktionen",
    )

    class Meta:
        model = Transaction
        fields = [
            "transaction_date",
            "price",
            "shipping_cost",
            "contact",
            "platform",
            "comment",
        ]


class PlatformForm(forms.ModelForm):
    """Formulär för att skapa och redigera plattformar"""

    class Meta:
        model = Platform
        fields = ["name", "color_class"]
        labels = {
            "name": "Namn",
            "color_class": "Färg för badge",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ange plattformsnamn"}
            ),
            "color_class": forms.Select(attrs={"class": "form-control"}),
        }
        help_texts = {
            "name": "Namn på plattformen (t.ex. Tradera, eBay, Blocket)",
            "color_class": "Välj färg för plattformens badge",
        }


class ContactForm(forms.ModelForm):
    """Formulär för att skapa och redigera kontakter"""

    country_code = forms.ChoiceField(
        choices=COUNTRIES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Land",
        help_text="Välj land (med flagga)",
    )

    class Meta:
        model = Contact
        fields = [
            "name",
            "email",
            "phone",
            "alias",
            "street",
            "postal_code",
            "city",
            "country_code",
            "comment",
            "is_naj_member",
        ]
        labels = {
            "name": "Namn",
            "email": "E-post",
            "phone": "Telefon",
            "alias": "Alias",
            "street": "Gata",
            "postal_code": "Postnummer",
            "city": "Ort",
            "country_code": "Land",
            "comment": "Kommentar",
            "is_naj_member": "Medlem i Nordic Axe Junkies",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ange namn"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "namn@example.com"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "070-123 45 67"}
            ),
            "alias": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Användarnamn på Tradera/eBay",
                }
            ),
            "street": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Gatunamn och nummer"}
            ),
            "postal_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "123 45"}
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Stockholm"}
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Lägg till kommentar om kontakten...",
                }
            ),
            "is_naj_member": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        help_texts = {
            "name": "Kontaktens namn",
            "email": "E-postadress",
            "phone": "Telefonnummer",
            "alias": "Användarnamn på plattformar som Tradera, eBay, etc.",
            "street": "Gatuadress",
            "postal_code": "Postnummer",
            "city": "Ort",
            "country_code": "Land",
            "comment": "Kommentar om kontakten",
            "is_naj_member": "Är kontakten medlem i Nordic Axe Junkies?",
        }
        error_messages = {
            "name": {
                "required": "Namn måste anges.",
                "max_length": "Namnet får inte vara längre än 200 tecken.",
            },
            "email": {
                "required": "E-postadress måste anges.",
                "invalid": "Ange en giltig e-postadress.",
            },
            "phone": {
                "max_length": "Telefonnumret får inte vara längre än 50 tecken.",
            },
            "alias": {
                "max_length": "Aliaset får inte vara längre än 100 tecken.",
            },
            "street": {
                "max_length": "Gatuadressen får inte vara längre än 200 tecken.",
            },
            "postal_code": {
                "max_length": "Postnumret får inte vara längre än 20 tecken.",
            },
            "city": {
                "max_length": "Orten får inte vara längre än 100 tecken.",
            },
            "country_code": {
                "max_length": "Landskoden får inte vara längre än 2 tecken.",
            },
        }


class MeasurementForm(forms.ModelForm):
    """Formulär för att lägga till mått på en yxa"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hämta aktiva måtttyper från databasen
        measurement_types = MeasurementType.objects.filter(is_active=True)
        choices = [("", "Välj måtttyp...")] + [
            (mt.name, mt.name) for mt in measurement_types
        ]
        choices.append(("Övrigt", "Övrigt"))

        self.fields["name"] = forms.ChoiceField(
            choices=choices,
            required=True,  # Gör fältet obligatoriskt
            widget=forms.Select(
                attrs={"class": "form-control", "id": "measurement-name"}
            ),
            label="Måtttyp",
            help_text="Välj typ av mått",
        )

        # Skapa en mapping av måtttyper till enheter för JavaScript
        self.measurement_types_data = {mt.name: mt.unit for mt in measurement_types}

    custom_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ange eget måttnamn...",
                "id": "custom-measurement-name",
            }
        ),
        label="Eget måttnamn",
        help_text='Ange eget måttnamn om "Övrigt" är valt',
    )

    value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,  # Gör fältet obligatoriskt
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
            }
        ),
        label="Värde",
        help_text="Mätvärde",
    )

    # Radio buttons för enhetsval
    UNIT_CHOICES = [
        ("mm", "mm"),
        ("gram", "gram"),
        ("grader", "grader"),
        ("ovrig", "Övrig"),
    ]

    unit_option = forms.ChoiceField(
        choices=UNIT_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "unit-radio-group"}),
        required=False,
        label="Enhet",
        initial="mm",
    )

    unit = forms.CharField(
        max_length=50,
        required=True,  # Gör fältet obligatoriskt
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "measurement-unit",
                "placeholder": "Ange egen enhet...",
                "style": "display: none;",  # Dolt från början
            }
        ),
        label="Anpassad enhet",
        help_text='Ange egen enhet när "Övrig" är valt',
    )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        custom_name = cleaned_data.get("custom_name")
        unit_option = cleaned_data.get("unit_option")
        unit = cleaned_data.get("unit")

        # Om "Övrigt" är valt för namn, använd custom_name som name
        if name == "Övrigt":
            if not custom_name:
                raise forms.ValidationError(
                    'Du måste ange ett eget måttnamn när "Övrigt" är valt.'
                )
            cleaned_data["name"] = custom_name

        # Hantera enhetsval
        if unit_option == "ovrig":
            # Om "Övrig" är valt för enhet, använd det anpassade unit-fältet
            if not unit:
                raise forms.ValidationError(
                    'Du måste ange en egen enhet när "Övrig" är valt.'
                )
            # unit behålls som det är
        elif unit_option:
            # Om en standardenhet är vald, använd den
            cleaned_data["unit"] = unit_option
        else:
            # Fallback till befintligt unit-fält om inget radio-val är gjort
            if not unit:
                raise forms.ValidationError("Du måste välja eller ange en enhet.")

        return cleaned_data

    class Meta:
        model = Measurement
        fields = ["name", "value", "unit"]


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class AxeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Sortera tillverkare hierarkiskt för dropdown-menyn
        all_manufacturers = Manufacturer.objects.all().order_by("name")

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

        # Sortera tillverkare hierarkiskt
        sorted_manufacturers = sort_hierarchically(all_manufacturers)

        # Skapa choices för dropdown-menyn med hierarkisk indentering
        choices = [("", "Välj tillverkare...")]
        for m in sorted_manufacturers:
            # Lägg till flaggemoji om country_code finns
            flag_emoji = ""
            if m.country_code:
                flag_emoji = f"{country_flag(m.country_code)} "

            if m.parent:
                # Skapa hierarkisk prefix med box-drawing characters
                prefix = self._get_hierarchy_prefix(m, sorted_manufacturers)
                choice_label = mark_safe(f"{prefix}{flag_emoji}{m.name}")
            else:
                # Huvudtillverkare - ingen indentering
                choice_label = f"{flag_emoji}{m.name}"
            choices.append((m.id, choice_label))

        # Uppdatera manufacturer-fältet med sorterade choices
        self.fields["manufacturer"] = forms.ChoiceField(
            choices=choices,
            required=True,
            widget=forms.Select(attrs={"class": "form-select"}),
            label="Tillverkare",
            help_text="Välj tillverkare av yxan",
        )

        # Om detta är en redigering av befintlig yxa, sätt rätt tillverkare som vald
        if self.instance and self.instance.pk and self.instance.manufacturer:
            self.fields["manufacturer"].initial = self.instance.manufacturer.id

    def _get_hierarchy_prefix(self, manufacturer, manufacturers_list):
        """
        Skapar hierarkisk prefix med box-drawing characters för tillverkare.
        Använder olika tecken beroende på position i hierarkin.
        """
        if not manufacturer.parent:
            return ""

        # Bygg vägen från roten till denna tillverkare
        path = []
        current = manufacturer
        while current.parent:
            path.append(current)
            current = current.parent
        path.reverse()  # Nu har vi vägen från roten till tillverkaren

        # Skapa prefix för varje nivå i vägen
        prefix = ""
        for i, node in enumerate(path):
            # Hitta alla syskon på denna nivå
            siblings = [m for m in manufacturers_list if m.parent == node.parent]
            siblings.sort(key=lambda x: x.name)

            try:
                position = siblings.index(node)
                is_last = position == len(siblings) - 1
            except ValueError:
                is_last = True

            if i == len(path) - 1:
                # Detta är den sista noden (tillverkaren själv)
                if is_last:
                    prefix += "└─&nbsp;"  # └─ + 1 space (total 4 units including the box characters)
                else:
                    prefix += "├─&nbsp;"  # ├─ + 1 space (total 4 units including the box characters)
            else:
                # Detta är en mellannivå, kontrollera om vi ska visa vertikalt streck
                # Vi visar vertikalt streck endast om det finns fler syskon efter denna nod
                # och om det finns barn under denna nod som kommer efter denna gren
                if is_last:
                    prefix = (
                        "&nbsp;&nbsp;&nbsp;&nbsp;" + prefix
                    )  # 4 spaces for consistent indentation
                else:
                    # Kontrollera om det finns barn under denna nod som kommer efter denna gren
                    has_children_after = False
                    for sibling in siblings[position + 1 :]:
                        if any(m.parent == sibling for m in manufacturers_list):
                            has_children_after = True
                            break

                    if has_children_after:
                        prefix = (
                            "│&nbsp;&nbsp;&nbsp;" + prefix
                        )  # │ + 3 spaces (total 4 units including the box character)
                    else:
                        prefix = (
                            "&nbsp;&nbsp;&nbsp;&nbsp;" + prefix
                        )  # 4 spaces for consistent indentation

        return mark_safe(prefix)

    def clean_manufacturer(self):
        """Konvertera manufacturer ID till Manufacturer-objekt"""
        manufacturer_id = self.cleaned_data.get("manufacturer")
        if manufacturer_id:
            try:
                return Manufacturer.objects.get(id=manufacturer_id)
            except Manufacturer.DoesNotExist:
                raise forms.ValidationError("Vald tillverkare finns inte.")
        else:
            raise forms.ValidationError("Tillverkare måste väljas.")

    images = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        label="Bilder",
        help_text="Ladda upp bilder av yxan (drag & drop stöds)",
    )

    # Kontaktrelaterade fält
    contact_search = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Sök efter befintlig kontakt eller ange ny...",
            }
        ),
        label="Försäljare",
        help_text="Sök efter befintlig kontakt eller ange namn för ny kontakt",
    )

    contact_name = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ange försäljarens namn"}
        ),
        label="Namn (ny kontakt)",
        help_text="Namn på försäljaren (t.ex. från Tradera, eBay)",
    )

    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "namn@example.com"}
        ),
        label="E-post (ny kontakt)",
        help_text="Försäljarens e-postadress",
    )

    contact_phone = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "070-123 45 67"}
        ),
        label="Telefon (ny kontakt)",
        help_text="Försäljarens telefonnummer",
    )

    contact_alias = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Användarnamn på Tradera/eBay",
            }
        ),
        label="Alias (ny kontakt)",
        help_text="Användarnamn på plattformen (t.ex. Tradera, eBay)",
    )

    contact_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Lägg till kommentar om försäljaren...",
            }
        ),
        label="Kommentar (ny kontakt)",
        help_text="Kommentar om försäljaren",
    )

    is_naj_member = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="NAJ-medlem (ny kontakt)",
        help_text="Är försäljaren medlem i Nordic Axe Junkies?",
    )

    # Adressfält för ny kontakt
    contact_street = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Gatunamn och nummer"}
        ),
        label="Gata (ny kontakt)",
        help_text="Gatuadress för försäljaren",
    )

    contact_postal_code = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "123 45"}
        ),
        label="Postnummer (ny kontakt)",
        help_text="Postnummer för försäljaren",
    )

    contact_city = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Stockholm"}
        ),
        label="Ort (ny kontakt)",
        help_text="Ort för försäljaren",
    )

    contact_country_code = forms.ChoiceField(
        choices=COUNTRIES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Land (ny kontakt)",
        help_text="Välj land (med flagga) för försäljaren",
    )

    # Transaktionsrelaterade fält
    transaction_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "0.00", "step": "0.01"}
        ),
        label="Pris (kr)",
        help_text="Pris för yxan (negativt för köp, positivt för sälj)",
    )

    transaction_shipping = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "0.00", "step": "0.01"}
        ),
        label="Fraktkostnad (kr)",
        help_text="Fraktkostnad (negativt för köp, positivt för sälj)",
    )

    transaction_date = forms.DateField(
        required=False,
        initial=timezone.now().date,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Transaktionsdatum",
        help_text="Datum för transaktionen",
    )

    transaction_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Lägg till kommentar om transaktionen...",
            }
        ),
        label="Transaktionskommentar",
        help_text="Kommentar om transaktionen (t.ex. betalningsmetod)",
    )

    # Plattformsrelaterade fält
    platform_search = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Sök efter befintlig plattform eller ange ny...",
            }
        ),
        label="Plattform",
        help_text="Börja skriva för att söka efter befintlig plattform eller skapa ny",
    )

    platform_name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ange plattformsnamn"}
        ),
        label="Namn (ny plattform)",
        help_text="Namn på plattformen (t.ex. Tradera, eBay)",
    )

    platform_url = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={"class": "form-control", "placeholder": "https://www.tradera.com"}
        ),
        label="URL (ny plattform)",
        help_text="URL till plattformen",
    )

    platform_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Lägg till kommentar om plattformen...",
            }
        ),
        label="Kommentar (ny plattform)",
        help_text="Kommentar om plattformen",
    )

    class Meta:
        model = Axe
        fields = [
            "manufacturer",
            "model",
            "comment",
            "status",
        ]  # Lägg till manufacturer tillbaka
        labels = {
            "manufacturer": "Tillverkare",
            "model": "Modell",
            "comment": "Kommentar",
            "status": "Status",
        }
        widgets = {
            "manufacturer": forms.Select(attrs={"class": "form-select"}),
            "model": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ange modellnamn"}
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Lägg till kommentar om yxan...",
                }
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class BackupUploadForm(forms.Form):
    """Form för att ladda upp backupfiler"""

    backup_file = forms.FileField(
        widget=forms.FileInput(attrs={"class": "form-control"}),
        label="Backupfil",
        help_text="Välj en .sqlite3-fil att återställa från",
    )

    def clean_backup_file(self):
        backup_file = self.cleaned_data.get("backup_file")
        if backup_file:
            # Kontrollera filtyp
            if not backup_file.name.endswith(".sqlite3"):
                raise forms.ValidationError("Endast .sqlite3-filer är tillåtna.")

            # Kontrollera filstorlek (max 100MB)
            if backup_file.size > 100 * 1024 * 1024:
                raise forms.ValidationError(
                    "Filen är för stor. Maximal storlek är 100MB."
                )

        return backup_file


# Stämpelregister-formulär
class StampForm(forms.ModelForm):
    """Formulär för att skapa och redigera stämplar"""

    class Meta:
        model = Stamp
        fields = [
            "name",
            "description",
            "manufacturer",
            "stamp_type",
            "status",
            "year_from",
            "year_to",
            "year_uncertainty",
            "year_notes",
            "source_category",
            "source_reference",
        ]
        labels = {
            "name": "Namn",
            "description": "Beskrivning",
            "manufacturer": "Tillverkare",
            "stamp_type": "Typ",
            "status": "Status",
            "year_from": "Från år",
            "year_to": "Till år",
            "year_uncertainty": "Osäker årtalsinformation",
            "year_notes": "Anteckningar om årtal",
            "source_category": "Källkategori",
            "source_reference": "Källhänvisning",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ange stämpelns namn"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Beskriv stämpeln...",
                }
            ),
            "manufacturer": forms.Select(attrs={"class": "form-control"}),
            "stamp_type": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "year_from": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "1884"}
            ),
            "year_to": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "1900"}
            ),
            "year_uncertainty": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "year_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": 'Anteckningar om årtal (t.ex. "cirka")',
                }
            ),
            "source_category": forms.Select(attrs={"class": "form-control"}),
            "source_reference": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": 'Specifik källhänvisning (t.ex. "eBay-auktion 2023")',
                }
            ),
        }
        help_texts = {
            "name": "Unikt namn för stämpeln",
            "description": "Detaljerad beskrivning av stämpeln",
            "manufacturer": "Tillverkare som använde denna stämpel (kan vara okänd)",
            "stamp_type": "Typ av stämpel (text, bild eller symbol)",
            "status": "Är stämpeln känd eller okänd",
            "year_from": "Startår för när stämpeln användes",
            "year_to": "Slutår för när stämpeln användes",
            "year_uncertainty": "Markera om årtalsinformationen är osäker",
            "year_notes": 'Anteckningar om årtal (t.ex. "cirka", "omkring")',
            "source_category": "Kategori för källan till stämpelinformationen",
            "source_reference": "Specifik hänvisning till källan",
        }

    def clean(self):
        """Validera formuläret"""
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        manufacturer = cleaned_data.get("manufacturer")

        # Validera att kända stämplar har tillverkare
        if status == "known" and not manufacturer:
            raise forms.ValidationError("Kända stämplar måste ha en tillverkare")

        return cleaned_data


class StampTranscriptionForm(forms.ModelForm):
    """Formulär för att lägga till transkriberingar"""

    class Meta:
        model = StampTranscription
        fields = ["text", "quality"]
        labels = {
            "text": "Text",
            "quality": "Kvalitet",
        }
        widgets = {
            "text": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": 'Ange text från stämpeln (t.ex. "GRÄNSFORS")',
                }
            ),
            "quality": forms.Select(attrs={"class": "form-control"}),
        }
        help_texts = {
            "text": "Textbaserad beskrivning av stämpeln",
            "quality": "Bedömning av hur säker transkriberingen är",
        }


class AxeStampForm(forms.ModelForm):
    """Formulär för att koppla stämpel till yxa"""

    def __init__(self, *args, **kwargs):
        axe = kwargs.pop("axe", None)
        super().__init__(*args, **kwargs)

        if axe and axe.manufacturer:
            # Hämta alla stämplar, prioritera tillverkarens stämplar först
            from .models import Stamp

            # Stämplar från yxans tillverkare (prioriterade)
            primary_stamps = Stamp.objects.filter(
                manufacturer=axe.manufacturer
            ).order_by("name")

            # Alla andra stämplar (sekundära)
            other_stamps = Stamp.objects.exclude(
                manufacturer=axe.manufacturer
            ).order_by("name")

            # Skapa choices med prioriterade stämplar först
            choices = [("", "Välj stämpel...")]

            # Lägg till prioriterade stämplar med separator
            if primary_stamps.exists():
                choices.append(("", f"--- Stämplar från {axe.manufacturer.name} ---"))
                for stamp in primary_stamps:
                    choices.append(
                        (stamp.id, f"{stamp.name} ({stamp.get_stamp_type_display()})")
                    )

            # Lägg till separator för andra stämplar
            if other_stamps.exists():
                choices.append(("", "--- Andra stämplar ---"))
                for stamp in other_stamps:
                    choices.append(
                        (
                            stamp.id,
                            f"{stamp.name} - {stamp.manufacturer.name if stamp.manufacturer else 'Okänd'} ({stamp.get_stamp_type_display()})",
                        )
                    )

            self.fields["stamp"] = forms.ChoiceField(
                choices=choices,
                required=True,
                widget=forms.Select(attrs={"class": "form-control"}),
                label="Stämpel",
                help_text=f"Prioriterade stämplar från {axe.manufacturer.name} visas först",
            )

    class Meta:
        model = AxeStamp
        fields = ["stamp", "comment", "position", "uncertainty_level"]
        labels = {
            "stamp": "Stämpel",
            "comment": "Kommentar",
            "position": "Position",
            "uncertainty_level": "Osäkerhetsnivå",
        }
        widgets = {
            "stamp": forms.Select(attrs={"class": "form-control"}),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Lägg till kommentar om stämpeln...",
                }
            ),
            "position": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Var på yxan stämpeln finns",
                }
            ),
            "uncertainty_level": forms.Select(attrs={"class": "form-control"}),
        }
        help_texts = {
            "stamp": "Välj stämpel att koppla till yxan",
            "comment": "Kommentar om stämpeln (kvalitet, synlighet, etc.)",
            "position": "Var på yxan stämpeln finns (valfritt)",
            "uncertainty_level": "Hur säker är identifieringen av stämpeln",
        }

    def clean_stamp(self):
        """Konvertera stamp ID till Stamp-objekt"""
        stamp_id = self.cleaned_data.get("stamp")
        if stamp_id:
            try:
                from .models import Stamp

                return Stamp.objects.get(id=stamp_id)
            except Stamp.DoesNotExist:
                raise forms.ValidationError("Vald stämpel finns inte.")
        else:
            raise forms.ValidationError("Stämpel måste väljas.")


class StampTagForm(forms.ModelForm):
    """Formulär för att skapa stämpeltaggar"""

    class Meta:
        model = StampTag
        fields = ["name", "description", "color"]
        labels = {
            "name": "Namn",
            "description": "Beskrivning",
            "color": "Färg",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": 'Ange taggnamn (t.ex. "tillverkarnamn")',
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Beskriv vad taggen representerar",
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "color",
                    "placeholder": "#007bff",
                }
            ),
        }
        help_texts = {
            "name": "Namn på taggen",
            "description": "Beskrivning av vad taggen representerar",
            "color": "Hex-färg för taggen (t.ex. #007bff)",
        }


class StampImageForm(forms.ModelForm):
    """Formulär för stämpelbilder med dynamisk fältvisning"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Sätt initial image_type till standalone för nya bilder
        if not self.initial.get("image_type"):
            self.initial["image_type"] = "standalone"

    class Meta:
        model = StampImage
        fields = [
            "image",
            "caption",
            "description",
            "x_coordinate",
            "y_coordinate",
            "width",
            "height",
            "position",
            "comment",
            "uncertainty_level",
            "external_source",
        ]
        labels = {
            "image": "Bild",
            "caption": "Bildtext",
            "description": "Beskrivning",
            "x_coordinate": "X-koordinat (%)",
            "y_coordinate": "Y-koordinat (%)",
            "width": "Bredd (%)",
            "height": "Höjd (%)",
            "position": "Position",
            "comment": "Kommentar",
            "uncertainty_level": "Osäkerhetsnivå",
            "external_source": "Extern källa",
        }
        widgets = {
            "image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "caption": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Kort beskrivning av bilden",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Detaljerad beskrivning av vad bilden visar",
                }
            ),
            "x_coordinate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                    "placeholder": "Markera på bilden",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "y_coordinate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                    "placeholder": "Markera på bilden",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "width": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                    "placeholder": "Markera på bilden",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "height": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                    "placeholder": "Markera på bilden",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "position": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": 'Var på bilden/yxan stämpeln finns (t.ex. "på bladet - vänstra sidan")',
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Lägg till kommentar om stämpeln...",
                }
            ),
            "uncertainty_level": forms.Select(attrs={"class": "form-control"}),
            "external_source": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": 'Källa för extern bild (t.ex. "Museum X", "Bok Y")',
                }
            ),
        }
        help_texts = {
            "image": "Ladda upp en bild av stämpeln",
            "caption": "Kort beskrivning som visas under bilden",
            "description": "Detaljerad beskrivning av vad bilden visar",
            "x_coordinate": "X-koordinat för stämpelområdet (procent från vänster)",
            "y_coordinate": "Y-koordinat för stämpelområdet (procent från toppen)",
            "width": "Bredd på stämpelområdet (procent av bildbredd)",
            "height": "Höjd på stämpelområdet (procent av bildhöjd)",
            "position": "Var på bilden/yxan stämpeln finns",
            "comment": "Anteckningar om stämpelområdet",
            "uncertainty_level": "Hur säker identifieringen av stämpeln är",
            "external_source": "Källa för extern bild",
        }

    def clean(self):
        """Validera formulärdata"""
        cleaned_data = super().clean()
        image_type = cleaned_data.get("image_type")
        axe_image = cleaned_data.get("axe_image")

        # Säkerställ att image_type är satt
        if not image_type:
            image_type = "standalone"
            cleaned_data["image_type"] = image_type

        # Validera att axe_image finns för axe_mark-typer
        if image_type == "axe_mark" and not axe_image:
            raise forms.ValidationError("Yxbild måste väljas för yxbildmarkeringar")

        # För standalone-bilder, säkerställ att axe_image är None
        if image_type == "standalone":
            cleaned_data["axe_image"] = None

        # Validera koordinater
        coords = [
            cleaned_data.get("x_coordinate"),
            cleaned_data.get("y_coordinate"),
            cleaned_data.get("width"),
            cleaned_data.get("height"),
        ]

        if any(coords) and not all(coords):
            raise forms.ValidationError("Alla koordinater måste anges tillsammans")

        return cleaned_data


class StampImageMarkForm(forms.ModelForm):
    """Formulär för redigering av stämpelmarkeringar på yxbilder"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Sätt initial image_type till axe_mark för stämpelmarkeringar
        if not self.initial.get("image_type"):
            self.initial["image_type"] = "axe_mark"

    class Meta:
        model = StampImage
        fields = [
            "image_type",
            "axe_image",
            "caption",
            "description",
            "x_coordinate",
            "y_coordinate",
            "width",
            "height",
            "position",
            "comment",
            "uncertainty_level",
            "external_source",
        ]
        labels = {
            "image_type": "Bildtyp",
            "axe_image": "Yxbild",
            "caption": "Bildtext",
            "description": "Beskrivning",
            "x_coordinate": "X-koordinat (%)",
            "y_coordinate": "Y-koordinat (%)",
            "width": "Bredd (%)",
            "height": "Höjd (%)",
            "position": "Position",
            "comment": "Kommentar",
            "uncertainty_level": "Osäkerhetsnivå",
            "external_source": "Extern källa",
        }
        widgets = {
            "image_type": forms.Select(
                attrs={
                    "class": "form-control",
                    "onchange": "updateAxeImageField(this.value)",
                }
            ),
            "axe_image": forms.Select(attrs={"class": "form-control"}),
            "caption": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Kort beskrivning av bilden",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Detaljerad beskrivning av vad bilden visar",
                }
            ),
            "x_coordinate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                    "placeholder": "Markera på bilden",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "y_coordinate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                    "placeholder": "Markera på bilden",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "width": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                    "placeholder": "Markera på bilden",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "height": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                    "placeholder": "Markera på bilden",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "position": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": 'Var på bilden/yxan stämpeln finns (t.ex. "på bladet - vänstra sidan")',
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Lägg till kommentar om stämpeln...",
                }
            ),
            "uncertainty_level": forms.Select(attrs={"class": "form-control"}),
            "external_source": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": 'Källa för extern bild (t.ex. "Museum X", "Bok Y")',
                }
            ),
        }
        help_texts = {
            "image_type": "Välj typ av bild",
            "axe_image": "Välj yxbild om detta är en markering på en befintlig yxbild",
            "caption": "Kort beskrivning som visas under bilden",
            "description": "Detaljerad beskrivning av vad bilden visar",
            "x_coordinate": "X-koordinat för stämpelområdet (procent från vänster)",
            "y_coordinate": "Y-koordinat för stämpelområdet (procent från toppen)",
            "width": "Bredd på stämpelområdet (procent av bildbredd)",
            "height": "Höjd på stämpelområdet (procent av bildhöjd)",
            "position": "Var på bilden/yxan stämpeln finns",
            "comment": "Anteckningar om stämpelområdet",
            "uncertainty_level": "Hur säker identifieringen av stämpeln är",
            "external_source": "Källa för extern bild",
        }
