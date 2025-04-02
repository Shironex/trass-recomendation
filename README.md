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

## Struktura projektu

```
trass-recomendation/
├── src/               # Kod źródłowy aplikacji
├── data/             # Pliki danych
├── requirements.txt  # Zależności Python
├── setup.py         # Konfiguracja instalacji
├── venv/            # Środowisko wirtualne (nie jest w repozytorium)
└── TODO.md          # Lista zadań do wykonania
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