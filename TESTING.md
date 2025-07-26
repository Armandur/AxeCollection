# Testning och Kodkvalitet för AxeCollection

## 🧪 Automatiska Tester

### Kör tester lokalt

```bash
# Installera test-beroenden
pip install -r requirements.txt

# Kör alla tester
pytest

# Kör tester med coverage
pytest --cov=axes --cov-report=html

# Kör specifika tester
pytest axes/tests/test_models.py
pytest axes/tests/test_models.py::ManufacturerModelTest

# Kör tester med markörer
pytest -m "not slow"  # Exkludera långsamma tester
pytest -m unit        # Kör endast unit-tester
pytest -m integration # Kör endast integration-tester
```

### Teststruktur

```
axes/tests/
├── __init__.py
├── factories.py          # Testdata-factories
├── test_models.py        # Modelltester
├── test_views.py         # Vytester (framtida)
├── test_forms.py         # Formulärtester (framtida)
└── conftest.py           # Pytest-konfiguration (framtida)
```

### Testdata med Factories

Vi använder `factory-boy` för att skapa testdata:

```python
from axes.tests.factories import ManufacturerFactory, AxeFactory

# Skapa en tillverkare
manufacturer = ManufacturerFactory(name="Test Tillverkare")

# Skapa en yxa kopplad till tillverkaren
axe = AxeFactory(manufacturer=manufacturer)
```

## 🔍 Linting och Kodkvalitet

### Flake8 (Kodkvalitet)

```bash
# Kör flake8
flake8 axes/

# Kör med specifika regler
flake8 axes/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

**Regler som används:**
- `E9`: Syntax-fel
- `F63`: Felaktig användning av `is`/`is not`
- `F7`: Odefinierade variabler
- `F82`: Odefinierade namn

### Black (Kodformatering)

```bash
# Kontrollera formatering
black --check axes/

# Formatera kod automatiskt
black axes/
```

**Inställningar:**
- Radlängd: 88 tecken
- Python 3.9+ kompatibilitet
- Exkluderar migrations, media, etc.

### Pylint (Avancerad kodanalys)

```bash
# Kör pylint
pylint axes/

# Kör med specifik konfiguration
pylint --rcfile=.pylintrc axes/
```

## 📊 Coverage

### Coverage-rapporter

```bash
# Generera HTML-rapport
pytest --cov=axes --cov-report=html

# Generera XML-rapport (för CI/CD)
pytest --cov=axes --cov-report=xml

# Visa saknade rader
pytest --cov=axes --cov-report=term-missing
```

### Coverage-krav

- **Minimum**: 70% kodtäckning
- **Mål**: 80% kodtäckning
- **Exkluderade filer**: migrations, settings, manage.py

## 🚀 CI/CD Pipeline

### GitHub Actions

Vår CI/CD pipeline körs automatiskt vid:
- Push till `main`, `develop`, eller `feature/*` branches
- Pull requests till `main` eller `develop`

### Pipeline-steg

1. **Test**: Kör tester, linting och formatering
2. **Security**: Säkerhetskontroller med bandit och safety
3. **Build**: Bygger Docker-image (endast på main)

### Lokal CI-simulation

```bash
# Kör alla CI-steg lokalt
flake8 axes/
black --check axes/
pytest --cov=axes --cov-report=xml
```

## 🛠️ Utvecklingsverktyg

### Pre-commit Hooks (Rekommenderat)

Skapa `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

Installera:
```bash
pip install pre-commit
pre-commit install
```

### VS Code-inställningar

Lägg till i `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "axes/tests"
    ]
}
```

## 📝 Teststrategi

### Testpyramiden

1. **Unit-tester** (70%): Testa enskilda funktioner och metoder
2. **Integration-tester** (20%): Testa interaktion mellan komponenter
3. **End-to-end-tester** (10%): Testa hela användarflöden

### Testprioritering

1. **Kritiska funktioner**: Transaktioner, beräkningar, datavalidering
2. **Modeller**: Alla Django-modeller och deras properties
3. **Vyer**: Användarinteraktioner och formulärhantering
4. **API**: REST-endpoints (framtida)

### Testdata-hantering

- Använd factories för konsistent testdata
- Undvik hårdkodade värden
- Använd faker för realistisk data
- Rensa testdata efter varje test

## 🔧 Felsökning

### Vanliga problem

**ImportError: No module named 'axes'**
```bash
# Säkerställ att du är i rätt mapp
cd /path/to/AxeCollection
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

**Database errors**
```bash
# Skapa test-databas
python manage.py migrate --settings=AxeCollection.settings
```

**Coverage saknas**
```bash
# Kontrollera .coveragerc
# Säkerställ att rätt filer inkluderas
```

### Debugging

```bash
# Kör tester med debug-utskrift
pytest -s -v

# Kör specifikt test med debug
pytest axes/tests/test_models.py::ManufacturerModelTest::test_manufacturer_creation -s -v

# Använd pdb för debugging
pytest --pdb
```

## 📚 Resurser

- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
- [Flake8](https://flake8.pycqa.org/)
- [Black](https://black.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/) 