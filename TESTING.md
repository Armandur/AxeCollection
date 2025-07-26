# Testning och Kodkvalitet

## 📊 Aktuell Status

### ✅ Implementerat
- **Pytest**: 28 modelltester som alla passerar
- **Coverage**: 15% kodtäckning (modeller)
- **Flake8**: Konfigurerat (152 linting-problem identifierade)
- **Black**: Kodformatering konfigurerad
- **WAL-mode**: Aktiverat för SQLite i alla miljöer
- **CI/CD**: GitHub Actions pipeline konfigurerad

### 🔧 Nästa Steg

#### 1. Linting-problem (152 st)
Prioriterade problem att åtgärda:
- **F401**: Oanvända imports (73 st) - Hög prioritet
- **F841**: Oanvända variabler (24 st) - Hög prioritet  
- **F811**: Redefinition av variabler (16 st) - Hög prioritet
- **C901**: För komplexa funktioner (24 st) - Medel prioritet
- **E722**: Bara `except` utan specifik exception (11 st) - Medel prioritet
- **F541**: F-string utan placeholders (4 st) - Låg prioritet

#### 2. Utöka testtäckning
Mål: Öka från 15% till minst 70%

**Prioriterade tester att implementera:**
1. **Views-tester** (530 rader kod, 0% täckning)
   - Formulärhantering
   - Autentisering
   - API-endpoints
   
2. **Forms-tester** (203 rader kod, 0% täckning)
   - Validering
   - Rendering
   
3. **Management Commands** (1 000+ rader kod, 0% täckning)
   - Backup/restore
   - Import/export
   - Testdata-generering

4. **Integrationstester**
   - Fullständiga arbetsflöden
   - Databasoperationer

## 🛠️ Verktyg och Konfiguration

### Pytest
```bash
# Kör alla tester
python -m pytest

# Kör med coverage
python -m pytest --cov=axes --cov-report=term-missing

# Kör specifika tester
python -m pytest axes/tests/test_models.py -v
```

### Linting
```bash
# Kör flake8
python -m flake8 axes/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

# Kör black (formatering)
python -m black --check axes/
```

### Coverage
```bash
# Generera HTML-rapport
python -m pytest --cov=axes --cov-report=html

# Öppna rapporten
start htmlcov/index.html
```

## 📁 Teststruktur

```
axes/tests/
├── __init__.py
├── test_models.py          # ✅ 28 tester (modeller)
├── test_views.py           # 🔄 Planerat
├── test_forms.py           # 🔄 Planerat
├── test_management.py      # 🔄 Planerat
└── test_integration.py     # 🔄 Planerat
```

## 🎯 Mål och KPI:er

### Kodtäckning
- **Nuvarande**: 15% (endast modeller)
- **Mål**: 70% (alla kritiska komponenter)
- **Deadline**: Iterativt under utveckling

### Linting
- **Nuvarande**: 152 problem
- **Mål**: 0 kritiska problem (F401, F841, F811)
- **Deadline**: Innan nästa release

### Testprestanda
- **Nuvarande**: 28 tester på ~30 sekunder
- **Mål**: <60 sekunder för alla tester
- **Deadline**: Kontinuerligt

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/ci.yml
jobs:
  test:
    - Linting (flake8)
    - Formatering (black)
    - Tester (pytest)
    - Coverage-rapport
    - Docker build
```

### Lokal CI-simulation
```bash
# Kör alla CI-steg lokalt
python -m flake8 axes/
python -m black --check axes/
python -m pytest --cov=axes --cov-report=xml
```

## 📝 Testdata-hantering

- Använd `generate_test_data` för realistisk testdata
- Undvik hårdkodade värden
- Använd befintlig data från management command
- Rensa testdata efter varje test med `--clear` flaggan

## 🔧 Felsökning

### Vanliga problem
1. **Django settings inte konfigurerade**
   ```bash
   export DJANGO_SETTINGS_MODULE=AxeCollection.settings
   ```

2. **Databasproblem**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

3. **Import-problem**
   ```bash
   python -m pytest --import-mode=importlib
   ```

### Debugging
```bash
# Kör tester med debug-output
python -m pytest -v -s

# Kör specifikt test med debug
python -m pytest axes/tests/test_models.py::ManufacturerModelTest::test_manufacturer_creation -v -s
```

## 📚 Resurser

- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Flake8](https://flake8.pycqa.org/)
- [Black](https://black.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

## 🚀 Nästa Aktioner

1. **Omedelbart**: Fixa kritiska linting-problem (F401, F841, F811)
2. **Kort sikt**: Implementera views-tester
3. **Medel sikt**: Utöka till forms och management commands
4. **Lång sikt**: Integrationstester och prestandaoptimering

---

*Senast uppdaterad: 2025-01-27* 