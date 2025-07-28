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
- Hierarkisk tillverkarsstruktur (huvudtillverkare och undertillverkare/smeder)



### Auktionsparsers
- **eBay-parser**: Automatisk extrahering av auktionsdata från eBay
- **Tradera-parser**: Automatisk extrahering av auktionsdata från Tradera
- **Stöd för flera eBay-domäner**: .com, .co.uk, .de, .se
- **Automatisk dataextrahering**: Titel, beskrivning, säljare, priser, bilder, slutdatum

### Statistik och analys
- Dedikerad statistik-dashboard med samlingsöversikt
- Topplistor för mest aktiva tillverkare, plattformar och kontakter
- Ekonomisk översikt med totala köp- och försäljningsvärden
- Realtidsstatistik som uppdateras baserat på aktiva filter

### Användarhantering
- **Fullständigt inloggningssystem** med Django Auth
- **Publik/privat vy** med konfigurerbara inställningar
- **Inställningssida** för administratörer
- **Intelligent filtrering** baserat på användarstatus
- **Demo-läge** med fördefinierade användaruppgifter

## Senaste uppdateringar



### Auktionsparsers (2025-01-XX)
- **eBay-parser** - Automatisk extrahering av auktionsdata från eBay
- **Tradera-parser** - Automatisk extrahering av auktionsdata från Tradera
- **Stöd för flera eBay-domäner** - .com, .co.uk, .de, .se
- **Automatisk dataextrahering** - Titel, beskrivning, säljare, priser, bilder, slutdatum

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

- **Backend**: Django 5.2.3
- **Frontend**: Bootstrap 5, JavaScript (ES6+)
- **Bildhantering**: Pillow 10.4.0, django-imagekit
- **Databas**: SQLite (alla miljöer) med WAL-mode för bättre prestanda och samtidighet
- **Auktionsparsers**: requests 2.31.0, beautifulsoup4 4.12.2
- **Testning**: pytest 8.0.0, pytest-django 4.8.0, coverage 7.10.0
- **Kodkvalitet**: flake8 7.0.0, black 24.1.1, pylint 3.0.3

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

**Databas-konfiguration:**
- SQLite med WAL-mode aktiverat automatiskt för bättre prestanda
- Automatisk aktivering vid Django-start via `axes/apps.py`
- Optimerad för samtidiga läs- och skrivoperationer

**Media-filhantering:**
- Nginx serverar media-filer direkt via `/media/` URL:er
- Automatisk sökvägsfix vid backup-återställning
- Korrekt URL-generering för både yxbilder och tillverkarbilder

Se `DEPLOYMENT_INTEGRATED.md` för detaljerade instruktioner.

## Testning

Projektet har en omfattande test-suite med över 200 tester:

```bash
# Kör alla tester
python manage.py test

# Kör tester med coverage
pytest --cov=axes

# Kör specifika testfiler
python manage.py test axes.tests.test_ebay_parser
python manage.py test axes.tests.test_tradera_parser
```

Se `TESTING.md` för detaljerade testinstruktioner.

## Utvecklingsverktyg

### TODO Manager
Ett kraftfullt verktyg för att hantera projektets TODO_FEATURES.md med automatisk numrering och hierarkisk struktur.

**Placering**: `todo-manager/` mappen innehåller alla relaterade filer och dokumentation.

**Snabbstart**:
```bash
cd todo-manager
python todo_manager.py stats          # Visa projektstatistik
python todo_manager.py sections       # Lista alla sektioner
python todo_manager.py list "Bildhantering" --incomplete  # Visa ofinished uppgifter
```

**Huvudfunktioner**:
- Automatisk global numrering (1, 2, 3...)
- Hierarkiska underuppgifter (5 nivåer: 42.1.2.3.4)
- Case-insensitive sektionshantering
- Batch-operationer (flera uppgifter samtidigt)
- Intelligent flytt- och organisationsfunktioner

**Viktiga kommandon**:
```bash
# Lägg till uppgifter
python todo_manager.py add "Ny uppgift" "Sektionsnamn"
python todo_manager.py add-multiple "Uppgift 1" "Uppgift 2" "Sektionsnamn"

# Markera som klara
python todo_manager.py complete 42
python todo_manager.py complete-multiple 42 43 44

# Organisera
python todo_manager.py move 42 "Målsektion"
python todo_manager.py new-section "Ny sektion"
```

Se `todo-manager/README.md` för fullständig dokumentation och `todo-manager/TODO_MANAGER_TESTING_README.md` för testinstruktioner.

## Dokumentation

### Funktioner och planering
- **[TODO_FEATURES.md](TODO_FEATURES.md)** - Komplett lista över funktioner och förbättringsförslag
- **[STAMP_REGISTER_FEATURE.md](STAMP_REGISTER_FEATURE.md)** - Detaljerad dokumentation för stämpelregister-funktionen

### Deployment och konfiguration
- **[DEPLOYMENT_INTEGRATED.md](DEPLOYMENT_INTEGRATED.md)** - Steg-för-steg deployment-guide
- **[HOST_CONFIGURATION.md](HOST_CONFIGURATION.md)** - Konfiguration av externa hosts
- **[MEDIA_FILES_PRODUCTION.md](MEDIA_FILES_PRODUCTION.md)** - Media-filhantering i produktion
- **[UNRAID_AUTOMATED_SETUP.md](UNRAID_AUTOMATED_SETUP.md)** - Automatisk Unraid-installation
- **[UNRAID_PERMISSIONS.md](UNRAID_PERMISSIONS.md)** - Behörighetshantering för Unraid

### Utveckling och testning
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Projektstruktur och arkitektur
- **[WORKFLOW_AND_COLLAB.md](WORKFLOW_AND_COLLAB.md)** - Utvecklingsarbetsflöde och samarbete
- **[TESTING.md](TESTING.md)** - Teststrategi och instruktioner
- **[UX_DESIGN_DISCUSSION.md](UX_DESIGN_DISCUSSION.md)** - UX-design och användarupplevelse

### Docker och deployment
- **[DOCKER_TAGGING_STRATEGY.md](DOCKER_TAGGING_STRATEGY.md)** - Docker image-taggningsstrategi
- **[CI_CD_README.md](CI_CD_README.md)** - CI/CD-pipeline och automation
- **[DEMO_SERVER_SETUP.md](DEMO_SERVER_SETUP.md)** - Demo-server-konfiguration

## Utveckling

- Kör tester: `python manage.py test`
- Samla statiska filer: `python manage.py collectstatic`
- Skapa migreringar: `python manage.py makemigrations`
- Kör kodkvalitetsverktyg: `flake8`, `black`, `pylint` 