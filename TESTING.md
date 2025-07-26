# Testning och Kodkvalitet

## 📊 Aktuell Status

### ✅ Implementerat
- **Pytest**: 51 tester som alla passerar ✅
- **Coverage**: 36% kodtäckning (modeller + views)
- **Flake8**: Konfigurerat (42 linting-problem kvar)
- **Black**: Kodformatering konfigurerad
- **WAL-mode**: Aktiverat för SQLite i alla miljöer
- **CI/CD**: GitHub Actions pipeline konfigurerad

### 🔧 Nästa Steg

#### 1. Linting-problem (24 st)
Prioriterade problem att åtgärda:
- **C901**: För komplexa funktioner (24 st) - Medel prioritet
  - Mest komplexa: `axe_create` (37), `axe_edit` (36), `global_search` (20)
  - Kräver refaktorering av stora funktioner till mindre delar

#### 2. Utöka testtäckning
Mål: Öka från 36% till minst 70%

**Prioriterade tester att implementera:**
1. **Forms-tester** (202 rader kod, 40% täckning)
   - Validering
   - Rendering
   
2. **Management Commands** (1 000+ rader kod, 0% täckning)
   - Backup/restore
   - Import/export
   - Testdata-generering

3. **Integrationstester**
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
├── test_views.py           # ✅ 23 tester (views)
├── test_forms.py           # 🔄 Planerat
├── test_management.py      # 🔄 Planerat
└── test_integration.py     # 🔄 Planerat
```

## 🎯 Mål och KPI:er

### Kodtäckning
- **Nuvarande**: 36% (modeller + views)
- **Mål**: 70% (alla kritiska komponenter)
- **Deadline**: Iterativt under utveckling

### Linting
- **Nuvarande**: 24 problem (endast C901 - komplexa funktioner)
- **Mål**: 0 kritiska problem (F401, F841, F811) ✅ UPPNÅTT
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

1. **Omedelbart**: Refaktorera komplexa funktioner (C901) eller öka komplexitetsgränsen
2. **Kort sikt**: Implementera forms-tester
3. **Medel sikt**: Utöka till management commands
4. **Lång sikt**: Integrationstester och prestandaoptimering

---

*Senast uppdaterad: 2025-01-27* 