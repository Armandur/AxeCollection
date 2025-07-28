import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EbayParser:
    """Parser för eBay-auktioner"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

    def is_ebay_url(self, url: str) -> bool:
        """Kontrollera om URL är en giltig eBay-auktions-URL"""
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc
                in ["www.ebay.com", "www.ebay.co.uk", "www.ebay.de", "www.ebay.se"]
                and "/itm/" in parsed.path
            )
        except Exception:
            return False

    def extract_item_id(self, url: str) -> Optional[str]:
        """Extrahera objekt-ID från eBay URL"""
        try:
            # URL-format: /itm/123456789012 eller /itm/123456789012?hash=...
            path_parts = urlparse(url).path.split("/")
            if len(path_parts) >= 3 and path_parts[1] == "itm":
                return path_parts[2]
            return None
        except Exception:
            return None

    def parse_ebay_page(self, url: str) -> Dict:
        """Huvudfunktion för att parsa eBay-auktionssida"""
        if not self.is_ebay_url(url):
            raise ValueError("Ogiltig eBay URL")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            # Extrahera data
            title = self._extract_title(soup)
            description = self._extract_description(soup)

            # Om ingen beskrivning hittas, använd titeln som beskrivning
            if description == "Ingen beskrivning tillgänglig":
                description = title

            seller_alias = self._extract_seller_alias(soup)
            prices = self._extract_prices(soup)
            images = self._extract_images(soup)
            auction_end_date = self._extract_auction_end_date(soup)

            return {
                "title": title,
                "description": description,
                "seller_alias": seller_alias,
                "prices": prices,
                "item_id": self.extract_item_id(url),
                "images": images,
                "auction_end_date": auction_end_date,
                "url": url,
            }

        except requests.RequestException as e:
            logger.error(f"Fel vid hämtning av eBay-sida: {e}")
            raise ValueError(f"Kunde inte hämta auktionssida: {e}")
        except Exception as e:
            logger.error(f"Fel vid parsning av eBay-sida: {e}")
            raise ValueError(f"Kunde inte parsa auktionssida: {e}")

    def _extract_auction_end_date(self, soup: BeautifulSoup) -> str:
        """Extrahera auktionens slutdatum"""
        current_year = datetime.now().year
        current_month = datetime.now().month

        # Leta efter slutdatum i olika format
        date_patterns = [
            r"sold on (\w+, \w+ \d+ at \d+:\d+ [AP]M)",
            r"ended on (\w+, \w+ \d+ at \d+:\d+ [AP]M)",
            r"(\w+, \w+ \d+ at \d+:\d+ [AP]M)",
            r"(\w+ \d+)",  # Bara månad och dag
        ]

        # Leta i text efter datum
        page_text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Försök parsa olika datumformat
                    if "at" in date_str:
                        # Format: "Tue, Jun 17 at 11:33 AM"
                        date_obj = datetime.strptime(date_str, "%a, %b %d at %I:%M %p")
                        # Använd aktuellt år
                        date_obj = date_obj.replace(year=current_year)
                    elif "," in date_str and len(date_str.split(",")) == 2:
                        # Format: "Jun 17, 2024" - använd året från texten
                        date_obj = datetime.strptime(date_str, "%b %d, %Y")
                    else:
                        # Format: "Jun 17" - använd aktuellt år
                        date_obj = datetime.strptime(date_str, "%b %d")
                        date_obj = date_obj.replace(year=current_year)

                    # Hantera kring nyår - om datum är flera månader framåt, använd föregående år
                    if date_obj.month < current_month - 6:
                        date_obj = date_obj.replace(year=current_year + 1)
                    elif date_obj.month > current_month + 6:
                        date_obj = date_obj.replace(year=current_year - 1)

                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

        # Fallback: leta efter datum i specifika element
        date_selectors = [
            ".x-item-title__timeLeft",
            ".timeLeft",
            ".item-time-left",
            '[data-testid="time-left"]',
        ]

        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                for pattern in date_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        date_str = match.group(1)
                        try:
                            if "at" in date_str:
                                date_obj = datetime.strptime(
                                    date_str, "%a, %b %d at %I:%M %p"
                                )
                                date_obj = date_obj.replace(year=current_year)
                            elif "," in date_str and len(date_str.split(",")) == 2:
                                date_obj = datetime.strptime(date_str, "%b %d, %Y")
                            else:
                                date_obj = datetime.strptime(date_str, "%b %d")
                                date_obj = date_obj.replace(year=current_year)

                            # Hantera kring nyår
                            if date_obj.month < current_month - 6:
                                date_obj = date_obj.replace(year=current_year + 1)
                            elif date_obj.month > current_month + 6:
                                date_obj = date_obj.replace(year=current_year - 1)

                            return date_obj.strftime("%Y-%m-%d")
                        except ValueError:
                            continue

        # Fallback: använd dagens datum om inget hittas
        return datetime.now().strftime("%Y-%m-%d")

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrahera auktionstitel"""
        # Leta efter h1 eller liknande element med titeln
        title_selectors = [
            "h1",
            ".x-item-title__mainTitle",
            '[data-testid="item-title"]',
            "title",
            'h1:contains("Axe")',
            'h1:contains("Tool")',
            'h1:contains("Hatchet")',
            'h1:contains("Vintage")',
            'h1:contains("Antique")',
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and title != "eBay" and len(title) > 5:
                    return title

        # Fallback: leta efter text som innehåller "Axe" eller liknande
        for element in soup.find_all(["h1", "h2", "h3"]):
            text = element.get_text(strip=True)
            if any(
                keyword in text.lower()
                for keyword in [
                    "axe",
                    "tool",
                    "vintage",
                    "antique",
                    "hatchet",
                    "billnäs",
                    "billnas",
                    "hults",
                    "gränsfors",
                ]
            ):
                return text

        # Leta efter titel i meta-taggar
        meta_title = soup.find("meta", property="og:title")
        if meta_title and meta_title.get("content"):
            return meta_title.get("content")

        return "Okänd titel"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extrahera produktbeskrivning"""
        # Ta bort navigationsmeny och andra störande element
        for element in soup.find_all(["nav", "header", "footer", "script", "style"]):
            element.decompose()

        # Ta bort element med navigationsklasser
        for element in soup.find_all(
            class_=lambda x: x
            and any(
                word in x.lower()
                for word in [
                    "nav",
                    "header",
                    "footer",
                    "menu",
                    "breadcrumb",
                    "sidebar",
                    "ad",
                    "banner",
                ]
            )
        ):
            element.decompose()

        # Leta efter beskrivning i olika format
        description_selectors = [
            ".x-item-description__content",
            ".item-description",
            ".description",
            '[data-testid="item-description"]',
            ".item-description__content",
            ".item-description__text",
        ]

        for selector in description_selectors:
            element = soup.select_one(selector)
            if element:
                text = self._convert_html_to_text_with_linebreaks(element)
                if text and len(text) > 50:
                    return text

        # Fallback: leta efter text som verkar vara beskrivning
        for element in soup.find_all(["p", "div", "span"]):
            text = element.get_text(strip=True)
            if (
                text
                and len(text) > 100
                and not any(
                    word in text.lower()
                    for word in [
                        "skip to main content",
                        "sign in",
                        "register",
                        "daily deals",
                        "brand outlet",
                        "gift cards",
                        "help & contact",
                        "sell",
                        "watchlist",
                        "my ebay",
                        "summary",
                        "recently viewed",
                        "bids/offers",
                        "purchase history",
                        "buy again",
                        "selling",
                        "saved feed",
                        "saved searches",
                        "saved sellers",
                        "my garage",
                        "sizes",
                        "my collection",
                        "messages",
                        "psa vault",
                        "notifications",
                        "cart",
                        "loading",
                        "ebay home",
                        "shop by category",
                        "enter your search keyword",
                        "all categories",
                        "search",
                        "advanced",
                        "new",
                        "live shopping",
                        "tune in",
                        "card breaks",
                        "style inspo",
                        "top sellers",
                        "join a livestream",
                        "this listing sold",
                        "see original listing",
                        "sell one like this",
                        "seller's other items",
                        "picture",
                        "gallery",
                        "have one to sell",
                        "sell now",
                        "share",
                        "contact seller",
                        "condition",
                        "used",
                        "more information",
                        "about this item condition",
                        "item that has been used previously",
                        "see the seller's listing",
                        "full details",
                        "description of any imperfections",
                        "shipping",
                        "free economy shipping",
                        "international shipment",
                        "customs processing",
                        "additional charges",
                        "sellers declare",
                        "customs value",
                        "comply with customs declaration laws",
                        "information",
                        "buyer should be aware",
                        "possible delays",
                        "customs inspection",
                        "import duties",
                        "taxes",
                        "buyers must pay",
                        "brokerage fees",
                        "payable at the point of delivery",
                        "country's customs office",
                        "offer more details",
                        "visit ebay's page",
                        "international trade",
                        "located in",
                        "delivery",
                        "estimated between",
                        "estimated delivery dates",
                        "opens in a new window",
                        "include seller's handling time",
                        "origin zip code",
                        "destination zip code",
                        "time of acceptance",
                        "will depend on shipping service",
                        "selected and receipt of cleared payment",
                        "delivery times may vary",
                        "especially during peak periods",
                        "returns",
                        "seller does not accept returns",
                        "details for more information",
                        "payments",
                        "special financing available",
                        "terms and apply now",
                        "paypal credit",
                        "opens in a new window",
                        "earn up to",
                        "points when you use",
                        "ebay mastercard",
                        "learn more",
                        "about earning points",
                        "mastercard",
                        "as low as",
                        "month",
                        "flexible payments",
                        "no surprises",
                        "spread the cost",
                        "purchases over",
                        "months with an interest rate",
                        "from",
                        "there's no fees",
                        "pay on time",
                        "how it works",
                        "select klarna",
                        "payment method",
                        "checkout",
                        "confirm order details",
                        "select pay with klarna",
                        "time to select",
                        "payment method",
                        "choose klarna",
                        "take you to klarna",
                        "securely choose",
                        "preferred plan",
                        "set",
                        "manage payments",
                        "klarna app",
                        "website",
                        "purchase amount",
                        "sample apr",
                        "tax and shipping",
                        "calculated at checkout",
                        "subtotal",
                        "estimated subtotal",
                        "payments",
                        "monthly payment plan",
                        "down payment",
                        "required",
                        "klarna monthly financing",
                        "issued by webbank",
                        "klarna and webbank",
                        "soft credit check",
                        "assess eligibility",
                        "will not impact",
                        "credit score",
                        "terms and conditions",
                        "shop with confidence",
                        "ebay money back guarantee",
                        "get the item",
                        "ordered or your money back",
                        "learn more",
                        "guarantee",
                        "new window",
                        "about this item",
                        "seller assumes",
                        "responsibility for this listing",
                        "ebay item number",
                        "last updated on",
                        "view all revisions",
                        "item specifics",
                        "condition",
                        "previously",
                        "details and description",
                        "imperfections",
                        "definitions",
                        "opens in a new window",
                        "seller notes",
                        "brand",
                        "original/reproduction",
                        "vintage",
                        "country/region of manufacture",
                        "category",
                        "breadcrumb",
                        "collectibles & art",
                        "collectibles",
                        "tools, hardware & locks",
                        "tools",
                        "carpentry, woodworking",
                        "axes, hatchets",
                        "item description",
                        "seller",
                        "about this seller",
                        "positive feedback",
                        "items sold",
                        "joined",
                        "usually responds",
                        "within",
                        "hours",
                        "other items",
                        "contact",
                        "save seller",
                        "feedback",
                        "filter",
                        "all ratings",
                        "positive",
                        "neutral",
                        "negative",
                        "feedback left by buyer",
                        "past",
                        "months",
                        "verified purchase",
                        "great description",
                        "communication",
                        "packaged",
                        "fair price",
                        "shipped",
                        "immediately",
                        "pleasure to work",
                        "absolutely buy",
                        "again and highly recommend",
                        "set of",
                        "finnish vintage axes",
                        "finland",
                        "fantastic purchase",
                        "good shipping",
                        "packaging was as described",
                        "great value",
                        "deal with",
                        "satisfied",
                        "as described",
                        "answered all questions",
                        "kept updated",
                        "process",
                        "back to home page",
                        "return to top",
                        "more to explore",
                        "tomahawk",
                        "collectible axes",
                        "throwing",
                        "tactical",
                        "battle",
                        "sog",
                        "gerber",
                        "camping",
                        "camillus",
                        "plumb",
                        "vintage",
                        "shop top sellers",
                        "highly rated products",
                        "hatchets",
                        "best sellers",
                        "valley",
                        "american hickory",
                        "wood handle",
                        "hults bruk",
                        "almike",
                        "lb",
                        "handle",
                        "ames companies",
                        "inc",
                        "true temper",
                        "replacement",
                        "single bit",
                        "marbles",
                        "belt",
                        "top rated",
                        "related searches",
                        "finnish",
                        "axe",
                        "finland",
                        "made in sweden",
                        "swedish",
                        "swedes",
                        "head",
                        "norway",
                        "old",
                        "heads",
                        "fiskars",
                        "viking's",
                        "copyright",
                        "inc",
                        "rights reserved",
                        "accessibility",
                        "user agreement",
                        "privacy",
                        "consumer health data",
                        "payments",
                        "terms of use",
                        "cookies",
                        "privacy notice",
                        "choices",
                        "adchoice",
                    ]
                )
                and not text.startswith("Skip")
                and not text.startswith("Hi")
                and not text.startswith("Sign")
                and not text.startswith("Daily")
                and not text.startswith("Brand")
                and not text.startswith("Gift")
                and not text.startswith("Help")
                and not text.startswith("Contact")
                and not text.startswith("Sell")
                and not text.startswith("Watchlist")
                and not text.startswith("Expand")
                and not text.startswith("My")
                and not text.startswith("Summary")
                and not text.startswith("Recently")
                and not text.startswith("Viewed")
                and not text.startswith("Bids")
                and not text.startswith("Offers")
                and not text.startswith("Purchase")
                and not text.startswith("History")
                and not text.startswith("Buy")
                and not text.startswith("Again")
                and not text.startswith("Selling")
                and not text.startswith("Saved")
                and not text.startswith("Feed")
                and not text.startswith("Searches")
                and not text.startswith("Sellers")
                and not text.startswith("Garage")
                and not text.startswith("Sizes")
                and not text.startswith("Collection")
                and not text.startswith("Messages")
                and not text.startswith("PSA")
                and not text.startswith("Vault")
                and not text.startswith("Notifications")
                and not text.startswith("Cart")
                and not text.startswith("Loading")
                and not text.startswith("Home")
                and not text.startswith("Shop")
                and not text.startswith("category")
                and not text.startswith("Enter")
                and not text.startswith("search")
                and not text.startswith("keyword")
                and not text.startswith("All")
                and not text.startswith("Categories")
                and not text.startswith("Advanced")
                and not text.startswith("NEW")
                and not text.startswith("Live")
                and not text.startswith("shopping")
                and not text.startswith("Tune")
                and not text.startswith("card")
                and not text.startswith("breaks")
                and not text.startswith("style")
                and not text.startswith("inspo")
                and not text.startswith("top")
                and not text.startswith("sellers")
                and not text.startswith("Join")
                and not text.startswith("livestream")
                and not text.startswith("This")
                and not text.startswith("listing")
                and not text.startswith("sold")
                and not text.startswith("See")
                and not text.startswith("original")
                and not text.startswith("Sell")
                and not text.startswith("one")
                and not text.startswith("like")
                and not text.startswith("this")
                and not text.startswith("Seller's")
                and not text.startswith("other")
                and not text.startswith("items")
                and not text.startswith("Picture")
                and not text.startswith("Gallery")
                and not text.startswith("Have")
                and not text.startswith("Share")
                and not text.startswith("Contact")
                and not text.startswith("seller")
                and not text.startswith("US")
                and not text.startswith("Condition")
                and not text.startswith("Used")
                and not text.startswith("More")
                and not text.startswith("information")
                and not text.startswith("About")
                and not text.startswith("item")
                and not text.startswith("condition")
                and not text.startswith("item")
                and not text.startswith("that")
                and not text.startswith("has")
                and not text.startswith("been")
                and not text.startswith("previously")
                and not text.startswith("see")
                and not text.startswith("seller's")
                and not text.startswith("listing")
                and not text.startswith("for")
                and not text.startswith("full")
                and not text.startswith("details")
                and not text.startswith("description")
                and not text.startswith("any")
                and not text.startswith("imperfections")
                and not text.startswith("Shipping")
                and not text.startswith("Free")
                and not text.startswith("Economy")
                and not text.startswith("from")
                and not text.startswith("outside")
                and not text.startswith("details")
                and not text.startswith("International")
                and not text.startswith("shipment")
                and not text.startswith("may")
                and not text.startswith("subject")
                and not text.startswith("customs")
                and not text.startswith("processing")
                and not text.startswith("additional")
                and not text.startswith("charges")
                and not text.startswith("Sellers")
                and not text.startswith("declare")
                and not text.startswith("customs")
                and not text.startswith("value")
                and not text.startswith("must")
                and not text.startswith("comply")
                and not text.startswith("declaration")
                and not text.startswith("laws")
                and not text.startswith("Information")
                and not text.startswith("As")
                and not text.startswith("buyer")
                and not text.startswith("should")
                and not text.startswith("aware")
                and not text.startswith("possible")
                and not text.startswith("delays")
                and not text.startswith("inspection")
                and not text.startswith("import")
                and not text.startswith("duties")
                and not text.startswith("taxes")
                and not text.startswith("buyers")
                and not text.startswith("pay")
                and not text.startswith("brokerage")
                and not text.startswith("fees")
                and not text.startswith("payable")
                and not text.startswith("point")
                and not text.startswith("delivery")
                and not text.startswith("country's")
                and not text.startswith("office")
                and not text.startswith("offer")
                and not text.startswith("details")
                and not text.startswith("visit")
                and not text.startswith("page")
                and not text.startswith("international")
                and not text.startswith("trade")
                and not text.startswith("Located")
                and not text.startswith("Orimattila")
                and not text.startswith("Finland")
                and not text.startswith("Delivery")
                and not text.startswith("Estimated")
                and not text.startswith("between")
                and not text.startswith("Aug")
                and not text.startswith("Sep")
                and not text.startswith("to")
                and not text.startswith("estimated")
                and not text.startswith("dates")
                and not text.startswith("opens")
                and not text.startswith("new")
                and not text.startswith("window")
                and not text.startswith("tab")
                and not text.startswith("include")
                and not text.startswith("handling")
                and not text.startswith("time")
                and not text.startswith("origin")
                and not text.startswith("ZIP")
                and not text.startswith("code")
                and not text.startswith("destination")
                and not text.startswith("acceptance")
                and not text.startswith("will")
                and not text.startswith("depend")
                and not text.startswith("service")
                and not text.startswith("selected")
                and not text.startswith("receipt")
                and not text.startswith("cleared")
                and not text.startswith("payment")
                and not text.startswith("times")
                and not text.startswith("vary")
                and not text.startswith("especially")
                and not text.startswith("during")
                and not text.startswith("peak")
                and not text.startswith("periods")
                and not text.startswith("Returns")
                and not text.startswith("does")
                and not text.startswith("accept")
                and not text.startswith("details")
                and not text.startswith("more")
                and not text.startswith("information")
                and not text.startswith("returns")
                and not text.startswith("Payments")
                and not text.startswith("Special")
                and not text.startswith("financing")
                and not text.startswith("available")
                and not text.startswith("terms")
                and not text.startswith("apply")
                and not text.startswith("PayPal")
                and not text.startswith("credit")
                and not text.startswith("opens")
                and not text.startswith("new")
                and not text.startswith("window")
                and not text.startswith("tab")
                and not text.startswith("Earn")
                and not text.startswith("points")
                and not text.startswith("when")
                and not text.startswith("use")
                and not text.startswith("eBay")
                and not text.startswith("Mastercard")
                and not text.startswith("Learn")
                and not text.startswith("more")
                and not text.startswith("about")
                and not text.startswith("earning")
                and not text.startswith("points")
                and not text.startswith("Mastercard")
                and not text.startswith("As")
                and not text.startswith("low")
                and not text.startswith("as")
                and not text.startswith("month")
                and not text.startswith("Flexible")
                and not text.startswith("payments")
                and not text.startswith("with")
                and not text.startswith("no")
                and not text.startswith("surprises")
                and not text.startswith("Spread")
                and not text.startswith("cost")
                and not text.startswith("purchases")
                and not text.startswith("over")
                and not text.startswith("months")
                and not text.startswith("interest")
                and not text.startswith("rate")
                and not text.startswith("from")
                and not text.startswith("There's")
                and not text.startswith("fees")
                and not text.startswith("pay")
                and not text.startswith("time")
                and not text.startswith("How")
                and not text.startswith("works")
                and not text.startswith("Select")
                and not text.startswith("Klarna")
                and not text.startswith("payment")
                and not text.startswith("method")
                and not text.startswith("checkout")
                and not text.startswith("Confirm")
                and not text.startswith("order")
                and not text.startswith("details")
                and not text.startswith("select")
                and not text.startswith("Pay")
                and not text.startswith("Klarna")
                and not text.startswith("time")
                and not text.startswith("select")
                and not text.startswith("method")
                and not text.startswith("choose")
                and not text.startswith("klarna")
                and not text.startswith("We'll")
                and not text.startswith("take")
                and not text.startswith("klarna")
                and not text.startswith("securely")
                and not text.startswith("choose")
                and not text.startswith("preferred")
                and not text.startswith("plan")
                and not text.startswith("set")
                and not text.startswith("manage")
                and not text.startswith("payments")
                and not text.startswith("klarna")
                and not text.startswith("app")
                and not text.startswith("website")
                and not text.startswith("Purchase")
                and not text.startswith("amount")
                and not text.startswith("Sample")
                and not text.startswith("APR")
                and not text.startswith("Tax")
                and not text.startswith("shipping")
                and not text.startswith("Calculated")
                and not text.startswith("checkout")
                and not text.startswith("Subtotal")
                and not text.startswith("Estimated")
                and not text.startswith("subtotal")
                and not text.startswith("payments")
                and not text.startswith("monthly")
                and not text.startswith("payment")
                and not text.startswith("plan")
                and not text.startswith("Down")
                and not text.startswith("payment")
                and not text.startswith("required")
                and not text.startswith("Klarna")
                and not text.startswith("Monthly")
                and not text.startswith("Financing")
                and not text.startswith("issued")
                and not text.startswith("WebBank")
                and not text.startswith("Klarna")
                and not text.startswith("WebBank")
                and not text.startswith("soft")
                and not text.startswith("credit")
                and not text.startswith("check")
                and not text.startswith("assess")
                and not text.startswith("eligibility")
                and not text.startswith("will")
                and not text.startswith("impact")
                and not text.startswith("credit")
                and not text.startswith("score")
                and not text.startswith("terms")
                and not text.startswith("conditions")
                and not text.startswith("Shop")
                and not text.startswith("confidence")
                and not text.startswith("Money")
                and not text.startswith("Back")
                and not text.startswith("Guarantee")
                and not text.startswith("Get")
                and not text.startswith("ordered")
                and not text.startswith("money")
                and not text.startswith("back")
                and not text.startswith("guarantee")
                and not text.startswith("new")
                and not text.startswith("window")
                and not text.startswith("tab")
                and not text.startswith("About")
                and not text.startswith("item")
                and not text.startswith("Seller")
                and not text.startswith("assumes")
                and not text.startswith("responsibility")
                and not text.startswith("listing")
                and not text.startswith("eBay")
                and not text.startswith("number")
                and not text.startswith("Last")
                and not text.startswith("updated")
                and not text.startswith("PDT")
                and not text.startswith("View")
                and not text.startswith("revisions")
                and not text.startswith("Item")
                and not text.startswith("specifics")
                and not text.startswith("Condition")
                and not text.startswith("previously")
                and not text.startswith("details")
                and not text.startswith("imperfections")
                and not text.startswith("definitions")
                and not text.startswith("opens")
                and not text.startswith("window")
                and not text.startswith("tab")
                and not text.startswith("Seller")
                and not text.startswith("Notes")
                and not text.startswith("head")
                and not text.startswith("scratches")
                and not text.startswith("patina")
                and not text.startswith("rust")
                and not text.startswith("use")
                and not text.startswith("photos")
                and not text.startswith("Brand")
                and not text.startswith("Original")
                and not text.startswith("Reproduction")
                and not text.startswith("Vintage")
                and not text.startswith("Country")
                and not text.startswith("Region")
                and not text.startswith("Manufacture")
                and not text.startswith("Finland")
                and not text.startswith("Category")
                and not text.startswith("breadcrumb")
                and not text.startswith("Collectibles")
                and not text.startswith("Art")
                and not text.startswith("collectibles")
                and not text.startswith("Tools")
                and not text.startswith("Hardware")
                and not text.startswith("Locks")
                and not text.startswith("carpentry")
                and not text.startswith("woodworking")
                and not text.startswith("Axes")
                and not text.startswith("Hatchets")
                and not text.startswith("Item")
                and not text.startswith("description")
                and not text.startswith("seller")
                and not text.startswith("About")
                and not text.startswith("positive")
                and not text.startswith("feedback")
                and not text.startswith("items")
                and not text.startswith("sold")
                and not text.startswith("Joined")
                and not text.startswith("Usually")
                and not text.startswith("responds")
                and not text.startswith("within")
                and not text.startswith("hours")
                and not text.startswith("other")
                and not text.startswith("contact")
                and not text.startswith("save")
                and not text.startswith("feedback")
                and not text.startswith("Filter")
                and not text.startswith("All")
                and not text.startswith("ratings")
                and not text.startswith("Positive")
                and not text.startswith("Neutral")
                and not text.startswith("Negative")
                and not text.startswith("feedback")
                and not text.startswith("left")
                and not text.startswith("buyer")
                and not text.startswith("past")
                and not text.startswith("months")
                and not text.startswith("verified")
                and not text.startswith("purchase")
                and not text.startswith("great")
                and not text.startswith("description")
                and not text.startswith("communication")
                and not text.startswith("packaged")
                and not text.startswith("fair")
                and not text.startswith("price")
                and not text.startswith("shipped")
                and not text.startswith("immediately")
                and not text.startswith("pleasure")
                and not text.startswith("work")
                and not text.startswith("absolutely")
                and not text.startswith("again")
                and not text.startswith("highly")
                and not text.startswith("recommend")
                and not text.startswith("set")
                and not text.startswith("finnish")
                and not text.startswith("vintage")
                and not text.startswith("axes")
                and not text.startswith("finland")
                and not text.startswith("fantastic")
                and not text.startswith("purchase")
                and not text.startswith("good")
                and not text.startswith("shipping")
                and not text.startswith("packaging")
                and not text.startswith("described")
                and not text.startswith("great")
                and not text.startswith("value")
                and not text.startswith("deal")
                and not text.startswith("satisfied")
                and not text.startswith("described")
                and not text.startswith("answered")
                and not text.startswith("questions")
                and not text.startswith("kept")
                and not text.startswith("updated")
                and not text.startswith("process")
                and not text.startswith("Back")
                and not text.startswith("home")
                and not text.startswith("page")
                and not text.startswith("Return")
                and not text.startswith("top")
                and not text.startswith("explore")
                and not text.startswith("tomahawk")
                and not text.startswith("collectible")
                and not text.startswith("throwing")
                and not text.startswith("tactical")
                and not text.startswith("battle")
                and not text.startswith("SOG")
                and not text.startswith("Gerber")
                and not text.startswith("camping")
                and not text.startswith("Camillus")
                and not text.startswith("Plumb")
                and not text.startswith("Shop")
                and not text.startswith("top")
                and not text.startswith("sellers")
                and not text.startswith("highly")
                and not text.startswith("rated")
                and not text.startswith("products")
                and not text.startswith("hatchets")
                and not text.startswith("Best")
                and not text.startswith("sellers")
                and not text.startswith("Valley")
                and not text.startswith("american")
                and not text.startswith("hickory")
                and not text.startswith("wood")
                and not text.startswith("handle")
                and not text.startswith("Hults")
                and not text.startswith("Almike")
                and not text.startswith("lb")
                and not text.startswith("handle")
                and not text.startswith("Ames")
                and not text.startswith("Companies")
                and not text.startswith("Inc")
                and not text.startswith("true")
                and not text.startswith("temper")
                and not text.startswith("replacement")
                and not text.startswith("single")
                and not text.startswith("bit")
                and not text.startswith("Marbles")
                and not text.startswith("belt")
                and not text.startswith("rated")
                and not text.startswith("related")
                and not text.startswith("searches")
                and not text.startswith("finnish")
                and not text.startswith("made")
                and not text.startswith("sweden")
                and not text.startswith("swedish")
                and not text.startswith("swedes")
                and not text.startswith("head")
                and not text.startswith("norway")
                and not text.startswith("old")
                and not text.startswith("heads")
                and not text.startswith("fiskars")
                and not text.startswith("viking's")
                and not text.startswith("Copyright")
                and not text.startswith("Inc")
                and not text.startswith("Rights")
                and not text.startswith("reserved")
                and not text.startswith("Accessibility")
                and not text.startswith("User")
                and not text.startswith("Agreement")
                and not text.startswith("Privacy")
                and not text.startswith("Consumer")
                and not text.startswith("Health")
                and not text.startswith("Data")
                and not text.startswith("Payments")
                and not text.startswith("Terms")
                and not text.startswith("Use")
                and not text.startswith("Cookies")
                and not text.startswith("Privacy")
                and not text.startswith("Notice")
                and not text.startswith("Choices")
                and not text.startswith("AdChoice")
            ):
                return text

        return "Ingen beskrivning tillgänglig"

    def _convert_html_to_text_with_linebreaks(self, element) -> str:
        """Konvertera HTML-element till text med radbrytningar"""
        # Ersätt <br> och <br/> taggar med radbrytningar
        for br in element.find_all(["br"]):
            br.replace_with("\n")

        # Ersätt block-element med radbrytningar
        for block in element.find_all(["p", "div", "h1", "h2", "h3", "h4", "h5", "h6"]):
            if block.name != element.name:  # Undvik att ersätta själva elementet
                block.insert_before("\n")
                block.insert_after("\n")

        # Hämta text och normalisera
        text = element.get_text()
        # Ta bort extra whitespace men behåll radbrytningar
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)

    def _extract_seller_alias(self, soup: BeautifulSoup) -> str:
        """Extrahera säljarens alias från URL:en eller sidans innehåll"""
        # Först försök hitta säljar-ID:t från URL:en via "Seller's other items"-länken
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if "sid=" in href and "sch/i.html" in href:
                # Extrahera säljar-ID:t från URL:en
                match = re.search(r"sid=([^&]+)", href)
                if match:
                    seller_id = match.group(1)
                    if seller_id and len(seller_id) >= 3:
                        return seller_id

        # Fallback: leta efter säljarinformation i olika format
        seller_selectors = [
            ".mbg-nw",
            ".si-inner",
            ".mbg-l a",
            '[data-testid="seller-name"]',
            ".mbg-l",
            ".si-inner a",
            "a[href*='/usr/']",
        ]

        for selector in seller_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and len(text) < 50:
                    # Rensa bort extra text som feedback-betyg
                    cleaned_text = re.sub(r"\s*\(\d+\)", "", text)  # Ta bort (108)
                    cleaned_text = re.sub(r"\s*[,\s].*$", "", cleaned_text).strip()
                    if cleaned_text and len(cleaned_text) >= 3:
                        return cleaned_text

        # Fallback: leta efter säljarinformation i länkar
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(strip=True)

            # Om länken går till en säljarprofil
            if "/usr/" in href and text:
                cleaned_text = re.sub(r"\s*\(\d+\)", "", text)  # Ta bort (108)
                cleaned_text = re.sub(r"\s*[,\s].*$", "", cleaned_text).strip()
                if cleaned_text and len(cleaned_text) >= 3:
                    return cleaned_text

        return "Okänd säljare"

    def _extract_prices(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrahera priser med etikett (slutpris, frakt med typ)"""
        prices = []

        # 1. Slutpris - leta efter specifika texter
        price_patterns = [
            (r"sold for.*?\$(\d+(?:,\d{3})*)", "Slutpris"),
            (r"winning bid.*?\$(\d+(?:,\d{3})*)", "Vinnande bud"),
            (r"you won.*?\$(\d+(?:,\d{3})*)", "Du vann"),
            (r"final price.*?\$(\d+(?:,\d{3})*)", "Slutpris"),
            (r"US \$(\d+(?:,\d{3})*)", "Slutpris"),  # eBay:s format
            (r"\$(\d+(?:,\d{3})*)\s*US", "Slutpris"),  # Alternativt format
        ]

        page_text = soup.get_text()
        for pattern, label in price_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                try:
                    # Ta bort kommatecken från pris
                    amount_str = match.replace(",", "")
                    amount = int(amount_str)
                    if 1 <= amount <= 50000:
                        prices.append({"label": label, "amount": amount})
                except ValueError:
                    continue

        # 2. Fraktpris
        shipping_patterns = [
            (r"shipping.*?\$(\d+(?:,\d{3})*)", "Frakt"),
            (r"postage.*?\$(\d+(?:,\d{3})*)", "Frakt"),
        ]

        for pattern, label in shipping_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.replace(",", "")
                    amount = int(amount_str)
                    if 1 <= amount <= 1000:
                        prices.append({"label": label, "amount": amount})
                except ValueError:
                    continue

        # 3. Fallback: leta efter alla priser med "$" (om inget hittats)
        if not prices:
            for element in soup.find_all(text=re.compile(r"\$(\d+(?:,\d{3})*)")):
                price = self._parse_price(element)
                if price:
                    prices.append({"label": "Pris", "amount": price})

        return prices

    def _parse_price(self, price_text: str) -> Optional[int]:
        """Parsa pris från text"""
        # Leta efter siffror följt av "$" eller siffror med kommatecken
        price_patterns = [
            r"\$(\d+(?:,\d{3})*)",  # $199 eller $1,999
            r"(\d+(?:,\d{3})*)\s*\$",  # 199 $ eller 1,999 $
        ]

        for pattern in price_patterns:
            match = re.search(pattern, price_text, re.IGNORECASE)
            if match:
                try:
                    price_str = match.group(1).replace(",", "")
                    price = int(price_str)
                    # Kontrollera att priset är rimligt (1-50000)
                    if 1 <= price <= 50000:
                        return price
                except ValueError:
                    continue

        return None

    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extrahera bildURL:er från eBay-sidan"""
        images = []
        seen_bases = set()  # För att undvika duplicerade bilder

        # Först: leta efter galleribilder i specifika eBay-galleri-element
        gallery_selectors = [
            ".ux-image-carousel img",
            ".ux-image-magnify img",
            ".ux-image-gallery img",
            ".ux-image-magnify__img",
            ".ux-image-carousel__img",
            ".ux-image-gallery__img",
            ".ux-image-magnify__image",
            ".ux-image-carousel__image",
            ".ux-image-gallery__image",
        ]

        for selector in gallery_selectors:
            for img in soup.select(selector):
                src = img.get("src") or img.get("data-src")
                if src and "i.ebayimg.com" in src:
                    # Försök få högre upplösning genom att ändra storlekskoden
                    # Ersätt l140, l500, m, s med l2000 för högre upplösning
                    high_res_src = re.sub(r"/s-l\d+", "/s-l2000", src)
                    high_res_src = re.sub(r"/s-m\d+", "/s-l2000", high_res_src)
                    high_res_src = re.sub(r"/s-\d+", "/s-l2000", high_res_src)

                    # Extrahera bas-URL utan filändelse för att undvika duplicerade bilder
                    base_url = re.sub(r"\.(jpg|jpeg|webp|png)$", "", high_res_src)

                    if base_url not in seen_bases:
                        seen_bases.add(base_url)
                        # Föredra .jpg över .webp
                        if ".webp" in high_res_src:
                            jpg_version = high_res_src.replace(".webp", ".jpg")
                            images.append(jpg_version)
                        else:
                            images.append(high_res_src)

        # Om inga galleribilder hittades, fallback till generiska bilder
        if not images:
            img_selectors = [
                "img[src*='i.ebayimg.com']",
                "img[data-src*='i.ebayimg.com']",
                "img[src*='ebayimg.com']",
            ]

            for selector in img_selectors:
                for img in soup.select(selector):
                    src = img.get("src") or img.get("data-src")
                    if src and "i.ebayimg.com" in src:
                        # Försök få högre upplösning genom att ändra storlekskoden
                        high_res_src = re.sub(r"/s-l\d+", "/s-l2000", src)
                        high_res_src = re.sub(r"/s-m\d+", "/s-l2000", high_res_src)
                        high_res_src = re.sub(r"/s-\d+", "/s-l2000", high_res_src)

                        # Extrahera bas-URL utan filändelse för att undvika duplicerade bilder
                        base_url = re.sub(r"\.(jpg|jpeg|webp|png)$", "", high_res_src)

                        if base_url not in seen_bases:
                            seen_bases.add(base_url)
                            # Föredra .jpg över .webp
                            if ".webp" in high_res_src:
                                jpg_version = high_res_src.replace(".webp", ".jpg")
                                images.append(jpg_version)
                            else:
                                images.append(high_res_src)

        # Ta bort meta-bilder för att undvika duplicering
        # Meta-bilder är ofta samma som galleribilder men i annat format

        return images[:10]  # Begränsa till max 10 bilder


def parse_ebay_url(url: str) -> Dict:
    """Enkel funktion för att parsa eBay URL"""
    parser = EbayParser()
    return parser.parse_ebay_page(url)
