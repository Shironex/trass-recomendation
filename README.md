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

4. Zainstaluj zależności Node.js (jeśli są wymagane):
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

## Rozwój projektu

1. Utwórz nową gałąź dla swoich zmian:
```bash
git checkout -b feature/nazwa-funkcjonalnosci
```

2. Wprowadź zmiany i zatwierdź je:
```bash
git add .
git commit -m "Opis zmian"
```

3. Wypchnij zmiany do repozytorium:
```bash
git push origin feature/nazwa-funkcjonalnosci
```

## Licencja

[Określ licencję projektu]

## Kontakt

[Informacje kontaktowe] 