# AxeCollection

Ett Django-baserat system för att hantera och katalogisera yxsamlingar med avancerad bildhantering, måttregistrering och transaktionshantering.

## Funktioner

### Yxhantering
- Skapa, redigera och ta bort yxor
- Avancerad bildhantering med drag & drop, URL-uppladdning och .webp-optimering
- Transaktionshantering för köp och försäljning
- Kontakt- och plattformshantering med AJAX-sökning

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