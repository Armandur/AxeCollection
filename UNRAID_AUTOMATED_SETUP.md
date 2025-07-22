# AxeCollection Unraid - Automatiserad Setup

## Översikt

AxeCollection har nu en automatiserad startup-process som hanterar:
- Databasinitialisering
- Migrations
- Behörighetsfixar
- Superuser-skapande (valfritt)

## Hur det fungerar

### 1. Startup Script (`start.sh`)

När containern startar körs `start.sh` som:

1. **Fixar behörigheter** för alla mappar (`data`, `logs`, `media`, `backups`, `staticfiles`)
2. **Kontrollerar om databasen finns**:
   - Om **INTE**: Skapar databas, kör migrations, skapar superuser (om miljövariabler är satta), importerar CSV-data
   - Om **FINNS**: Kör bara migrations som behövs
3. **Fixar databasbehörigheter** specifikt
4. **Startar supervisord** för att hantera Nginx och Gunicorn

### 2. Migrations-hantering

Scriptet använder `python manage.py migrate --plan` för att kolla om det finns nya migrations:

```bash
python manage.py migrate --plan | grep -q "No planned operations" || {
    echo "🔄 Running pending migrations..."
    python manage.py migrate
}
```

Detta betyder:
- Om inga migrations behövs: gör ingenting
- Om migrations behövs: kör dem automatiskt

### 3. Miljövariabler

Du kan sätta följande miljövariabler i `.env`-filen:

```bash
# Obligatorisk
SECRET_KEY=din_secret_key_här

# Valfria (för automatisk superuser)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=your_secure_password
```

## Deployment

### Första gången

1. Kör deploy-scriptet:
   ```bash
   ./deploy-unraid.sh
   ```

2. Uppdatera `.env`-filen med din SECRET_KEY

3. Starta containern:
   ```bash
   docker-compose up -d
   ```

### Uppdateringar

1. Hämta ny imagen:
   ```bash
   docker pull armandur/axecollection:unraid
   ```

2. Starta om:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

Scriptet kommer automatiskt att:
- Fixa alla behörigheter
- Köra nya migrations om de finns
- Behålla din data

## Felsökning

### Loggar

Kolla startup-loggar:
```bash
docker logs axecollection-axecollection-1
```

### Manuell körning

Om du behöver köra startup-scriptet manuellt:
```bash
docker exec -it axecollection-axecollection-1 /app/start.sh
```

### Databas-reset

Om du vill starta om från början:
```bash
# Stoppa containern
docker-compose down

# Ta bort databasen
rm /mnt/cache/appdata/axecollection/data/db.sqlite3

# Starta om
docker-compose up -d
```

## Fördelar

1. **Automatisk**: Inga manuella steg vid deployment
2. **Säker**: Behörigheter fixas automatiskt
3. **Flexibel**: Hanterar både nya installationer och uppdateringar
4. **Robust**: Felhantering och tydliga loggar
5. **Valfri superuser**: Kan aktiveras via miljövariabler

## Kompatibilitet

- Fungerar med befintliga installationer
- Automatisk migration-hantering
- Behåller alla data vid uppdateringar
- Kompatibel med Unraid's `nobody:users` standard (UID 99, GID 100) 