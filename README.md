# Trass Recommendation System

System rekomendacji tras oparty na PyQt6.

## Wymagania systemowe

- Python 3.8 lub nowszy
- pnpm (menedżer pakietów)

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone [adres-repozytorium]
cd trass-recomendation
```

2. Utwórz i aktywuj środowisko wirtualne:

Na Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

Na Linux/MacOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Zainstaluj zależności Python:
```bash
pip install -r requirements.txt
```

4. Zainstaluj pakiet w trybie edycyjnym:
```bash
pip install -e .
```

5. Zainstaluj zależności Node.js (jeśli są wymagane):
```bash
pnpm install
```

## Zarządzanie zależnościami

Projekt wykorzystuje plik `setup.py` do zarządzania zależnościami. Zalety tego rozwiązania:

1. Instalacja podstawowych zależności:
```bash
pip install -e .
```

2. Instalacja zależności deweloperskich/testowych:
```bash
pip install -e ".[dev]"
```

Główne zależności projektu:
- PyQt6 >= 6.6.1 - biblioteka do tworzenia interfejsu graficznego

Zależności deweloperskie:
- pytest >= 7.0.0 - framework do testów jednostkowych
- pytest-cov >= 4.0.0 - rozszerzenie do analizy pokrycia kodu testami

Możesz również dodać lub zaktualizować zależności, modyfikując pliki `setup.py` i `requirements.txt`.

## Struktura projektu

```
trass-recomendation/
├── src/                # Kod źródłowy aplikacji
├── tests/              # Testy aplikacji
├── data/               # Pliki danych
├── requirements.txt    # Zależności Python
├── setup.py           # Konfiguracja instalacji
├── venv/              # Środowisko wirtualne (nie jest w repozytorium)
└── TODO.md            # Lista zadań do wykonania
```

## Uruchomienie aplikacji

1. Upewnij się, że środowisko wirtualne jest aktywne:
```bash
# Windows
.\venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

2. Uruchom aplikację:
```bash
python src/main.py
```

## Uruchamianie testów

Aby uruchomić testy jednostkowe, należy wykonać następujące kroki:

1. Upewnić się, że zainstalowane są wszystkie zależności testowe:
```bash
pip install -e ".[dev]"
```

2. Uruchomić testy przy użyciu pytest:
```bash
# Uruchomienie wszystkich testów
pytest

# Uruchomienie testów z określonego modułu
pytest tests/test_weather_data.py

# Uruchomienie testów z pokryciem kodu
pytest --cov=src tests/
```

## Rozwiązywanie problemów

### Problem z importami

Jeśli występuje błąd `ModuleNotFoundError: No module named 'src'`, upewnij się, że:

1. Pakiet został zainstalowany w trybie edycyjnym:
```bash
pip install -e .
```

2. Środowisko wirtualne jest aktywne

3. Jesteś w głównym katalogu projektu podczas uruchamiania aplikacji

## Licencja

[Określ licencję projektu]

## Kontakt

[Informacje kontaktowe] 