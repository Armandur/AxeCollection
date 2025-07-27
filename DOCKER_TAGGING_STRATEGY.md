# Docker Tagging Strategy för AxeCollection

## Översikt

Denna dokumentation beskriver hur Docker-imager taggas och pushas baserat på vilken branch som bygger.

## Tagging Strategi

### Branch-specifika taggar

| Branch | Docker Taggar | Beskrivning |
|--------|---------------|-------------|
| `main` | `latest`, `main` | Produktionsversion |
| `develop` | `dev`, `develop` | Utvecklingsversion |
| `feature/*` | `feature-{branch-name}` | Feature-specifika versioner |
| Övriga | `{branch-name}` | Andra branches |

### SHA-taggar

Alla builds får också en SHA-tag baserad på commit-hashen:
- **Kort SHA**: `{first-7-chars}` (t.ex. `a1b2c3d`)
- **Full SHA**: `{full-hash}` (t.ex. `a1b2c3d4e5f6...`)

## Exempel

### Main Branch
```bash
# När du pushar till main
docker push armandur/axecollection:latest
docker push armandur/axecollection:main
docker push armandur/axecollection:a1b2c3d  # SHA-tag
```

### Feature Branch
```bash
# När du pushar till feature/automatic-testing
docker push armandur/axecollection:feature-automatic-testing
docker push armandur/axecollection:a1b2c3d  # SHA-tag
```

### Develop Branch
```bash
# När du pushar till develop
docker push armandur/axecollection:dev
docker push armandur/axecollection:develop
docker push armandur/axecollection:a1b2c3d  # SHA-tag
```

## Fördelar

### 1. **Isolering**
- Feature-branches påverkar inte produktion
- Varje branch har sin egen image
- Enkel rollback till specifika commits

### 2. **Spårbarhet**
- SHA-taggar gör det möjligt att spåra exakt vilken kod som byggdes
- Branch-taggar gör det enkelt att identifiera källan

### 3. **Säkerhet**
- Endast main-branch pushar till `:latest`
- Feature-branches kan testas utan att påverka produktion

### 4. **Flexibilitet**
- Olika miljöer kan använda olika taggar
- Enkel A/B-testning med olika versioner

## Användning

### Produktion
```bash
# Använd latest för produktion
docker pull armandur/axecollection:latest
```

### Utveckling
```bash
# Använd dev för utveckling
docker pull armandur/axecollection:dev
```

### Feature-testning
```bash
# Använd specifik feature-tag
docker pull armandur/axecollection:feature-automatic-testing
```

### Specifik commit
```bash
# Använd SHA-tag för exakt version
docker pull armandur/axecollection:a1b2c3d
```

## CI/CD Integration

Denna strategi är integrerad i GitHub Actions workflow:

1. **Automatisk tag-determinering** baserat på branch
2. **SHA-taggar** för alla builds
3. **Branch-specifika taggar** för enkel identifiering

## Best Practices

### 1. **Använd rätt tag för rätt miljö**
- Produktion: `:latest`
- Staging: `:dev`
- Feature-testing: `:feature-{name}`

### 2. **Spåra SHA-taggar**
- Använd SHA-taggar för debugging
- Spara SHA-taggar i deployment-loggar

### 3. **Cleanup**
- Ta bort gamla feature-taggar regelbundet
- Behåll SHA-taggar för viktiga commits

### 4. **Dokumentation**
- Uppdatera denna dokumentation vid ändringar
- Dokumentera nya taggar i release-notes 