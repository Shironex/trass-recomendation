# Budowanie aplikacji jako plik EXE

Na tej stronie znajdziesz szczegółowe instrukcje dotyczące budowania aplikacji Trass Recommendation jako samodzielny plik wykonywalny EXE dla systemów Windows.

## Wprowadzenie

Zbudowanie aplikacji jako plik EXE pozwala na dystrybucję oprogramowania do użytkowników końcowych bez konieczności instalowania przez nich Pythona i wymaganych zależności. Uzyskany plik EXE zawiera wszystkie potrzebne składniki i może być uruchamiany na dowolnym komputerze z systemem Windows.

## Wymagania

Przed rozpoczęciem procesu budowania upewnij się, że masz:

- Python 3.8 lub nowszy
- Zainstalowane następujące pakiety:
  - PyInstaller (do tworzenia pliku EXE)
  - Pillow (do generowania ikony)
  - Colorama (do kolorowych logów)

## Instalacja wymaganych zależności

Możesz zainstalować wymagane zależności na kilka sposobów:

```bash
# Sposób 1: Bezpośrednia instalacja wymaganych pakietów
pip install colorama pyinstaller pillow

# Sposób 2: Instalacja za pomocą setup.py (zalecane)
pip install -e ".[build]"
```

## Narzędzia do budowania

Wszystkie narzędzia do budowania aplikacji jako plik EXE znajdują się w module `src.tools`. Zawiera on dwa główne komponenty:

1. **build_exe.py** - skrypt do budowania aplikacji jako plik EXE
2. **create_icon.py** - skrypt do generowania ikony aplikacji

### Generowanie ikony aplikacji

Możesz wygenerować ikonę aplikacji bez budowania całej aplikacji:

```bash
# Sposób 1: Uruchomienie bezpośrednio jako moduł Python
python -m src.tools.create_icon

# Sposób 2: Używając skrótu komendy (po instalacji z setup.py)
trass-create-icon
```

Dodatkowe opcje dla generowania ikony:

```bash
# Określenie niestandardowej ścieżki wyjściowej
trass-create-icon --output path/to/icon.ico

# Określenie niestandardowych rozmiarów (domyślnie: 16, 32, 48, 64, 128, 256)
trass-create-icon --sizes 32 64 128

# Tryb cichy (mniej komunikatów)
trass-create-icon --quiet
```

Wygenerowana ikona zostanie zapisana domyślnie w katalogu `src/tools/resources/`.

### Budowanie aplikacji jako plik EXE

Aby zbudować aplikację jako plik EXE, użyj jednego z poniższych poleceń:

```bash
# Sposób 1: Uruchomienie bezpośrednio jako moduł Python
python -m src.tools.build_exe --onefile --clean --generate-icon

# Sposób 2: Używając skrótu komendy (po instalacji z setup.py)
trass-build-exe --onefile --clean --generate-icon
```

Dostępne opcje:

```bash
# Budowanie jako pojedynczy plik EXE (zalecane dla dystrybucji)
trass-build-exe --onefile --clean --generate-icon

# Budowanie jako katalog z zależnościami (szybsze uruchamianie)
trass-build-exe --clean --generate-icon

# Budowanie z konsolą (do debugowania)
trass-build-exe --onefile --console --clean --generate-icon

# Budowanie bez ponownego generowania ikony
trass-build-exe --onefile --clean
```

## Lokalizacja pliku EXE

Po pomyślnym zakończeniu procesu budowania, plik EXE (lub katalog z aplikacją) znajdziesz w katalogu `dist/`:

- Pojedynczy plik EXE: `dist/TrassRecommendation.exe`