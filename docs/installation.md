# Instalacja

Na tej stronie znajdziesz szczegółowe instrukcje dotyczące instalacji i konfiguracji projektu Trass Recommendation.

## Wymagania systemowe

Przed rozpoczęciem instalacji upewnij się, że spełniasz następujące wymagania:

- Python 3.8 lub nowszy
- Node.js 20.0.0 lub nowszy
- pnpm 9.12.3 lub nowszy
- Git (do klonowania repozytorium)

## Krok 1: Klonowanie repozytorium

Aby pobrać kod źródłowy, wykonaj następujące polecenia w terminalu:

```bash
git clone [adres-repozytorium]
cd trass-recomendation
```

## Krok 2: Utworzenie i aktywacja środowiska wirtualnego

Zalecamy korzystanie z wirtualnego środowiska Python, aby uniknąć konfliktów z innymi projektami.

### Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

### Linux/MacOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Krok 3: Instalacja zależności Python

Po aktywacji środowiska wirtualnego zainstaluj wymagane pakiety:

```bash
pip install -r requirements.txt
```

## Krok 4: Instalacja pakietu w trybie edycyjnym

Zainstaluj pakiet w trybie edycyjnym, co ułatwi pracę nad kodem:

```bash
pip install -e .
```

## Krok 6: Instalacja zależności JavaScript/TypeScript

Projekt wykorzystuje TypeScript i VitePress do dokumentacji, zainstaluj zależności za pomocą pnpm:

```bash
pnpm install
```

## Zarządzanie zależnościami

Projekt wykorzystuje plik `setup.py` do zarządzania zależnościami Python. Możesz zainstalować:

1. Podstawowe zależności:
```bash
pip install -e .
```

2. Zależności deweloperskie/testowe:
```bash
pip install -e ".[dev]"
```

3. Zależności do budowania pliku EXE:
```bash
pip install -e ".[build]"
```

## Główne zależności

### Zależności Python:
- PyQt6 >= 6.6.1 - biblioteka do tworzenia interfejsu graficznego

### Zależności deweloperskie Python:
- pytest >= 7.0.0 - framework do testów jednostkowych
- pytest-cov >= 4.0.0 - rozszerzenie do analizy pokrycia kodu testami

### Zależności do budowania EXE:
- pyinstaller >= 6.0.0 - narzędzie do tworzenia plików EXE
- pillow >= 9.0.0 - biblioteka do przetwarzania obrazów (dla ikon)
- colorama >= 0.4.6 - obsługa kolorowych logów w konsoli

### Zależności JavaScript/TypeScript:
- VitePress 1.6.3 - generator statycznej dokumentacji
- TypeScript 5.3.3 - język programowania będący nadzbiorem JavaScript
- Vue 3.4.15 - framework do tworzenia interfejsów użytkownika

## Aktualizacja zależności

Aby zaktualizować lub dodać nowe zależności, możesz zmodyfikować pliki:
- `setup.py` - dla głównych zależności pakietu Python
- `requirements.txt` - dla bezpośrednich zależności Python
- `package.json` - dla zależności JavaScript/TypeScript

## Następne kroki

Po pomyślnej instalacji możesz przejść do:
- [Uruchamiania aplikacji](/running)
- [Zapoznania się ze strukturą projektu](/structure)
- [Budowania aplikacji jako plik EXE](/building-exe) (tylko Windows)
- [Uruchamiania testów](/testing) 