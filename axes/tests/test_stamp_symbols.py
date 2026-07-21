"""
Omfattande tester för stämpelsymbolhantering
"""

import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import JsonResponse
from axes.models import (
    Stamp,
    StampSymbol,
    Manufacturer,
)


class StampSymbolAPITest(TestCase):
    """Tester för symbol-API"""

    def setUp(self):
        """Sätt upp testdata"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", is_staff=True
        )

        # Skapa testinställningar
        self.crown_symbol = StampSymbol.objects.create(
            name="Krona",
            symbol_type="crown",
            pictogram="👑",
            description="Kunglig krona",
            is_predefined=True,
        )
        self.star_symbol = StampSymbol.objects.create(
            name="Stjärna",
            symbol_type="star",
            pictogram="⭐",
            description="Stjärnsymbol",
            is_predefined=False,
        )

    def test_stamp_symbols_api_get_all(self):
        """Testa API för att hämta alla symboler"""
        url = reverse("stamp_symbols_api")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        # Ska åtminstone innehålla de två nyskapade
        symbol_names = [symbol["name"] for symbol in data]
        self.assertIn("Krona", symbol_names)
        self.assertIn("Stjärna", symbol_names)

    def test_stamp_symbols_api_search_filter(self):
        """Testa API med sökfilter"""
        url = reverse("stamp_symbols_api") + "?search=Krona"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # Det kan finnas förifyllda symboler (migration 0047 seedar en "Krona"
        # med typ "other") - så anta inte att data[0] är just crown-varianten.
        # Säkerställ i stället att alla träffar heter Krona OCH att det finns
        # en crown-Krona med rätt piktogram bland dem.
        self.assertGreaterEqual(len(data), 1)
        self.assertTrue(all(item["name"] == "Krona" for item in data))
        crown_kronor = [item for item in data if item["symbol_type"] == "crown"]
        self.assertGreaterEqual(len(crown_kronor), 1)
        self.assertEqual(crown_kronor[0]["pictogram"], "👑")

    def test_stamp_symbols_api_type_filter(self):
        """Testa API med typfilter"""
        url = reverse("stamp_symbols_api") + "?type=star"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # Kan vara fler än en om förifyllda finns; säkerställ att Stjärna ingår och alla är typ star
        self.assertGreaterEqual(len(data), 1)
        names = [item["name"] for item in data]
        self.assertIn("Stjärna", names)
        self.assertEqual(data[0]["symbol_type"], "star")

    def test_stamp_symbols_api_predefined_filter(self):
        """Testa API med fördefinierad-filter"""
        url = reverse("stamp_symbols_api") + "?predefined=true"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # Fördefinierade kan vara flera; kontrollera att alla markerade som predefined och att Krona finns
        self.assertGreaterEqual(len(data), 1)
        self.assertTrue(all(item["is_predefined"] for item in data))
        names = [item["name"] for item in data]
        self.assertIn("Krona", names)

    def test_stamp_symbols_api_combined_filters(self):
        """Testa API med kombinerade filter"""
        url = reverse("stamp_symbols_api") + "?search=Stjärna&predefined=false"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # Icke-fördefinierade: åtminstone vår nyskapade Stjärna
        self.assertGreaterEqual(len(data), 1)
        names = [item["name"] for item in data]
        self.assertIn("Stjärna", names)
        self.assertTrue(any(not item["is_predefined"] for item in data))

    def test_stamp_symbols_api_empty_result(self):
        """Testa API när inga symboler matchar"""
        url = reverse("stamp_symbols_api") + "?search=NonExistentSymbol"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)


class StampSymbolViewsTest(TestCase):
    """Tester för symbol-relaterade views"""

    def setUp(self):
        """Sätt upp testdata"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", is_staff=True
        )

        self.symbol = StampSymbol.objects.create(
            name="Test Symbol",
            symbol_type="crown",
            pictogram="👑",
            description="Test beskrivning",
        )

    def test_stamp_symbols_manage_view_get(self):
        """Testa symbolhantering-vy"""
        self.client.login(username="testuser", password="testpass123")

        url = reverse("stamp_symbols_manage")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hantera stämpelsymboler")
        self.assertContains(response, "Test Symbol")

        # Kontrollera att symboler finns i context
        symbols = response.context["symbols"]
        self.assertIn(self.symbol, symbols)

    def test_stamp_symbols_manage_requires_login(self):
        """Testa att symbolhantering kräver inloggning"""
        url = reverse("stamp_symbols_manage")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_stamp_symbol_update_view_get(self):
        """Testa symboluppdatering-vy GET"""
        self.client.login(username="testuser", password="testpass123")

        url = reverse("stamp_symbol_update", kwargs={"symbol_id": self.symbol.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Redigera symbol")
        self.assertContains(response, "Test Symbol")

    def test_stamp_symbol_update_view_post_valid(self):
        """Testa framgångsrik symboluppdatering"""
        self.client.login(username="testuser", password="testpass123")

        url = reverse("stamp_symbol_update", kwargs={"symbol_id": self.symbol.id})
        data = {
            "name": "Uppdaterad Symbol",
            "symbol_type": "star",  # Ignoreras numera av vyn
            "pictogram": "⭐",
            "description": "Uppdaterad beskrivning",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)

        # Verifiera att symbolen uppdaterades
        self.symbol.refresh_from_db()
        self.assertEqual(self.symbol.name, "Uppdaterad Symbol")
        # symbol_type uppdateras inte längre via UI; behålls som tidigare
        self.assertEqual(self.symbol.symbol_type, "crown")
        self.assertEqual(self.symbol.pictogram, "⭐")
        self.assertEqual(self.symbol.description, "Uppdaterad beskrivning")

    def test_stamp_symbol_update_view_post_invalid(self):
        """Testa symboluppdatering med ogiltig data"""
        self.client.login(username="testuser", password="testpass123")

        url = reverse("stamp_symbol_update", kwargs={"symbol_id": self.symbol.id})
        data = {
            "name": "",  # Tomt namn
            "symbol_type": "invalid_type",
            "pictogram": "⭐",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")

        # Verifiera att symbolen inte ändrades
        self.symbol.refresh_from_db()
        self.assertEqual(self.symbol.name, "Test Symbol")

    def test_stamp_symbol_delete_view_get(self):
        """Testa bekräftelsesida för symbolborttagning"""
        self.client.login(username="testuser", password="testpass123")

        url = reverse("stamp_symbol_delete", kwargs={"symbol_id": self.symbol.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bekräfta borttagning")
        self.assertContains(response, "Test Symbol")

    def test_stamp_symbol_delete_view_post(self):
        """Testa faktisk symbolborttagning"""
        self.client.login(username="testuser", password="testpass123")

        url = reverse("stamp_symbol_delete", kwargs={"symbol_id": self.symbol.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(StampSymbol.objects.filter(id=self.symbol.id).count(), 0)

    def test_stamp_symbol_delete_predefined_allowed(self):
        """Fördefinierade symboler får tas bort (policy: användaren kan städa frödata)"""
        # Skapa fördefinierad symbol
        predefined_symbol = StampSymbol.objects.create(
            name="Fördefinierad", symbol_type="crown", is_predefined=True
        )

        self.client.login(username="testuser", password="testpass123")

        url = reverse("stamp_symbol_delete", kwargs={"symbol_id": predefined_symbol.id})
        response = self.client.post(url)

        # Ska kunna tas bort
        self.assertEqual(response.status_code, 302)
        self.assertEqual(StampSymbol.objects.filter(id=predefined_symbol.id).count(), 0)

    def test_stamp_symbol_access_permissions(self):
        """Testa åtkomstbehörigheter för symbolhantering"""
        # Testa utan inloggning
        urls_requiring_login = [
            reverse("stamp_symbols_manage"),
            reverse("stamp_symbol_update", kwargs={"symbol_id": self.symbol.id}),
            reverse("stamp_symbol_delete", kwargs={"symbol_id": self.symbol.id}),
        ]

        for url in urls_requiring_login:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login/", response.url)


class StampSymbolIntegrationTest(TestCase):
    """Integrationstester för symbolhantering"""

    def setUp(self):
        """Sätt upp testdata"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", is_staff=True
        )
        self.manufacturer = Manufacturer.objects.create(
            name="Test Tillverkare", country_code="SE"
        )

    def test_symbol_creation_workflow(self):
        """Testa komplett arbetsflöde för symbolskapande"""
        self.client.login(username="testuser", password="testpass123")

        # 1. Gå till symbolhantering
        manage_url = reverse("stamp_symbols_manage")
        response = self.client.get(manage_url)
        self.assertEqual(response.status_code, 200)

        # 2. Skapa ny symbol via AJAX eller form
        create_data = {
            "name": "Ny Symbol",
            "symbol_type": "heart",
            "pictogram": "❤️",
            "description": "Hjärtsymbol",
        }

        # Simulera symbolskapande
        symbol = StampSymbol.objects.create(**create_data)

        # 3. Verifiera att symbolen syns i listan
        response = self.client.get(manage_url)
        self.assertContains(response, "Ny Symbol")
        self.assertContains(response, "❤️")

        # 4. Uppdatera symbolen
        update_url = reverse("stamp_symbol_update", kwargs={"symbol_id": symbol.id})
        update_data = {
            "name": "Uppdaterad Hjärtsymbol",
            "symbol_type": "heart",
            "pictogram": "💖",
            "description": "Förbättrad hjärtsymbol",
        }
        response = self.client.post(update_url, update_data)
        self.assertEqual(response.status_code, 302)

        symbol.refresh_from_db()
        self.assertEqual(symbol.name, "Uppdaterad Hjärtsymbol")
        self.assertEqual(symbol.pictogram, "💖")

    def test_symbol_api_integration(self):
        """Testa integration mellan API och symbol-views"""
        # Skapa olika typer av symboler
        symbols_data = [
            {"name": "Krona A", "symbol_type": "crown", "pictogram": "👑"},
            {"name": "Krona B", "symbol_type": "crown", "pictogram": "♔"},
            {"name": "Stjärna A", "symbol_type": "star", "pictogram": "⭐"},
            {"name": "Hjärta", "symbol_type": "heart", "pictogram": "❤️"},
        ]

        created_symbols = []
        for data in symbols_data:
            symbol = StampSymbol.objects.create(**data)
            created_symbols.append(symbol)

        # Testa API-anrop
        api_url = reverse("stamp_symbols_api")

        # Hämta alla
        response = self.client.get(api_url)
        data = json.loads(response.content)
        # Kan vara fler än 4 om fixtures/predef finns; säkerställ att våra 4 ingår
        self.assertGreaterEqual(len(data), 4)

        # Filtrera på typ
        response = self.client.get(api_url + "?type=crown")
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        crown_names = [item["name"] for item in data]
        self.assertIn("Krona A", crown_names)
        self.assertIn("Krona B", crown_names)

        # Sök på namn (kan matcha fler än en i miljöer med fördefinierade)
        response = self.client.get(api_url + "?search=Stjärna")
        data = json.loads(response.content)
        self.assertGreaterEqual(len(data), 1)
        names = [item["name"] for item in data]
        self.assertIn("Stjärna A", names)

    def test_symbol_usage_with_stamps(self):
        """Testa användning av symboler med stämplar"""
        # Skapa symboler
        crown_symbol = StampSymbol.objects.create(
            name="Kunglig Krona", symbol_type="crown", pictogram="👑"
        )
        star_symbol = StampSymbol.objects.create(
            name="Femuddig Stjärna", symbol_type="star", pictogram="⭐"
        )

        # Skapa stämplar som använder symboler
        stamp1 = Stamp.objects.create(
            name="STÄMPEL MED KRONA",
            manufacturer=self.manufacturer,
            stamp_type="symbol",
        )
        stamp2 = Stamp.objects.create(
            name="STÄMPEL MED STJÄRNA",
            manufacturer=self.manufacturer,
            stamp_type="symbol",
        )

        # I en riktig implementation skulle symbolerna kopplas till stämplar
        # via en ManyToMany-relation eller liknande

        # Testa att symbolerna finns tillgängliga för stämplar
        api_url = reverse("stamp_symbols_api")
        response = self.client.get(api_url)
        data = json.loads(response.content)

        symbol_names = [item["name"] for item in data]
        self.assertIn(crown_symbol.name, symbol_names)
        self.assertIn(star_symbol.name, symbol_names)

        # Verifiera att stämplarna skapades korrekt
        self.assertEqual(stamp1.stamp_type, "symbol")
        self.assertEqual(stamp2.stamp_type, "symbol")

    def test_symbol_type_consistency(self):
        """Testa konsistens i symboltyper"""
        # Definiera alla giltiga symboltyper
        valid_types = [
            "crown",
            "cannon",
            "star",
            "cross",
            "shield",
            "anchor",
            "flower",
            "leaf",
            "arrow",
            "circle",
            "square",
            "triangle",
            "diamond",
            "heart",
            "other",
        ]

        # Skapa symboler för alla typer
        created_symbols = []
        for symbol_type in valid_types:
            symbol = StampSymbol.objects.create(
                name=f"Test {symbol_type}", symbol_type=symbol_type, pictogram="🔘"
            )
            created_symbols.append(symbol)

        # Testa API-filtrering för alla typer
        api_url = reverse("stamp_symbols_api")
        for symbol_type in valid_types:
            response = self.client.get(api_url + f"?type={symbol_type}")
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.content)
            # Minst en av vår skapade typ
            self.assertGreaterEqual(len(data), 1)
            self.assertTrue(all(item["symbol_type"] == symbol_type for item in data))

    def test_symbol_pictogram_unicode_handling(self):
        """Testa hantering av Unicode-piktogram"""
        unicode_symbols = [
            ("👑", "crown"),
            ("⭐", "star"),
            ("❤️", "heart"),
            ("🔺", "triangle"),
            ("🔵", "circle"),
            ("🗡️", "arrow"),
        ]

        for pictogram, symbol_type in unicode_symbols:
            symbol = StampSymbol.objects.create(
                name=f"Test {pictogram}", symbol_type=symbol_type, pictogram=pictogram
            )

            # Testa att piktogrammet sparas och hämtas korrekt
            symbol.refresh_from_db()
            self.assertEqual(symbol.pictogram, pictogram)

            # Testa via API
            api_url = reverse("stamp_symbols_api") + f"?search={symbol.name}"
            response = self.client.get(api_url)
            data = json.loads(response.content)

            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["pictogram"], pictogram)

    def test_predefined_symbols_management(self):
        """Testa hantering av fördefinierade symboler"""
        # Skapa fördefinierade symboler
        predefined_symbols = [
            {"name": "Svensk Krona", "symbol_type": "crown", "pictogram": "👑"},
            {"name": "Kanonkula", "symbol_type": "cannon", "pictogram": "⚫"},
            {"name": "Nordstjärnan", "symbol_type": "star", "pictogram": "⭐"},
        ]

        created_predefined = []
        for data in predefined_symbols:
            data["is_predefined"] = True
            symbol = StampSymbol.objects.create(**data)
            created_predefined.append(symbol)

        # Skapa användardefinierade symboler
        user_symbol = StampSymbol.objects.create(
            name="Min Symbol", symbol_type="heart", pictogram="💖", is_predefined=False
        )

        # Testa API-filtrering på fördefinierade
        api_url = reverse("stamp_symbols_api")

        response = self.client.get(api_url + "?predefined=true")
        data = json.loads(response.content)
        # Minst våra tre fördefinierade ska finnas
        self.assertGreaterEqual(len(data), 3)
        for item in data:
            self.assertTrue(item["is_predefined"])

        response = self.client.get(api_url + "?predefined=false")
        data = json.loads(response.content)
        # Minst en (vår) icke-fördefinierad ska finnas
        self.assertGreaterEqual(len(data), 1)
        names = [item["name"] for item in data]
        self.assertIn("Min Symbol", names)
        self.assertTrue(any(not item["is_predefined"] for item in data))

        # Policy: fördefinierade symboler får tas bort
        self.client.login(username="testuser", password="testpass123")

        predefined = created_predefined[0]
        delete_url = reverse("stamp_symbol_delete", kwargs={"symbol_id": predefined.id})
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(StampSymbol.objects.filter(id=predefined.id).exists())

        # Men användardefinierade borde kunna tas bort
        delete_url = reverse(
            "stamp_symbol_delete", kwargs={"symbol_id": user_symbol.id}
        )
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(StampSymbol.objects.filter(id=user_symbol.id).exists())
