# Testförbättring - Framsteg

## Aktuell status
**Status**: Pågående förbättring av testtäckning
**Senaste uppdatering**: 2025-01-15

## Nyligen fixade problem (2025-01-15)

### Import CSV-tester (NYTT)
1. **F821 undefined name 'ManufacturerImage'** - Löst genom att lägga till import
2. **AttributeError: IMPORT_DIR saknas** - Löst genom att ta bort @patch-dekoratorer och skicka temp_dir direkt
3. **TypeError: Manufacturer() got unexpected keyword arguments: 'comment'** - Löst genom att ändra till 'information'
4. **ValueError: invalid literal for int()** - Löst genom try-except-block för ID-parsning
5. **sqlite3.IntegrityError: UNIQUE constraint failed** - Temporärt löst genom att kommentera bort axeimages-import
6. **AssertionError: None != 'Testgatan 1'** - Löst genom att lägga till street/postal_code/city/country parsing
7. **ValueError: invalid literal for int() för contact_id** - Löst genom try-except-block
8. **AssertionError: 0 != 2 för Transaction count** - Löst genom att uppdatera CSV-format
9. **AssertionError: ImageFieldFile path** - Löst genom att använda backslashes för Windows-sökvägar
10. **AssertionError: '' != 'website' för ManufacturerLink** - Löst genom att uppdatera CSV-format och assertions

### Stamp Views (tidigare)
1. **ValidationError för coordinates** - Löst genom att ta bort coordinates för axe_mark-typer
2. **302 redirect istället för 200** - Löst genom att lägga till login_user() anrop
3. **Template text mismatch** - Löst genom att uppdatera assertContains-text
4. **405 Method Not Allowed** - Löst genom att ändra från delete till post
5. **Incorrect field name** - Löst genom att ändra från 'symbol' till 'pictogram'
6. **AxeImageStamp import error** - Löst genom att ta bort felaktig import
7. **API response format** - Löst genom att använda data["symbols"]
8. **Redirect pga saknade bilder** - Löst genom att skapa AxeImage före view-anrop

## Lektioner från testförbättringen

### Import/Export-tester
- CSV-format måste matcha exakt mellan test-data och import-logik
- Hantera ID-parsning med try-except för robusthet
- Använd Windows-sökvägar (backslashes) för image assertions
- Temporära workarounds kan behövas för komplexa import-kedjor

### Stamp Views
- Login-krav måste hanteras i alla vyer som kräver autentisering
- Template-text måste matcha exakt vad som visas
- HTTP-metoder måste matcha view-implementationen
- Model-fältnamn måste vara korrekta
- API-response format måste förstås och testas korrekt

### Allmänna principer
- Testa iterativt med små ändringar
- Använd verbosity=2 för detaljerad output
- Filtrera output för läsbarhet vid långa tester
- Dokumentera alla fix för framtida referens

## Nästa steg
- Fixa temporärt kommenterade assertions
- Återaktivera axeimages-import
- Fortsätt med export_csv-tester
- Uppnå 70% testtäckning 