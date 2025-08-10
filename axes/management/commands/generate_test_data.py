import os
import shutil
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from decimal import Decimal
import random
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont
import io

from axes.models import (
    Manufacturer,
    Axe,
    AxeImage,
    ManufacturerImage,
    ManufacturerLink,
    Contact,
    Platform,
    Transaction,
    Measurement,
    MeasurementType,
    MeasurementTemplate,
    MeasurementTemplateItem,
    Settings,
    NextAxeID,
    Stamp,
    AxeStamp,
    StampImage,
    StampSymbol,
)


class Command(BaseCommand):
    help = "Generera realistisk testdata för AxeCollection"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Rensa befintlig data innan generering",
        )
        parser.add_argument(
            "--axes",
            type=int,
            default=50,
            help="Antal yxor att generera (default: 50)",
        )
        parser.add_argument(
            "--manufacturers",
            type=int,
            default=15,
            help="Antal tillverkare att generera (default: 15)",
        )
        parser.add_argument(
            "--contacts",
            type=int,
            default=25,
            help="Antal kontakter att generera (default: 25)",
        )
        parser.add_argument(
            "--no-images",
            action="store_true",
            help="Generera testdata utan bildfiler",
        )
        parser.add_argument(
            "--clean-stamp-images",
            action="store_true",
            help="Rensa gamla StampImage-objekt även utan --clear",
        )
        parser.add_argument(
            "--no-stamp-images",
            action="store_true",
            help="Skapa inte StampImage-objekt automatiskt (låt användaren markera manuellt)",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Minska output till endast viktiga meddelanden",
        )

    def handle(self, *args, **options):
        quiet = options.get("quiet", False)

        if options["clear"]:
            self.stdout.write("Rensar befintlig data...")
            self.clear_data()

        self.stdout.write("Genererar testdata...")

        # Skapa måtttyper och mallar först
        self.create_measurement_types()
        self.create_measurement_templates()

        # Initiera stämpelsymboler
        self.init_stamp_symbols(quiet=quiet)

        # Skapa grunddata
        manufacturers = self.create_manufacturers(options["manufacturers"], quiet=quiet)
        contacts = self.create_contacts(options["contacts"], quiet=quiet)
        platforms = self.create_platforms(quiet=quiet)

        # Skapa yxor och relaterad data
        axes = self.create_axes(manufacturers, options["axes"], quiet=quiet)
        self.create_transactions(axes, contacts, platforms, quiet=quiet)
        self.create_measurements(axes, quiet=quiet)

        # Skapa specifika yxor med riktiga bilder först så att vi känner till deras IDs
        specific_axes = self.create_specific_axes_with_real_images(
            manufacturers, no_stamp_images=False, quiet=quiet
        )

        # Skapa specifika stämplar EFTER att yxorna finns, och koppla sedan
        self.create_specific_stamps(manufacturers, quiet=quiet)
        # Säkerställ deterministiska kopplingar till befintliga specific_axes
        if specific_axes:
            self._create_stamp_images_with_manual_coordinates(
                specific_axes, quiet=quiet
            )

        if not quiet:
            self.stdout.write("Skapade yxor med manuella stämpelmarkeringar")

        # Skapa tillverkarlänkar och bilder
        self.create_manufacturer_links(manufacturers, quiet=quiet)

        if not options["no_images"]:
            self.create_manufacturer_images(manufacturers, quiet=quiet)
            # Skapa yxbilder
            self.create_axe_images(axes, quiet=quiet)

        # Skapa standardinställningar
        self.create_settings()

        # Skapa demo-användare
        self.create_demo_user(quiet=quiet)

        self.stdout.write(
            self.style.SUCCESS(
                f"Testdata genererat! "
                f"{len(manufacturers)} tillverkare, "
                f"{len(contacts)} kontakter, "
                f"{len(axes)} yxor, "
                f"{len(platforms)} plattformar"
            )
        )

    def clear_data(self):
        """Rensa all befintlig data"""
        # Rensa stämpel-relaterad data först
        from axes.models import (
            StampImage,
            AxeStamp,
            Stamp,
            StampTranscription,
            StampTag,
            StampVariant,
            StampUncertaintyGroup,
            StampSymbol,
        )

        StampImage.objects.all().delete()
        AxeStamp.objects.all().delete()
        StampTranscription.objects.all().delete()
        StampTag.objects.all().delete()
        StampVariant.objects.all().delete()
        StampUncertaintyGroup.objects.all().delete()
        Stamp.objects.all().delete()
        StampSymbol.objects.all().delete()

        # Rensa övrig data
        Transaction.objects.all().delete()
        Measurement.objects.all().delete()
        AxeImage.objects.all().delete()
        Axe.objects.all().delete()
        ManufacturerImage.objects.all().delete()
        ManufacturerLink.objects.all().delete()
        Manufacturer.objects.all().delete()
        Contact.objects.all().delete()
        Platform.objects.all().delete()
        MeasurementTemplateItem.objects.all().delete()
        MeasurementTemplate.objects.all().delete()
        MeasurementType.objects.all().delete()
        Settings.objects.all().delete()
        NextAxeID.objects.all().delete()  # Återställ nästa yx-ID

        # Rensa alla användare förutom superuser
        User.objects.filter(is_superuser=False).delete()

    def create_measurement_types(self):
        """Skapa måtttyper"""
        types = [
            ("Vikt", "gram", "Total vikt av yxan"),
            ("Skaftlängd", "mm", "Längd på yxskaftet"),
            ("Eggbredd", "mm", "Bredd på yxeggen"),
            ("Nacke till egg", "mm", "Avstånd från nacke till egg"),
            ("Huvudvikt", "gram", "Vikt på yxhuvudet"),
            ("Ögats bredd", "mm", "Bredd på ögat (skafthålet)"),
            ("Ögats höjd", "mm", "Höjd på ögat (skafthålet)"),
        ]

        for name, unit, description in types:
            MeasurementType.objects.get_or_create(
                name=name,
                defaults={
                    "unit": unit,
                    "description": description,
                    "sort_order": len(MeasurementType.objects.all()),
                },
            )

    def create_measurement_templates(self):
        """Skapa måttmallar"""
        templates_data = [
            {
                "name": "Standard yxa",
                "description": "Grundläggande mått för vanliga yxor",
                "items": [
                    ("Bladlängd", "mm"),
                    ("Bladbredd", "mm"),
                    ("Bladtjocklek", "mm"),
                    ("Ögatjocklek", "mm"),
                    ("Ögabredd", "mm"),
                    ("Halslängd", "mm"),
                    ("Halsbredd", "mm"),
                    ("Handtagslängd", "mm"),
                    ("Handtagsbredd", "mm"),
                    ("Total längd", "mm"),
                    ("Vikt", "gram"),
                ],
            },
            {
                "name": "Fällkniv",
                "description": "Mått för fällknivar",
                "items": [
                    ("Bladlängd", "mm"),
                    ("Bladbredd", "mm"),
                    ("Bladtjocklek", "mm"),
                    ("Handtagslängd", "mm"),
                    ("Handtagsbredd", "mm"),
                    ("Total längd (öppen)", "mm"),
                    ("Total längd (stängd)", "mm"),
                    ("Vikt", "gram"),
                ],
            },
            {
                "name": "Köksyxa",
                "description": "Mått för köksyxor",
                "items": [
                    ("Bladlängd", "mm"),
                    ("Bladbredd", "mm"),
                    ("Bladtjocklek", "mm"),
                    ("Handtagslängd", "mm"),
                    ("Handtagsbredd", "mm"),
                    ("Total längd", "mm"),
                    ("Vikt", "gram"),
                ],
            },
        ]

        for template_data in templates_data:
            template, created = MeasurementTemplate.objects.get_or_create(
                name=template_data["name"],
                defaults={
                    "description": template_data["description"],
                    "sort_order": len(MeasurementTemplate.objects.all()),
                },
            )

            for i, (name, unit) in enumerate(template_data["items"]):
                measurement_type, _ = MeasurementType.objects.get_or_create(
                    name=name, defaults={"unit": unit}
                )
                MeasurementTemplateItem.objects.get_or_create(
                    template=template,
                    measurement_type=measurement_type,
                    defaults={"sort_order": i},
                )

    def init_stamp_symbols(self, quiet=False):
        """Initiera stämpelsymboler"""
        from axes.management.commands.init_stamp_symbols import (
            Command as InitStampSymbolsCommand,
        )

        if not quiet:
            self.stdout.write("Initierar stämpelsymboler...")
        init_command = InitStampSymbolsCommand()
        init_command.handle(quiet=quiet)
        if not quiet:
            self.stdout.write("Stämpelsymboler initierade.")

    def create_manufacturers(self, count, quiet=False):
        """Skapa tillverkare med hierarkisk struktur"""
        # Definiera hierarkiska tillverkare
        hierarchical_manufacturers = {
            # Huvudtillverkare (fabriker/bruk)
            "Hjärtumssmedjan": {
                "type": "TILLVERKARE",
                "info": "Traditionell smedja i Hjärtum, grundad 1850. Känd för handgjorda kvalitetsyxor.",
                "country_code": "SE",
                "sub_manufacturers": [
                    {
                        "name": "Johan Jonsson",
                        "type": "SMED",
                        "info": "Mästersmed vid Hjärtumssmedjan. Specialiserar sig på slöjdyxor och huggyxor.",
                        "country_code": "SE",
                    },
                    {
                        "name": "Johan Skog",
                        "type": "SMED",
                        "info": "Erfaren smed vid Hjärtumssmedjan. Känd för sina fällyxor och timmerbilor.",
                        "country_code": "SE",
                    },
                    {
                        "name": "Willy Persson",
                        "type": "SMED",
                        "info": "Ung smed vid Hjärtumssmedjan. Specialiserar sig på handyxor och tapphålsyxor.",
                        "country_code": "SE",
                    },
                ],
            },
            "Billnäs bruk": {
                "type": "TILLVERKARE",
                "info": "Historiskt bruk grundat 1641. En av Finlands äldsta yxtillverkare.",
                "country_code": "FI",
                "sub_manufacturers": [],
            },
            "Gränsfors bruk": {
                "type": "TILLVERKARE",
                "info": "Modernt bruk grundat 1902. Känd för handgjorda kvalitetsyxor.",
                "country_code": "SE",
                "sub_manufacturers": [],
            },
            "Hults bruk": {
                "type": "TILLVERKARE",
                "info": "Bruk grundat 1697. Traditionell tillverkning av handyxor.",
                "country_code": "SE",
                "sub_manufacturers": [],
            },
            "S. A. Wetterlings yxfabrik": {
                "type": "TILLVERKARE",
                "info": "Yxfabrik grundad 1880. Känd för robusta huggyxor.",
                "country_code": "SE",
                "sub_manufacturers": [],
            },
        }

        # Lägg till fler huvudtillverkare om count är större
        additional_manufacturers = [
            {
                "name": "Mariefors Bruk",
                "country_code": "FI",
                "info": "Finsk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på traditionella yxor.",
            },
            {
                "name": "Säters yxfabrik",
                "country_code": "SE",
                "info": "Svensk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på handgjorda yxor.",
            },
            {
                "name": "Jäders bruk",
                "country_code": "SE",
                "info": "Svensk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på industriella yxor.",
            },
            {
                "name": "Svenska Yxfabriken AB, Kristinehamn",
                "country_code": "SE",
                "info": "Svensk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på slöjdyxor.",
            },
            {
                "name": "Edsbyn Industri Aktiebolag",
                "country_code": "SE",
                "info": "Svensk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på huggyxor.",
            },
            {
                "name": "Dansk Stålindustri",
                "country_code": "DK",
                "info": "Dansk tillverkare av kvalitetsyxor. Grundad 1900-talet. Specialiserar sig på moderna yxor.",
            },
            {
                "name": "Mustad",
                "country_code": "NO",
                "info": "Norsk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på handgjorda yxor.",
            },
            {
                "name": "Øyo",
                "country_code": "NO",
                "info": "Norsk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på traditionella yxor.",
            },
        ]

        manufacturers = []

        # Skapa hierarkiska tillverkare först
        for main_name, data in hierarchical_manufacturers.items():
            if len(manufacturers) >= count:
                break

            # Skapa huvudtillverkare
            main_manufacturer = Manufacturer.objects.create(
                name=main_name,
                information=data["info"],
                manufacturer_type=data["type"],
                country_code=data["country_code"],
            )
            manufacturers.append(main_manufacturer)

            # Skapa undertillverkare
            for sub_data in data["sub_manufacturers"]:
                if len(manufacturers) >= count:
                    break

                sub_manufacturer = Manufacturer.objects.create(
                    name=sub_data["name"],
                    information=sub_data["info"],
                    manufacturer_type=sub_data["type"],
                    parent=main_manufacturer,
                    country_code=sub_data["country_code"],
                )
                manufacturers.append(sub_manufacturer)

        # Lägg till ytterligare huvudtillverkare om det behövs
        for manufacturer_data in additional_manufacturers:
            if len(manufacturers) >= count:
                break

            manufacturer = Manufacturer.objects.create(
                name=manufacturer_data["name"],
                information=manufacturer_data["info"],
                manufacturer_type="TILLVERKARE",
                country_code=manufacturer_data["country_code"],
            )
            manufacturers.append(manufacturer)

        return manufacturers

    def create_contacts(self, count, quiet=False):
        """Skapa kontakter"""
        countries = [
            ("Sverige", "SE"),
            ("Finland", "FI"),
            ("Norge", "NO"),
            ("Danmark", "DK"),
            ("Tyskland", "DE"),
            ("USA", "US"),
            ("Kanada", "CA"),
            ("Storbritannien", "GB"),
            ("Polen", "PL"),
            ("Tjeckien", "CZ"),
            ("Österrike", "AT"),
            ("Schweiz", "CH"),
        ]

        first_names = [
            "Erik",
            "Anna",
            "Lars",
            "Maria",
            "Johan",
            "Karin",
            "Anders",
            "Eva",
            "Mikael",
            "Sofia",
        ]
        last_names = [
            "Andersson",
            "Johansson",
            "Karlsson",
            "Nilsson",
            "Eriksson",
            "Larsson",
            "Olsson",
            "Persson",
            "Svensson",
            "Gustafsson",
        ]

        contacts = []
        for i in range(count):
            country, country_code = random.choice(countries)
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"

            contact = Contact.objects.create(
                name=name,
                email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                phone=f"+46{random.randint(700000000, 799999999)}",
                alias=f"{first_name.lower()}_{last_name.lower()}",
                street=f"Testgatan {random.randint(1, 100)}",
                postal_code=f"{random.randint(10000, 99999)}",
                city=random.choice(
                    [
                        "Stockholm",
                        "Göteborg",
                        "Malmö",
                        "Uppsala",
                        "Västerås",
                        "Örebro",
                        "Linköping",
                        "Helsingborg",
                    ]
                ),
                country=country,
                country_code=country_code,
                comment=f"Testkontakt {i+1}. {random.choice(['Privatperson', 'Företag', 'Auktionshus'])}",
                is_naj_member=random.choice([True, False]),
            )
            contacts.append(contact)

        return contacts

    def create_platforms(self, quiet=False):
        """Skapa plattformar"""
        platforms_data = [
            ("Tradera", "bg-primary"),
            ("Blocket", "bg-success"),
            ("Facebook Marketplace", "bg-info"),
            ("Ebay", "bg-warning"),
            ("Auktion", "bg-danger"),
            ("Privat", "bg-secondary"),
            ("Butik", "bg-dark"),
            ("Instagram", "bg-primary bg-opacity-75"),
        ]

        platforms = []
        for name, color in platforms_data:
            platform = Platform.objects.create(name=name, color_class=color)
            platforms.append(platform)

        return platforms

    def create_axes(self, manufacturers, count, quiet=False):
        """Skapa yxor"""
        axe_models = [
            "Slöjdyxa",
            "Huggyxa",
            "Fällyxa",
            "Klyvyxa",
            "Timmerbila",
            "Handyxa",
            "Tapphålsyxa",
            "Tväryxa",
            "Tjäckla",
            "Snickaryxa",
        ]

        comments = [
            "Fin kvalitetsyxa",
            "Handgjord",
            "Vintage",
            "Ny i förpackning",
            "Lite använd",
            "Bra skick",
            "Kollektion",
            "Sällsynt modell",
            "Begagnad men bra",
            "Perfekt för slöjd",
            "Professionell kvalitet",
            "Gammal svensk yxa",
            "Traditionell tillverkning",
            "Kollektionsföremål",
        ]

        axes = []
        for i in range(count):
            manufacturer = random.choice(manufacturers)
            model = random.choice(axe_models)
            comment = random.choice(comments) if random.random() > 0.3 else ""
            status = random.choice(["KÖPT", "MOTTAGEN"])

            axe = Axe.objects.create(
                manufacturer=manufacturer, model=model, comment=comment, status=status
            )
            axes.append(axe)

        return axes

    def create_transactions(self, axes, contacts, platforms, quiet=False):
        """Skapa transaktioner"""
        for axe in axes:
            # Skapa 1-2 transaktioner per yxa (ett köp och eventuellt ett sälj)
            # 30% chans att ha en andra transaktion (sälj) - fler yxor behålls
            has_second_transaction = random.random() > 0.7
            num_transactions = 2 if has_second_transaction else 1

            # Generera datum i kronologisk ordning (nyaste först)
            base_days_ago = random.randint(30, 730)  # Mellan 1 månad och 2 år sedan
            transaction_dates = []

            for i in range(num_transactions):
                # Varje transaktion är minst 1 dag tidigare än föregående
                days_ago = base_days_ago + (i * random.randint(1, 30))
                transaction_date = timezone.now().date() - timedelta(days=days_ago)
                transaction_dates.append(transaction_date)

            # Sortera datum i kronologisk ordning (äldsta först)
            transaction_dates.sort()

            for i, transaction_date in enumerate(transaction_dates):
                # Första transaktionen är alltid ett köp
                if i == 0:
                    transaction_type = "KÖP"
                    price = Decimal(random.randint(500, 5000))  # 500-5000 kr
                else:
                    # Andra transaktionen är alltid ett sälj
                    transaction_type = "SÄLJ"
                    price = Decimal(random.randint(800, 8000))  # Sälj för mer

                shipping_cost = Decimal(random.randint(0, 200))

                Transaction.objects.create(
                    axe=axe,
                    contact=random.choice(contacts) if random.random() > 0.2 else None,
                    platform=(
                        random.choice(platforms) if random.random() > 0.1 else None
                    ),
                    transaction_date=transaction_date,
                    type=transaction_type,
                    price=price,
                    shipping_cost=shipping_cost,
                    comment=(
                        random.choice(
                            [
                                "Snabb leverans",
                                "Bra förpackning",
                                "Som beskrivet",
                                "Kollektion",
                                "Auktion",
                                "Direktköp",
                                "Förhandling",
                            ]
                        )
                        if random.random() > 0.5
                        else ""
                    ),
                )

    def create_measurements(self, axes, quiet=False):
        """Skapa mått för yxor"""
        measurement_types = MeasurementType.objects.all()

        for axe in axes:
            # 80% chans att ha mått
            if random.random() > 0.2:
                # Välj måttmall (70% standardyxa, 30% detaljerad yxa)
                if random.random() > 0.3:
                    # Standardyxa: Vikt, Skaftlängd, Eggbredd, Nacke till egg
                    selected_types = measurement_types.filter(
                        name__in=["Vikt", "Skaftlängd", "Eggbredd", "Nacke till egg"]
                    )
                else:
                    # Detaljerad yxa: Vikt, Skaftlängd, Eggbredd, Huvudvikt, Ögats bredd, Ögats höjd
                    selected_types = measurement_types.filter(
                        name__in=[
                            "Vikt",
                            "Skaftlängd",
                            "Eggbredd",
                            "Huvudvikt",
                            "Ögats bredd",
                            "Ögats höjd",
                        ]
                    )

                for mtype in selected_types:
                    # Generera realistiska värden baserat på måtttyp
                    if mtype.name == "Vikt":
                        value = Decimal(random.randint(800, 2500))
                    elif mtype.name == "Huvudvikt":
                        value = Decimal(random.randint(600, 1800))
                    elif mtype.name == "Skaftlängd":
                        value = Decimal(random.randint(300, 600))
                    elif mtype.name == "Eggbredd":
                        value = Decimal(random.randint(80, 150))
                    elif mtype.name == "Nacke till egg":
                        value = Decimal(random.randint(120, 250))
                    elif mtype.name == "Ögats bredd":
                        value = Decimal(random.randint(25, 40))
                    elif mtype.name == "Ögats höjd":
                        value = Decimal(random.randint(35, 55))
                    else:
                        value = Decimal(random.randint(50, 300))

                    Measurement.objects.create(
                        axe=axe, name=mtype.name, value=value, unit=mtype.unit
                    )

    def create_demo_image(
        self,
        width=800,
        height=600,
        text="Demo Bild",
        bg_color=(240, 240, 240),
        text_color=(100, 100, 100),
    ):
        """Skapa en demo-bild med text"""
        # Skapa en ny bild
        image = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(image)

        # Försök använda en standardfont, annars använd default
        try:
            # Försök hitta en font som fungerar på Windows
            font_size = min(width, height) // 10
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()

        # Beräkna textposition för centrering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Rita texten
        draw.text((x, y), text, fill=text_color, font=font)

        # Konvertera till bytes
        img_io = io.BytesIO()
        image.save(img_io, format="JPEG", quality=85)
        img_io.seek(0)

        return img_io

    def create_manufacturer_images(self, manufacturers, quiet=False):
        """Skapa tillverkarbilder"""
        for manufacturer in manufacturers:
            # 40% chans att ha bilder
            if random.random() > 0.6:
                num_images = random.randint(1, 3)

                for i in range(num_images):
                    # Skapa demo-bild
                    img_io = self.create_demo_image(
                        width=600,
                        height=400,
                        text=f"{manufacturer.name}\nStämpel {i+1}",
                        bg_color=(
                            random.randint(200, 255),
                            random.randint(200, 255),
                            random.randint(200, 255),
                        ),
                        text_color=(
                            random.randint(50, 150),
                            random.randint(50, 150),
                            random.randint(50, 150),
                        ),
                    )

                    # Skapa filnamn enligt namnstandard: Tillverkarnamn_Stämpel.jpg
                    image_letter = self.get_image_letter(i)
                    safe_name = (
                        manufacturer.name.replace(" ", "_")
                        .replace(",", "")
                        .replace(".", "")
                    )
                    filename = f"{safe_name}_{image_letter}.jpg"

                    # Skapa ManufacturerImage
                    manufacturer_image = ManufacturerImage.objects.create(
                        manufacturer=manufacturer,
                        image_type="STAMP" if i == 0 else "OTHER",
                        caption=f"Stämpel {i+1} från {manufacturer.name}",
                        description=f"Demo-bild av stämpel från {manufacturer.name}",
                        order=i,
                    )

                    # Spara bilden
                    manufacturer_image.image.save(
                        filename, ContentFile(img_io.getvalue()), save=True
                    )

    def create_manufacturer_links(self, manufacturers, quiet=False):
        """Skapa tillverkarlänkar"""
        link_types = ["WEBSITE", "CATALOG", "VIDEO", "ARTICLE", "DOCUMENT", "OTHER"]

        for manufacturer in manufacturers:
            # 60% chans att ha länkar
            if random.random() > 0.4:
                num_links = random.randint(1, 3)

                for i in range(num_links):
                    link_type = random.choice(link_types)
                    title = f"{link_type.title()} för {manufacturer.name}"
                    url = f"https://example.com/{manufacturer.name.lower().replace(' ', '-')}/{i+1}"
                    description = f"Länk till {title.lower()}"

                    ManufacturerLink.objects.create(
                        manufacturer=manufacturer,
                        title=title,
                        url=url,
                        link_type=link_type,
                        description=description,
                        is_active=random.choice(
                            [True, True, True, False]
                        ),  # 75% chans att vara aktiv
                        order=i,
                    )

    def get_image_letter(self, order):
        """Konvertera order (0,1,2,3...) till bokstav (a,b,c,d...)"""
        return chr(97 + order)  # 97 = 'a' i ASCII

    def create_axe_images(self, axes, quiet=False):
        """Skapa yxbilder"""
        for axe in axes:
            # 70% chans att ha bilder
            if random.random() > 0.3:
                num_images = random.randint(1, 4)

                for i in range(num_images):
                    # Skapa demo-bild med yxinformation
                    img_io = self.create_demo_image(
                        width=800,
                        height=600,
                        text=f"Yxa #{axe.display_id}\n{axe.manufacturer.name}\n{axe.model}\nBild {i+1}",
                        bg_color=(
                            random.randint(180, 220),
                            random.randint(180, 220),
                            random.randint(180, 220),
                        ),
                        text_color=(
                            random.randint(30, 100),
                            random.randint(30, 100),
                            random.randint(30, 100),
                        ),
                    )

                    # Skapa filnamn enligt namnstandard: YXIDa/b/c/d.jpg
                    image_letter = self.get_image_letter(i)
                    filename = f"{axe.display_id}{image_letter}.jpg"

                    # Skapa AxeImage
                    axe_image = AxeImage.objects.create(
                        axe=axe,
                        description=f"Bild {i+1} av {axe.model} från {axe.manufacturer.name}",
                        order=i,
                    )

                    # Spara bilden
                    axe_image.image.save(
                        filename, ContentFile(img_io.getvalue()), save=True
                    )

    def create_settings(self):
        """Skapa standardinställningar"""
        Settings.objects.get_or_create(
            id=1,
            defaults={
                "show_contacts_public": False,
                "show_prices_public": True,
                "show_platforms_public": True,
                "show_only_received_axes_public": False,
                "default_axes_rows_public": "20",
                "default_transactions_rows_public": "15",
                "default_manufacturers_rows_public": "25",
                "default_axes_rows_private": "50",
                "default_transactions_rows_private": "30",
                "default_manufacturers_rows_private": "50",
                "site_title": "AxeCollection Demo",
                "site_description": "Demo-version av AxeCollection - Yxsamlingshantering",
            },
        )

    def create_demo_user(self, quiet=False):
        """Skapa demo-användare"""
        # Skapa demo-användare om den inte finns
        demo_user, created = User.objects.get_or_create(
            username="demo",
            defaults={
                "email": "demo@axecollection.se",
                "first_name": "Demo",
                "last_name": "Användare",
                "is_staff": True,
                "is_active": True,
            },
        )

        if created:
            # Sätt lösenord för demo-användare
            demo_user.set_password("demo123")
            demo_user.save()
            if not quiet:
                self.stdout.write("Demo-användare skapad: demo/demo123")
        else:
            # Uppdatera lösenord om användaren redan finns
            demo_user.set_password("demo123")
            demo_user.save()
            if not quiet:
                self.stdout.write("Demo-användare uppdaterad: demo/demo123")

    def create_specific_axes_with_real_images(
        self, manufacturers, no_stamp_images=False, quiet=False
    ):
        """Skapa specifika yxor med riktiga bilder från testdatabilder-mappen"""
        if not quiet:
            self.stdout.write("Skapar specifika yxor med riktiga bilder...")

        # Hitta tillverkarna vi behöver
        johan_jonsson = None
        johan_skog = None
        hults_bruk = None

        for manufacturer in manufacturers:
            if manufacturer.name == "Johan Jonsson":
                johan_jonsson = manufacturer
            elif manufacturer.name == "Johan Skog":
                johan_skog = manufacturer
            elif manufacturer.name == "Hults bruk":
                hults_bruk = manufacturer

        # Skapa Hjärtumssmedjan om den inte finns
        if not johan_jonsson or not johan_skog:
            hjärtumssmedjan = None
            for manufacturer in manufacturers:
                if manufacturer.name == "Hjärtumssmedjan":
                    hjärtumssmedjan = manufacturer
                    break

            if not hjärtumssmedjan:
                hjärtumssmedjan = Manufacturer.objects.create(
                    name="Hjärtumssmedjan",
                    information="Traditionell smedja i Hjärtum, grundad 1850. Känd för handgjorda kvalitetsyxor.",
                    manufacturer_type="TILLVERKARE",
                    country_code="SE",
                )

            # Skapa Johan Jonsson om den inte finns
            if not johan_jonsson:
                johan_jonsson = Manufacturer.objects.create(
                    name="Johan Jonsson",
                    information="Mästersmed vid Hjärtumssmedjan. Specialiserar sig på slöjdyxor och huggyxor.",
                    manufacturer_type="SMED",
                    parent=hjärtumssmedjan,
                    country_code="SE",
                )

            # Skapa Johan Skog om den inte finns
            if not johan_skog:
                johan_skog = Manufacturer.objects.create(
                    name="Johan Skog",
                    information="Erfaren smed vid Hjärtumssmedjan. Känd för sina fällyxor och timmerbilor.",
                    manufacturer_type="SMED",
                    parent=hjärtumssmedjan,
                    country_code="SE",
                )

        # Skapa Hults bruk om den inte finns
        if not hults_bruk:
            hults_bruk = Manufacturer.objects.create(
                name="Hults bruk",
                information="Bruk grundat 1697. Traditionell tillverkning av handyxor.",
                manufacturer_type="TILLVERKARE",
                country_code="SE",
            )

        # Definiera specifika yxor med bilder (utan stämplar för ren start)
        specific_axes = [
            {
                "display_id": "33",
                "manufacturer": johan_jonsson,
                "model": "Hjärtumyxa",
                "comment": "Handgjord kvalitetsyxa från Johan Jonsson",
                "images": ["33a.jpg", "33b.jpg"],
            },
            {
                "display_id": "166",
                "manufacturer": johan_jonsson,
                "model": "Klyvyxa",
                "comment": "Robust klyvyxa från Johan Jonsson",
                "images": ["166a.jpg", "166c.jpg"],
            },
            {
                "display_id": "152",
                "manufacturer": hults_bruk,
                "model": "Täljbila",
                "comment": "Traditionell täljbila från Hults bruk",
                "images": ["152c.jpg", "152d.jpg", "152e.jpg"],
            },
            {
                "display_id": "20",
                "manufacturer": johan_skog,
                "model": "Hjärtumyxa",
                "comment": "Handgjord yxa från Johan Skog",
                "images": ["20a.jpg", "20b.jpg"],
            },
        ]

        # Skapa yxorna och kopiera bilderna
        created_axes = []
        for axe_data in specific_axes:
            # Skapa yxan
            # Undvik dubbletter: om en yxa med samma kombination redan finns, återanvänd
            axe = Axe.objects.create(
                manufacturer=axe_data["manufacturer"],
                model=axe_data["model"],
                comment=axe_data["comment"],
                status="MOTTAGEN",
            )
            created_axes.append(axe)

            if not quiet:
                self.stdout.write(
                    f"  Skapade yxa {axe.display_id} ({axe.model}) från {axe.manufacturer.name}"
                )

            # Kopiera och koppla bilderna
            axe_images = []
            for i, image_filename in enumerate(axe_data["images"]):
                source_path = os.path.join("testdatabilder", image_filename)
                if os.path.exists(source_path):
                    # Skapa AxeImage
                    axe_image = AxeImage.objects.create(
                        axe=axe,
                        description=f"Bild {i+1} av {axe.model} från {axe.manufacturer.name}",
                        order=i,
                    )
                    axe_images.append(axe_image)

                    # Kopiera bilden till media-mappen
                    with open(source_path, "rb") as f:
                        axe_image.image.save(
                            image_filename, ContentFile(f.read()), save=True
                        )

                    if not quiet:
                        self.stdout.write(
                            f"    Kopierade {image_filename} till yxa {axe.display_id} (AxeImage ID: {axe_image.id})"
                        )
                else:
                    if not quiet:
                        self.stdout.write(
                            f"    VARNING: Bildfil {image_filename} hittades inte!"
                        )

            if not quiet:
                self.stdout.write(
                    f"    Skapade {len(axe_images)} bilder för yxa {axe.display_id}"
                )

        if not quiet:
            self.stdout.write(f"Skapade {len(created_axes)} yxor med riktiga bilder")
            self.stdout.write("Yxor skapade:")
            for axe in created_axes:
                self.stdout.write(
                    f"  - Yxa {axe.display_id}: {axe.model} från {axe.manufacturer.name}"
                )
                axe_images = AxeImage.objects.filter(axe=axe).order_by("order")
                for axe_image in axe_images:
                    self.stdout.write(
                        f"    * Bild {axe_image.order+1}: {axe_image.image.name} (ID: {axe_image.id})"
                    )

        # Skapa stämpelmarkeringar med manuella koordinater om det inte är inaktiverat
        if not no_stamp_images:
            if not quiet:
                self.stdout.write(
                    "\nSkapar stämpelmarkeringar med manuella koordinater..."
                )
            # Återvänd listan så den kan användas av anropare för att säkra kopplingar
            pass

        return created_axes

    def create_specific_stamps(self, manufacturers, quiet=False):
        """Skapa specifika stämplar för testdata"""
        if not quiet:
            self.stdout.write("Skapar specifika stämplar...")

        # Hitta tillverkarna vi behöver
        johan_jonsson = None
        johan_skog = None
        hults_bruk = None

        for manufacturer in manufacturers:
            if manufacturer.name == "Johan Jonsson":
                johan_jonsson = manufacturer
            elif manufacturer.name == "Johan Skog":
                johan_skog = manufacturer
            elif manufacturer.name == "Hults bruk":
                hults_bruk = manufacturer

        # Skapa Hjärtumssmedjan om den inte finns
        if not johan_jonsson or not johan_skog:
            hjärtumssmedjan = None
            for manufacturer in manufacturers:
                if manufacturer.name == "Hjärtumssmedjan":
                    hjärtumssmedjan = manufacturer
                    break

            if not hjärtumssmedjan:
                hjärtumssmedjan = Manufacturer.objects.create(
                    name="Hjärtumssmedjan",
                    information="Traditionell smedja i Hjärtum, grundad 1850. Känd för handgjorda kvalitetsyxor.",
                    manufacturer_type="TILLVERKARE",
                    country_code="SE",
                )

            # Skapa Johan Jonsson om den inte finns
            if not johan_jonsson:
                johan_jonsson = Manufacturer.objects.create(
                    name="Johan Jonsson",
                    information="Mästersmed vid Hjärtumssmedjan. Specialiserar sig på slöjdyxor och huggyxor.",
                    manufacturer_type="SMED",
                    parent=hjärtumssmedjan,
                    country_code="SE",
                )

            # Skapa Johan Skog om den inte finns
            if not johan_skog:
                johan_skog = Manufacturer.objects.create(
                    name="Johan Skog",
                    information="Erfaren smed vid Hjärtumssmedjan. Känd för sina fällyxor och timmerbilor.",
                    manufacturer_type="SMED",
                    parent=hjärtumssmedjan,
                    country_code="SE",
                )

        # Skapa Hults bruk om den inte finns
        if not hults_bruk:
            hults_bruk = Manufacturer.objects.create(
                name="Hults bruk",
                information="Bruk grundat 1697. Traditionell tillverkning av handyxor.",
                manufacturer_type="TILLVERKARE",
                country_code="SE",
            )

        # Skapa stämplar
        stamps_data = [
            {
                "name": "J.JONSSON",
                "manufacturer": johan_jonsson,
                "stamp_type": "text",
                "status": "known",
                "source_category": "own_collection",
                "description": "Stämpel från Johan Jonsson vid Hjärtumssmedjan",
            },
            {
                "name": "J.SKOG HJÄRTUM",
                "manufacturer": johan_skog,
                "stamp_type": "text",
                "status": "known",
                "source_category": "own_collection",
                "description": "Stämpel från Johan Skog vid Hjärtumssmedjan",
            },
            {
                "name": "S",
                "manufacturer": johan_skog,
                "stamp_type": "symbol",
                "status": "known",
                "source_category": "internet",
                "description": "Symbolstämpel från Johan Skog",
            },
            {
                "name": "HM",
                "manufacturer": hults_bruk,
                "stamp_type": "text",
                "status": "known",
                "source_category": "internet",
                "year_from": 1884,
                "year_to": 1900,
                "source_reference": "Hults bruks stämpelnyckel",
                "description": "Stämpel från Hults bruk 1884-1900",
            },
        ]

        created_stamps = []
        for stamp_data in stamps_data:
            if stamp_data["manufacturer"]:
                stamp = Stamp.objects.create(
                    name=stamp_data["name"],
                    manufacturer=stamp_data["manufacturer"],
                    stamp_type=stamp_data["stamp_type"],
                    status=stamp_data["status"],
                    source_category=stamp_data["source_category"],
                    description=stamp_data["description"],
                    year_from=stamp_data.get("year_from"),
                    year_to=stamp_data.get("year_to"),
                    source_reference=stamp_data.get("source_reference"),
                )
                created_stamps.append(stamp)
                if not quiet:
                    self.stdout.write(
                        f"  Skapade stämpel: {stamp.name} för {stamp.manufacturer.name}"
                    )
            else:
                if not quiet:
                    self.stdout.write(
                        f"  VARNING: Tillverkare för stämpel {stamp_data['name']} hittades inte!"
                    )

        if not quiet:
            self.stdout.write(f"Skapade {len(created_stamps)} stämplar")

    def create_axe_stamp_connections(self):
        """Koppla stämplar till yxor för testdata med realistiska positioner"""
        self.stdout.write("Kopplar stämplar till yxor...")

        # Hämta alla stämplar och yxor
        stamps = Stamp.objects.all()
        axes = Axe.objects.all()

        if not stamps.exists():
            self.stdout.write("  VARNING: Inga stämplar att koppla!")
            return

        if not axes.exists():
            self.stdout.write("  VARNING: Inga yxor att koppla!")
            return

        # Hitta de specifika yxorna med riktiga bilder
        specific_axes = {}
        for axe in axes:
            if axe.display_id in ["33", "166", "152", "20"]:
                specific_axes[axe.display_id] = axe
                self.stdout.write(f"  Hittade yxa {axe.display_id} (ID {axe.id})")

        # Om vi inte hittade de specifika yxorna, använd de första 4 yxorna
        if not specific_axes:
            self.stdout.write("  Hittade inte specifika yxor, använder första 4 yxorna")
            first_axes = list(axes.order_by("id")[:4])
            if len(first_axes) >= 4:
                specific_axes = {
                    "33": first_axes[0],
                    "166": first_axes[1],
                    "152": first_axes[2],
                    "20": first_axes[3],
                }
                for display_id, axe in specific_axes.items():
                    self.stdout.write(
                        f"  Mappade yxa {axe.display_id} (ID {axe.id}) till display_id {display_id}"
                    )

        # Definiera realistiska kopplingar baserat på faktiska data
        realistic_connections = [
            # Yxa 33 (Hjärtumyxa från Johan Jonsson)
            {
                "axe_display_id": "33",
                "stamp_name": "J.JONSSON",
                "position": "Vid nacken",
                "uncertainty_level": "certain",
            },
            # Yxa 166 (Klyvyxa från Johan Jonsson)
            {
                "axe_display_id": "166",
                "stamp_name": "J.JONSSON",
                "position": "Vid nacken",
                "uncertainty_level": "certain",
            },
            # Yxa 152 (Täljbila från Hults bruk)
            {
                "axe_display_id": "152",
                "stamp_name": "HM",
                "position": "Vid nacken",
                "uncertainty_level": "certain",
            },
            # Yxa 20 (Hjärtumyxa från Johan Skog)
            {
                "axe_display_id": "20",
                "stamp_name": "J.SKOG HJÄRTUM",
                "position": "Mitt på kinden",
                "uncertainty_level": "certain",
            },
            {
                "axe_display_id": "20",
                "stamp_name": "S",
                "position": "På bladet",
                "uncertainty_level": "certain",
            },
        ]

        # Skapa kopplingarna
        created_connections = []
        for connection_data in realistic_connections:
            try:
                axe = specific_axes.get(connection_data["axe_display_id"])
                if not axe:
                    self.stdout.write(
                        f"  VARNING: Yxa {connection_data['axe_display_id']} hittades inte!"
                    )
                    continue

                stamp = Stamp.objects.get(name=connection_data["stamp_name"])

                axe_stamp = AxeStamp.objects.create(
                    axe=axe,
                    stamp=stamp,
                    position=connection_data["position"],
                    uncertainty_level=connection_data["uncertainty_level"],
                    comment=f"Stämpel från {stamp.manufacturer.name} på {axe.model}",
                )
                created_connections.append(axe_stamp)
                self.stdout.write(
                    f"  Kopplade {axe_stamp.stamp.name} till yxa {axe_stamp.axe.display_id} ({connection_data['position']})"
                )

            except Stamp.DoesNotExist as e:
                self.stdout.write(
                    f"  VARNING: Kunde inte koppla {connection_data['stamp_name']} till yxa {connection_data['axe_display_id']}: {e}"
                )

        # Lägg till slumpmässiga kopplingar för andra yxor
        specific_axe_ids = [axe.id for axe in specific_axes.values()]
        other_axes = axes.exclude(id__in=specific_axe_ids)
        for axe in other_axes:
            # Hitta stämplar som matchar yxans tillverkare
            matching_stamps = stamps.filter(manufacturer=axe.manufacturer)

            if matching_stamps.exists():
                # Välj slumpmässigt 1-2 stämplar för denna yxa
                num_stamps = random.randint(1, min(2, matching_stamps.count()))
                selected_stamps = random.sample(list(matching_stamps), num_stamps)

                for stamp in selected_stamps:
                    # Generera realistiska kommentarer och positioner
                    positions = [
                        "På bladet - vänstra sidan",
                        "På bladet - högra sidan",
                        "På nacken",
                        "På ögat",
                        "På skaftet",
                        "På eggen",
                        "På ryggen",
                        "Vid nacken",
                        "Mitt på kinden",
                    ]

                    uncertainty_levels = ["certain", "uncertain", "tentative"]
                    weights = [0.7, 0.2, 0.1]  # 70% säkra, 20% osäkra, 10% preliminära

                    axe_stamp = AxeStamp.objects.create(
                        axe=axe,
                        stamp=stamp,
                        position=random.choice(positions),
                        uncertainty_level=random.choices(
                            uncertainty_levels, weights=weights
                        )[0],
                        comment=f"Stämpel från {stamp.manufacturer.name} på {axe.model}",
                    )
                    created_connections.append(axe_stamp)
                    self.stdout.write(
                        f"  Kopplade {axe_stamp.stamp.name} till yxa {axe_stamp.axe.display_id}"
                    )

        self.stdout.write(f"Skapade {len(created_connections)} stämpelkopplingar")

    def convert_existing_axe_stamps_to_stamp_images(self):
        """Konvertera befintliga AxeStamp-objekt till StampImage-objekt med koordinater"""
        self.stdout.write(
            "Konverterar befintliga AxeStamp-markeringar till StampImage med koordinater..."
        )

        # Rensa gamla StampImage-objekt som skapats av tidigare körningar
        old_stamp_images = StampImage.objects.filter(
            image_type="axe_mark", comment__startswith="Genererad från AxeStamp"
        )
        if old_stamp_images.exists():
            deleted_count = old_stamp_images.count()
            old_stamp_images.delete()
            self.stdout.write(
                f"Rensade {deleted_count} gamla StampImage-objekt från tidigare körningar"
            )

        # Hämta alla AxeStamp-objekt
        axe_stamps = AxeStamp.objects.all()

        created_count = 0
        for axe_stamp in axe_stamps:
            # Hitta alla bilder för yxan
            axe_images = AxeImage.objects.filter(axe=axe_stamp.axe).order_by("order")
            if not axe_images.exists():
                self.stdout.write(
                    f"  Ingen bild hittad för yxa {axe_stamp.axe.display_id}"
                )
                continue

            # Kontrollera om StampImage redan finns för denna kombination
            existing_stamp_images = StampImage.objects.filter(
                axe_image__axe=axe_stamp.axe,
                stamp=axe_stamp.stamp,
                image_type="axe_mark",
            )

            if existing_stamp_images.exists():
                self.stdout.write(
                    f"  StampImage redan finns för {axe_stamp.stamp.name} på yxa {axe_stamp.axe.display_id}, hoppar över"
                )
                continue

            # Skapa StampImage för varje bild
            for axe_image in axe_images:
                # Använd manuella koordinater om tillgängliga, annars generera automatiskt
                x_coord, y_coord, width, height = self._get_manual_coordinates(
                    axe_stamp.axe.display_id, axe_stamp.stamp.name
                )

                # Skapa demo-bild för StampImage
                demo_image = self.create_demo_image()

                # Skapa StampImage
                stamp_image = StampImage.objects.create(
                    axe_image=axe_image,
                    stamp=axe_stamp.stamp,
                    image_type="axe_mark",
                    x_coordinate=Decimal(str(x_coord)),
                    y_coordinate=Decimal(str(y_coord)),
                    width=Decimal(str(width)),
                    height=Decimal(str(height)),
                    position=axe_stamp.position,
                    uncertainty_level=axe_stamp.uncertainty_level,
                    comment=f"Genererad från AxeStamp ID {axe_stamp.id}",
                    show_full_image=False,
                    is_primary=False,
                )

                # Spara demo-bilden
                stamp_image.image.save(
                    f"stamp_demo_{stamp_image.id}.jpg", demo_image, save=True
                )

                self.stdout.write(
                    f"  Skapade StampImage för {axe_stamp.stamp.name} på yxa {axe_stamp.axe.display_id} vid ({x_coord}%, {y_coord}%)"
                )
                created_count += 1

        self.stdout.write(
            f"Skapade {created_count} StampImage-objekt från befintliga markeringar"
        )

    def _get_manual_coordinates(self, axe_display_id, stamp_name):
        """Hämta manuellt markerade koordinater för specifika yxor och stämplar"""
        from decimal import Decimal

        # Manuellt markerade koordinater från användaren (extraherade från databasen)
        manual_coordinates = {
            # Yxa 51 (display_id 51) - Hjärtumyxa från Johan Jonsson
            51: {"J.JONSSON": {"x": 33.0, "y": 40.0, "width": 27.0, "height": 14.0}},
            # Yxa 52 (display_id 52) - Klyvyxa från Johan Jonsson
            52: {
                "J.JONSSON": {
                    "x": 40.0,
                    "y": 17.0,
                    "width": 9.0,
                    "height": 3.0,
                },  # Bild 1
                "J.JONSSON_2": {
                    "x": 37.0,
                    "y": 19.0,
                    "width": 18.0,
                    "height": 7.0,
                },  # Bild 2
            },
            # Yxa 53 (display_id 53) - Täljbila från Hults bruk
            53: {"HM": {"x": 43.0, "y": 50.0, "width": 18.0, "height": 12.0}},
            # Yxa 54 (display_id 54) - Hjärtumyxa från Johan Skog
            54: {
                "J.SKOG HJÄRTUM": {"x": 54.0, "y": 30.0, "width": 19.0, "height": 12.0}
            },
        }

        # Kontrollera om vi har manuella koordinater för denna kombination
        if (
            axe_display_id in manual_coordinates
            and stamp_name in manual_coordinates[axe_display_id]
        ):
            coords = manual_coordinates[axe_display_id][stamp_name]
            return coords["x"], coords["y"], coords["width"], coords["height"]

        # Hantera specialfall för J.JONSSON_2
        if stamp_name == "J.JONSSON_2" and axe_display_id in manual_coordinates:
            if "J.JONSSON_2" in manual_coordinates[axe_display_id]:
                coords = manual_coordinates[axe_display_id]["J.JONSSON_2"]
                return coords["x"], coords["y"], coords["width"], coords["height"]

        # Fallback till automatisk generering om inga manuella koordinater finns
        return self._generate_coordinates_for_position("Vid nacken", axe_display_id)

    def _create_stamp_images_with_manual_coordinates(self, axes, quiet=False):
        """Skapa StampImage-objekt med manuella koordinater för specifika yxor"""
        from axes.models import Stamp, AxeStamp, StampImage
        from decimal import Decimal

        # Definiera vilka stämplar som ska kopplas till vilka yxor
        stamp_assignments = {
            51: [("J.JONSSON", 1)],  # Yxa 51: J.JONSSON på bild 2 (index 1)
            52: [
                ("J.JONSSON", 0),
                ("J.JONSSON_2", 1),
            ],  # Yxa 52: J.JONSSON på bild 1, J.JONSSON_2 på bild 2
            53: [("HM", 1)],  # Yxa 53: HM på bild 2 (index 1)
            54: [("J.SKOG HJÄRTUM", 1)],  # Yxa 54: J.SKOG HJÄRTUM på bild 2 (index 1)
        }

        created_count = 0
        for axe in axes:
            axe_display_id = axe.id  # Använd faktiska ID:n från databasen
            if axe_display_id in stamp_assignments:
                if not quiet:
                    self.stdout.write(
                        f"  Bearbetar yxa {axe.display_id} ({axe.model})..."
                    )

                # Hämta alla bilder för denna yxa
                axe_images = AxeImage.objects.filter(axe=axe).order_by("order")

                for stamp_name, image_index in stamp_assignments[axe_display_id]:
                    if image_index < len(axe_images):
                        axe_image = axe_images[image_index]

                        # Hitta stämpeln (hantera specialfall för J.JONSSON_2)
                        actual_stamp_name = stamp_name
                        if stamp_name == "J.JONSSON_2":
                            actual_stamp_name = "J.JONSSON"

                        try:
                            stamp = Stamp.objects.get(name=actual_stamp_name)
                        except Stamp.DoesNotExist:
                            if not quiet:
                                self.stdout.write(
                                    f"    VARNING: Stämpel '{actual_stamp_name}' finns inte!"
                                )
                            continue

                        # Skapa AxeStamp-koppling
                        axe_stamp, created = AxeStamp.objects.get_or_create(
                            axe=axe,
                            stamp=stamp,
                            defaults={
                                "position": "Vid nacken",
                                "uncertainty_level": "certain",
                            },
                        )

                        # Hämta manuella koordinater
                        x_coord, y_coord, width, height = self._get_manual_coordinates(
                            axe_display_id, stamp_name
                        )

                        # Bestäm om denna stämpel ska vara primär
                        is_primary = False
                        if axe_display_id == 51 and stamp_name == "J.JONSSON":
                            is_primary = True

                        # Skapa StampImage med manuella koordinater
                        stamp_image = StampImage.objects.create(
                            axe_image=axe_image,
                            stamp=stamp,
                            x_coordinate=Decimal(str(x_coord)),
                            y_coordinate=Decimal(str(y_coord)),
                            width=Decimal(str(width)),
                            height=Decimal(str(height)),
                            image_type="axe_mark",
                            uncertainty_level="certain",
                            comment=f"Manuellt markerad koordinat för {stamp_name}",
                            show_full_image=False,
                            is_primary=is_primary,
                        )

                        # Skapa demo-bild för StampImage
                        demo_image = self.create_demo_image(
                            width=200,
                            height=150,
                            text=f"Stämpel: {stamp_name}",
                            bg_color=(255, 255, 200),
                            text_color=(100, 100, 100),
                        )
                        stamp_image.image.save(
                            f"stamp_manual_{stamp_image.id}.jpg", demo_image, save=True
                        )

                        if not quiet:
                            self.stdout.write(
                                f"    Skapade StampImage för {stamp_name} på bild {image_index+1} (x={x_coord}%, y={y_coord}%, w={width}%, h={height}%)"
                            )
                        created_count += 1
                    else:
                        if not quiet:
                            self.stdout.write(
                                f"    VARNING: Bildindex {image_index} finns inte för yxa {axe.display_id}"
                            )

        if not quiet:
            self.stdout.write(
                f"Skapade {created_count} StampImage-objekt med manuella koordinater"
            )

    def _generate_coordinates_for_position(self, position, axe_display_id):
        """Generera realistiska koordinater baserat på position och yxa"""
        from decimal import Decimal

        # Basera koordinater på position och yxa för variation
        base_x = (axe_display_id * 7) % 80  # 0-80% för att undvika kanter
        base_y = (axe_display_id * 11) % 70  # 0-70% för att undvika kanter

        if "nacken" in position.lower():
            x_coord = 15.0 + (base_x * 0.3)
            y_coord = 5.0 + (base_y * 0.2)
            width = 8.0 + (base_x * 0.1)
            height = 12.0 + (base_y * 0.1)
        elif "ryggen" in position.lower():
            x_coord = 25.0 + (base_x * 0.4)
            y_coord = 20.0 + (base_y * 0.3)
            width = 10.0 + (base_x * 0.15)
            height = 15.0 + (base_y * 0.15)
        elif "bladet" in position.lower():
            x_coord = 35.0 + (base_x * 0.5)
            y_coord = 30.0 + (base_y * 0.4)
            width = 12.0 + (base_x * 0.2)
            height = 18.0 + (base_y * 0.2)
        elif "skaftet" in position.lower():
            x_coord = 45.0 + (base_x * 0.6)
            y_coord = 40.0 + (base_y * 0.5)
            width = 14.0 + (base_x * 0.25)
            height = 20.0 + (base_y * 0.25)
        elif "kinden" in position.lower():
            x_coord = 55.0 + (base_x * 0.7)
            y_coord = 25.0 + (base_y * 0.35)
            width = 16.0 + (base_x * 0.3)
            height = 22.0 + (base_y * 0.3)
        else:
            # Standardposition
            x_coord = 30.0 + (base_x * 0.4)
            y_coord = 25.0 + (base_y * 0.3)
            width = 10.0 + (base_x * 0.15)
            height = 15.0 + (base_y * 0.15)

        # Säkerställ att koordinaterna är inom 0-100%
        x_coord = max(1.0, min(85.0, x_coord))
        y_coord = max(1.0, min(85.0, y_coord))
        width = max(5.0, min(20.0, width))
        height = max(5.0, min(25.0, height))

        # Säkerställ att rektangeln inte går utanför bilden
        if x_coord + width > 95.0:
            x_coord = 95.0 - width
        if y_coord + height > 95.0:
            y_coord = 95.0 - height

        return x_coord, y_coord, width, height
