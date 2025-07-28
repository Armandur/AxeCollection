import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TraderaParser:
    """Parser för Tradera-auktioner"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def is_tradera_url(self, url: str) -> bool:
        """Kontrollera om URL är en giltig Tradera-auktions-URL"""
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc == "www.tradera.com"
                and parsed.path.startswith("/item/")
                and len(parsed.path.split("/")) >= 4
            )
        except Exception:
            return False

    def extract_item_id(self, url: str) -> Optional[str]:
        """Extrahera objekt-ID från Tradera URL"""
        try:
            # URL-format: /item/343327/683953821/yxa-saw-stamplat-ph-
            path_parts = urlparse(url).path.split("/")
            if len(path_parts) >= 4:
                return path_parts[3]  # 683953821
            return None
        except Exception:
            return None

    def parse_tradera_page(self, url: str) -> Dict:
        """Huvudfunktion för att parsa Tradera-auktionssida"""
        if not self.is_tradera_url(url):
            raise ValueError("Ogiltig Tradera URL")

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            prices = self._extract_prices(soup)

            return {
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "seller_alias": self._extract_seller_alias(soup),
                "prices": prices,
                "item_id": self.extract_item_id(url),
                "images": self._extract_images(soup),
                "auction_end_date": self._extract_auction_end_date(soup),
                "url": url,
            }

        except requests.RequestException as e:
            logger.error(f"Fel vid hämtning av Tradera-sida: {e}")
            raise ValueError(f"Kunde inte hämta auktionssida: {e}")
        except Exception as e:
            logger.error(f"Fel vid parsning av Tradera-sida: {e}")
            raise ValueError(f"Kunde inte parsa auktionssida: {e}")

    def _extract_auction_end_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrahera auktionsslutdatum"""
        # Leta efter text som indikerar när auktionen slutade
        page_text = soup.get_text()

        # Mönster för att hitta slutdatum
        date_patterns = [
            # Format: "avslutad 27 jul 14:00" (implicit år 2025)
            r"avslutad\s+(\d{1,2})\s+(jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec)\s+(\d{1,2}):(\d{2})",
            r"avslutad\s+(\d{1,2})\s+(januari|februari|mars|april|maj|juni|juli|augusti|september|oktober|november|december)\s+(\d{1,2}):(\d{2})",
            # Format: "slutade 27 juli 2025"
            r"slutade\s+(\d{1,2})\s+(januari|februari|mars|april|maj|juni|juli|augusti|september|oktober|november|december)\s+(\d{4})",
            r"slutade\s+(\d{1,2})/(\d{1,2})/(\d{4})",
            r"slutade\s+(\d{4})-(\d{1,2})-(\d{1,2})",
            r"(\d{1,2})\s+(januari|februari|mars|april|maj|juni|juli|augusti|september|oktober|november|december)\s+(\d{4})\s+slutade",
            r"(\d{1,2})/(\d{1,2})/(\d{4})\s+slutade",
            r"(\d{4})-(\d{1,2})-(\d{1,2})\s+slutade",
        ]

        month_names = {
            "jan": 1, "januari": 1,
            "feb": 2, "februari": 2,
            "mar": 3, "mars": 3,
            "apr": 4, "april": 4,
            "maj": 5,
            "jun": 6, "juni": 6,
            "jul": 7, "juli": 7,
            "aug": 8, "augusti": 8,
            "sep": 9, "september": 9,
            "okt": 10, "oktober": 10,
            "nov": 11, "november": 11,
            "dec": 12, "december": 12,
        }

        for pattern in date_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 4:
                        # Format: "avslutad 27 jul 14:00" (4 grupper: dag, månad, timme, minut)
                        day = int(groups[0])
                        month_name = groups[1].lower()
                        # Timme och minut ignoreras för datum
                        if month_name in month_names:
                            month = month_names[month_name]
                            
                            # Intelligent årbestämning baserat på dagens datum
                            today = datetime.now().date()
                            current_year = today.year
                            current_month = today.month
                            
                            # Om auktionsmånad är senare än nuvarande månad, 
                            # och vi är i slutet av året, så är auktionen från föregående år
                            if month > current_month and current_month >= 11:
                                year = current_year - 1
                            # Om auktionsmånad är tidigare än nuvarande månad,
                            # och vi är i början av året, så är auktionen från föregående år
                            elif month < current_month and current_month <= 2:
                                year = current_year - 1
                            else:
                                # Annars använd nuvarande år
                                year = current_year
                            
                            # Validera datum
                            if 1 <= day <= 31 and 1 <= month <= 12:
                                return f"{year:04d}-{month:02d}-{day:02d}"
                    elif len(groups) == 3:
                        if groups[1].lower() in month_names:
                            # Svenskt format: 15 januari 2024
                            day = int(groups[0])
                            month = month_names[groups[1].lower()]
                            year = int(groups[2])
                        else:
                            # Numeriskt format: 15/01/2024 eller 2024-01-15
                            if len(groups[0]) == 4:
                                # ISO format: 2024-01-15
                                year = int(groups[0])
                                month = int(groups[1])
                                day = int(groups[2])
                            else:
                                # Numeriskt format: 15/01/2024
                                day = int(groups[0])
                                month = int(groups[1])
                                year = int(groups[2])

                        # Validera datum
                        if 1 <= day <= 31 and 1 <= month <= 12 and 2020 <= year <= 2030:
                            return f"{year:04d}-{month:02d}-{day:02d}"
                except (ValueError, IndexError):
                    continue

        # Fallback: om vi inte hittar slutdatum, använd dagens datum
        # Detta är rimligt eftersom användaren troligen vinner auktioner som nyligen slutade
        today = datetime.now().date()
        return today.strftime("%Y-%m-%d")

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrahera auktionstitel"""
        # Leta efter h1 eller liknande element med titeln
        title_selectors = [
            "h1",
            ".item-title",
            '[data-testid="item-title"]',
            "title",
            'h1:contains("Yxa")',
            'h1:contains("Axe")',
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and title != "Tradera":
                    return title

        # Fallback: leta efter text som innehåller "Yxa" eller liknande
        for element in soup.find_all(["h1", "h2", "h3"]):
            text = element.get_text(strip=True)
            if any(
                keyword in text.lower() for keyword in ["yxa", "axe", "verktyg", "saw"]
            ):
                return text

        return "Okänd titel"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extrahera auktionsbeskrivning"""
        # Leta efter beskrivningssektion
        desc_selectors = [
            ".description",
            ".item-description",
            '[data-testid="description"]',
            ".Beskrivning",
        ]

        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                # Konvertera HTML-element till radbrytningar
                text = self._convert_html_to_text_with_linebreaks(element)
                return text

        # Fallback: leta efter text som verkar vara beskrivning
        for element in soup.find_all(["p", "div"]):
            text = element.get_text()
            if len(text) > 50 and any(
                keyword in text.lower() for keyword in ["skick", "kvalité", "granska"]
            ):
                # Konvertera HTML-element till radbrytningar
                text = self._convert_html_to_text_with_linebreaks(element)
                return text

        return ""

    def _convert_html_to_text_with_linebreaks(self, element) -> str:
        """Konvertera HTML-element till text med radbrytningar"""
        # Ersätt <br> och <br/> taggar med radbrytningar
        for br in element.find_all(['br']):
            br.replace_with('\n')
        
        # Ersätt block-element med radbrytningar
        for block in element.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if block.name != element.name:  # Undvik att ersätta själva elementet
                block.insert_before('\n')
                block.insert_after('\n')
        
        # Hämta text och normalisera
        text = element.get_text()
        # Ta bort extra whitespace men behåll radbrytningar
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

    def _extract_seller_alias(self, soup: BeautifulSoup) -> str:
        """Extrahera säljarens alias"""
        # Först försök hitta aliaset från display-texten för att få rätt versalisering
        display_aliases = []
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            
            # Om länken går till en profil och texten verkar vara ett alias
            if "/profile/" in href and text:
                # Filtrera bort text som inte är alias
                # Undantag: tillåt alias som innehåller "auktioner" om det verkar vara ett riktigt alias
                text_lower = text.lower()
                is_valid_alias = (
                    len(text) < 50
                    and not any(char in text for char in ["kr", "€", "$", "£"])
                    and not any(
                        word in text_lower
                        for word in [
                            "köp",
                            "spara",
                            "frakt",
                            "tradera",
                            "mer",
                            "och",
                            "läs",
                            "omdömen",
                            "meny",
                        ]
                    )
                )
                
                # Specialfall: tillåt alias som innehåller "auktioner" om det verkar vara ett riktigt alias
                if "auktioner" in text_lower and len(text) < 30 and not any(char in text for char in [" ", ","]):
                    is_valid_alias = True
                
                if is_valid_alias:
                    display_aliases.append(text)
        
        # Prioritera renare alias från display-texten (med rätt versalisering)
        for text in display_aliases:
            # Rensa bort recensionsbetyg som "5.0", "4.8", etc. och extra text
            # Försök hitta mönster där betyget är tydligt separerat från aliaset
            # Exempel: "Sandra123895.0" -> "Sandra12389", "PetrusAuktioner4.8" -> "PetrusAuktioner"
            
            # Ta bort decimaltal i slutet om det verkar vara ett betyg
            # Kontrollera först om texten slutar med ett decimaltal
            if re.search(r"\d+\.\d+$", text):
                # Om det finns en kombination av bokstäver och siffror följt av decimaltal
                # så är det troligen alias + betyg
                match = re.search(r"([a-zA-ZåäöÅÄÖ]+[a-zA-ZåäöÅÄÖ0-9_]*)\d+\.\d+$", text)
                if match:
                    cleaned_text = match.group(1)
                else:
                    # Fallback: ta bort decimaltal i slutet
                    cleaned_text = re.sub(r"\d+\.\d+$", "", text).strip()
            else:
                cleaned_text = text.strip()
            
            # Ta bort extra text som städer, länder, etc.
            cleaned_text = re.sub(r"\s*[,\s].*$", "", cleaned_text).strip()
            # Kontrollera att det verkar vara ett rimligt alias
            if cleaned_text and len(cleaned_text) >= 3 and not any(char in cleaned_text for char in [" ", "\n", "\t"]):
                # Behåll ursprunglig versalisering från display-texten
                return cleaned_text
        
        # Fallback: använd URL-baserad extraktion om display-texten inte fungerar
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            
            # Leta efter profil-URL:er som innehåller aliaset
            # Exempel: /profile/items/1376193/sandra12389
            profile_match = re.search(r"/profile/items/\d+/([^/]+)$", href)
            if profile_match:
                alias = profile_match.group(1)
                # Kontrollera att det verkar vara ett rimligt alias
                if alias and len(alias) >= 3 and not any(char in alias for char in [" ", "\n", "\t"]):
                    # Behåll ursprunglig versalisering från URL:en
                    return alias
        
        # Fallback: försök hitta säljaralias i länkar till butik/profil
        profile_links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(strip=True)

            # Om länken går till en profil och texten verkar vara ett alias
            if "/profile/" in href and text:
                # Filtrera bort text som inte är alias
                # Undantag: tillåt alias som innehåller "auktioner" om det verkar vara ett riktigt alias
                text_lower = text.lower()
                is_valid_alias = (
                    len(text) < 50
                    and not any(char in text for char in ["kr", "€", "$", "£"])
                    and not any(
                        word in text_lower
                        for word in [
                            "köp",
                            "spara",
                            "frakt",
                            "tradera",
                            "mer",
                            "och",
                            "läs",
                            "omdömen",
                            "meny",
                        ]
                    )
                )
                
                # Specialfall: tillåt alias som innehåller "auktioner" om det verkar vara ett riktigt alias
                if "auktioner" in text_lower and len(text) < 30 and not any(char in text for char in [" ", ","]):
                    is_valid_alias = True
                
                if is_valid_alias:
                    profile_links.append(text)

        # Prioritera renare alias (utan extra text som städer, etc.)
        for text in profile_links:
            # Rensa bort recensionsbetyg som "5.0", "4.8", etc. och extra text
            # Försök hitta mönster där betyget är tydligt separerat från aliaset
            # Exempel: "Sandra123895.0" -> "Sandra12389", "PetrusAuktioner4.8" -> "PetrusAuktioner"
            
            # Ta bort decimaltal i slutet om det verkar vara ett betyg
            # Kontrollera först om texten slutar med ett decimaltal
            if re.search(r"\d+\.\d+$", text):
                # Om det finns en kombination av bokstäver och siffror följt av decimaltal
                # så är det troligen alias + betyg
                match = re.search(r"([a-zA-ZåäöÅÄÖ]+[a-zA-ZåäöÅÄÖ0-9_]*)\d+\.\d+$", text)
                if match:
                    cleaned_text = match.group(1)
                else:
                    # Fallback: ta bort decimaltal i slutet
                    cleaned_text = re.sub(r"\d+\.\d+$", "", text).strip()
            else:
                cleaned_text = text.strip()
            
            # Ta bort extra text som städer, länder, etc.
            cleaned_text = re.sub(r"\s*[,\s].*$", "", cleaned_text).strip()
            # Kontrollera att det verkar vara ett rimligt alias
            if cleaned_text and len(cleaned_text) >= 3 and not any(char in cleaned_text for char in [" ", "\n", "\t"]):
                # Behåll ursprunglig versalisering från display-texten
                return cleaned_text

                    # Specifikt leta efter text som innehåller "Auktioner" (som PetrusAuktioner)
            for element in soup.find_all(["a", "span", "div"]):
                text = element.get_text(strip=True)
                if text and "auktioner" in text.lower() and len(text) < 30:
                    # Rensa bort versioner som "5.0"
                    cleaned_text = re.sub(r"\d+\.\d+$", "", text).strip()
                    # Behåll ursprunglig versalisering från display-texten
                    return cleaned_text

        # Fallback: leta efter text som verkar vara säljare
        for element in soup.find_all(["span", "div", "a"]):
            text = element.get_text(strip=True)
            if (
                text
                and len(text) < 50
                and not any(char in text for char in ["kr", "€", "$", "£"])
                and not any(
                    word in text.lower()
                    for word in [
                        "köp",
                        "spara",
                        "frakt",
                        "auktioner",
                        "tradera",
                        "mer",
                        "och",
                    ]
                )
            ):
                # Behåll ursprunglig versalisering från display-texten
                return text

        return "Okänd säljare"

    def _extract_prices(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrahera priser med etikett (slutpris, köparskydd, frakt med typ)"""
        prices = []

        # 1. Slutpris och köparskydd - leta efter specifika texter
        price_patterns = [
            (r"slutpris.*?(\d+)\s*kr", "Slutpris"),
            (r"vinnande bud.*?(\d+)\s*kr", "Vinnande bud"),
            (r"du vann.*?(\d+)\s*kr", "Du vann"),
        ]

        page_text = soup.get_text()
        for pattern, label in price_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = int(match)
                    if 10 <= amount <= 50000:
                        prices.append({"label": label, "amount": amount})
                except ValueError:
                    continue

        # 3. Specifikt leta efter köparskydd-pris
        # Leta efter text som innehåller köparskydd och klimatkompenseras
        köparskydd_match = re.search(
            r"(\d+)\s*kr.*?klimatkompenseras", page_text, re.IGNORECASE
        )
        if köparskydd_match:
            try:
                amount = int(köparskydd_match.group(1))
                if 200 <= amount <= 10000:  # Rimligt köparskydd-pris
                    # Ta bort eventuella duplicerade köparskydd-priser
                    prices = [
                        p
                        for p in prices
                        if not (p["label"] == "med köparskydd" and p["amount"] < 200)
                    ]
                    prices.append({"label": "med köparskydd", "amount": amount})
            except ValueError:
                pass

        # 3b. Alternativ: leta efter köparskydd-pris utan klimatkompenseras
        köparskydd_match2 = re.search(
            r"(\d+)\s*kr\s+med\s+köparskydd", page_text, re.IGNORECASE
        )
        if köparskydd_match2:
            try:
                amount = int(köparskydd_match2.group(1))
                if 200 <= amount <= 1000:  # Rimligt köparskydd-pris
                    # Ta bort eventuella duplicerade köparskydd-priser
                    # Kontrollera om detta pris redan finns
                    if not any(
                        p["label"] == "med köparskydd" and p["amount"] == amount
                        for p in prices
                    ):
                        prices.append({"label": "med köparskydd", "amount": amount})
            except ValueError:
                pass

        # 4. Alternativ: leta efter köparskydd-pris baserat på slutpris
        # Ofta är köparskydd-priset slutpris + 6% (eller liknande)
        slutpris = None
        for price in prices:
            if price["label"] == "Slutpris":
                slutpris = price["amount"]
                break

        if slutpris:
            # Beräkna troligt köparskydd-pris (slutpris + 6%)
            expected_köparskydd = int(slutpris * 1.06)
            # Leta efter köparskydd-pris nära det förväntade värdet
            for price in prices:
                if (
                    price["label"] == "med köparskydd"
                    and abs(price["amount"] - expected_köparskydd) <= 50
                ):  # ±50 kr tolerans
                    # Detta är troligen rätt köparskydd-pris
                    break
            else:
                # Om vi inte hittar rätt köparskydd-pris, ta bort de felaktiga
                prices = [
                    p
                    for p in prices
                    if not (p["label"] == "med köparskydd" and p["amount"] < 200)
                ]

        # 5. Fallback: leta efter alla priser med "kr" (om inget hittats)
        if not prices:
            for element in soup.find_all(text=re.compile(r"(\d+)\s*kr")):
                price = self._parse_price(element)
                if price:
                    prices.append({"label": "Pris", "amount": price})

        return prices

    def _find_price_nearby(self, element) -> Optional[int]:
        """Hjälpfunktion för att hitta pris i samma element eller närliggande"""
        text = element.get_text()
        price = self._parse_price(text)
        if price:
            return price
        # Leta i syskon
        for sib in element.find_next_siblings(["span", "div"]):
            price = self._parse_price(sib.get_text())
            if price:
                return price
        return None

    def _parse_price(self, price_text: str) -> Optional[int]:
        """Parsa pris från text"""
        # Leta efter siffror följt av "kr" eller siffror med mellanslag
        price_patterns = [
            r"(\d+)\s*kr",  # 199 kr
            r"(\d+)\s*SEK",  # 199 SEK
            r"(\d+)\s*:-",  # 199 :-
            r"(\d{1,4})\s*(\d{1,3})",  # 1 999 (med mellanslag)
        ]

        for pattern in price_patterns:
            match = re.search(pattern, price_text, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) == 2:
                        # Kombinera två grupper (t.ex. "1 999")
                        price_str = match.group(1) + match.group(2)
                    else:
                        price_str = match.group(1)

                    price = int(price_str)
                    # Kontrollera att priset är rimligt (10-50000 kr)
                    if 10 <= price <= 50000:
                        return price
                except ValueError:
                    continue

        return None

    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        images = []
        # Hämta alla img-taggar med src eller data-src som innehåller tradera.net
        img_selectors = ['img[src*="tradera.net"]', 'img[data-src*="tradera.net"]']

        # Hitta auktionens ID för att filtrera bilder
        auction_id = None
        for element in soup.find_all(["img", "a"]):
            src = element.get("src") or element.get("href") or ""
            if "img.tradera.net" in src:
                # Extrahera ID från URL (t.ex. /902/ från /902/607442902_...)
                match = re.search(r"/(\d+)/\d+_", src)
                if match:
                    auction_id = match.group(1)
                    break

        for selector in img_selectors:
            elements = soup.select(selector)
            for element in elements:
                src = element.get("src") or element.get("data-src")
                if src:
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = "https://www.tradera.com" + src

                    # Konvertera till /images/-formatet om det är en Tradera-bild
                    if "img.tradera.net" in src:
                        # Byt ut alla format mot /images/
                        src = re.sub(
                            r"/(small-square|medium-fit|large-fit|heroimages)/",
                            "/images/",
                            src,
                        )

                        # Ta bara med om det nu är en /images/-URL och tillhör rätt auktion
                        if "/images/" in src:
                            # Filtrera så att endast bilder från aktuell auktion tas med
                            if auction_id and f"/{auction_id}/" in src:
                                images.append(src)
                            elif (
                                not auction_id
                            ):  # Fallback om vi inte hittar auktion-ID
                                images.append(src)

        return list(set(images))


def parse_tradera_url(url: str) -> Dict:
    """Enkel funktion för att parsa Tradera URL"""
    parser = TraderaParser()
    return parser.parse_tradera_page(url)
