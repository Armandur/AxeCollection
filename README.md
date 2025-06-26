# AxeCollection

AxeCollection är ett modernt Django-baserat system för att katalogisera, visa och hantera en yxsamling – komplett med bildgalleri, transaktionshistorik och tillverkardetaljer.

## Funktioner
- **Responsivt bildgalleri** med stöd för swipe och carousel
- **Lightbox** (PhotoSwipe) för att visa bilder i stort format
- **Mörkt läge** (dark mode) – följer systeminställning eller kan växlas manuellt
- **Transaktionshistorik** för varje yxa
- **Tillverkarsidor** med möjlighet till stämpelbilder
- **Sök och filtrering** (planerat)
- **Nätverksåtkomst** – kör servern på 0.0.0.0 för att nås från andra enheter i nätverket

## Snabbstart
1. Klona repot:
   ```bash
   git clone https://github.com/Armandur/AxeCollection.git
   cd AxeCollection
   ```
2. Installera beroenden:
   ```bash
   pip install -r requirements.txt
   ```
3. Starta utvecklingsservern (tillgänglig på hela nätverket):
   ```bash
   python manage.py runserver
   ```
   Gå till `http://<din-ip-adress>:8000/` i webbläsaren.

## Utvecklingstips
- Alla nya features bör utvecklas i en egen branch och PR:as mot main.
- Se TODO_FEATURES.md för planerade och pågående förbättringar.
- För att lägga till nya bilder, använd admin eller importera via CSV.
- Lightbox-funktionen finns i både galleri- och detaljvy.

## TODO & Vidareutveckling
Se [TODO_FEATURES.md](TODO_FEATURES.md) för aktuell lista över förbättringar och idéer.

## Skärmdumpar
*Lägg gärna till bilder här!*

---

Utvecklad av och för yxentusiaster. Bidrag och feedback välkomnas! 