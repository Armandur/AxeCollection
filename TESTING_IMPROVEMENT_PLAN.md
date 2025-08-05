# Testtäckningsförbättringsplan för AxeCollection

## Aktuell Status
- **Aktuell täckning**: 69%
- **Mål**: 70% (nästan uppnått!)
- **Antal tester**: 349
- **Prioritet**: Högt - vi är mycket nära målet

## Prioriterade områden för förbättring

### 1. Views med låg täckning (Högsta prioritet)

#### 1.1 `views.py` (41% täckning - 312 missade rader)
**Problematik**: Huvudvy-filen med många missade rader
**Åtgärder**:
- [ ] Testa `global_search` funktionen med olika sökparametrar
- [ ] Testa `handle_backup_upload` med olika filtyper och storlekar
- [ ] Testa felhantering för backup-uppladdning
- [ ] Testa AJAX-svar för global sökning
- [ ] Testa autentiseringshantering för olika vyer

#### 1.2 `views_manufacturer.py` (74% täckning - 142 missade rader)
**Problematik**: Tillverkare-vyer med vissa missade rader
**Åtgärder**:
- [ ] Testa hierarkisk tillverkare-hantering
- [ ] Testa bilduppladdning för tillverkare
- [ ] Testa länkhantering för tillverkare
- [ ] Testa AJAX-funktioner för tillverkare
- [ ] Testa felhantering för tillverkare-operationer

#### 1.3 `admin.py` (65% täckning - 41 missade rader)
**Problematik**: Admin-gränssnitt med vissa missade rader
**Åtgärder**:
- [ ] Testa admin-modellkonfigurationer
- [ ] Testa admin-åtgärder och list_display
- [ ] Testa admin-filtrering och sökning
- [ ] Testa anpassade admin-funktioner

#### 1.4 `context_processors.py` (67% täckning - 10 missade rader)
**Problematik**: Context processors med få missade rader
**Åtgärder**:
- [ ] Testa alla context processor-funktioner
- [ ] Testa felhantering i context processors
- [ ] Testa olika användarscenarier

### 2. Management Commands med 0% täckning

#### 2.1 `export_csv.py` (0% täckning)
**Prioritet**: Låg (gamla funktioner)
**Åtgärder**:
- [ ] Testa CSV-export för alla modeller
- [ ] Testa felhantering vid export
- [ ] Testa olika exportformat

#### 2.2 `import_csv.py` (0% täckning)
**Prioritet**: Låg (gamla funktioner)
**Åtgärder**:
- [ ] Testa CSV-import för alla modeller
- [ ] Testa validering av importdata
- [ ] Testa felhantering vid import

### 3. Utilitetsfunktioner

#### 3.1 `utils/currency_converter.py`
**Åtgärder**:
- [ ] Testa valutakonvertering med olika valutor
- [ ] Testa felhantering för API-anrop
- [ ] Testa cache-funktionalitet
- [ ] Testa offline-läge

#### 3.2 `utils/ebay_parser.py` och `utils/tradera_parser.py`
**Åtgärder**:
- [ ] Testa parsning av olika HTML-format
- [ ] Testa bildextrahering
- [ ] Testa prisparsning med olika format
- [ ] Testa felhantering för ogiltig HTML

### 4. Template Tags och Filters

#### 4.1 `templatetags/axe_filters.py`
**Åtgärder**:
- [ ] Testa alla custom template filters
- [ ] Testa felhantering i filters
- [ ] Testa olika datatyper och format

### 5. Forms med förbättringspotential

#### 5.1 `forms.py` (86% täckning - bra men kan förbättras)
**Åtgärder**:
- [ ] Testa edge cases för alla formulär
- [ ] Testa validering med ogiltig data
- [ ] Testa filuppladdning med olika filtyper
- [ ] Testa hierarkiska tillverkare i formulär

## Implementeringsplan

### Fas 1: Snabba vinster (1-2 dagar)
1. **Fixa `context_processors.py`** - Endast 10 missade rader
2. **Förbättra `admin.py`** - Endast 41 missade rader
3. **Fokusera på `views_manufacturer.py`** - 142 missade rader men högst prioritet

### ✅ Fas 0: Kompletterade framsteg (2025-01-15)
**Stamp Views-tester - KOMPLETT FIXADE!**
- **Från 9 fel till 0 fel** i `test_stamp_views.py`
- Alla stamp views-tester fungerar nu korrekt
- Fixade problem med:
  - StampImage validering (koordinater)
  - Inloggningskrav (302 redirects)
  - Template-text matchning
  - Symboluppdatering och radering
  - Yxstämpel-tilläggning (bilder krävs)
  - API-data-struktur (`data["symbols"]`)

### Lärdomar från stamp views-fixarna
- **Template-text**: Tester måste använda exakt text som visas i templaten
- **Inloggning**: Alla vyer som kräver inloggning måste testas med `self.login_user()`
- **API-struktur**: JSON-svar måste matcha faktisk API-struktur
- **Förutsättningar**: Vyer som kräver specifika data (t.ex. bilder) måste förberedas i testerna
- **Validering**: StampImage-koordinater är inte obligatoriska för `axe_mark`-typer

## Nästa steg
1. ✅ **Stamp Views-tester** - KLAR!
2. **Fixa återstående import-problem** i andra testfiler
3. **Förbättra context processor-tester** (endast 10 missade rader)
4. **Fokusera på admin.py** (endast 41 missade rader)
5. **Arbeta med views_manufacturer.py** (142 missade rader)

## Förväntad påverkan på testtäckning
- **Stamp Views**: +5-10% täckning (nu fixade)
- **Context Processors**: +1-2% täckning (10 missade rader)
- **Admin**: +2-3% täckning (41 missade rader)
- **Total förväntad förbättring**: 8-15% → **77-84% täckning** 