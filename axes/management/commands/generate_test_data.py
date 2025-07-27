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

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Rensar befintlig data...")
            self.clear_data()

        self.stdout.write("Genererar testdata...")

        # Skapa måtttyper och mallar först
        self.create_measurement_types()
        self.create_measurement_templates()

        # Skapa grunddata
        manufacturers = self.create_manufacturers(options["manufacturers"])
        contacts = self.create_contacts(options["contacts"])
        platforms = self.create_platforms()

        # Skapa yxor och relaterad data
        axes = self.create_axes(manufacturers, options["axes"])
        self.create_transactions(axes, contacts, platforms)
        self.create_measurements(axes)

        # Skapa tillverkarlänkar och bilder
        self.create_manufacturer_links(manufacturers)
        self.create_manufacturer_images(manufacturers)

        # Skapa yxbilder
        self.create_axe_images(axes)

        # Skapa standardinställningar
        self.create_settings()

        # Skapa demo-användare
        self.create_demo_user()

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
        templates = [
            ("Standardyxa", "Grundläggande mått för en vanlig yxa"),
            ("Detaljerad yxa", "Utökade mått för detaljerad dokumentation"),
        ]

        for name, description in templates:
            template, created = MeasurementTemplate.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "sort_order": len(MeasurementTemplate.objects.all()),
                },
            )

            if created:
                # Lägg till måtttyper i mallen
                if name == "Standardyxa":
                    # Standardyxa: Vikt, Skaftlängd, Eggbredd, Nacke till egg
                    measurement_types = MeasurementType.objects.filter(
                        name__in=["Vikt", "Skaftlängd", "Eggbredd", "Nacke till egg"]
                    )
                else:  # Detaljerad yxa
                    # Detaljerad yxa: Vikt, Skaftlängd, Eggbredd, Huvudvikt, Ögats bredd, Ögats höjd
                    measurement_types = MeasurementType.objects.filter(
                        name__in=[
                            "Vikt",
                            "Skaftlängd",
                            "Eggbredd",
                            "Huvudvikt",
                            "Ögats bredd",
                            "Ögats höjd",
                        ]
                    )

                for i, mtype in enumerate(measurement_types):
                    MeasurementTemplateItem.objects.create(
                        template=template, measurement_type=mtype, sort_order=i
                    )

    def create_manufacturers(self, count):
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
            {"name": "Mariefors Bruk", "country_code": "FI", "info": "Finsk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på traditionella yxor."},
            {"name": "Säters yxfabrik", "country_code": "SE", "info": "Svensk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på handgjorda yxor."},
            {"name": "Jäders bruk", "country_code": "SE", "info": "Svensk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på industriella yxor."},
            {"name": "Svenska Yxfabriken AB, Kristinehamn", "country_code": "SE", "info": "Svensk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på slöjdyxor."},
            {"name": "Edsbyn Industri Aktiebolag", "country_code": "SE", "info": "Svensk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på huggyxor."},
            {"name": "Dansk Stålindustri", "country_code": "DK", "info": "Dansk tillverkare av kvalitetsyxor. Grundad 1900-talet. Specialiserar sig på moderna yxor."},
            {"name": "Mustad", "country_code": "NO", "info": "Norsk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på handgjorda yxor."},
            {"name": "Øyo", "country_code": "NO", "info": "Norsk tillverkare av kvalitetsyxor. Grundad 1800-talet. Specialiserar sig på traditionella yxor."},
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
                country_code=data["country_code"]
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
                    country_code=sub_data["country_code"]
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
                country_code=manufacturer_data["country_code"]
            )
            manufacturers.append(manufacturer)

        return manufacturers

    def create_contacts(self, count):
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

    def create_platforms(self):
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

    def create_axes(self, manufacturers, count):
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

    def create_transactions(self, axes, contacts, platforms):
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

    def create_measurements(self, axes):
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

    def create_manufacturer_images(self, manufacturers):
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

    def create_manufacturer_links(self, manufacturers):
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

    def create_axe_images(self, axes):
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

    def create_demo_user(self):
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
            self.stdout.write("Demo-användare skapad: demo/demo123")
        else:
            # Uppdatera lösenord om användaren redan finns
            demo_user.set_password("demo123")
            demo_user.save()
            self.stdout.write("Demo-användare uppdaterad: demo/demo123")
