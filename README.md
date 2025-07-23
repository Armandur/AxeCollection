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

### Docker-integration och Unraid-deployment (2025-07-23)
- **Integrerad Docker-image** - En enda container med Nginx, Gunicorn och Django för enkel deployment
- **Unraid-optimering** - Konfigurerad för Unraid's `nobody:users` (UID 99, GID 100) och `/mnt/cache/appdata` volymer
- **Automatisk startup** - Smart startup-script som hanterar databasinitialisering, migreringar och behörigheter
- **Backup-hantering** - Integrerad backup-uppladdning via webbgränssnitt (stöd för filer upp till 2GB)
- **CSRF-fixar** - Korrekt konfiguration för HTTPS-produktion (`https://yxor.pettersson-vik.se/`)
- **Docker Hub-publishing** - Image tillgänglig som `armandur/axecollection:latest` och `armandur/axecollection:unraid`
- **Dynamisk host-konfiguration** - UI-baserad konfiguration av externa hosts och CSRF origins
- **Robust startup-process** - Fixade line endings, behörigheter och Nginx-konfiguration för stabil deployment

### Media-filhantering i produktion (2025-07-22)
- **Nginx-integration** - Konfigurerad Nginx för att servera media-filer direkt i produktion
- **Automatisk sökvägsfix** - `restore_backup.py` fixar automatiskt Windows backslashes och sökvägar vid återställning
- **Korrekt URL-generering** - Django genererar korrekta `/media/` URL:er för både yxbilder och tillverkarbilder
- **Robust deployment** - Media-filer fungerar korrekt i både utveckling och produktion
- **Docker-optimering** - Uppdaterad Docker-konfiguration med volymer för data-persistens

### Användarhantering och publik/privat vy (2025-07-21)
- **Inloggningssystem** - Fullständigt Django Auth-system med anpassade templates, långa sessioner (30 dagar) och starka lösenord (minst 12 tecken)
- **Publik/privat vy** - Konfigurerbart system där känsliga uppgifter (kontakter, priser, plattformar) kan döljas för icke-inloggade användare
- **Inställningssida** - Dedikerad sida för administratörer att konfigurera publika inställningar och sajtinformation
- **Intelligent filtrering** - Global sökning, yxlistor och transaktionsdata respekterar publika inställningar automatiskt
- **Responsiv användarupplevelse** - Login-modal, användardropdown och konsekvent navigation som anpassas efter användarstatus

### Flaggemoji för kontakter (2025-01-17)
- **Landskod-stöd** - Kontakter kan nu ha en landskod (ISO 3166-1 alpha-2) som visas som flaggemoji
- **Konsekvent visning** - Flaggemoji visas på alla ställen där kontakter visas: kontaktdetaljsidan, transaktionshistorik, tillverkardetaljsidan, statistik-sidan och kontaktlistan
- **Sökbart landsfält** - ContactForm har nu ett sökbart select-fält med flagg-emoji och landsnamn
- **Automatisk uppdatering** - Befintliga kontakter med land "Sverige" och "Finland" har uppdaterats automatiskt med rätt landskod

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

### Utvecklingsmiljö

1. Klona repot
2. Skapa virtuell miljö: `python -m venv venv`
3. Aktivera miljö: `source venv/bin/activate` (Linux/Mac) eller `venv\Scripts\activate` (Windows)
4. Installera beroenden: `pip install -r requirements.txt`
5. **Konfigurera SECRET_KEY**: Kopiera `SECRET_KEY.example` till `SECRET_KEY` och ersätt med din egen nyckel:
   ```bash
   cp SECRET_KEY.example SECRET_KEY
   # Generera ny nyckel: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
6. Kör migreringar: `python manage.py migrate`
7. Skapa superuser: `python manage.py createsuperuser`
8. Starta servern: `python manage.py runserver`

### Produktionsmiljö

**Snabb start för produktion:**
```bash
cp env.example .env
# Redigera .env och sätt SECRET_KEY
docker-compose up -d
```

**Media-filhantering:**
- Nginx serverar media-filer direkt via `/media/` URL:er
- Automatisk sökvägsfix vid backup-återställning
- Korrekt URL-generering för både yxbilder och tillverkarbilder

Se `deploy/DEPLOYMENT.md` för detaljerade instruktioner.

## Utveckling

- Kör tester: `python manage.py test`
- Samla statiska filer: `python manage.py collectstatic`
- Skapa migreringar: `python manage.py makemigrations` 