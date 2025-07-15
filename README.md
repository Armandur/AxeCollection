# AxeCollection

Ett Django-baserat system för att hantera och katalogisera yxsamlingar med avancerad bildhantering, måttregistrering och transaktionshantering.

## Funktioner

### Yxhantering
- Skapa, redigera och ta bort yxor
- Avancerad bildhantering med drag & drop, URL-uppladdning och .webp-optimering
- Transaktionshantering för köp och försäljning
- Kontakt- och plattformshantering med AJAX-sökning
- Filtrering och sökning med realtidsstatistik

### Måtthantering
- **Batch-mått från mallar**: Snabbt lägga till flera mått samtidigt med fördefinierade mallar
- **Enskilda mått**: Lägga till och redigera mått ett i taget
- **Dynamisk UI**: Automatisk uppdatering av räknare och tomt tillstånd
- **Mottagningsarbetsflöde**: Dedikerad process för att registrera mått vid mottagning
- **Inline-redigering**: Redigera måttvärden direkt i gränssnittet
- **Snygga notifikationer**: Visuell feedback för alla måttoperationer

### Bildhantering
- Drag & drop för bilduppladdning
- URL-uppladdning med förhandsvisning
- Automatisk .webp-konvertering för bättre prestanda
- Lightbox för bildförhandsvisning
- Drag & drop för bildordning

### Tillverkare
- Avancerad tillverkarsida med bildgalleri och länkar
- Inline-redigering av information
- Markdown-stöd för beskrivningar
- Kategoriserad bildhantering (stämplar vs övriga bilder)

### Statistik och analys
- Dedikerad statistik-dashboard med samlingsöversikt
- Topplistor för mest aktiva tillverkare, plattformar och kontakter
- Ekonomisk översikt med totala köp- och försäljningsvärden
- Realtidsstatistik som uppdateras baserat på aktiva filter

## Senaste uppdateringar

### Statistik och visualisering
- **Staplat stapeldiagram för mest aktiva månader** - Visar antal köp och sälj per månad med färgkodning (röd för köp, blå för sälj)
- **Senaste aktivitet-sektion** - Tre kort som visar de 5 senaste köpen, försäljningarna och tillagda yxorna med datum och pris/tillverkare
- **Förbättrat datumformat** - Alla datum visas nu i ISO-format (ÅÅÅÅ-MM-DD) för konsekvent formatering

### Tidigare funktioner
- **Ekonomisk stapeldiagram** - Visar transaktionsvärden per månad (köp och försäljning)
- **Linjegraf för yxor över tid** - Visar "Yxor köpta" och "Yxor i samlingen" över tid
- **Topplistor med länkar** - Länkar till yxorna från dyraste/billigaste köp/försäljningar
- **Samlingsstatistik** - Totala värden, vinstmarginal och mest aktiva tillverkare/plattformar/kontakter

## Teknisk stack

- **Backend**: Django 4.x
- **Frontend**: Bootstrap 5, JavaScript (ES6+)
- **Bildhantering**: Pillow, django-imagekit
- **Databas**: SQLite (utveckling), PostgreSQL (produktion)

## Installation

1. Klona repot
2. Skapa virtuell miljö: `python -m venv venv`
3. Aktivera miljö: `source venv/bin/activate` (Linux/Mac) eller `venv\Scripts\activate` (Windows)
4. Installera beroenden: `pip install -r requirements.txt`
5. Kör migreringar: `python manage.py migrate`
6. Skapa superuser: `python manage.py createsuperuser`
7. Starta servern: `python manage.py runserver`

## Utveckling

- Kör tester: `python manage.py test`
- Samla statiska filer: `python manage.py collectstatic`
- Skapa migreringar: `python manage.py makemigrations` 