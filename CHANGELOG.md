# Changelog

Alla viktiga ändringar i AxeCollection dokumenteras i denna fil.

## [2025-07-23] - Docker-integration och Unraid-deployment

### Lagt till
- **Integrerad Docker-image** med Nginx, Gunicorn och Django i en container
- **Unraid-optimering** med korrekt UID/GID (99:100) och volymhantering
- **Automatisk startup-script** som hanterar databasinitialisering och migreringar
- **Backup-uppladdning via webbgränssnitt** med stöd för filer upp till 2GB
- **CSRF-konfiguration** för HTTPS-produktion (`https://yxor.pettersson-vik.se/`)
- **Docker Hub-publishing** av image som `armandur/axecollection:unraid`

### Ändrat
- **Nginx-konfiguration** för stora filer (`client_max_body_size 2G`)
- **Django-inställningar** för filuppladdning (`DATA_UPLOAD_MAX_MEMORY_SIZE 2GB`)
- **Supervisor-konfiguration** för korrekt användarhantering
- **Startup-process** med automatisk behörighetsfix för Unraid

### Fixat
- **Behörighetsproblem** för Unraid's `nobody:users` användare
- **CSRF-fel** för HTTPS-produktion
- **Timeout-problem** för stora backupfiler
- **JavaScript-URL-problem** i backup-uppladdning

### Tekniska detaljer
- **Dockerfile.unraid**: Multi-stage build med korrekt användarhantering
- **supervisor.unraid.conf**: Konfiguration för Django och Nginx
- **nginx.integrated.conf**: Optimerad för stora filer och HTTPS
- **start.sh**: Smart startup-script med databasinitialisering
- **settings_production_http.py**: HTTP-version för lokal testning

## [2025-07-22] - Media-filhantering i produktion

### Lagt till
- **Nginx-integration** för att servera media-filer direkt
- **Automatisk sökvägsfix** i `restore_backup.py`
- **Docker-optimering** med volymer för data-persistens

### Fixat
- **Windows backslashes** konverteras automatiskt till Linux forward slashes
- **Media-URL:er** genereras korrekt för både yxbilder och tillverkarbilder

## [2025-07-21] - Användarhantering och publik/privat vy

### Lagt till
- **Fullständigt inloggningssystem** med Django Auth
- **Publik/privat vy** med konfigurerbara inställningar
- **Inställningssida** för administratörer
- **Intelligent filtrering** baserat på användarstatus

### Ändrat
- **Session-längd** till 30 dagar för bättre användarupplevelse
- **Lösenordskrav** till minst 12 tecken
- **Navigation** anpassas efter inloggningsstatus

## [2025-01-17] - Flaggemoji för kontakter

### Lagt till
- **Landskod-stöd** (ISO 3166-1 alpha-2) för kontakter
- **Flaggemoji-visning** på alla ställen där kontakter visas
- **Sökbart landsfält** med flagg-emoji och landsnamn

### Ändrat
- **Contact-modellen** med `country_code` fält
- **Befintliga kontakter** uppdaterade med landskoder för Sverige och Finland

## [2024-12-XX] - Tidigare versioner

### Statistik och visualisering
- Ekonomiska stapeldiagram
- Linjegraf för yxor över tid
- Topplistor med länkar
- Senaste aktivitet-sektion

### Bildhantering
- Drag & drop för bilduppladdning
- URL-uppladdning med förhandsvisning
- Automatisk .webp-konvertering
- Lightbox för bildförhandsvisning

### Måtthantering
- Batch-mått från mallar
- Inline-redigering av mått
- Mottagningsarbetsflöde
- Dynamisk UI med notifikationer 