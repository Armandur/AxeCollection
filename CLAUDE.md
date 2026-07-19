# CLAUDE.md - AxeCollection (yxsamling)

Kodbasbeskrivning för Claude. Repot heter `AxeCollection` på GitHub
(`Armandur/AxeCollection`) men klonas lokalt som `yxsamling`.

## Vad projektet är

Django-system för att katalogisera en yxsamling: yxor, bilder, mått,
transaktioner (köp/sälj), tillverkare, kontakter, plattformar och ett
omfattande stämpelregister (stamps). Både publik och inloggad vy.

**OBS - avviker från Rasmus standardstack.** Detta är INTE FastAPI/Pico.
Det är Django + Bootstrap 5 + vanilla JS. Följ projektets befintliga
konventioner här, inte de globala FastAPI-defaulterna.

## Produktion

- Körs skarpt på TERVO2, publikt på https://yxor.pettersson-vik.se
- Deployas som integrerad Docker-image (Nginx + Gunicorn + Django i en
  container) på Unraid. Image: `armandur/axecollection` (`:latest`, `:unraid`).
- **Var varsam** - det finns riktig samlingsdata i produktion. Testa lokalt,
  be om bekräftelse innan deploy, rör inte produktionscontainern utan att fråga.

## Teknisk stack

- **Backend:** Django 5.2.3, Python
- **Frontend:** Bootstrap 5, vanilla JS (ES6+), Django-templates (Jinja-lik DTL)
- **Databas:** SQLite med WAL-mode (aktiveras i `axes/apps.py` vid start)
- **Bildhantering:** Pillow 10.4.0, django-imagekit, .webp-optimering
- **Parsers:** requests + beautifulsoup4 (eBay, Tradera)
- **Test:** pytest 8 + pytest-django, coverage (mål ~70%)
- **Kodkvalitet:** black (line-length 88), flake8, pylint

## Filstruktur

```
AxeCollection/              # Django-projektet (settings, wsgi, asgi)
  settings.py              # dev
  settings_production.py   # produktion (HTTPS)
  settings_production_http.py
  wsgi.py / wsgi_production.py / asgi.py
  urls.py                  # root urlconf -> inkluderar axes.urls
axes/                       # enda appen (stor)
  models.py                # ~1800 rader, 23 modeller (se nedan)
  urls.py                  # alla routes
  views.py                 # gemensamma/statistik/login/settings-vyer
  views_axe.py             # yxor + mått + bilder (~2150 rader)
  views_stamp.py           # stämpelregister (~2040 rader)
  views_manufacturer.py    # tillverkare
  views_contact.py / views_platform.py / views_transaction.py
  forms.py                 # alla formulär (~1580 rader)
  admin.py
  apps.py                  # aktiverar SQLite WAL
  context_processors.py    # publika inställningar globalt i templates
  templatetags/axe_filters.py   # custom template-filter, laddas via {% load axe_filters %}
  utils/                   # currency_converter, ebay_parser, tradera_parser
  management/commands/     # ~25 kommandon (testdata, backup/restore, csv, reset)
  templates/axes/          # DTL-templates (flera >2000 rader)
  static/js/               # measurement_templates.js, stamp_crop_canvas.js, stamp_search.js
  migrations/              # 54 migrations
  tests/                   # ~35 testfiler
todo-manager/               # separat Python-CLI för att hantera TODO_FEATURES.md
```

### Kärnmodeller (axes/models.py)

`Axe` (central), `AxeImage`, `Manufacturer` (hierarkisk: huvud + smeder),
`ManufacturerImage`, `ManufacturerLink`, `Measurement` + `MeasurementType`/
`MeasurementTemplate`/`MeasurementTemplateItem`, `Contact` (med landskod/
flaggemoji), `Platform`, `Transaction` (negativt pris = köp, positivt = sälj),
`Settings` (publik/privat-konfig), `NextAxeID`.

Stämpel-subsystem: `Stamp`, `StampTranscription`, `StampTag`, `StampImage`,
`AxeStamp`, `StampVariant`, `StampUncertaintyGroup`, `StampSymbol`,
`SymbolCategory`.

## Miljövariabler (env.example)

- `SECRET_KEY` (i fil `SECRET_KEY` lokalt, kopieras från `SECRET_KEY.example`)
- `DJANGO_SETTINGS_MODULE` - `AxeCollection.settings` (dev) / `...settings_production`
- `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` (komma-separerade)
- `DEMO_MODE` - automatisk testdata-generering
- Host/CSRF kan även konfigureras via UI (settings-sidan) - se HOST_CONFIGURATION.md

## Vanliga kommandon

```bash
python manage.py runserver          # dev-server
python manage.py migrate
python manage.py makemigrations
python manage.py test               # eller: pytest --cov=axes
python manage.py collectstatic
black . && flake8                   # formatering + linting
```

Management-kommandon av intresse: `generate_test_data`, `reset_to_test_data`,
`backup_database`, `restore_backup`, `import_csv`/`export_csv`,
`init_stamp_symbols`, `update_hosts`.

## Konventioner (från .cursorrules)

- Svenska i commits, dokumentation, kodkommentarer, användartexter.
- `@property` för beräknade modellfält; `related_name` på relationer.
- `select_related`/`prefetch_related` för att minska queries.
- `{% load axe_filters %}` krävs i includes som använder custom-filter.
- Platta ut nästlade listor i Python innan de skickas till templates.
- AJAX-flöden med debouncing, felhantering och feedback; Bootstrap Modal API
  i stället för browser-dialoger. Mobil-först, verifiera desktop + mobil.
- `@login_required` på skyddade vyer; känsliga uppgifter (kontakter, priser,
  plattformar) döljs för icke-inloggade via `Settings` + context processor.
- Exportera data innan större modelländringar; migrations för alla DB-ändringar.

## Todo-hantering

Historiskt via `TODO_FEATURES.md` + `todo-manager/todo_manager.py` (338 klara,
få öppna kvar). Öppna punkter migreras till backlog-verktyget
(projekt-alias `axecollection`). Nya todos: använd backlog, inte TODO_FEATURES.md.

## Dokumentation i repot

README.md, PROJECT_STRUCTURE.md, WORKFLOW_AND_COLLAB.md, TESTING.md,
DEPLOYMENT_INTEGRATED.md, HOST_CONFIGURATION.md, MEDIA_FILES_PRODUCTION.md,
STAMP_REGISTER_FEATURE.md, DOCKER_TAGGING_STRATEGY.md, CI_CD_README.md.

Uppdatera denna CLAUDE.md i samma commit när filstrukturen ändras.
