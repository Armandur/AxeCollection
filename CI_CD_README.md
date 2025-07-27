# CI/CD Pipeline för AxeCollection

## Översikt

Denna CI/CD pipeline körs automatiskt vid varje push till GitHub och säkerställer kodkvalitet, säkerhet och funktionalitet.

## Workflow-steg

### 1. Test Job
- **Körs på**: Ubuntu Latest
- **Python-version**: 3.11
- **Steg**:
  - Installerar dependencies från `requirements.txt`
  - Kör linting med flake8
  - Kontrollerar kodformatering med black
  - Kör alla tester med Django's testrunner
  - Genererar coverage-rapport (75% täckning)
  - Laddar upp coverage till Codecov
  - Sparar HTML coverage-rapport som artifact

### 2. Security Job
- **Körs på**: Ubuntu Latest
- **Väntar på**: Test job completion
- **Steg**:
  - Kör säkerhetsscanning med bandit
  - Kontrollerar kända säkerhetsproblem med safety
  - Sparar säkerhetsrapporter som artifacts

### 3. Build Job
- **Körs på**: Ubuntu Latest
- **Väntar på**: Test och Security job completion
- **Körs endast på**: main branch
- **Steg**:
  - Bygger Docker image
  - Loggar in på Docker Hub
  - Pushar image med taggar: `latest` och `unraid`

## Coverage-rapport

- **Total täckning**: 75%
- **427 tester** passerar
- **3 tester** hoppas över (kända begränsningar med file uploads)

### Högsta täckning (90%+)
- `axes/templatetags/axe_filters.py`: 98%
- `axes/views_transaction.py`: 97%
- `axes/management/commands/generate_test_data.py`: 96%
- `axes/models.py`: 91%

### Låg täckning (under 50%)
- `axes/management/commands/export_csv.py`: 0%
- `axes/management/commands/import_csv.py`: 0%

## Konfiguration

### GitHub Secrets
Följande secrets måste konfigureras i GitHub repository settings:

- `DOCKER_USERNAME`: Docker Hub användarnamn
- `DOCKER_PASSWORD`: Docker Hub lösenord/token

### Lokal testning
För att testa workflow lokalt:

```bash
# Kör tester med coverage
python -m coverage run --source='.' manage.py test
python -m coverage report
python -m coverage html

# Kör linting
python -m flake8 axes/ --count --select=E9,F63,F7,F82 --show-source --statistics
python -m flake8 axes/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

# Kontrollera kodformatering
python -m black --check axes/
```

## Artifacts

Pipeline genererar följande artifacts:
- **coverage-report**: HTML-rapport med detaljerad testtäckning
- **security-reports**: JSON-rapporter från säkerhetsscanning

## Nästa steg

1. ✅ **81.1** Skapa GitHub Actions workflow för automatisk testning
2. ⏳ **81.2** Konfigurera Docker build och push i CI/CD
3. ⏳ **81.3** Lägg till test coverage reporting i CI/CD
4. ⏳ **81.4** Konfigurera automatisk deployment till testmiljö

## Felsökning

### Vanliga problem
1. **Test failures**: Kontrollera att alla tester passerar lokalt
2. **Coverage regression**: Se till att nya kod har tillräcklig testtäckning
3. **Docker build failures**: Verifiera att Dockerfile fungerar lokalt
4. **Security warnings**: Granska säkerhetsrapporter och åtgärda problem

### Loggar
Alla workflow-loggar finns tillgängliga i GitHub Actions-fliken i repository. 